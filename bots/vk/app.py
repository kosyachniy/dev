import os
from random import randint
import json
import string
import random
import time
import base64

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


# Пользователи
tokens = dict()
ids = dict()


# Генерация токена

ALL_SYMBOLS = string.ascii_lowercase + string.digits
generate = lambda length=32: ''.join(random.choice(ALL_SYMBOLS) for _ in range(length))


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)

# Первый запрос к LongPoll: получаем server и key
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']


# Отправить сообщение
def send(user, cont, keyboard=[], keyboard_inline=False):
	keyb = None
	if len(keyboard):
		keyb = {
			# 'one_time': True,
			# 'inline': True,
			'buttons': [
				[{
					'action': {
						'type': 'text',
						'label': i,
					},
					'color': 'positive',
				}] for i in keyboard
			]
		}

		if keyboard_inline:
			keyb['inline'] = True
		else:
			keyb['one_time'] = True

		keyb = json.dumps(keyb)

	api.messages.send(
		user_id=user,
		# peer_id='2000000001',
		random_id=randint(-2147483648, 2147483647),
		message=cont,
		keyboard=keyb,
	)

# Запрос к API
def api(user_social_id, method, data):
	req = {
		'method': method,
		'params': data,
		'token': tokens[user_social_id],
		'language': 'ru',
	}

	print('req', user_social_id, req, sep='\t')
	res = requests.post(SERVER_LINK, json=req).json()
	print('res', user_social_id, res, sep='\t')

	if 'result' in res:
		res = res['result']
	else:
		res = None

	return res

# Зарегистрироваться / авторизоваться
def auth(user_social_id):
	user = api.users.get(
		user_ids=user_social_id,
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

	## Токен
	token = generate()
	tokens[user_social_id] = token

	## Запрос к API
	res = api(user_social_id, 'account.bot', {
		**user_new,
		'social': [{
			'id': 1,
			'user': user_social_id,
		}],
	})

	## Параметры
	ids[user_social_id] = res['id']

	return res

def process(user_social_id, text, file=None):
	print('→', user_social_id, text, sep='\t')

	# Помечаем сообщение как прочитанное
	api.messages.markAsRead(peer_id=user_social_id)

	# Определяем пользователя
	if user_social_id not in tokens:
		res = auth(user_social_id)

		if res['new']:
			send(user_social_id, 'Привет!\nЭто ВКонтакте бот 😉')
			return

	# Изображение
	if file:
		try:
			text += '<img src="data:image/png;base64,{}" />'.format(str(base64.b64encode(requests.get(file).content))[2:-1])
		except:
			print('! Ошибка загрузки изображения: {}'.format(file))

	# Обращение к системе
	## Вводная информация
	if text.lower() in ('начать', 'start', 'задать вопрос', 'старт', 'инфо', 'о', 'об', 'about', 'info'):
		send(user_social_id, 'Привет!\nЭто ВКонтакте бот 😉')
		return

	send(user_social_id, text)


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
			# print(update['object'])

			# Приём сообщений
			if update['object']['from_id'] > 0 and update['object']['peer_id'] != update['object']['from_id']:
				print('!'*100)
				continue

			if update['object']['from_id'] > 0 and update['type'] == 'message_new':
				user_social_id = update['object']['from_id']
				text = update['object']['text']
				file = None
				file_width = 0

				# Изображение
				if 'attachments' in update['object'] and len(update['object']['attachments']) and update['object']['attachments'][0]['type'] == 'photo':
					for size in update['object']['attachments'][0]['photo']['sizes']:
						if size['width'] > file_width:
							file = size['url']
							file_width = size['width']

				process(user_social_id, text, file)

			# Сброс активного задания
			# elif update['type'] == 'message_reply':
			# 	if 'finish' in update['object']['text']:
			# 		if update['object']['peer_id'] in tokens:
			# 			# send(update['object']['peer_id'], '', ['Начать'])

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