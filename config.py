'''Bot config'''

import os
import logging

##############################

logging.basicConfig(
	level=logging.INFO,
	format='{asctime} - {name}.{funcName} - {levelname} - {message}',
	style='{',
)
bot_token = os.getenv('BOT_TOKEN')
proxy = os.getenv('PROXY')
group_id = int(os.getenv('GROUP_ID'))
bot_id = int(bot_token.split(':')[0])
