import logging
import time
import unittest
from datetime import datetime, timedelta

from redis import ConnectionError as RedisConnectionError

from src.alerting.channels.channel import ChannelSet
from src.alerting.periodic.periodic import send_alive_alert
from src.utils.redis_api import RedisApi
from src.utils.timing import TimedTaskLimiter
from test import TestInternalConf, TestUserConf
from test.node.test_node import CounterChannel


class TestPeriodic(unittest.TestCase):
    def setUp(self) -> None:
        self.alerter_name = 'testalerter'
        self.logger = logging.getLogger('dummy')
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])

        self.db = TestInternalConf.redis_test_database
        self.host = TestUserConf.redis_host
        self.port = TestUserConf.redis_port
        self.password = TestUserConf.redis_password
        self.redis = RedisApi(self.logger, self.db, self.host,
                              self.port, self.password)
        self.redis.delete_all_unsafe()

        try:
            self.redis.ping_unsafe()
        except RedisConnectionError:
            self.fail('Redis is not online.')

        self.timedelta = TestUserConf.interval_seconds
        self.timing = TimedTaskLimiter(self.timedelta)
        self.mute_key = TestInternalConf.redis_periodic_alive_reminder_mute_key

    def test_periodic_alive_reminder_can_do_task_no_mute_key(self):
        self.timing.did_task()
        time.sleep(TestUserConf.interval_seconds.seconds)
        self.counter_channel.reset()  # ignore previous alerts
        send_alive_alert(self.timing, self.redis, self.mute_key, self.channel_set)
        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_periodic_alive_reminder_cannot_do_task_no_mute_key(self):
        self.timing.did_task()
        time.sleep(TestUserConf.interval_seconds.seconds - 2)
        self.counter_channel.reset()  # ignore previous alerts
        send_alive_alert(self.timing, self.redis, self.mute_key, self.channel_set)
        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_periodic_alive_reminder_can_do_task_mute_key_present(self):
        self.timing.did_task()
        time.sleep(TestUserConf.interval_seconds.seconds)
        hours = timedelta(hours=float(1))
        until = str(datetime.now() + hours)
        self.redis.set_for(self.mute_key, until, hours)
        self.counter_channel.reset()  # ignore previous alerts
        send_alive_alert(self.timing, self.redis, self.mute_key, self.channel_set)
        self.redis.remove(self.mute_key)
        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_periodic_alive_reminder_cannot_do_task_mute_key_present(self):
        self.timing.did_task()
        time.sleep(TestUserConf.interval_seconds.seconds - 3)
        hours = timedelta(hours=float(1))
        until = str(datetime.now() + hours)
        self.redis.set_for(self.mute_key, until, hours)
        self.counter_channel.reset()  # ignore previous alerts
        send_alive_alert(self.timing, self.redis, self.mute_key, self.channel_set)
        self.redis.remove(self.mute_key)
        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.error_count, 0)
