from configparser import ConfigParser
from typing import Optional, List

from src.monitoring.monitor_utils.get_json import get_json
from src.utils.config_parsers.user import NodeConfig
from src.utils.logging import DUMMY_LOGGER
from src.utils.user_input import yn_prompt


def get_node(nodes_so_far: List[NodeConfig]) -> Optional[NodeConfig]:
    # Get node's name
    node_names_so_far = [n.node_name for n in nodes_so_far]
    while True:
        node_name = input('Unique node name:\n')
        if node_name in node_names_so_far:
            print('Node name must be unique.')
        else:
            break

    # Get node's RPC url
    while True:
        rpc_url = input('Node\'s RPC url (typically http://NODE_IP:26657):\n')
        print('Trying to connect to endpoint {}/health'.format(rpc_url))
        try:
            get_json(rpc_url + '/health', DUMMY_LOGGER)
            print('Success.')
            break
        except Exception:
            if not yn_prompt('Failed to connect to endpoint. Do '
                             'you want to try again? (Y/n)\n'):
                return None

    # Ask if node is a validator
    node_is_validator = yn_prompt('Is this node a validator? (Y/n)\n')

    # Return node
    return NodeConfig(node_name, rpc_url, node_is_validator, True, True)


def setup_nodes(cp: ConfigParser) -> None:
    print('==== Nodes')
    print('To produce alerts, the alerter needs something to monitor! The list '
          'of nodes to be included in the monitoring will now be set up. This '
          'includes validators, sentries, and any full nodes that can be used '
          'as a data source to monitor from the network\'s perspective. You '
          'may include nodes from multiple networks in any order; P.A.N.I.C. '
          'will figure out which network they belong to when you run it. Node '
          'names must be unique!')

    # Check if list already set up
    already_set_up = len(cp.sections()) > 0
    if already_set_up:
        if not yn_prompt(
                'The list of nodes is already set up. Do you wish '
                'to replace this list with a new one? (Y/n)\n'):
            return

    # Otherwise ask if they want to set it up
    if not already_set_up and \
            not yn_prompt('Do you wish to set up the list of nodes? (Y/n)\n'):
        return

    # Clear config and initialise new list
    cp.clear()
    nodes = []

    # Get node details and append them to the list of nodes
    while True:
        node = get_node(nodes)
        if node is not None:
            nodes.append(node)
            if node.node_is_validator:
                print('Successfully added validator node.')
            else:
                print('Successfully added full node.')

        if not yn_prompt('Do you want to add another node? (Y/n)\n'):
            break

    # Add nodes to config
    for i, node in enumerate(nodes):
        section = 'node_' + str(i)
        cp.add_section(section)
        cp[section]['node_name'] = node.node_name
        cp[section]['node_rpc_url'] = node.node_rpc_url
        cp[section]['node_is_validator'] = \
            'true' if node.node_is_validator else 'false'
        cp[section]['include_in_node_monitor'] = \
            'true' if node.include_in_node_monitor else 'false'
        cp[section]['include_in_network_monitor'] = \
            'true' if node.include_in_network_monitor else 'false'
