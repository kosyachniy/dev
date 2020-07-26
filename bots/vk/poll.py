import os
from random import randint
import json
import time

import requests
import vk


# Настройки

with open('keys.json', 'r') as file:
	VK_API_ACCESS_TOKEN = json.loads(file.read())['vk']['token']

with open('sets.json', 'r') as file:
	GROUP_ID = json.loads(file.read())['vk']['group']

VK_API_VERSION = '5.95'


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)

# Первый запрос к LongPoll: получаем server и key
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']


def process(update):
	# print(update)
	print('→', update['from_id'], update['text'])

	# Помечаем сообщение как прочитанное
	api.messages.markAsRead(peer_id=update['from_id'])

	# Определяем пользователя

	user = api.users.get(
		user_ids=update['from_id'],
		fields='first_name, last_name, photo_id, screen_name',
	)[0]

	user_new = dict()
	param_map = {
		'first_name': 'name',
		'last_name': 'surname',
		'screen_name': 'login',
		'photo_id': 'avatar',
	}

	for param in param_map:
		if param in user:
			user_new[param_map[param]] = user[param]

	print(user_new)

	# Отправляем сообщение
	api.messages.send(
		user_id=update['from_id'],
		random_id=randint(-2147483648, 2147483647),
		message='Чё надо',
	)


while True:
	# Последующие запросы: меняется только ts
	try:
		longPoll = requests.post(server, data={
			'act': 'a_check',
			'key': key,
			'ts': ts,
			'wait': 25,
		}).json()
	except:
		print('Error 1')
		time.sleep(1)
		continue

	if 'updates' in longPoll and len(longPoll['updates']):
		for update in longPoll['updates']:
			if update['type'] == 'message_new':
				process(update['object'])

	# Меняем ts для следующего запроса
	try:
		ts = longPoll['ts']

	except:
		print('Error 2')
		period = 0

		while True:
			period += 1

			try:
				session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
				api = vk.API(session, v=VK_API_VERSION)

				# Первый запрос к LongPoll: получаем server и key
				longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
				server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']

			except:
				print('Error 3')
				time.sleep(period)

			else:
				break