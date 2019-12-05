from typing import Optional, List

from telegram import Update
from telegram.ext import Updater, CommandHandler, \
    Handler, CallbackContext

from src.alerting.alert_utils.telegram_bot_api import TelegramBotApi


class TelegramCommandHandler:

    def __init__(self, bot_token: str, authorised_chat_id: Optional[str],
                 handlers: Optional[List[Handler]] = None) -> None:
        self._bot_token = bot_token
        self._authorised_chat_id = authorised_chat_id

        # Set up updater
        self._updater = Updater(token=bot_token, use_context=True)

        # Set up handlers
        ping_handler = CommandHandler('ping', self._ping_callback)
        self._updater.dispatcher.add_handler(ping_handler)
        if handlers is not None:
            for h in handlers:
                self._updater.dispatcher.add_handler(h)

    def start_handling(self, run_in_background: bool = False) -> None:
        # Start polling
        self._updater.start_polling(clean=True)

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        if not run_in_background:
            self._updater.idle(stop_signals=[])

    def authorise(self, update: Update, context: CallbackContext) -> bool:
        if self._authorised_chat_id in [None, str(update.message.chat_id)]:
            return True
        else:
            update.message.reply_text("Unrecognised user. "
                                      "This event has been reported.")
            api = TelegramBotApi(self._bot_token, self._authorised_chat_id)
            api.send_message(
                'Received command from unrecognised user: '
                'update={}, context={}'.format(update, context))
            return False

    def _ping_callback(self, update: Update, context: CallbackContext) -> None:
        if self.authorise(update, context):
            update.message.reply_text('PONG!')

    def stop(self) -> None:
        # This is useful only when the Updater is set to run in background
        self._updater.stop()
