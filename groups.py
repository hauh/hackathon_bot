'''Creating telegram group and returng invite link'''

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import (
	CreateChatRequest, ExportChatInviteRequest)
from telethon.tl.functions.channels import EditAdminRequest, EditCreatorRequest
from telethon.tl.types import ChatAdminRights

import config

##############################


def with_client(action):
	def start_client(*args, **kwargs):
		client = TelegramClient('Conducte', *config.client_id, **config.proxy)
		client.start(config.manager_phone)
		return action(client, *args, **kwargs)
	return start_client


@with_client
def create_group(client, shop_id):
	update = client(CreateChatRequest(
		title=f'Shop chat ID {shop_id}',
		users=[config.bot_name]
	))
	new_chat = update.updates[2].message.to_id
	update = client(ExportChatInviteRequest(new_chat))
	return update.link


@with_client
def promote_admin(client, group_id, user_id):
	chat = client.get_input_entity(group_id)
	for member in client.get_participants(chat):
		if member.id == user_id:
			client(EditAdminRequest(
				channel=group_id,
				user_id=member,
				admin_rights=ChatAdminRights(
					add_admins=True,
					invite_users=True,
					change_info=True,
					ban_users=True,
					delete_messages=True,
					pin_messages=True,
					invite_link=True,
				)
			))
			# then transfer ownership and leave the group
			# client(EditCreatorRequest(chat, member, ...)
