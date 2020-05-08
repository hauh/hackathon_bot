'''Shops handler bot'''

import logging
import asyncio

from requests.exceptions import RequestException
from telethon import events
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import RPCError, FloodWaitError
from telethon.tl.functions.messages import (
	CreateChatRequest, ExportChatInviteRequest)

import config
import sessions
import conducte_requests

##############################

logger = logging.getLogger('bot')
sessions.init_db()
client = TelegramClient(
	StringSession(sessions.load_session(config.bot_name)),
	*config.client_id, **config.proxy
)


# logging error and warning admin
async def error(text, err):
	logger.error(text, exc_info=(type(err), err, None))
	await client.send_message(config.admin_group_id, text)


# launching manager
def get_code():
	auth_code = None

	async def get_code_from_admin(event):
		nonlocal auth_code
		auth_code = event.message.text

	async def waiting_for_code():
		for _ in range(10):
			if auth_code:
				return auth_code
			await asyncio.sleep(5)
		return None

	new_loop = asyncio.new_event_loop()
	asyncio.set_event_loop(new_loop)
	client.add_event_handler(
		get_code_from_admin,
		events.NewMessage(chats=config.admin_group_id, func=lambda _: not auth_code)
	)
	try:
		return new_loop.run_until_complete(waiting_for_code())
	finally:
		client.remove_event_handler(get_code_from_admin)
		new_loop.close()


def with_manager(handler):
	async def connect_manager(event):
		manager = TelegramClient(
			StringSession(sessions.load_session(config.manager_phone)),
			*config.client_id, **config.proxy
		)
		try:
			await manager.connect()
			if not await manager.is_user_authorized():
				await client.send_message(
					config.admin_group_id,
					f"Send auth_code for phone {config.manager_phone}"
				)
			await manager.start(
				config.manager_phone,
				code_callback=lambda: client.loop.run_in_executor(None, get_code)
			)
		except FloodWaitError as err:
			await error(f"Flood wait for {err.seconds} seconds for manager", err)
		except RPCError as err:
			await error(f"Error with manager: {type(err)}, {err.args}", err)
		else:
			await handler(manager, event)
			await manager.disconnect()
			sessions.save_session(config.manager_phone, manager.session.save())
	return connect_manager


# handling events

@with_manager
async def promote_admin(manager, event):
	await manager.edit_admin(event.input_chat, event.user, is_admin=True)
	await manager.kick_participant(event.input_chat, 'me')

	# removing this handler
	client.remove_event_handler(
		promote_admin,
		events.ChatAction(
			chats=event.input_chat.chat_id, func=lambda event: event.user_joined)
	)
	logger.info("Seller joined, permissions granted, now leaving")


@client.on(events.NewMessage(chats=config.admin_group_id, pattern=r'^/group .+'))
@with_manager
async def create_group(manager, event):
	# creating group with our bot added and getting invite link for it
	try:
		update = await manager(CreateChatRequest(
			title=f'Shop chat ID {event.message.text[7:]}',
			users=[config.bot_name]
		))
		new_group = update.updates[2].message.to_id
		update = await manager(ExportChatInviteRequest(new_group))
	except RPCError as err:
		await error("Group creation failed", err)
		return
	else:
		await event.message.reply(update.link)

	# group created, sending id to app
	try:
		conducte_requests.send_group(new_group.chat_id, update.link)
	except RequestException as err:
		await error("App request failed", err)
		await manager.kick_participant(new_group, 'me')
	else:
		# adding event handler for when first user has joined
		client.add_event_handler(
			promote_admin,
			events.ChatAction(
				chats=new_group.chat_id, func=lambda event: event.user_joined)
		)
		logger.info("Group created, id: %s", new_group.chat_id)


# reacting to seller's replies
@client.on(events.NewMessage(func=lambda event: event.message.is_reply))
async def send_request(event):
	# sending answer only to bot's original messages
	if reply_message := await event.message.get_reply_message():
		if not reply_message.is_reply and reply_message.from_id == config.bot_id:
			group_id = event.input_chat.chat_id
			try:
				conducte_requests.send_answer(group_id, event.message.text)
			except RequestException as err:
				await error(f"Error with answer from group id {group_id}!", err)


##############################

if __name__ == '__main__':
	client.start(bot_token=config.bot_token)
	client.run_until_disconnected()
	sessions.save_session(config.bot_name, client.session.save())
