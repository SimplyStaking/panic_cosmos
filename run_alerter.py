import concurrent.futures
import sys
from typing import List, Tuple

from src.alerting.alert_utils.get_channel_set import get_full_channel_set
from src.alerting.alert_utils.get_channel_set import \
    get_periodic_alive_reminder_channel_set
from src.alerting.alerts.alerts import TerminatedDueToExceptionAlert
from src.alerting.periodic.periodic import periodic_alive_reminder
from src.commands.handlers.telegram import TelegramCommands
from src.monitoring.monitor_utils.get_json import get_cosmos_json, get_json
from src.monitoring.monitors.github import GitHubMonitor
from src.monitoring.monitors.monitor_starters import start_node_monitor, \
    start_network_monitor, start_github_monitor
from src.monitoring.monitors.network import NetworkMonitor
from src.monitoring.monitors.node import NodeMonitor
from src.node.node import Node, NodeType
from src.utils.config_parsers.internal_parsed import InternalConf, \
    INTERNAL_CONFIG_FILE_FOUND, INTERNAL_CONFIG_FILE
from src.utils.config_parsers.user import NodeConfig, RepoConfig
from src.utils.config_parsers.user_parsed import UserConf, \
    MISSING_USER_CONFIG_FILES
from src.utils.exceptions import InitialisationException
from src.utils.logging import create_logger
from src.utils.redis_api import RedisApi


def log_and_print(text: str):
    logger_general.info(text)
    print(text)


def node_from_node_config(node_config: NodeConfig):
    # Test connection
    log_and_print('Trying to connect to {}/status'
                  ''.format(node_config.node_rpc_url))
    try:
        node_status = get_cosmos_json(node_config.node_rpc_url + '/status',
                                      logger_general)
        log_and_print('Success.')
    except Exception:
        raise InitialisationException('Failed to connect to {} at {}'.format(
            node_config.node_name, node_config.node_rpc_url))

    # Get node type
    node_type = NodeType.VALIDATOR_FULL_NODE \
        if node_config.node_is_validator \
        else NodeType.NON_VALIDATOR_FULL_NODE

    # Get pubkey if validator
    if node_config.node_is_validator:
        pubkey = node_status['validator_info']['address']
    else:
        pubkey = None

    # Get network
    network = node_status['node_info']['network']

    # Initialise node and load any state
    node = Node(node_config.node_name, node_config.node_rpc_url,
                node_type, pubkey, network, REDIS)
    node.load_state(logger_general)

    # Return node
    return node


def test_connection_to_github_pages():
    for repo in UserConf.filtered_repos:
        # Get releases page
        releases_page = InternalConf.github_releases_template.format(
            repo.repo_page)

        # Test connection
        log_and_print('Trying to connect to {}'.format(releases_page))
        try:
            releases = get_json(releases_page, logger_general)
            if 'message' in releases and releases['message'] == 'Not Found':
                raise InitialisationException(
                    'Successfully reached {} but URL is '
                    'not valid.'.format(releases_page))
            else:
                log_and_print('Success.')
        except Exception:
            raise InitialisationException('Could not reach {}.'
                                          ''.format(releases_page))


def run_monitor_nodes(node: Node):
    # Monitor name based on node
    monitor_name = 'Node monitor ({})'.format(node.name)

    # Logger initialisation
    logger_monitor_node = create_logger(
        InternalConf.node_monitor_general_log_file_template.format(node.name),
        node.name, InternalConf.logging_level, rotating=True)

    # Initialise monitor
    node_monitor = NodeMonitor(monitor_name, full_channel_set,
                               logger_monitor_node, REDIS, node)

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        sys.stdout.flush()
        try:
            start_node_monitor(node_monitor,
                               InternalConf.node_monitor_period_seconds,
                               logger_monitor_node)
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_monitor_network(network_nodes_tuple: Tuple[str, List[Node]]):
    # Get network and nodes
    network = network_nodes_tuple[0]
    nodes = network_nodes_tuple[1]

    # Monitor name based on network
    monitor_name = 'Network monitor ({})'.format(network)

    # Initialisation
    try:
        # Logger initialisation
        logger_monitor_network = create_logger(
            InternalConf.network_monitor_general_log_file_template.format(
                network), network, InternalConf.logging_level, rotating=True)

        # Organize as validators and full nodes
        validators = [n for n in nodes if n.is_validator]
        full_nodes = [n for n in nodes if not n.is_validator]

        # Do not start if not enough nodes
        if 0 in [len(validators), len(full_nodes)]:
            log_and_print('!!! Could not start {}. It must have at least 1 '
                          'validator and 1 full node!!!'.format(monitor_name))
            return

        # Initialise monitor
        network_monitor = NetworkMonitor(monitor_name, full_channel_set,
                                         logger_monitor_network,
                                         InternalConf.
                                         network_monitor_max_catch_up_blocks,
                                         REDIS, full_nodes, validators)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started with {} validator(s) and {} full node(s).'
                      ''.format(monitor_name, len(validators), len(full_nodes)))
        sys.stdout.flush()
        try:
            start_network_monitor(network_monitor,
                                  InternalConf.network_monitor_period_seconds,
                                  logger_monitor_network)
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_commands_telegram():
    # Fixed monitor name
    monitor_name = 'Telegram commands'

    # Check if Telegram commands enabled
    if not UserConf.telegram_cmds_enabled:
        return

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        sys.stdout.flush()
        try:
            TelegramCommands(
                UserConf.telegram_cmds_bot_token,
                UserConf.telegram_cmds_bot_chat_id,
                logger_commands_telegram, REDIS,
                InternalConf.redis_twilio_snooze_key,
                InternalConf.redis_periodic_alive_reminder_mute_key,
                InternalConf.redis_node_monitor_alive_key_prefix,
                InternalConf.redis_network_monitor_alive_key_prefix,
                InternalConf.redis_network_monitor_last_height_key_prefix,
            ).start_listening()
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_monitor_github(repo_config: RepoConfig):
    # Monitor name based on repository
    monitor_name = 'GitHub monitor ({})'.format(repo_config.repo_name)

    # Initialisation
    try:
        # Logger initialisation
        logger_monitor_github = create_logger(
            InternalConf.github_monitor_general_log_file_template.format(
                repo_config.repo_page.replace('/', '_')), repo_config.repo_page,
            InternalConf.logging_level, rotating=True)

        # Get releases page
        releases_page = InternalConf.github_releases_template.format(
            repo_config.repo_page)

        # Initialise monitor
        github_monitor = GitHubMonitor(
            monitor_name, full_channel_set, logger_monitor_github, REDIS,
            repo_config.repo_name, releases_page,
            InternalConf.redis_github_releases_key_prefix)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        sys.stdout.flush()
        try:
            start_github_monitor(github_monitor,
                                 InternalConf.github_monitor_period_seconds,
                                 logger_monitor_github)
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_periodic_alive_reminder():
    if not UserConf.periodic_alive_reminder_enabled:
        return

    name = "Periodic alive reminder"

    while True:
        log_and_print('{} started.'.format(name))
        try:
            periodic_alive_reminder(
                UserConf.interval_seconds,
                periodic_alive_reminder_channel_set,
                InternalConf.redis_periodic_alive_reminder_mute_key, REDIS)
        except Exception as e:
            periodic_alive_reminder_channel_set.alert_error(
                TerminatedDueToExceptionAlert(name, e))
        log_and_print('{} stopped.'.format(name))


if __name__ == '__main__':
    if not INTERNAL_CONFIG_FILE_FOUND:
        sys.exit('Config file {} is missing.'.format(INTERNAL_CONFIG_FILE))
    elif len(MISSING_USER_CONFIG_FILES) > 0:
        sys.exit('Config file {} is missing. Make sure that you run the setup '
                 'script (run_setup.py) before running the alerter.'
                 ''.format(MISSING_USER_CONFIG_FILES[0]))

    # Global loggers initialisation
    logger_redis = create_logger(
        InternalConf.redis_log_file, 'redis',
        InternalConf.logging_level)
    logger_general = create_logger(
        InternalConf.general_log_file, 'general',
        InternalConf.logging_level, rotating=True)
    logger_commands_telegram = create_logger(
        InternalConf.telegram_commands_general_log_file, 'commands_telegram',
        InternalConf.logging_level, rotating=True)
    log_file_alerts = InternalConf.alerts_log_file

    # Redis initialisation
    if UserConf.redis_enabled:
        REDIS = RedisApi(
            logger_redis, InternalConf.redis_database, UserConf.redis_host,
            UserConf.redis_port, password=UserConf.redis_password,
            namespace=UserConf.unique_alerter_identifier)
    else:
        REDIS = None

    # Alerters initialisation
    alerter_name = 'P.A.N.I.C.'
    full_channel_set = get_full_channel_set(
        alerter_name, logger_general, REDIS, log_file_alerts)
    log_and_print('Enabled alerting channels (general): {}'.format(
        full_channel_set.enabled_channels_list()))
    periodic_alive_reminder_channel_set = \
        get_periodic_alive_reminder_channel_set(alerter_name, logger_general,
                                                REDIS, log_file_alerts)
    log_and_print('Enabled alerting channels (periodic alive reminder): {}'
                  ''.format(periodic_alive_reminder_channel_set.
                            enabled_channels_list()))
    sys.stdout.flush()

    # Nodes initialisation
    try:
        nodes = [node_from_node_config(n) for n in UserConf.filtered_nodes]
    except InitialisationException as ie:
        logger_general.error(ie)
        sys.exit(ie)

    # Organize nodes into lists according to how they will be monitored
    node_monitor_nodes = []
    network_monitor_nodes = []
    for node, node_conf in zip(nodes, UserConf.filtered_nodes):
        if node_conf.include_in_node_monitor:
            node_monitor_nodes.append(node)
        if node_conf.include_in_network_monitor:
            network_monitor_nodes.append(node)

    # Get unique networks and group nodes by network
    unique_networks = {n.network for n in network_monitor_nodes}
    nodes_by_network = {net: [node for node in network_monitor_nodes
                              if node.network == net]
                        for net in unique_networks}

    # Test connection to GitHub pages
    try:
        test_connection_to_github_pages()
    except InitialisationException as ie:
        logger_general.error(ie)
        sys.exit(ie)

    # Run monitors
    monitor_node_count = len(node_monitor_nodes)
    monitor_network_count = len(unique_networks)
    monitor_github_count = len(UserConf.filtered_repos)
    commands_telegram_count = 1
    periodic_alive_reminder_count = 1
    total_count = sum([monitor_node_count, monitor_network_count,
                       monitor_github_count, commands_telegram_count,
                       periodic_alive_reminder_count])
    with concurrent.futures.ThreadPoolExecutor(max_workers=total_count) \
            as executor:
        executor.map(run_monitor_nodes, node_monitor_nodes)
        executor.map(run_monitor_network, nodes_by_network.items())
        executor.map(run_monitor_github, UserConf.filtered_repos)
        executor.submit(run_commands_telegram)
        executor.submit(run_periodic_alive_reminder)
