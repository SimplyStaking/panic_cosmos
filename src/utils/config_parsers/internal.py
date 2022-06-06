import configparser
import sys
from datetime import timedelta

from src.utils.config_parsers.config_parser import ConfigParser


def to_bool(bool_str: str) -> bool:
    return bool_str.lower() in ['true', 'yes', 'y']


class InternalConfig(ConfigParser):
    # Use internal_parsed.py rather than creating a new instance of this class
    def __init__(self, config_file_path: str) -> None:
        super().__init__([config_file_path])

        cp = configparser.ConfigParser()
        cp.read(config_file_path)

        # [logging]
        section = cp['logging']
        self.logging_level = section['logging_level']

        self.telegram_commands_general_log_file = section[
            'telegram_commands_general_log_file']
        self.github_monitor_general_log_file_template = section[
            'github_monitor_general_log_file_template']
        self.network_monitor_general_log_file_template = section[
            'network_monitor_general_log_file_template']
        self.node_monitor_general_log_file_template = section[
            'node_monitor_general_log_file_template']

        self.alerts_log_file = section['alerts_log_file']
        self.redis_log_file = section['redis_log_file']
        self.general_log_file = section['general_log_file']

        # [twilio]
        section = cp['twilio']
        self.twiml = section['twiml']
        self.twiml_is_url = to_bool(section['twiml_is_url'])

        # [redis]
        section = cp['redis']
        self.redis_database = int(section['redis_database'])
        self.redis_test_database = int(section['redis_test_database'])

        self.redis_twilio_snooze_key = section['redis_twilio_snooze_key']
        self.redis_github_releases_key_prefix = section[
            'redis_github_releases_key_prefix']
        self.redis_node_monitor_alive_key_prefix = section[
            'redis_node_monitor_alive_key_prefix']
        self.redis_network_monitor_alive_key_prefix = section[
            'redis_network_monitor_alive_key_prefix']
        self.redis_network_monitor_last_height_key_prefix = section[
            'redis_network_monitor_last_height_key_prefix']
        self.redis_periodic_alive_reminder_mute_key = \
            section['redis_periodic_alive_reminder_mute_key']

        self.redis_twilio_snooze_key_default_hours = timedelta(hours=float(
            section['redis_twilio_snooze_key_default_hours']))
        self.redis_periodic_alive_reminder_mute_key_default_hours = timedelta(
            hours=float(section['redis_periodic_alive_reminder_mute_key_'
                                'default_hours']))

        self.redis_node_monitor_alive_key_timeout = int(
            section['redis_node_monitor_alive_key_timeout'])
        self.redis_network_monitor_alive_key_timeout = int(
            section['redis_network_monitor_alive_key_timeout'])
        self.redis_network_monitor_last_height_key_timeout = int(
            section['redis_network_monitor_last_height_key_timeout'])

        # [monitoring_periods]
        section = cp['monitoring_periods']
        self.node_monitor_period_seconds = int(
            section['node_monitor_period_seconds'])
        self.network_monitor_period_seconds = int(
            section['network_monitor_period_seconds'])
        self.network_monitor_max_catch_up_blocks = int(
            section['network_monitor_max_catch_up_blocks'])
        self.github_monitor_period_seconds = int(
            section['github_monitor_period_seconds'])

        # [alert_intervals_and_limits]
        section = cp['alert_intervals_and_limits']
        self.downtime_initial_alert_delay = timedelta(seconds=int(
            section['downtime_initial_alert_delay_seconds']))
        self.downtime_reminder_interval_seconds = timedelta(seconds=int(
            section['downtime_reminder_interval_seconds']))
        self.max_missed_blocks_time_interval = timedelta(seconds=int(
            section['max_missed_blocks_interval_seconds']))
        self.max_missed_blocks_in_time_interval = int(
            section['max_missed_blocks_in_time_interval'])
        self.validator_peer_danger_boundary = int(
            section['validator_peer_danger_boundary'])
        self.validator_peer_safe_boundary = int(
            section['validator_peer_safe_boundary'])
        self._check_if_peer_safe_and_danger_boundaries_are_valid()
        self.full_node_peer_danger_boundary = int(
            section['full_node_peer_danger_boundary'])
        self.missed_blocks_danger_boundary = int(
            section['missed_blocks_danger_boundary'])
        self.github_error_interval_seconds = timedelta(seconds=int(
            section['github_error_interval_seconds']))
        self.change_in_voting_power_threshold = int(
            section['change_in_voting_power_threshold'])

        # [links]
        section = cp['links']
        self.validators_hubble_link = section['validators_hubble_link']
        self.validators_big_dipper_link = section['validators_big_dipper_link']
        self.validators_stargazer_link = section['validators_stargazer_link']
        self.validators_mintscan_link = section['validators_mintscan_link']
        self.validators_lunie_link = section['validators_lunie_link']

        self.block_hubble_link_prefix = section['block_hubble_link_prefix']
        self.block_big_dipper_link_prefix = section[
            'block_big_dipper_link_prefix']
        self.block_stargazer_link_prefix = section[
            'block_stargazer_link_prefix']
        self.block_mintscan_link_prefix = section['block_mintscan_link_prefix']
        self.block_lunie_link_prefix = section['block_lunie_link_prefix']

        self.tx_hubble_link_prefix = section['tx_hubble_link_prefix']
        self.tx_big_dipper_link_prefix = section['tx_big_dipper_link_prefix']
        self.tx_mintscan_link_prefix = section['tx_mintscan_link_prefix']

        self.github_releases_template = section['github_releases_template']

    # Safe boundary must be greater than danger boundary at all times for
    # correct execution. The >= -2 allows the following config to be valid:
    #  - safe = -1, danger = -2
    # This disables peer alerts since in any case the following will be true:
    #  - peers > safe > danger
    def _peer_safe_and_danger_boundaries_are_valid(self) -> bool:
        return self.validator_peer_safe_boundary > \
               self.validator_peer_danger_boundary >= -2

    def _check_if_peer_safe_and_danger_boundaries_are_valid(self):
        while not self._peer_safe_and_danger_boundaries_are_valid():
            print("validator_peer_safe_boundary must be STRICTLY GREATER than "
                  "validator_peer_danger_boundary, which in turn must be "
                  "greater or equal to -2 for correct execution (S > D >= -2)."
                  "\nPlease do the necessary modifications in the "
                  "config/internal_config.ini file and restart the alerter.")
            sys.exit(-1)
