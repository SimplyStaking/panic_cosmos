from datetime import timedelta
from time import sleep

from src.alerting.alerts.alerts import AlerterAliveAlert
from src.alerting.channels.channel import ChannelSet
from src.utils.redis_api import RedisApi


def periodic_alive_reminder(interval: timedelta, channel_set: ChannelSet,
                            mute_key: str, redis: RedisApi):
    while True:
        sleep(interval.total_seconds())
        send_alive_alert(redis, mute_key, channel_set)


def send_alive_alert(redis: RedisApi, mute_key: str,
                     channel_set: ChannelSet) -> None:
    # If reminder is not muted, inform operator that alerter is still alive.
    if not redis.exists(mute_key):
        channel_set.alert_info(AlerterAliveAlert())
