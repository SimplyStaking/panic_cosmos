import logging
import unittest
from datetime import datetime, timedelta
from time import sleep

import dateutil.parser
from redis import ConnectionError as RedisConnectionError

from src.alerting.alerts.alerts import VotingPowerDecreasedByAlert, \
    VotingPowerIncreasedByAlert
from src.alerting.channels.channel import ChannelSet
from src.node.node import Node, NodeType
from src.utils.redis_api import RedisApi
from test import TestInternalConf, TestUserConf
from test.test_helpers import CounterChannel, DummyException


class TestNodeWithoutRedis(unittest.TestCase):

    def setUp(self) -> None:
        self.node_name = 'testnode'
        self.logger = logging.getLogger('dummy')

        self.downtime_initial_alert_delay = \
            TestInternalConf.downtime_initial_alert_delay
        self.downtime_initial_alert_delay_with_error_margin = \
            self.downtime_initial_alert_delay + timedelta(seconds=0.5)

        self.downtime_reminder_alert_interval = \
            TestInternalConf.downtime_reminder_interval_seconds
        self.downtime_reminder_alert_interval_with_error_margin = \
            self.downtime_reminder_alert_interval + timedelta(seconds=0.5)

        self.max_missed_blocks_time_interval = \
            TestInternalConf.max_missed_blocks_time_interval
        self.max_missed_blocks_time_interval_with_error_margin = \
            self.max_missed_blocks_time_interval + timedelta(seconds=0.5)

        self.max_missed_blocks_in_time_interval = \
            TestInternalConf.max_missed_blocks_in_time_interval

        self.voting_power_threshold = \
            TestInternalConf.change_in_voting_power_threshold

        self.full_node = Node(name=self.node_name, rpc_url=None,
                              node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                              pubkey=None, network='', redis=None,
                              internal_conf=TestInternalConf)

        self.validator = Node(name=self.node_name, rpc_url=None,
                              node_type=NodeType.VALIDATOR_FULL_NODE,
                              pubkey=None, network='', redis=None,
                              internal_conf=TestInternalConf)

        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])
        self.dummy_exception = DummyException()

        self.dummy_block_height = -1
        self.dummy_block_time = datetime.min + timedelta(days=123)
        self.dummy_block_time_after_time_interval = \
            self.dummy_block_time + \
            self.max_missed_blocks_time_interval_with_error_margin
        self.dummy_missing_validators = -1
        self.dummy_voting_power = 1000
        self.dummy_no_of_peers = 1000

        self.peers_validator_danger_boundary = \
            TestInternalConf.validator_peer_danger_boundary
        self.peers_less_than_validator_danger_boundary = \
            self.peers_validator_danger_boundary - 2
        self.peers_more_than_validator_danger_boundary = \
            self.peers_validator_danger_boundary + 2

        self.peers_validator_safe_boundary = \
            TestInternalConf.validator_peer_safe_boundary
        self.peers_less_than_validator_safe_boundary = \
            self.peers_validator_safe_boundary - 2
        self.peers_more_than_validator_safe_boundary = \
            self.peers_validator_safe_boundary + 2

        self.peers_full_node_danger_boundary = \
            TestInternalConf.full_node_peer_danger_boundary
        self.peers_less_than_full_node_danger_boundary = \
            self.peers_full_node_danger_boundary - 2
        self.peers_more_than_full_node_danger_boundary = \
            self.peers_full_node_danger_boundary + 2

    def test_is_validator_true_if_is_validator(self):
        self.assertTrue(self.validator.is_validator)

    def test_is_validator_false_if_not_validator(self):
        self.assertFalse(self.full_node.is_validator)

    def test_is_down_false_by_default(self):
        self.assertFalse(self.validator.is_down)

    def test_is_missing_blocks_false_by_default(self):
        self.assertFalse(self.validator.is_missing_blocks)

    def test_consecutive_blocks_missed_is_0_by_default(self):
        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 0)

    def test_voting_power_is_none_by_default(self):
        self.assertIsNone(self.validator.voting_power)

    def test_catching_up_is_false_by_default(self):
        self.assertFalse(self.validator.catching_up)

    def test_no_of_peers_is_none_by_default(self):
        self.assertIsNone(self.validator.no_of_peers)

    def test_status_returns_three_values(self):
        self.validator._voting_power = 123
        self.validator._catching_up = True
        self.validator._no_of_peers = 999

        self.assertEqual(self.validator.status(), 'voting_power=123, '
                                                  'catching_up=True, '
                                                  'number_of_peers=999')

    def test_set_as_down_validator(self):
        NODE = self.validator
        self.assertFalse(NODE.is_down)

        # First one sets validator to down but sends no alerts
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # Second one sends info alert and keeps validator down
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # Next is the initial downtime alert, but this is
        # not sent if not enough time has passed for it
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # ...if enough time passed for an initial alert, a major alert is sent
        sleep(self.downtime_initial_alert_delay_with_error_margin.seconds)
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.major_count, 1)
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # Next is the downtime reminder alert, but this is
        # not sent if not enough time has passed for it
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # ...if enough time passed for a reminder, a major alert is sent again
        sleep(self.downtime_reminder_alert_interval_with_error_margin.seconds)
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.major_count, 1)
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

    def test_set_as_down_full_node(self):
        NODE = self.full_node
        self.assertFalse(NODE.is_down)

        # First one sets full node to down but sends no alerts
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # Second one sends info alert and keeps full node down
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # Next is the initial downtime alert, but this is
        # not sent if not enough time has passed for it
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # ...if enough time passed for an initial alert, a minor alert is sent
        sleep(self.downtime_initial_alert_delay_with_error_margin.seconds)
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.minor_count, 1)
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # Next is the downtime reminder alert, but this is
        # not sent if not enough time has passed for it
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

        # ...if enough time passed for a reminder, a minor alert is sent again
        sleep(self.downtime_reminder_alert_interval_with_error_margin.seconds)
        NODE.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.minor_count, 1)
        self.assertTrue(NODE.is_down)

        self.counter_channel.reset()

    def test_set_as_up_sends_no_alerts_if_not_down(self):
        self.validator.set_as_up(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertFalse(self.validator.is_down)

    def test_set_as_up_sends_no_alerts_if_initial_downtime_alert_not_sent(self):
        self.validator._went_down_at = datetime.min  # non-None, i.e. down
        self.validator._initial_downtime_alert_sent = False

        # Confirm that nodes down
        self.assertTrue(self.validator.is_down)

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_up(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())

        self.assertFalse(self.validator.is_down)

    def test_set_as_up_sends_info_alerts_if_initial_downtime_alert_sent(self):
        self.validator._went_down_at = datetime.min  # non-None, i.e. down
        self.validator._initial_downtime_alert_sent = True

        # Confirm that nodes down
        self.assertTrue(self.validator.is_down)

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_up(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.info_count, 1)

        self.assertFalse(self.validator.is_down)

    def test_set_as_up_resets_initial_downtime_alert_timing(self):
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        sleep(self.downtime_initial_alert_delay_with_error_margin.seconds)
        self.validator.set_as_up(self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(self.validator.is_down)

        # Without the set_as_up, the set_as_down produces an alert. We can try
        # this out by first setting the validator back to up
        self.validator.set_as_up(self.channel_set, self.logger)

        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        sleep(self.downtime_initial_alert_delay_with_error_margin.seconds)
        # self.validator.set_as_up(self.channel_set, self.logger) # !!

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.major_count, 1)
        self.assertTrue(self.validator.is_down)

    def test_set_as_up_resets_downtime_reminder_alert_timing(self):
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        sleep(self.downtime_initial_alert_delay_with_error_margin.seconds)
        self.validator.set_as_down(self.channel_set, self.logger)
        sleep(self.downtime_reminder_alert_interval_with_error_margin.seconds)
        self.validator.set_as_up(self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_down(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(self.validator.is_down)

        # Without the set_as_up, the set_as_down produces an alert. We can try
        # this out by first setting the validator back to up
        self.validator.set_as_up(self.channel_set, self.logger)

        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        sleep(self.downtime_initial_alert_delay_with_error_margin.seconds)
        self.validator.set_as_down(self.channel_set, self.logger)
        sleep(self.downtime_reminder_alert_interval_with_error_margin.seconds)
        # self.validator.set_as_up(self.channel_set, self.logger) # !!

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.major_count, 1)
        self.assertTrue(self.validator.is_down)

    def test_first_missed_block_increases_missed_blocks_count_but_no_alerts(
            self):
        if TestInternalConf.missed_blocks_danger_boundary != 5:
            self.fail('Expected missed blocks danger boundary to be 5.')

        self.validator.add_missed_block(self.dummy_block_height,
                                        self.dummy_block_time,
                                        self.dummy_missing_validators,
                                        self.channel_set, self.logger)

        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 1)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_four_missed_blocks_increases_missed_blocks_count_and_alerts(
            self):
        if TestInternalConf.missed_blocks_danger_boundary != 5:
            self.fail('Expected missed blocks danger boundary to be 5.')

        for i in range(4):
            self.validator.add_missed_block(self.dummy_block_height,
                                            self.dummy_block_time,
                                            self.dummy_missing_validators,
                                            self.channel_set, self.logger)

        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 4)
        self.assertEqual(self.counter_channel.info_count, 3)
        # 1 raises no alerts, 2,3,4 raise an info alert

    def test_five_missed_blocks_increases_missed_blocks_count_and_alerts(
            self):
        if TestInternalConf.missed_blocks_danger_boundary != 5:
            self.fail('Expected missed blocks danger boundary to be 5.')

        for i in range(5):
            self.validator.add_missed_block(self.dummy_block_height,
                                            self.dummy_block_time,
                                            self.dummy_missing_validators,
                                            self.channel_set, self.logger)

        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 5)
        self.assertEqual(self.counter_channel.info_count, 3)
        self.assertEqual(self.counter_channel.minor_count, 1)
        # 1 raises no alerts, 2,3,4 raise an info alert, 5 raises a minor alert

    def test_ten_missed_blocks_increases_missed_blocks_count_and_alerts(
            self):
        if TestInternalConf.missed_blocks_danger_boundary != 5:
            self.fail('Expected missed blocks danger boundary to be 5.')

        for i in range(10):
            self.validator.add_missed_block(self.dummy_block_height,
                                            self.dummy_block_time,
                                            self.dummy_missing_validators,
                                            self.channel_set, self.logger)

        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 10)
        self.assertEqual(self.counter_channel.info_count, 3)
        self.assertEqual(self.counter_channel.minor_count, 1)
        self.assertEqual(self.counter_channel.major_count, 1)
        # 1 raises no alerts, 2,3,4 raise an info alert,
        # 5 raises a minor alert, 10 raises a major alert

    def test_ten_non_consecutive_missed_blocks_within_time_interval_triggers_major_alert(
            self):
        if TestInternalConf.missed_blocks_danger_boundary != 5:
            self.fail('Expected missed blocks danger boundary to be 5.')

        # Miss 9 non-consecutive blocks
        for i in range(9):
            self.validator.add_missed_block(self.dummy_block_height,
                                            self.dummy_block_time,
                                            self.dummy_missing_validators,
                                            self.channel_set, self.logger)
            self.validator.clear_missed_blocks(self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts

        # Miss 10th block within time interval
        self.validator.add_missed_block(
            self.dummy_block_height, self.dummy_block_time,
            self.dummy_missing_validators, self.channel_set, self.logger)

        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 1)
        self.assertEqual(self.counter_channel.major_count, 1)

    def test_ten_non_consecutive_missed_blocks_outside_time_interval_does_nothing(
            self):
        if TestInternalConf.missed_blocks_danger_boundary != 5:
            self.fail('Expected missed blocks danger boundary to be 5.')

        # Miss 9 non-consecutive blocks
        for i in range(9):
            self.validator.add_missed_block(self.dummy_block_height,
                                            self.dummy_block_time,
                                            self.dummy_missing_validators,
                                            self.channel_set, self.logger)
            self.validator.clear_missed_blocks(self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts

        # Miss 10th block outside of time interval
        self.validator.add_missed_block(
            self.dummy_block_height, self.dummy_block_time_after_time_interval,
            self.dummy_missing_validators, self.channel_set, self.logger)

        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 1)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_clear_missed_blocks_raises_no_alert_if_was_not_missing_blocks(
            self):
        self.validator.clear_missed_blocks(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_clear_missed_blocks_raises_info_alert_if_no_longer_missing_blocks_for_one_missed_block(
            self):
        # Miss one block
        self.validator.add_missed_block(
            self.dummy_block_height, self.dummy_block_time,
            self.dummy_missing_validators, self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts
        self.validator.clear_missed_blocks(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_clear_missed_blocks_raises_info_alert_if_no_longer_missing_blocks_for_two_missed_blocks(
            self):
        # Miss two blocks
        self.validator.add_missed_block(
            self.dummy_block_height, self.dummy_block_time,
            self.dummy_missing_validators, self.channel_set, self.logger)
        self.validator.add_missed_block(
            self.dummy_block_height, self.dummy_block_time,
            self.dummy_missing_validators, self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts
        self.validator.clear_missed_blocks(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_voting_power_raises_no_alerts_first_time_round(self):
        self.validator.set_voting_power(0, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_voting_power_raises_no_alerts_if_voting_power_the_same(self):
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_voting_power_raises_info_alert_if_voting_power_increases_from_0(
            self):
        # This is just to cover the unique message when power increases from 0

        self.validator.set_voting_power(0, self.channel_set, self.logger)
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_voting_power_raises_major_alert_if_voting_power_decreases_to_0(
            self):
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        self.validator.set_voting_power(0, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.major_count, 1)

    def test_set_voting_power_no_alerts_if_difference_is_negative_below_threshold_and_no_balance_is_0(
            self) -> None:
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        new_voting_power = self.dummy_voting_power - \
                           self.voting_power_threshold + 1
        self.validator.set_voting_power(new_voting_power, self.channel_set,
                                        self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.voting_power,
                         new_voting_power)

    def test_set_voting_power_no_alerts_if_difference_is_positive_below_threshold_and_no_balance_is_0(
            self) -> None:
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        new_voting_power = self.dummy_voting_power + \
                           self.voting_power_threshold - 1
        self.validator.set_voting_power(new_voting_power, self.channel_set,
                                        self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.voting_power,
                         new_voting_power)

    def test_set_voting_power_no_alerts_if_difference_is_negative_and_equal_to_threshold_and_no_balance_is_0(
            self):
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        new_voting_power = self.dummy_voting_power - \
                           self.voting_power_threshold
        self.validator.set_voting_power(new_voting_power, self.channel_set,
                                        self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.voting_power,
                         new_voting_power)

    def test_set_voting_power_no_alerts_if_difference_is_positive_and_equal_to_threshold_and_no_balance_is_0(
            self):
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        new_voting_power = self.dummy_voting_power + \
                           self.voting_power_threshold
        self.validator.set_voting_power(new_voting_power, self.channel_set,
                                        self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.voting_power,
                         new_voting_power)

    def test_set_voting_power_raises_info_alert_if_difference_is_positive_above_threshold_no_balance_is_0(
            self):
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        new_voting_power = self.dummy_voting_power + \
                           self.voting_power_threshold + 1
        self.validator.set_voting_power(new_voting_power, self.channel_set,
                                        self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              VotingPowerIncreasedByAlert)
        self.assertEqual(self.validator.voting_power,
                         new_voting_power)

    def test_set_voting_power_raises_info_alert_if_difference_is_negative_above_threshold_no_balance_is_0(
            self):
        self.validator.set_voting_power(self.dummy_voting_power,
                                        self.channel_set, self.logger)
        new_voting_power = self.dummy_voting_power - \
                           self.voting_power_threshold - 1
        self.validator.set_voting_power(new_voting_power, self.channel_set,
                                        self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              VotingPowerDecreasedByAlert)
        self.assertEqual(self.validator.voting_power, new_voting_power)

    def test_set_catching_up_raises_minor_alert_first_time_round_if_true(self):
        self.validator.set_catching_up(True, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 1)

    def test_set_catching_up_raises_no_alerts_first_time_round_if_false(self):
        self.validator.set_catching_up(False, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_catching_up_raises_no_alerts_if_from_true_to_true(self):
        self.validator.set_catching_up(True, self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_catching_up(True, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_catching_up_raises_no_alerts_if_from_false_to_false(self):
        self.validator.set_catching_up(False, self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_catching_up(False, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_catching_up_raises_minor_alert_if_from_false_to_true(self):
        self.validator.set_catching_up(False, self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_catching_up(True, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 1)

    def test_set_catching_up_raises_info_alert_if_from_true_to_false(self):
        self.validator.set_catching_up(True, self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_catching_up(False, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_no_of_peers_raises_no_alerts_first_time_round_for_validator(
            self):
        self.validator.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_peers_raises_no_alerts_first_time_round_for_full_node(
            self):
        self.full_node.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_peers_raises_no_alerts_if_increase_for_validator_if_outside_safe_range(
            self):
        increased_no_of_peers = self.dummy_no_of_peers + 1

        self.validator.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(increased_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_set_no_of_peers_raises_info_alert_if_increase_for_full_node_if_inside_danger(
            self):
        self.full_node.set_no_of_peers(
            self.peers_less_than_full_node_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_no_of_peers(
            self.peers_less_than_full_node_danger_boundary + 1,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_no_of_peers_raises_no_alerts_if_increase_for_full_node_if_outside_danger(
            self):
        self.full_node.set_no_of_peers(
            self.peers_more_than_full_node_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_no_of_peers(
            self.peers_more_than_full_node_danger_boundary + 1,
            self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_peers_raises_info_alert_if_increase_for_full_node_if_inside_to_outside_danger(
            self):
        self.full_node.set_no_of_peers(
            self.peers_less_than_full_node_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_no_of_peers(
            self.peers_more_than_full_node_danger_boundary,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_no_of_peers_raises_info_alert_if_increase_for_validator_if_inside_danger(
            self):
        self.validator.set_no_of_peers(
            self.peers_less_than_validator_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_less_than_validator_danger_boundary + 1,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_no_of_peers_raises_info_alert_if_increase_for_validator_if_outside_danger_inside_safe(
            self):
        self.validator.set_no_of_peers(
            self.peers_validator_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_validator_danger_boundary + 1,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)

    def test_set_no_of_peers_raises_info_alert_if_decrease_for_validator_if_outside_danger_inside_safe(
            self):
        self.validator.set_no_of_peers(
            self.peers_validator_safe_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_validator_safe_boundary - 1,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 1)

    def test_set_no_of_peers_raises_minor_alert_if_decrease_for_full_node_if_inside_danger(
            self):
        self.full_node.set_no_of_peers(
            self.peers_more_than_full_node_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_no_of_peers(
            self.peers_less_than_full_node_danger_boundary,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 1)

    def test_set_no_of_peers_raises_no_alerts_if_decrease_for_full_node_if_outside_danger(
            self):
        self.full_node.set_no_of_peers(
            self.peers_more_than_full_node_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_no_of_peers(
            self.peers_more_than_full_node_danger_boundary - 1,
            self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_peers_raises_major_alert_if_decrease_for_validator_if_inside_danger(
            self):
        self.validator.set_no_of_peers(
            self.peers_validator_danger_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_less_than_validator_danger_boundary,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.major_count, 1)

    def test_set_no_of_peers_raises_minor_alert_if_decrease_for_validator_if_outside_danger_inside_safe(
            self):
        self.validator.set_no_of_peers(
            self.peers_validator_safe_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_validator_safe_boundary - 1,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 1)

    def test_set_no_of_peers_raises_no_alerts_if_decrease_for_validator_if_outside_safe(
            self):
        self.validator.set_no_of_peers(
            self.peers_more_than_validator_safe_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_more_than_validator_safe_boundary - 1,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_set_no_of_peers_raises_info_alert_if_increase_for_validator_outside_safe_for_first_time(
            self):
        self.validator.set_no_of_peers(
            self.peers_less_than_validator_safe_boundary,
            self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_no_of_peers(
            self.peers_more_than_validator_safe_boundary,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.minor_count, 0)
        self.assertEqual(self.counter_channel.major_count, 0)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertEqual(self.counter_channel.error_count, 0)


class TestNodeWithRedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Same as in setUp(), to avoid running all tests if Redis is offline

        logger = logging.getLogger('dummy')
        db = TestInternalConf.redis_test_database
        host = TestUserConf.redis_host
        port = TestUserConf.redis_port
        password = TestUserConf.redis_password
        redis = RedisApi(logger, db, host, port, password)

        # try:
        #     redis.ping_unsafe()
        # except RedisConnectionError:
        #     raise Exception('Redis is not online.')

    def setUp(self) -> None:
        self.node_name = 'testnode'
        self.network_name = 'testnetwork'
        self.redis_prefix = self.node_name + "@" + self.network_name
        self.date = datetime.min + timedelta(days=123)
        self.logger = logging.getLogger('dummy')

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

        self.non_validator = Node(name=self.node_name, rpc_url=None,
                                  node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                  pubkey=None, network=self.network_name,
                                  redis=self.redis,
                                  internal_conf=TestInternalConf)

        self.validator = Node(name=self.node_name, rpc_url=None,
                              node_type=NodeType.VALIDATOR_FULL_NODE,
                              pubkey=None, network=self.network_name,
                              redis=self.redis, internal_conf=TestInternalConf)

    def test_load_state_changes_nothing_if_nothing_saved(self):
        self.validator.load_state(self.logger)

        self.assertFalse(self.validator.is_down)
        self.assertFalse(self.validator.is_missing_blocks)
        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 0)
        self.assertIsNone(self.validator.voting_power)
        self.assertFalse(self.validator.catching_up)
        self.assertIsNone(self.validator.no_of_peers)

    def test_load_state_sets_values_to_saved_values(self):
        # Set Redis values manually
        self.redis.set_unsafe(self.redis_prefix + '_went_down_at',
                              str(self.date))
        self.redis.set_unsafe(self.redis_prefix + '_consecutive_blocks_missed',
                              123)
        self.redis.set_unsafe(self.redis_prefix + '_voting_power', 456)
        self.redis.set_unsafe(self.redis_prefix + '_catching_up', str(True))
        self.redis.set_unsafe(self.redis_prefix + '_no_of_peers', 789)

        # Load the Redis values
        self.validator.load_state(self.logger)

        # Assert
        self.assertEqual(self.validator._went_down_at, self.date)
        self.assertEqual(self.validator.consecutive_blocks_missed_so_far, 123)
        self.assertEqual(self.validator.voting_power, 456)
        self.assertTrue(self.validator.catching_up)
        self.assertEqual(self.validator.no_of_peers, 789)

    def test_load_state_sets_went_down_at_to_none_if_incorrect_type(self):
        # Set Redis values manually
        self.redis.set_unsafe(self.redis_prefix + '_went_down_at', str(True))

        # Load the Redis values
        self.validator.load_state(self.logger)

        # Assert
        self.assertIsNone(self.validator._went_down_at)

    def test_save_state_sets_values_to_current_values(self):
        # Set node values manually
        self.validator._went_down_at = self.date
        self.validator._consecutive_blocks_missed = 123
        self.validator._voting_power = 456
        self.validator._catching_up = True
        self.validator._no_of_peers = 789

        # Save the values to Redis
        self.validator.save_state(self.logger)

        # Assert
        self.assertEqual(
            dateutil.parser.parse(self.redis.get_unsafe(
                self.redis_prefix + '_went_down_at')), self.date)
        self.assertEqual(
            self.redis.get_int_unsafe(
                self.redis_prefix + '_consecutive_blocks_missed'), 123)
        self.assertEqual(
            self.redis.get_int_unsafe(self.redis_prefix + '_voting_power'), 456)
        self.assertTrue(
            self.redis.get_bool_unsafe(self.redis_prefix + '_catching_up'))
        self.assertEqual(
            self.redis.get_int_unsafe(self.redis_prefix + '_no_of_peers'), 789)
