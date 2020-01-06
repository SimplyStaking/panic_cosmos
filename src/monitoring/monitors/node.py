import logging
from datetime import datetime, timedelta
from typing import Optional

from src.alerting.channels.channel import ChannelSet
from src.monitoring.monitor_utils.get_json import get_cosmos_json
from src.monitoring.monitor_utils.live_check import live_check_unsafe
from src.monitoring.monitors.monitor import Monitor
from src.node.node import Node
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.redis_api import RedisApi


class NodeMonitor(Monitor):

    def __init__(self, monitor_name: str, channels: ChannelSet,
                 logger: logging.Logger, redis: Optional[RedisApi], node: Node,
                 internal_conf: InternalConfig = InternalConf):
        super().__init__(monitor_name, channels, logger, redis, internal_conf)
        self.node = node

        self._redis_alive_key = \
            self._internal_conf.redis_node_monitor_alive_key_prefix + \
            self._monitor_name
        self._redis_alive_key_timeout = \
            self._internal_conf.redis_node_monitor_alive_key_timeout

    def save_state(self) -> None:
        # If Redis is enabled, save the current time, indicating
        # that the node monitor was alive at this time
        if self.redis_enabled:
            self.logger.debug('Saving %s state.', self._monitor_name)

            # Set alive key (to be able to query latest update from Telegram)
            key = self._redis_alive_key
            until = timedelta(seconds=self._redis_alive_key_timeout)
            self.redis.set_for(key, str(datetime.now()), until)

    def monitor(self) -> None:
        # Check if node is accessible
        live_check_unsafe(self.node.rpc_url + '/health', self._logger)
        self.node.set_as_up(self.channels, self.logger)

        # Get status
        status = get_cosmos_json(self.node.rpc_url + '/status',
                                 self._logger)

        # Set voting power
        voting_power = int(status['validator_info']['voting_power'])
        self._logger.debug('%s voting power: %s', self.node, voting_power)
        self.node.set_voting_power(voting_power, self.channels, self.logger)

        # Set catching-up
        catching_up = status['sync_info']['catching_up']
        self._logger.debug('%s catching up: %s', self.node, catching_up)
        self.node.set_catching_up(catching_up, self.channels, self.logger)

        # Get net_info
        net_info = get_cosmos_json(self.node.rpc_url + '/net_info',
                                   self._logger)

        # Set number of peers
        no_of_peers = int(net_info['n_peers'])
        self._logger.debug('%s no. of peers: %s', self.node, no_of_peers)
        self.node.set_no_of_peers(no_of_peers, self.channels, self.logger)

        # Output status
        self._logger.info('%s status: %s', self.node, self.node.status())
