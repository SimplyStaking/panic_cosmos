import logging
from typing import Optional, List

from src.alerting.alert_utils.twilio_api import TwilioApi
from src.alerting.alerts.alerts import Alert, \
    ProblemWhenCheckingIfCallsAreSnoozedAlert, ProblemWhenDialingNumberAlert
from src.alerting.channels.channel import Channel, ChannelSet
from src.utils.redis_api import RedisApi


class TwilioChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi], twilio: TwilioApi,
                 call_from: str, call_to: List[str], twiml: str,
                 twiml_is_url: bool, snooze_key: str,
                 backup_channels: ChannelSet) -> None:
        super().__init__(channel_name, logger, redis)

        self._twilio = twilio
        self._call_from = call_from
        self._call_to = call_to
        self._twiml = twiml
        self._twiml_is_url = twiml_is_url
        self._snooze_key = snooze_key
        self._backup_channels = backup_channels

    def _calls_snoozed(self, logger: logging.Logger) \
            -> bool:
        if self.redis_enabled:
            if self.redis.exists(self._snooze_key):
                snooze_until = self.redis.get(self._snooze_key).decode("utf-8")
                logger.info('Tried to call but calls are snoozed until {}.'
                            ''.format(snooze_until))
                return True
            else:
                logger.info('Twilio did not find a snooze in Redis.')
                return False

    def alert_major(self, alert: Alert) -> None:
        # Check if snoozed
        try:
            snoozed = self._calls_snoozed(self.logger)
        except Exception as e:
            self._backup_channels.alert_error(
                ProblemWhenCheckingIfCallsAreSnoozedAlert())
            self.logger.error(
                'Error when checking if Twilio calls are snoozed: %s.', e)
            snoozed = False

        # Dial the numbers if not snoozed
        if not snoozed:
            for number in self._call_to:
                self.logger.info("Twilio now dialing " + number)
                try:
                    self._twilio.dial_number(self._call_from, number,
                                             self._twiml, self._twiml_is_url)
                except Exception as e:
                    self._backup_channels.alert_error(
                        ProblemWhenDialingNumberAlert(number, e))
