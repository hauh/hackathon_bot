'''Hackathon echo-bot'''

import logging

from telegram import ParseMode
from telegram.ext import Defaults, Updater, MessageHandler, Filters

import config
import groups

##############################

logger = logging.getLogger('bot')


def reply(update, context):
	if update.effective_message.reply_to_message.from_user.id == config.bot_id:
		update.effective_message.reply_text("I'm sending request here!")


def promote(update, context):
	for new_member in update.effective_message.new_chat_members:
		if new_member.id != config.bot_id:
			groups.promote_admin(update.effective_message.chat.id, new_member.id)


def error(update, context):
	logger.error("SHIEEEET happened", exc_info=context.error)


def main():
	updater = Updater(
		token=config.bot_token,
		use_context=True,
		defaults=Defaults(parse_mode=ParseMode.MARKDOWN)
	)
	updater.dispatcher.add_handler(
		MessageHandler(Filters.reply, reply))
	updater.dispatcher.add_handler(
		MessageHandler(Filters.status_update.new_chat_members, reply))
	updater.dispatcher.add_error_handler(error)

	logger.info("Bot started")

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()
