import logging
from typing import Optional

from src.alerting.channels.channel import ChannelSet
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.redis_api import RedisApi


class Monitor:

    def __init__(self, monitor_name: str, channels: ChannelSet,
                 logger: logging.Logger, redis: Optional[RedisApi],
                 internal_conf: InternalConfig = InternalConf) -> None:
        super().__init__()

        self._monitor_name = monitor_name
        self._channels = channels
        self._logger = logger
        self._redis = redis
        self._internal_conf = internal_conf

    @property
    def channels(self) -> ChannelSet:
        return self._channels

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def redis(self) -> RedisApi:
        return self._redis

    @property
    def redis_enabled(self) -> bool:
        return self._redis is not None

    def load_state(self) -> None:
        pass

    def save_state(self) -> None:
        pass

    def monitor(self) -> None:
        pass
