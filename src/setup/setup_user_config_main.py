from configparser import ConfigParser

from src.alerting.alert_utils.telegram_bot_api import TelegramBotApi
from src.alerting.alert_utils.twilio_api import TwilioApi
from src.setup.setup_user_config_main_tests import test_telegram_alerts, \
    TestOutcome, test_email_alerts, test_twilio_alerts, \
    test_telegram_commands, test_redis
from src.utils.user_input import yn_prompt


def is_already_set_up(cp: ConfigParser, section: str) -> bool:
    # Find out if the section exists
    if section not in cp:
        return False

    # Find out if any value in the section (except for enabled) is filled-in
    for key in cp[section]:
        if key != 'enabled' and cp[section][key] != '':
            return True
    return False


def reset_section(section: str, cp: ConfigParser) -> None:
    # Remove and re-add specified section if it exists
    if cp.has_section(section):
        cp.remove_section(section)
    cp.add_section(section)


def setup_general(cp: ConfigParser) -> None:
    print('==== General')
    print('The first step is to set a unique identifier for the alerter. This '
          'can be any word that uniquely describes the setup being monitored. '
          'Uniqueness is very important if you are running multiple instances '
          'of the P.A.N.I.C. alerter, to avoid any possible Redis clashes. The '
          'name will only be used internally and will not show up in alerts.')

    already_set_up = is_already_set_up(cp, 'general')
    if already_set_up:
        identifier = cp['general']['unique_alerter_identifier']
        if not yn_prompt(
                'A unique alerter identifier \'{}\' is already set. Do you '
                'wish to change this identifier? (Y/n)\n'.format(identifier)):
            return

    reset_section('general', cp)
    cp['general']['unique_alerter_identifier'] = ''

    while True:
        identifier = input('Please insert the unique identifier:\n')
        if len(identifier) != 0:
            break
        else:
            print('The unique identifier cannot be blank.')

    cp['general']['unique_alerter_identifier'] = identifier


def setup_telegram_alerts(cp: ConfigParser) -> None:
    print('---- Telegram Alerts')
    print('Alerts sent via Telegram are a fast and reliable means of alerting '
          'that we highly recommend setting up. This requires you to have a '
          'Telegram bot set up, which is a free and quick procedure.')

    already_set_up = is_already_set_up(cp, 'telegram_alerts')
    if already_set_up and \
            not yn_prompt('Telegram alerts are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    reset_section('telegram_alerts', cp)
    cp['telegram_alerts']['enabled'] = str(False)
    cp['telegram_alerts']['bot_token'] = ''
    cp['telegram_alerts']['bot_chat_id'] = ''

    if not already_set_up and \
            not yn_prompt('Do you wish to set up Telegram alerts? (Y/n)\n'):
        return

    while True:
        while True:
            bot_token = input('Please insert your Telegram bot\'s API token:\n')
            bot_api = TelegramBotApi(bot_token, None)

            confirmation = bot_api.get_me()
            if not confirmation['ok']:
                print(str(confirmation))
            else:
                print('Successfully connected to Telegram bot.')
                break

        bot_chat_id = input('Please insert the chat ID for Telegram alerts:\n')
        bot_api = TelegramBotApi(bot_token, bot_chat_id)

        if yn_prompt('Do you wish to test Telegram alerts now? (Y/n)\n'):
            test = test_telegram_alerts(bot_api)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['telegram_alerts']['enabled'] = str(True)
    cp['telegram_alerts']['bot_token'] = bot_token
    cp['telegram_alerts']['bot_chat_id'] = bot_chat_id


def setup_email_alerts(cp: ConfigParser) -> None:
    print('---- Email Alerts')
    print('Email alerts are more useful as a backup alerting channel rather '
          'than the main one, given that one is much more likely to notice a '
          'a message on Telegram or a phone call. Email alerts also require '
          'an SMTP server to be set up for the alerter to be able to send.')

    already_set_up = is_already_set_up(cp, 'email_alerts')
    if already_set_up and \
            not yn_prompt('Email alerts are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    reset_section('email_alerts', cp)
    cp['email_alerts']['enabled'] = str(False)
    cp['email_alerts']['smtp'] = ''
    cp['email_alerts']['from'] = ''
    cp['email_alerts']['to'] = ''

    if not already_set_up and \
            not yn_prompt('Do you wish to set up email alerts? (Y/n)\n'):
        return

    while True:
        email_smtp = input('Please insert the SMTP server\'s address:\n')

        email_from = input('Please specify the details of the sender in the '
                           'format shown below:\n\t'
                           'example_sender@email.com\n')

        email_to = input('Please specify the email address where you wish to '
                         'receive email alerts:\n\t'
                         'example_recipient@email.com\n')

        while yn_prompt('Do you wish to add another email address? (Y/n)\n'):
            email_to += ';' + input('Please insert the email address:\n')

        if yn_prompt('Do you wish to test email alerts now? The first '
                     'email address inserted will be used. (Y/n)\n'):
            test = test_email_alerts(email_smtp, email_from,
                                     email_to.split(';')[0])
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['email_alerts']['enabled'] = str(True)
    cp['email_alerts']['smtp'] = email_smtp
    cp['email_alerts']['from'] = email_from
    cp['email_alerts']['to'] = email_to


def setup_twilio_alerts(cp: ConfigParser) -> None:
    print('---- Twilio Alerts')
    print('Twilio phone-call alerts are the most important alerts since they '
          'are the best at grabbing your attention, especially when you\'re '
          'asleep! To set these up, you have to have a Twilio account set up, '
          'with a registered Twilio phone number and a verified phone number.'
          'The timed trial version of Twilio is free.')

    already_set_up = is_already_set_up(cp, 'twilio_alerts')
    if already_set_up and \
            not yn_prompt('Twilio alerts are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    reset_section('twilio_alerts', cp)
    cp['twilio_alerts']['enabled'] = str(False)
    cp['twilio_alerts']['account_sid'] = ''
    cp['twilio_alerts']['auth_token'] = ''
    cp['twilio_alerts']['twilio_phone_number'] = ''
    cp['twilio_alerts']['phone_numbers_to_dial'] = ''

    if not already_set_up and \
            not yn_prompt('Do you wish to set up Twilio alerts? (Y/n)\n'):
        return

    while True:

        while True:
            account_sid = input('Please insert your Twilio account SID:\n')
            auth_token = input('Please insert your Twilio account AuthToken:\n')

            try:
                twilio_api = TwilioApi(account_sid, auth_token)
                print('Successfully connected to Twilio.')
                break
            except Exception as e:
                print('Something went wrong: {}'.format(e))

        twilio_no = input('Please insert your registered Twilio phone number '
                          'in the format shown below:\n\t'
                          'E.164 format, for example: +12025551234\n')

        to_dial = input('Please insert the first phone number to dial for '
                        'alerting purposes in the format shown below:\n\t'
                        'E.164 format, for example: +12025551234\n')

        while yn_prompt('Do you wish to add another number? (Y/n)\n'):
            to_dial += ';' + input('Please insert the phone number:\n')

        if yn_prompt('Do you wish to test Twilio alerts now? The first '
                     'phone number inserted will be called. (Y/n)\n'):
            test = test_twilio_alerts(twilio_no, to_dial.split(';')[0],
                                      twilio_api)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['twilio_alerts']['enabled'] = str(True)
    cp['twilio_alerts']['account_sid'] = account_sid
    cp['twilio_alerts']['auth_token'] = auth_token
    cp['twilio_alerts']['twilio_phone_number'] = twilio_no
    cp['twilio_alerts']['phone_numbers_to_dial'] = to_dial


def setup_alerts(cp: ConfigParser) -> None:
    print('==== Alerts')
    print('By default, alerts are output to a log file and to '
          'the console. Let\'s set up the rest of the alerts.')
    setup_telegram_alerts(cp)
    setup_email_alerts(cp)
    setup_twilio_alerts(cp)


def setup_telegram_commands(cp: ConfigParser) -> None:
    print('---- Telegram Commands')
    print('Telegram is also used as a two-way interface with the alerter and '
          'as an assistant, allowing you to do things such as snooze phone '
          'call alerts and to get the alerter\'s current status from Telegram. '
          'Once again, this requires you to set up a Telegram bot, which is '
          'free and easy. You can reuse the Telegram bot set up for alerts.')

    already_set_up = is_already_set_up(cp, 'telegram_commands')
    if already_set_up and \
            not yn_prompt('Telegram commands are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    print('NOTE: If you are running more than one instance of the P.A.N.I.C. '
          'alerter, do not use the same telegram bot as the other instance/s.')

    reset_section('telegram_commands', cp)
    cp['telegram_commands']['enabled'] = str(False)
    cp['telegram_commands']['bot_token'] = ''
    cp['telegram_commands']['bot_chat_id'] = ''

    if not already_set_up and \
            not yn_prompt('Do you wish to set up Telegram commands? (Y/n)\n'):
        return

    while True:
        while True:
            bot_token = input('Please insert your Telegram bot\'s API token:\n')
            bot_api = TelegramBotApi(bot_token, None)

            confirmation = bot_api.get_me()
            if not confirmation['ok']:
                print(str(confirmation))
            else:
                print('Successfully connected to Telegram bot.')
                break

        bot_chat_id = input('Please insert the authorised chat ID:\n')

        if yn_prompt('Do you wish to test Telegram commands now? (Y/n)\n'):
            test = test_telegram_commands(bot_token, bot_chat_id)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['telegram_commands']['enabled'] = str(True)
    cp['telegram_commands']['bot_token'] = bot_token
    cp['telegram_commands']['bot_chat_id'] = bot_chat_id


def setup_commands(cp: ConfigParser) -> None:
    print('==== Commands')
    setup_telegram_commands(cp)


def setup_redis(cp: ConfigParser) -> None:
    print('==== Redis')
    print('Redis is used by the alerter to persist data every now and then, '
          'so that it can continue where it left off if it is restarted. It '
          'is also used to be able to get the status of the alerter and to '
          'have some control over it, such as to snooze Twilio phone calls.')

    already_set_up = is_already_set_up(cp, 'redis')
    if already_set_up and \
            not yn_prompt('Redis is already set up. Do you wish '
                          'to clear the current config? (Y/n)\n'):
        return

    reset_section('redis', cp)
    cp['redis']['enabled'] = str(False)
    cp['redis']['host'] = ''
    cp['redis']['port'] = ''
    cp['redis']['password'] = ''

    if not already_set_up and \
            not yn_prompt('Do you wish to set up Redis? (Y/n)\n'):
        return

    while True:
        host = input('Please insert the Redis host IP: (default: localhost)\n')
        host = 'localhost' if host == '' else host

        port = input('Please insert the Redis host port: (default: 6379)\n')
        port = '6379' if port == '' else port

        password = input('Please insert the Redis password:\n')

        if yn_prompt('Do you wish to test Redis now? (Y/n)\n'):
            test = test_redis(host, port, password)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['redis']['enabled'] = str(True)
    cp['redis']['host'] = host
    cp['redis']['port'] = port
    cp['redis']['password'] = password


def setup_all(cp: ConfigParser) -> None:
    setup_general(cp)
    print()
    setup_alerts(cp)
    print()
    setup_commands(cp)
    print()
    setup_redis(cp)
    print('Setup finished.')
