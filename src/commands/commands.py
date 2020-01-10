import logging
from typing import Optional

from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import UserConfig
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.redis_api import RedisApi


class Commands:

    def __init__(self, logger: logging.Logger, redis: Optional[RedisApi],
                 redis_snooze_key: Optional[str], redis_mute_key: Optional[str],
                 redis_node_monitor_alive_key_prefix: Optional[str],
                 redis_network_monitor_alive_key_prefix: Optional[str],
                 redis_network_monitor_last_height_key_prefix: Optional[str],
                 internal_conf: InternalConfig = InternalConf,
                 user_conf: UserConfig = UserConf) -> None:
        self._logger = logger

        self._redis = redis
        self._redis_enabled = redis is not None
        self._redis_snooze_key = redis_snooze_key
        self._redis_mute_key = redis_mute_key
        self._redis_node_monitor_alive_key_prefix = \
            redis_node_monitor_alive_key_prefix
        self._redis_network_monitor_alive_key_prefix = \
            redis_network_monitor_alive_key_prefix
        self._redis_network_monitor_last_height_key_prefix = \
            redis_network_monitor_last_height_key_prefix

        self._internal_conf = internal_conf
        self._user_conf = user_conf

    def snooze(self) -> None:
        pass

    def unsnooze(self) -> None:
        pass

    def mute(self) -> None:
        pass

    def unmute(self) -> None:
        pass

    def add_node(self) -> None:
        pass

    def remove_node(self) -> None:
        pass

    def current_nodes(self) -> None:
        pass
