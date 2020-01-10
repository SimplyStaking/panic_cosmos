from datetime import timedelta
from time import sleep
from typing import Optional

from src.alerting.alerts.alerts import AlerterAliveAlert
from src.alerting.channels.channel import ChannelSet
from src.utils.redis_api import RedisApi


class PeriodicAliveReminder:

    def __init__(self, interval: timedelta, channel_set: ChannelSet,
                 mute_key: str, redis: Optional[RedisApi]):
        self._interval = interval
        self._channel_set = channel_set
        self._mute_key = mute_key
        self._redis = redis
        self._redis_enabled = redis is not None

    def start(self):
        while True:
            sleep(self._interval.total_seconds())
            self.send_alive_alert()

    def send_alive_alert(self) -> None:
        # If it is not the case that Redis is enabled and the reminder is muted,
        # inform the node operator that the alerter is still running.
        if not (self._redis_enabled and self._redis.exists(self._mute_key)):
            self._channel_set.alert_info(AlerterAliveAlert())
