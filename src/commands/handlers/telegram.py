import logging
from datetime import timedelta, datetime
from typing import Optional

from redis import RedisError
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, \
    CallbackContext

from src.commands.commands import Commands
from src.commands.handler_utils.telegram_handler import TelegramCommandHandler
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import UserConfig
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.redis_api import RedisApi


class TelegramCommands(Commands):

    def __init__(self, bot_token: str, authorised_chat_id: str,
                 logger: logging.Logger, redis: Optional[RedisApi],
                 redis_snooze_key: Optional[str], redis_mute_key: Optional[str],
                 redis_node_monitor_alive_key_prefix: Optional[str],
                 redis_network_monitor_alive_key_prefix: Optional[str],
                 internal_conf: InternalConfig = InternalConf,
                 user_conf: UserConfig = UserConf) -> None:

        super().__init__(logger, redis, redis_snooze_key, redis_mute_key,
                         redis_node_monitor_alive_key_prefix,
                         redis_network_monitor_alive_key_prefix, internal_conf,
                         user_conf)

        # Set up command handlers (command and respective callback function)
        command_handlers = [
            CommandHandler('start', self._start_callback),
            CommandHandler('snooze', self._snooze_callback),
            CommandHandler('mute', self._mute_callback),
            CommandHandler('unmute', self._unmute_callback),
            CommandHandler('unsnooze', self._unsnooze_callback),
            CommandHandler('status', self._status_callback),
            CommandHandler('validators', self._validators_callback),
            CommandHandler('block', self._block_callback),
            CommandHandler('tx', self._tx_callback),
            CommandHandler('help', self._help_callback),
            MessageHandler(Filters.command, self._unknown_callback)
        ]

        # Create command handler with the command handlers
        self.cmd_handler = TelegramCommandHandler(
            bot_token, authorised_chat_id, command_handlers)

    def start_listening(self) -> None:
        # Start listening for commands
        self.cmd_handler.start_handling()

    @staticmethod
    def formatted_reply(update: Update, reply: str):
        # Adds Markdown formatting
        update.message.reply_text(reply, parse_mode='Markdown')

    def _start_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /start command: update=%s, context=%s',
                          update, context)

        # If authorised, send welcome message
        if self.cmd_handler.authorise(update, context):
            update.message.reply_text("Welcome to the P.A.N.I.C. alerter bot!\n"
                                      "Type /help for more information.")

    def _snooze_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /snooze command: update=%s, context=%s',
                          update, context)

        # If authorised, snooze phone calls if Redis enabled
        if self.cmd_handler.authorise(update, context):
            if self._redis_enabled:
                # Expected: /snooze <hours>
                message_parts = update.message.text.split(' ')
                if len(message_parts) == 2:
                    try:
                        # Get number of hours and set temporary Redis key
                        hours = timedelta(hours=float(message_parts[1]))
                        until = str(datetime.now() + hours)
                        set_ret = self._redis.set_for(
                            self._redis_snooze_key, until, hours)
                        if set_ret is None:
                            update.message.reply_text(
                                'Snoozing unsuccessful due to an issue with '
                                'Redis. Check /status to see if it is online.')
                        else:
                            update.message.reply_text(
                                'Calls have been snoozed for {} hours until {}.'
                                ''.format(hours, until))
                    except ValueError:
                        update.message.reply_text('I expected a no. of hours.')
                else:
                    update.message.reply_text('I expected exactly one value.')
            else:
                update.message.reply_text('Snoozing is not available given '
                                          'that Redis is not set up.')

    def _unsnooze_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /unsnooze command: update=%s, context=%s',
                          update, context)
        # If authorised, unsnooze phone calls if Redis enabled
        if self.cmd_handler.authorise(update, context):
            if self._redis_enabled:
                # Remove snooze key if it exists
                if self._redis.exists(self._redis_snooze_key):
                    self._redis.remove(self._redis_snooze_key)
                    update.message.reply_text(
                        'Twilio calls have been unsnoozed.')
                else:
                    update.message.reply_text('Twilio calls were not snoozed.')
            else:
                update.message.reply_text('Unsnoozing is not available given '
                                          'that Redis is not set up.')

    def _mute_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /mute command: update=%s, context=%s',
                          update, context)

        # If authorised, mute the periodic alive reminder if Redis enabled
        if self.cmd_handler.authorise(update, context):
            if self._redis_enabled:
                # Expected: /mute <hours>
                message_parts = update.message.text.split(' ')
                if len(message_parts) == 2:
                    try:
                        # Get number of hours and set temporary Redis key
                        hours = timedelta(hours=float(message_parts[1]))
                        until = str(datetime.now() + hours)
                        set_ret = self._redis.set_for(
                            self._redis_mute_key, until, hours)
                        if set_ret is None:
                            update.message.reply_text(
                                'Muting unsuccessful due to an issue with '
                                'Redis. Check /status to see if it is online.')
                        else:
                            update.message.reply_text(
                                'The periodic alive reminder has been muted for'
                                ' {} hours until {}'.format(hours, until))
                    except ValueError:
                        update.message.reply_text('I expected a no. of hours.')
                else:
                    update.message.reply_text('I expected exactly one value.')
            else:
                update.message.reply_text('Muting is not available given '
                                          'that Redis is not set up.')

    def _unmute_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /unmute command: update=%s, context=%s',
                          update, context)
        # If authorised, unmute the periodic alive reminder if Redis enabled
        if self.cmd_handler.authorise(update, context):
            if self._redis_enabled:
                # Remove mute key if it exists
                if self._redis.exists(self._redis_mute_key):
                    self._redis.remove(self._redis_mute_key)
                    update.message.reply_text(
                        'The periodic alive reminder has been unmuted.')
                else:
                    update.message.reply_text('The periodic alive reminder was '
                                              'not muted.')
            else:
                update.message.reply_text('Unmuting is not available given '
                                          'that Redis is not set up.')

    def _status_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /status command: update=%s, context=%s',
                          update, context)

        # If authorised, send status if Redis enabled
        if self.cmd_handler.authorise(update, context):
            if self._redis_enabled:
                status = ""

                # Add Redis status
                # (step 1: check if it is running)
                try:
                    self._redis.ping_unsafe()
                    redis_running = True
                except (RedisError, ConnectionResetError):
                    redis_running = False
                except Exception as e:
                    self._logger.error('Unrecognized error when accessing '
                                       'Redis: %s', e)
                    redis_running = False

                # (step 2: add the actual status)
                if redis_running:
                    if self._redis.is_live:
                        status += '- Redis is running normally.\n'
                    else:
                        status += '- Redis is running normally but was not ' \
                                  'accessible a short while ago. Recent ' \
                                  'updates might be unavailable until the ' \
                                  'monitors detect Redis being active again.\n'
                else:
                    status += '- Redis is NOT accessible!\n'

                # Add Twilio calls snooze state to status
                if redis_running:
                    if self._redis.exists(self._redis_snooze_key):
                        until = self._redis.get(
                            self._redis_snooze_key).decode("utf-8")
                        status += '- Twilio calls are snoozed until {}.\n' \
                                  ''.format(until)
                    else:
                        status += '- Twilio calls are not snoozed.\n'

                # Add periodic alive reminder mute state to status
                if redis_running:
                    if self._redis.exists(self._redis_mute_key):
                        until = self._redis.get(
                            self._redis_mute_key).decode("utf-8")
                        status += '- The periodic alive reminder has been ' \
                                  'muted until {}.\n'.format(until)
                    else:
                        status += '- The periodic alive reminder is not ' \
                                  'muted.\n'

                # Add node monitor latest updates to status
                if redis_running:
                    node_monitor_keys_list = self._redis.get_keys(
                        self._redis_node_monitor_alive_key_prefix + '*')
                    node_monitor_names = [
                        k.replace(self._redis_node_monitor_alive_key_prefix, '')
                        for k in node_monitor_keys_list
                    ]
                    for key, name in zip(node_monitor_keys_list,
                                         node_monitor_names):
                        last_update = self._redis.get(key).decode('utf-8')
                        last_update = last_update.split('.')[
                            0]  # remove seconds
                        status += '- Last update from *{}*: `{}`.\n' \
                                  ''.format(name, last_update)

                    # Add note if no latest node monitor updates
                    if len(node_monitor_keys_list) == 0:
                        status += '- No recent update from node monitors.\n'

                # Add network monitor latest updates to status
                if redis_running:
                    net_monitor_keys_list = self._redis.get_keys(
                        self._redis_network_monitor_alive_key_prefix + '*')
                    net_monitor_names = [
                        k.replace(self._redis_network_monitor_alive_key_prefix,
                                  '')
                        for k in net_monitor_keys_list
                    ]
                    for key, name in zip(net_monitor_keys_list,
                                         net_monitor_names):
                        last_update = self._redis.get(key).decode('utf-8')
                        last_update = last_update.split('.')[
                            0]  # remove seconds
                        status += '- Last update from *{}*: `{}`.\n' \
                                  ''.format(name, last_update)

                    # Add note if no latest network monitor updates
                    if len(net_monitor_keys_list) == 0:
                        status += '- No recent update from network monitors.\n'

                    for name in net_monitor_names:
                        redis_last_height_checked_key = \
                            self._internal_conf. \
                                redis_network_monitor_last_height_key_prefix + \
                            name
                        last_height_checked = self._redis.get(
                            redis_last_height_checked_key).decode('utf-8')
                        status += '- *{}* is currently in block height {}' \
                                  '.\n'.format(name, last_height_checked)

                # If redis is not running
                if not redis_running:
                    status += \
                        '- Since Redis is not accessible, Twilio calls are ' \
                        'considered not snoozed, the periodic alive reminder ' \
                        'is not muted, and any recent update from ' \
                        'node or network monitors is not accessible.\n'

                # Send status
                TelegramCommands.formatted_reply(
                    update, status[:-1] if status.endswith('\n') else status)
            else:
                update.message.reply_text('Status update not available given '
                                          'that Redis is not set up.')

    def _validators_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /validators command: update=%s, context=%s',
                          update, context)

        # If authorised, send list of links to validators
        if self.cmd_handler.authorise(update, context):
            update.message.reply_text(
                'Links to validators:\n'
                '  Hubble: {}\n'
                '  BigDipper: {}\n'
                '  Stargazer: {}\n'
                '  Mintscan: {}\n'
                '  Lunie: {}'.format(
                    self._internal_conf.validators_hubble_link,
                    self._internal_conf.validators_big_dipper_link,
                    self._internal_conf.validators_stargazer_link,
                    self._internal_conf.validators_mintscan_link,
                    self._internal_conf.validators_lunie_link))

    def _block_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /block command: update=%s, context=%s',
                          update, context)

        # If authorised, send list of links to specified block
        if self.cmd_handler.authorise(update, context):
            # Expected: /block <block>
            message_parts = update.message.text.split(' ')
            if len(message_parts) == 2:
                try:
                    block_height = int(message_parts[1])
                    update.message.reply_text(
                        'Links to block:\n'
                        '  Hubble: {}{}\n'
                        '  BigDipper: {}{}\n'
                        '  Stargazer: {}{}\n'
                        '  Mintscan: {}{}\n'
                        '  Lunie: {}{}'.format(
                            self._internal_conf.block_hubble_link_prefix,
                            block_height,
                            self._internal_conf.block_big_dipper_link_prefix,
                            block_height,
                            self._internal_conf.block_stargazer_link_prefix,
                            block_height,
                            self._internal_conf.block_mintscan_link_prefix,
                            block_height,
                            self._internal_conf.block_lunie_link_prefix,
                            block_height))
                except ValueError:
                    update.message.reply_text("I expected a block height.")
            else:
                update.message.reply_text("I expected exactly one value.")

    def _tx_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /tx command: update=%s, context=%s',
                          update, context)

        # If authorised, send list of links to specified transaction
        if self.cmd_handler.authorise(update, context):
            # Expected: /tx <tx-hash>
            message_parts = update.message.text.split(' ')
            if len(message_parts) == 2:
                tx_hash = message_parts[1]
                update.message.reply_text(
                    'Links to transaction:\n'
                    '  Hubble: {}\n'
                    '  BigDipper: {}\n'
                    '  Mintscan: {}'.format(
                        self._internal_conf.tx_hubble_link_prefix +
                        str(tx_hash),
                        self._internal_conf.tx_big_dipper_link_prefix +
                        str(tx_hash),
                        self._internal_conf.tx_mintscan_link_prefix +
                        str(tx_hash)))
            else:
                update.message.reply_text("I expected exactly one value.")

    def _help_callback(self, update: Update, context: CallbackContext):
        self._logger.info('Received /help command: update=%s, context=%s',
                          update, context)

        # If authorised, send help message with available commands
        if self.cmd_handler.authorise(update, context):
            update.message.reply_text(
                'Hey! These are the available commands:\n'
                '  /start: welcome message\n'
                '  /ping: ping the Telegram commands handler\n'
                '  /snooze <hours>: snoozes phone calls for <hours>\n'
                '  /unsnooze: unsnoozes phone calls\n'
                '  /mute <hours>: mute periodic alive reminder for <hours>\n'
                '  /unmute: unmute periodic alive reminder\n'
                '  /status: shows status message\n'
                '  /validators: shows links to validators\n'
                '  /block <height>: shows link to specified block\n'
                '  /tx <tx-hash>: shows link to specified transaction\n'
                '  /help: shows this message')

    def _unknown_callback(self, update: Update,
                          context: CallbackContext) -> None:
        self._logger.info(
            'Received unrecognized command: update=%s, context=%s',
            update, context)

        # If authorised, send a default message for unrecognized commands
        if self.cmd_handler.authorise(update, context):
            update.message.reply_text('I did not understand (Type /help)')

    # TODO: Need to add callbacks for add_node, remove_node, current_nodes
