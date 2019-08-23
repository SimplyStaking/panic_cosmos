import logging
from typing import Optional, List

from src.alerting.alerts.alerts import Alert
from src.utils.redis_api import RedisApi


class Channel:

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi]) -> None:
        self._channel_name = channel_name
        self._logger = logger
        self._redis = redis

    def alert_info(self, alert: Alert) -> None:
        pass

    def alert_minor(self, alert: Alert) -> None:
        pass

    def alert_major(self, alert: Alert) -> None:
        pass

    def alert_error(self, alert: Alert) -> None:
        pass

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def redis(self) -> RedisApi:
        return self._redis

    @property
    def redis_enabled(self) -> bool:
        return self._redis is not None


class ChannelSet:

    def __init__(self, channels: List[Channel]) -> None:
        # self._channels is not set to channels to disallow adding more
        # channels to the set by appending to the channels list directly
        self._channels = []
        for c in channels:
            self.add_channel(c)

    def enabled_channels_list(self) -> str:
        return ', '.join([type(c).__name__ for c in self._channels]) \
            if len(self._channels) > 0 else 'None'

    def add_channel(self, channel: Channel) -> None:
        self._channels.append(channel)

    def unsafe_alert_info(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_info(alert)

    def unsafe_alert_minor(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_minor(alert)

    def unsafe_alert_major(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_major(alert)

    def unsafe_alert_error(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_error(alert)

    def alert_info(self, alert: Alert) -> None:
        for c in self._channels:
            try:
                c.alert_info(alert)
            except Exception as e:
                c.logger.error('Error in alert_info of %s (%s): %s',
                               type(c).__name__, c.channel_name, e)

    def alert_minor(self, alert: Alert) -> None:
        for c in self._channels:
            try:
                c.alert_minor(alert)
            except Exception as e:
                c.logger.error('Error in alert_minor of %s (%s): %s',
                               type(c).__name__, c.channel_name, e)

    def alert_major(self, alert: Alert) -> None:
        for c in self._channels:
            try:
                c.alert_major(alert)
            except Exception as e:
                c.logger.error('Error in alert_major of %s (%s): %s',
                               type(c).__name__, c.channel_name, e)

    def alert_error(self, alert: Alert) -> None:
        for c in self._channels:
            try:
                c.alert_error(alert)
            except Exception as e:
                c.logger.error('Error in alert_error of %s (%s): %s',
                               type(c).__name__, c.channel_name, e)
