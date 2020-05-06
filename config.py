'''Bot config'''

import os
import logging
from telethon import connection


##############################

logging.basicConfig(
	level=logging.INFO,
	format='{asctime} - {name}.{funcName} - {levelname} - {message}',
	style='{',
)
if (proxy := os.getenv('MTPROTO_PROXY', {})):
	address, port, secret = proxy.split(':')
	proxy = {
		'connection': connection.ConnectionTcpMTProxyRandomizedIntermediate,
		'proxy': (address, int(port), secret)
	}

# bot
bot_token = os.getenv('BOT_TOKEN')
bot_id = int(bot_token.split(':')[0])
bot_name = os.getenv('BOT_NAME')
client_id = (os.getenv('API_ID'), os.getenv('API_HASH'))
manager_phone = os.getenv('MANAGER_PHONE')
