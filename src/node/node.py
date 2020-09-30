import logging
from enum import Enum
from typing import Optional

import dateutil.parser

from src.alerting.alerts.alerts import *
from src.alerting.channels.channel import ChannelSet
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.datetime import strfdelta
from src.utils.redis_api import RedisApi
from src.utils.timing import TimedTaskLimiter, TimedOccurrenceTracker


class NodeType(Enum):
    VALIDATOR_FULL_NODE = 1,
    NON_VALIDATOR_FULL_NODE = 2


class Node:
    def __init__(self, name: str, rpc_url: Optional[str], node_type: NodeType,
                 pubkey: Optional[str], network: str, redis: Optional[RedisApi],
                 internal_conf: InternalConfig = InternalConf) -> None:
        super().__init__()

        self.name = name
        self.rpc_url = rpc_url
        self.node_type = node_type
        self.pubkey = pubkey
        self.network = network
        self._redis = redis
        self._redis_enabled = redis is not None
        self._redis_prefix = self.name + "@" + self.network

        self._went_down_at = None
        self._consecutive_blocks_missed = 0
        self._voting_power = None
        self._catching_up = False
        self._no_of_peers = None
        self._experiencing_delays_alert_sent = False
        self._initial_downtime_alert_sent = False

        self._validator_peer_danger_boundary = \
            internal_conf.validator_peer_danger_boundary
        self._validator_peer_safe_boundary = \
            internal_conf.validator_peer_safe_boundary
        self._full_node_peer_danger_boundary = \
            internal_conf.full_node_peer_danger_boundary
        self._missed_blocks_danger_boundary = \
            internal_conf.missed_blocks_danger_boundary

        self._downtime_initial_alert_delayer = TimedTaskLimiter(
            internal_conf.downtime_initial_alert_delay)
        self._downtime_reminder_limiter = TimedTaskLimiter(
            internal_conf.downtime_reminder_interval_seconds)
        self._timed_block_miss_tracker = TimedOccurrenceTracker(
            internal_conf.max_missed_blocks_in_time_interval,
            internal_conf.max_missed_blocks_time_interval)

    def __str__(self) -> str:
        return self.name

    @property
    def is_validator(self) -> bool:
        return self.node_type == NodeType.VALIDATOR_FULL_NODE

    @property
    def is_down(self) -> bool:
        return self._went_down_at is not None

    @property
    def is_missing_blocks(self) -> bool:
        return self.consecutive_blocks_missed_so_far > 0

    @property
    def consecutive_blocks_missed_so_far(self) -> int:
        return self._consecutive_blocks_missed

    @property
    def voting_power(self) -> int:
        return self._voting_power

    @property
    def catching_up(self) -> bool:
        return self._catching_up

    @property
    def no_of_peers(self) -> int:
        return self._no_of_peers

    def status(self) -> str:
        return "voting_power={}, catching_up={}, number_of_peers={}".format(
            self.voting_power, self.catching_up, self.no_of_peers)

    def load_state(self, logger: logging.Logger) -> None:
        # If Redis is enabled, load any previously stored state
        if self._redis_enabled:
            self._went_down_at = self._redis.get(
                self._redis_prefix + '_went_down_at', None)
            self._consecutive_blocks_missed = self._redis.get_int(
                self._redis_prefix + '_consecutive_blocks_missed', 0)
            self._voting_power = self._redis.get_int(
                self._redis_prefix + '_voting_power', None)
            self._catching_up = self._redis.get_bool(
                self._redis_prefix + '_catching_up', False)
            self._no_of_peers = self._redis.get_int(
                self._redis_prefix + '_no_of_peers', None)

            # String to actual values
            if self._went_down_at is not None:
                try:
                    self._went_down_at = \
                        dateutil.parser.parse(self._went_down_at)
                except (TypeError, ValueError) as e:
                    logger.error('Error when parsing '
                                 '_went_down_at: %s', e)
                    self._went_down_at = None

            logger.debug(
                'Restored %s state: _went_down_at=%s, '
                '_consecutive_blocks_missed=%s, _voting_power=%s, '
                '_catching_up=%s, _no_of_peers=%s',
                self.name, self._went_down_at, self._consecutive_blocks_missed,
                self._voting_power, self._catching_up, self._no_of_peers)

    def save_state(self, logger: logging.Logger) -> None:
        # If Redis is enabled, store the current state
        if self._redis_enabled:
            logger.debug(
                'Saving %s state: _went_down_at=%s, _consecutive_blocks_missed'
                '=%s, _voting_power=%s, _catching_up=%s, _no_of_peers=%s',
                self.name, self._went_down_at, self._consecutive_blocks_missed,
                self._voting_power, self._catching_up, self._no_of_peers)

            # Set values
            self._redis.set_multiple({
                self._redis_prefix + '_went_down_at': str(self._went_down_at),
                self._redis_prefix + '_consecutive_blocks_missed':
                    self._consecutive_blocks_missed,
                self._redis_prefix + '_voting_power': self._voting_power,
                self._redis_prefix + '_catching_up': str(self._catching_up),
                self._redis_prefix + '_no_of_peers': self._no_of_peers
            })

    def set_as_down(self, channels: ChannelSet, logger: logging.Logger) -> None:

        logger.debug('%s set_as_down: is_down(currently)=%s, channels=%s',
                     self, self.is_down, channels)

        # If node was not down before, do not alert for now, just in case it's
        # a connection hiccup but take note of the start of the downtime
        if not self.is_down:
            self._went_down_at = datetime.now()
            self._experiencing_delays_alert_sent = False
            self._initial_downtime_alert_sent = False
            self._downtime_initial_alert_delayer.did_task()
        # If node was down and we have not yet sent an alert about this, send
        # an informational 'experiencing delays' alert as a warning
        elif not self._experiencing_delays_alert_sent:
            channels.alert_info(ExperiencingDelaysAlert(self.name))
            self._experiencing_delays_alert_sent = True
        # If we have not yet sent an initial downtime alert, and enough
        # time has passed for it, then send an initial alert
        elif not self._initial_downtime_alert_sent:
            if self._downtime_initial_alert_delayer.can_do_task():
                downtime = strfdelta(datetime.now() - self._went_down_at,
                                     "{hours}h, {minutes}m, {seconds}s")
                if self.is_validator:
                    channels.alert_major(CannotAccessNodeAlert(
                        self.name, self._went_down_at, downtime))
                else:
                    channels.alert_minor(CannotAccessNodeAlert(
                        self.name, self._went_down_at, downtime))
                self._downtime_reminder_limiter.did_task()
                self._initial_downtime_alert_sent = True
        # If we already sent an initial alert and enough time has passed
        # for a reminder alert, then send a reminder alert
        else:
            if self._downtime_reminder_limiter.can_do_task():
                downtime = strfdelta(datetime.now() - self._went_down_at,
                                     "{hours}h, {minutes}m, {seconds}s")
                if self.is_validator:
                    channels.alert_major(StillCannotAccessNodeAlert(
                        self.name, self._went_down_at, downtime))
                else:
                    channels.alert_minor(StillCannotAccessNodeAlert(
                        self.name, self._went_down_at, downtime))
                self._downtime_reminder_limiter.did_task()

    def set_as_up(self, channels: ChannelSet, logger: logging.Logger) -> None:

        logger.debug('%s set_as_up: is_down(currently)=%s, channels=%s',
                     self, self.is_down, channels)

        # Alert if node was down
        if self.is_down:
            # Only send accessible alert if inaccessible alert was sent
            if self._initial_downtime_alert_sent:
                downtime = strfdelta(datetime.now() - self._went_down_at,
                                     "{hours}h, {minutes}m, {seconds}s")
                channels.alert_info(NowAccessibleAlert(
                    self.name, self._went_down_at, downtime))

            # Reset downtime-related values
            self._downtime_initial_alert_delayer.reset()
            self._downtime_reminder_limiter.reset()
            self._went_down_at = None

    def add_missed_block(self, block_height: int, block_time: datetime,
                         missing_validators: int, channels: ChannelSet,
                         logger: logging.Logger) -> None:
        # NOTE: This function assumes that the node is a validator

        # Calculate the actual blocks missed as of when this function was called
        blocks_missed = self._consecutive_blocks_missed + 1

        # Variable alias for improved readability
        danger = self._missed_blocks_danger_boundary

        logger.debug(
            '%s add_missed_block: before=%s, new=%s, missing_validators = %s, '
            'channels=%s', self, self.consecutive_blocks_missed_so_far,
            blocks_missed, missing_validators, channels)

        # Let timed tracker know that block missed
        self._timed_block_miss_tracker.action_happened(at_time=block_time)

        # Alert (varies depending on whether was already missing blocks)
        if not self.is_missing_blocks:
            pass  # Do not alert on first missed block
        elif 2 <= blocks_missed < danger:
            channels.alert_info(MissedBlocksAlert(
                self.name, blocks_missed, block_height, missing_validators)
            )  # 2+ blocks missed inside danger range
        elif blocks_missed == 5:
            channels.alert_minor(MissedBlocksAlert(
                self.name, blocks_missed, block_height, missing_validators)
            )  # reached danger range
        elif blocks_missed >= max(10, danger) and blocks_missed % 10 == 0:
            channels.alert_major(MissedBlocksAlert(
                self.name, blocks_missed, block_height, missing_validators)
            )  # Every (10N)th block missed for N >= 1 inside danger range
            self._timed_block_miss_tracker.reset()

        if self._timed_block_miss_tracker.too_many_occurrences(block_time):
            blocks_in_interval = self._timed_block_miss_tracker.max_occurrences
            time_interval = self._timed_block_miss_tracker.time_interval_pretty
            channels.alert_major(TimedMissedBlocksAlert(
                self.name, blocks_in_interval, time_interval,
                block_height, missing_validators)
            )  # More blocks missed than is acceptable in the time interval
            self._timed_block_miss_tracker.reset()

        # Update consecutive blocks missed
        self._consecutive_blocks_missed = blocks_missed

    def clear_missed_blocks(self, channels: ChannelSet,
                            logger: logging.Logger) -> None:
        # NOTE: This function assumes that the node is a validator

        logger.debug(
            '%s clear_missed_blocks: channels=%s', self, channels)

        # Alert if validator was missing blocks (only if more than 1 block)
        if self.is_missing_blocks and self._consecutive_blocks_missed > 1:
            channels.alert_info(NoLongerMissingBlocksAlert(
                self.name, self._consecutive_blocks_missed))

        # Reset missed blocks related values
        self._consecutive_blocks_missed = 0

    def set_voting_power(self, new_voting_power: int, channels: ChannelSet,
                         logger: logging.Logger) -> None:
        # NOTE: This function assumes that the node is a validator

        logger.debug(
            '%s set_voting_power: before=%s, new=%s, channels=%s',
            self, self.voting_power, new_voting_power, channels)

        # Alert if voting power has changed
        if self.voting_power not in [None, new_voting_power]:
            if self.is_validator and new_voting_power == 0:  # N to 0
                channels.alert_major(VotingPowerDecreasedAlert(
                    self.name, self.voting_power, new_voting_power))
            elif self.is_validator and self.voting_power == 0:  # 0 to N
                channels.alert_info(VotingPowerIncreasedAlert(
                    self.name, self.voting_power, new_voting_power))
            else:  # Any change
                diff = new_voting_power - self.voting_power
                if abs(diff) > InternalConf.change_in_voting_power_threshold:
                    if diff > 0:
                        channels.alert_info(VotingPowerIncreasedByAlert(
                            self.name, self.voting_power, new_voting_power))
                    else:
                        channels.alert_info(VotingPowerDecreasedByAlert(
                            self.name, self.voting_power, new_voting_power))

        # Update voting power
        self._voting_power = new_voting_power

    def set_catching_up(self, now_catching_up: bool,
                        channels: ChannelSet, logger: logging.Logger) -> None:

        logger.debug(
            '%s set_catching_up: before=%s, new=%s, channels=%s',
            self, self.catching_up, now_catching_up, channels)

        # Alert if catching up has changed
        if not self.catching_up and now_catching_up:
            channels.alert_minor(IsCatchingUpAlert(self.name))
        elif self.catching_up and not now_catching_up:
            channels.alert_info(IsNoLongerCatchingUpAlert(self.name))

        # Update catching-up
        self._catching_up = now_catching_up

    def set_no_of_peers(self, new_no_of_peers: int, channels: ChannelSet,
                        logger: logging.Logger) -> None:

        logger.debug(
            '%s set_no_of_peers: before=%s, new=%s, channels=%s',
            self, self.no_of_peers, new_no_of_peers, channels)

        # Variable alias for improved readability
        if self.is_validator:
            danger = self._validator_peer_danger_boundary
            safe = self._validator_peer_safe_boundary
        else:
            danger = self._full_node_peer_danger_boundary
            safe = None

        # Alert if number of peers has changed
        if self.no_of_peers not in [None, new_no_of_peers]:
            if self.is_validator:
                if new_no_of_peers <= self._validator_peer_safe_boundary:
                    # beneath safe boundary
                    if new_no_of_peers > self.no_of_peers:  # increase
                        channels.alert_info(PeersIncreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                    elif new_no_of_peers > danger:
                        # decrease outside danger range
                        channels.alert_minor(PeersDecreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                    else:  # decrease inside danger range
                        channels.alert_major(PeersDecreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                elif self._no_of_peers <= self._validator_peer_safe_boundary \
                        < new_no_of_peers:
                    # increase outside safe range for the first time
                    channels.alert_info(
                        PeersIncreasedOutsideSafeRangeAlert(self.name, safe))
            else:
                if new_no_of_peers > self.no_of_peers:  # increase
                    if new_no_of_peers <= danger:
                        # increase inside danger range
                        channels.alert_info(PeersIncreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                    elif self.no_of_peers <= danger < new_no_of_peers:
                        # increase outside danger range
                        channels.alert_info(
                            PeersIncreasedOutsideDangerRangeAlert(
                                self.name, danger))
                elif new_no_of_peers > danger:  # decrease outside danger range
                    pass
                else:  # decrease inside danger range
                    channels.alert_minor(PeersDecreasedAlert(
                        self.name, self.no_of_peers, new_no_of_peers))

        # Update number of peers
        self._no_of_peers = new_no_of_peers
