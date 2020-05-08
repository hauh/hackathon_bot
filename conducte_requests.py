'''Requesting bot to send a message to the group'''

import os
import json
import requests

##############################

HEADERS = {
	'Content-Type': 'application/json',
	'X-Hasura-Admin-Secret': os.environ['ADMIN_SECRET'],
}
HGE_URL = f"{os.environ['HGE_ENDPOINT']}/v1/graphql"

answer_to_message_query = """
	mutation addMessage($group_id: String!, $text: String!) {
		insert_Message_one(object: {group_id: $group_id, text: $text}){
			id
		}
	}
"""


def _send(data):
	response = requests.post(HGE_URL, data=json.dumps(data), headers=HEADERS)
	if not response.ok:
		response.raise_for_status()


def send_answer(group_id, text):
	_send({
		'query': answer_to_message_query,
		'variables': {
			'group_id': str(group_id),
			'text': text,
		}
	})


def send_group(group_id, invite_link):
	_send({
		'statusCode': 200,
		'group_id': str(group_id),
		'invite_link': invite_link,
	})
