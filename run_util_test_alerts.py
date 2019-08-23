from src.alerting.alert_utils.get_channel_set import get_full_channel_set
from src.alerting.alerts.alerts import Alert
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.logging import DUMMY_LOGGER

if __name__ == '__main__':
    channel_set = get_full_channel_set(
        channel_name='TEST', logger_general=DUMMY_LOGGER, redis=None,
        alerts_log_file=InternalConf.alerts_log_file)

    channel_set.alert_info(Alert('This is a test info alert.'))
    channel_set.alert_minor(Alert('This is a test minor alert.'))
    channel_set.alert_major(Alert('This is a test major alert.'))
    channel_set.alert_error(Alert('This is a test error alert.'))
