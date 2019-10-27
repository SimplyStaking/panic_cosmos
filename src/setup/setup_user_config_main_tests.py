from enum import Enum

from src.alerting.alert_utils.email_sending import EmailSender
from src.alerting.alert_utils.telegram_bot_api import TelegramBotApi
from src.alerting.alert_utils.twilio_api import TwilioApi
from src.commands.handler_utils.telegram_handler import TelegramCommandHandler
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.logging import DUMMY_LOGGER
from src.utils.redis_api import RedisApi
from src.utils.user_input import yn_prompt


class TestOutcome(Enum):
    OK = 1,
    RestartSetup = 2,
    SkipSetup = 3


def test_telegram_alerts(bot_api: TelegramBotApi) -> TestOutcome:
    response = bot_api.send_message('*Test Alert*')
    if response['ok']:
        print('Test alert sent successfully.')
        if yn_prompt('Was the testing successful? (Y/n)\n'):
            return TestOutcome.OK
        elif yn_prompt('Retry Telegram alerts setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup
    else:
        print('Something went wrong: {}'.format(response))
        if yn_prompt('Retry Telegram alerts setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup


def test_email_alerts(email_smtp: str, email_from: str, email_to: str,
                      email_user: str, email_pass: str) -> TestOutcome:
    email_sender = EmailSender(email_smtp, email_from, email_user, email_pass)
    try:
        email_sender.send_email('Test Alert', 'Test Alert', email_to)
        print('Test email sent.')

        if yn_prompt('Was the testing successful? (Y/n)\n'):
            return TestOutcome.OK
        elif yn_prompt('Retry email alerts setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup
    except Exception as e:
        print('Something went wrong: {}'.format(e))
        if yn_prompt('Retry email alerts setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup


def test_twilio_alerts(twilio_no: str, to_dial: str, twilio_api: TwilioApi,
                       internal_conf: InternalConfig = InternalConf) \
        -> TestOutcome:
    try:
        twilio_api.dial_number(twilio_no, to_dial,
                               internal_conf.twiml_instructions_url)
        print('Test phone call requested successfully. Please wait a bit.')

        if yn_prompt('Was the testing successful? (Y/n)\n'):
            return TestOutcome.OK
        elif yn_prompt('Retry Twilio alerts setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup
    except Exception as e:
        print('Something went wrong: {}'.format(e))
        print('The Twilio details you provided might be incorrect.')
        if yn_prompt('Retry Twilio alerts setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup


def test_telegram_commands(bot_token: str, bot_chat_id: str) -> TestOutcome:
    cmd_handler = TelegramCommandHandler(
        bot_token, bot_chat_id, None)
    cmd_handler.start_handling(run_in_background=True)
    print('Go ahead and send /ping to the Telegram bot.')
    input('Press ENTER once you are done sending commands...')
    print('Stopping the Telegram bot...')
    cmd_handler.stop()

    if yn_prompt('Was the testing successful? (Y/n)\n'):
        return TestOutcome.OK
    elif yn_prompt('Retry Telegram commands setup? (Y/n)\n'):
        return TestOutcome.RestartSetup
    else:
        return TestOutcome.SkipSetup


def test_redis(host: str, port: str, password: str) -> TestOutcome:
    redis = RedisApi(DUMMY_LOGGER, 0, host, int(port),
                     password=password, namespace='')
    try:
        redis.ping_unsafe()
        print('Test completed successfully.')
        return TestOutcome.OK
    except Exception as e:
        print('Something went wrong: {}'.format(e))
        if yn_prompt('Retry Redis setup? (Y/n)\n'):
            return TestOutcome.RestartSetup
        else:
            return TestOutcome.SkipSetup
