import logging
from typing import Optional, List

from src.alerting.alert_utils.email_sending import EmailSender
from src.alerting.alerts.alerts import Alert
from src.alerting.channels.channel import Channel
from src.utils.redis_api import RedisApi


class EmailChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi], email: EmailSender,
                 email_to: List[str]) -> None:
        super().__init__(channel_name, logger, redis)

        self._email = email
        self._email_to = email_to
        self._space = ' ' if self.channel_name != '' else ''

    def alert_info(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}INFO Alert'.format(self.channel_name,
                                                    self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)

    def alert_minor(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}MINOR Alert'.format(self.channel_name,
                                                     self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)

    def alert_major(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}MAJOR Alert'.format(self.channel_name,
                                                     self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)

    def alert_error(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}ERROR Alert'.format(self.channel_name,
                                                     self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)
