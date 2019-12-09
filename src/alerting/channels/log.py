import logging

from src.alerting.alerts.alerts import Alert
from src.alerting.channels.channel import Channel


class LogChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 alerts_logger: logging.Logger) -> None:
        super().__init__(channel_name, logger, None)

        self._alerts_logger = alerts_logger
        self._space = ' ' if self.channel_name != '' else ''

    def alert_info(self, alert: Alert) -> None:
        self._alerts_logger.info('%s%sINFO - %s',
                                 self.channel_name, self._space, alert)

    def alert_minor(self, alert: Alert) -> None:
        self._alerts_logger.warning('%s%sMINOR - %s',
                                    self.channel_name, self._space, alert)

    def alert_major(self, alert: Alert) -> None:
        self._alerts_logger.critical('%s%sMAJOR - %s',
                                     self.channel_name, self._space, alert)

    def alert_error(self, alert: Alert) -> None:
        self._alerts_logger.error('%s%sERROR - %s',
                                  self.channel_name, self._space, alert)
