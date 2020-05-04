'''Hackathon echo-bot'''

import logging

from telegram import ParseMode
from telegram.ext import Defaults, Updater, MessageHandler, Filters

import config

##############################

logger = logging.getLogger('bot')


def reply(update, context):
	if update.effective_message.reply_to_message.from_user.id == config.bot_id:
		update.effective_message.reply_text("I'm sending request here!")


def error(update, context):
	logger.error("SHIEEEET happened", exc_info=context.error)


def main():
	updater = Updater(
		token=config.bot_token,
		use_context=True,
		defaults=Defaults(parse_mode=ParseMode.MARKDOWN),
		request_kwargs=dict(proxy_url=config.proxy) if config.proxy else None
	)
	updater.dispatcher.add_handler(
		MessageHandler(Filters.chat(config.group_id) & Filters.reply, reply)
	)
	updater.dispatcher.add_error_handler(error)

	logger.info("Bot started")

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()
