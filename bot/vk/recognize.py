from random import randint
import json
import time

import requests
import vk


# Настройки

with open('keys.json', 'r') as file:
	VK_API_ACCESS_TOKEN = json.loads(file.read())['vk']['token']

with open('sets.json', 'r') as file:
	sets = json.loads(file.read())
	GROUP_ID = sets['vk']['group']
	SERVER_LINK = sets['server']['link']
	CLIENT_LINK = sets['client']['link']

VK_API_VERSION = '5.95'


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)

# Первый запрос к LongPoll: получаем server и key
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']


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
			print(update['object'])

			# Приём сообщений
			# if update['object']['from_id'] < 0: # and update['object']['peer_id'] != update['object']['from_id']:
			# 	continue

			if update['type'] == 'message_new':
				api.messages.send(
					peer_id=update['object']['peer_id'],
					random_id=randint(-2147483648, 2147483647),
					message='идентификатор #{}/{}'.format(update['object']['from_id'], update['object']['peer_id']),
				)

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
				time.sleep(5 * period)

			else:
				break