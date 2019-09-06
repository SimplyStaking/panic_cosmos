import logging
from typing import Optional

from src.alerting.alert_utils.email_sending import EmailSender
from src.alerting.alert_utils.telegram_bot_api import TelegramBotApi
from src.alerting.alert_utils.twilio_api import TwilioApi
from src.alerting.channels.channel import ChannelSet
from src.alerting.channels.console import ConsoleChannel
from src.alerting.channels.email import EmailChannel
from src.alerting.channels.log import LogChannel
from src.alerting.channels.telegram import TelegramChannel
from src.alerting.channels.twilio import TwilioChannel
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import UserConfig
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.logging import create_logger
from src.utils.redis_api import RedisApi


def get_full_channel_set(channel_name: str, logger_general: logging.Logger,
                         redis: Optional[RedisApi], alerts_log_file: str,
                         internal_conf: InternalConfig = InternalConf,
                         user_conf: UserConfig = UserConf) -> ChannelSet:
    # Logger initialisation
    logger_alerts = create_logger(alerts_log_file, 'alerts',
                                  internal_conf.logging_level)

    # Initialise list of channels with default channels
    channels = [
        ConsoleChannel(channel_name, logger_general),
        LogChannel(channel_name, logger_general, logger_alerts)
    ]

    # Initialise backup channel sets with default channels
    backup_channels_for_telegram = ChannelSet(channels)
    backup_channels_for_twilio = ChannelSet(channels)

    # Add telegram alerts to channel set
    if user_conf.telegram_alerts_enabled:
        telegram_bot = TelegramBotApi(user_conf.telegram_alerts_bot_token,
                                      user_conf.telegram_alerts_bot_chat_id)
        telegram_channel = TelegramChannel(channel_name, logger_general, redis,
                                           telegram_bot,
                                           backup_channels_for_telegram)
        channels.append(telegram_channel)
    else:
        telegram_channel = None

    # Add email alerts to channel set
    if user_conf.email_alerts_enabled:
        email = EmailSender(user_conf.email_smtp, user_conf.email_from,
                            user_conf.email_user, user_conf.email_pass)
        email_channel = EmailChannel(channel_name, logger_general,
                                     redis, email, user_conf.email_to)
        channels.append(email_channel)
    else:
        email_channel = None

    # Add twilio alerts to channel set
    if user_conf.twilio_alerts_enabled:
        twilio = TwilioApi(user_conf.twilio_account_sid,
                           user_conf.twilio_auth_token)
        twilio_channel = TwilioChannel(channel_name, logger_general, redis,
                                       twilio, user_conf.twilio_phone_number,
                                       user_conf.twilio_dial_numbers,
                                       internal_conf.twiml_instructions_url,
                                       internal_conf.redis_twilio_snooze_key,
                                       backup_channels_for_twilio)
        channels.append(twilio_channel)
    else:
        # noinspection PyUnusedLocal
        twilio_channel = None

    # Set up email channel as backup channel for telegram and twilio
    if email_channel is not None:
        backup_channels_for_telegram.add_channel(email_channel)
        backup_channels_for_twilio.add_channel(email_channel)

    # Set up telegram channel as backup channel for twilio
    if telegram_channel is not None:
        backup_channels_for_twilio.add_channel(telegram_channel)

    return ChannelSet(channels)
