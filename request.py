'''Requesting bot to send a message to the group'''

import requests
import config

##############################


def send_message(text):
	response = requests.post(
		f"https://api.telegram.org/bot{config.bot_token}/sendMessage",
		data={
			'chat_id': config.group_id,
			'text': text
		},
		proxies=dict(https=config.proxy) if config.proxy else None
	)
	if not response.ok:
		response.raise_for_status()
