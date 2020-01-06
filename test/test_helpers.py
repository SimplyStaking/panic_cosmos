import logging

from src.alerting.alerts.alerts import Alert
from src.alerting.channels.channel import Channel


class DummyException(Exception):
    pass


class CounterChannel(Channel):

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__('counter_channel', logger, redis=None)
        self.info_count = 0
        self.minor_count = 0
        self.major_count = 0
        self.error_count = 0

    def reset(self) -> None:
        self.info_count = 0
        self.minor_count = 0
        self.major_count = 0
        self.error_count = 0

    def alert_info(self, alert: Alert) -> None:
        self.info_count += 1

    def alert_minor(self, alert: Alert) -> None:
        self.minor_count += 1

    def alert_major(self, alert: Alert) -> None:
        self.major_count += 1

    def alert_error(self, alert: Alert) -> None:
        self.error_count += 1

    def no_alerts(self):
        return self.info_count == 0 and self.minor_count == 0 and \
               self.major_count == 0 and self.error_count == 0
