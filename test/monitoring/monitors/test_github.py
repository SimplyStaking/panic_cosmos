import logging
import unittest
from unittest.mock import patch

from redis import ConnectionError as RedisConnectionError

from src.alerting.channels.channel import ChannelSet
from src.monitoring.monitors.github import GitHubMonitor
from src.utils.redis_api import RedisApi
from test import TestInternalConf, TestUserConf
from test.test_helpers import CounterChannel

GET_JSON_FUNCTION = 'src.monitoring.monitors.github.get_json'
DUMMY_RELEASES = [
    {'name': 'Release 1'},
    {'name': 'Release 2'},
    {'name': 'Release 3'}
]


class TestGitHubMonitorWithoutRedis(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.monitor_name = 'testmonitor'
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])
        self.repo_name = 'dummy/repository/'
        self.releases_page = 'dummy.releases.page'
        self.redis_prefix = TestInternalConf.redis_github_releases_key_prefix

        self.db = TestInternalConf.redis_test_database
        self.host = TestUserConf.redis_host
        self.port = TestUserConf.redis_port
        self.password = TestUserConf.redis_password

        self.monitor = GitHubMonitor(self.monitor_name, self.channel_set,
                                     self.logger, None, self.repo_name,
                                     self.releases_page, self.redis_prefix)
        self.monitor._internal_conf = TestInternalConf

    @patch(GET_JSON_FUNCTION, return_value={
        'message': 'this would be some error message from GitHub'})
    def test_monitor_raises_no_alert_if_message_in_return(self, _):
        self.monitor.monitor()

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertIsNone(self.monitor._prev_no_of_releases)

    @patch(GET_JSON_FUNCTION, return_value=DUMMY_RELEASES)
    def test_monitor_raises_no_alert_if_first_time_round(self, _):
        self.monitor.monitor()

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(len(DUMMY_RELEASES), self.monitor._prev_no_of_releases)

    @patch(GET_JSON_FUNCTION, return_value=DUMMY_RELEASES)
    def test_monitor_raises_no_alert_no_of_releases_decreases(self, _):
        self.monitor._prev_no_of_releases = len(DUMMY_RELEASES) + 1
        self.monitor.monitor()

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(len(DUMMY_RELEASES), self.monitor._prev_no_of_releases)

    @patch(GET_JSON_FUNCTION, return_value=DUMMY_RELEASES)
    def test_monitor_raises_info_alert_if_no_of_releases_increases(self, _):
        self.monitor._prev_no_of_releases = len(DUMMY_RELEASES) - 1
        self.monitor.monitor()

        self.assertEqual(1, self.counter_channel.info_count)
        self.assertEqual(len(DUMMY_RELEASES), self.monitor._prev_no_of_releases)


class TestGitHubMonitorWithRedis(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Same as in setUp(), to avoid running all tests if Redis is offline

        logger = logging.getLogger('dummy')
        db = TestInternalConf.redis_test_database
        host = TestUserConf.redis_host
        port = TestUserConf.redis_port
        password = TestUserConf.redis_password
        redis = RedisApi(logger, db, host, port, password)

        try:
            redis.ping_unsafe()
        except RedisConnectionError:
            raise Exception('Redis is not online.')

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.monitor_name = 'testmonitor'
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])
        self.repo_name = 'dummy/repository/'
        self.releases_page = 'dummy.releases.page'
        self.redis_prefix = TestInternalConf.redis_github_releases_key_prefix

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

        self.monitor = GitHubMonitor(self.monitor_name, self.channel_set,
                                     self.logger, self.redis, self.repo_name,
                                     self.releases_page, self.redis_prefix)
        self.monitor._internal_conf = TestInternalConf

    def test_load_state_changes_nothing_if_nothing_saved(self):
        self.monitor.load_state()

        self.assertIsNone(self.monitor._prev_no_of_releases)

    def test_load_state_sets_values_to_saved_values(self):
        # Set Redis values manually
        key = self.redis_prefix + self.repo_name
        self.redis.set_unsafe(key, 10)

        # Load the values from Redis
        self.monitor.load_state()

        # Assert
        self.assertEqual(10, self.monitor._prev_no_of_releases)

    def test_save_state_sets_values_to_current_values(self):
        # Set monitor values manually
        self.monitor._prev_no_of_releases = 10

        # Save the values to Redis
        self.monitor.save_state()

        # Assert
        key = self.redis_prefix + self.repo_name
        self.assertEqual(10, self.redis.get_int(key))

    def test_save_state_sets_nothing_if_no_previous_state(self):
        # Save the values to Redis
        self.monitor.save_state()

        # Assert
        key = self.redis_prefix + self.repo_name
        self.assertIsNone(self.redis.get_int(key))
