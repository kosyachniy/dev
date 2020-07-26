import json
import random
import string
import requests
import time
import base64

from flask import Flask, request
from pymessenger.bot import Bot


with open('keys.json', 'r') as file:
	ACCESS_TOKEN = json.loads(file.read())['facebook']['token']
	VERIFY_TOKEN = 'alexpoloz'

with open('sets.json', 'r') as file:
	sets = json.loads(file.read())
	PORT = sets['port']
	# GROUP_ID = sets['fb']['group']
	SERVER_LINK = sets['server']['link']
	CLIENT_LINK = sets['client']['link']


app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)


# Пользователи
tokens = dict()
ids = dict()

# Генерация токена
ALL_SYMBOLS = string.ascii_lowercase + string.digits
generate = lambda length=32: ''.join(random.choice(ALL_SYMBOLS) for _ in range(length))


def verify_fb_token(token_sent):
	if token_sent == VERIFY_TOKEN:
		return request.args['hub.challenge']
	else:
		return 'Invalid verification token'

def send(user_social_id, text, keyboard=[]):
	# if len(keyboard):
	# 	for i in range(len(keyboard)):
	# 		keyboard[i] = {
	# 			'type': 'postback',
	# 			'title': keyboard[i],
	# 			'payload': keyboard[i],
	# 		}

	# 	bot.send_button_message(user_social_id, text, keyboard)
	# else:
	bot.send_text_message(user_social_id, text)

# Запрос к API
def api(user_social_id, method, data):
	req = {
		'method': method,
		'params': data,
		'token': tokens[user_social_id],
		'language': 'en',
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
	user = bot.get_user_info(user_social_id, fields=('id', 'name', 'first_name', 'last_name', 'profile_pic'))

	user_new = dict()
	param_map = {
		'first_name': 'name',
		'last_name': 'surname',
		'profile_pic': 'avatar',
	}

	try:
		for param in param_map:
			if param in user:
				user_new[param_map[param]] = user[param]
	except:
		user_new['name'] = ''
		user_new['surname'] = ''
		user_new['login'] = ''
		user_new['avatar'] = ''

	## Токен
	token = generate()
	tokens[user_social_id] = token

	## Запрос к API
	res = api(user_social_id, 'account.bot', {
		**user_new,
		'social': [{
			'id': 4,
			'user': user_social_id,
		}],
	})

	## Параметры
	ids[user_social_id] = res['id']

	return res

def process(user_social_id, text, file=None):
	print('→', user_social_id, text, sep='\t')

	# Определяем пользователя
	if user_social_id not in tokens:
		auth(user_social_id)

		send(user_social_id, 'Welcome to Facebook bot!')
		return

	# Изображение
	if file:
		try:
			text += '<img src="data:image/png;base64,{}" />'.format(str(base64.b64encode(requests.get(file).content))[2:-1])
		except:
			print('! Ошибка загрузки изображения: {}'.format(file))

	# Обращение к системе
	## Старт
	if text.lower() in ('start', 'begin', 'about', 'info', 'help', 'menu'):
		send(user_social_id, 'Welcome to Facebook bot!')
		return

	send(user_social_id, 'Answer')


# Facebook bot
@app.route('/', methods=['GET', 'POST'])
def fb():
	# return request.args.get('hub.challenge')

	# Verify
	if request.method == 'GET':
		token_sent = request.args['hub.verify_token']
		return verify_fb_token(token_sent)

	# Message processing
	output = request.get_json()
	# print('---', output)
	for event in output['entry']:
		messaging = event['messaging']
		for message in messaging:
			if message.get('message'):
				user_social_id = int(message['sender']['id'])

			# print('!!!!!!', message)
			# print(tokens, ids)

			# # Text
			# if message['message'].get('text'):
			# 	send(user_social_id, 'Ok')

			# # Media
			# if message['message'].get('attachments'):
			# 	send(user_social_id, 'Media')

			# Приём сообщений
			# if update['object']['from_id'] > 0 and update['object']['peer_id'] != update['object']['from_id']:
			# 	print('!'*100)
			# 	continue

			if 'is_echo' not in message['message'] or not message['message']['is_echo']:
				if 'text' in message['message']:
					text = message['message']['text']
				else:
					text = ''

				file = None

				# Изображение
				if 'attachments' in message['message'] and len(message['message']['attachments']) and message['message']['attachments'][0]['type'] == 'image':
					file = message['message']['attachments'][0]['payload']['url']

				process(user_social_id, text, file)

			# # Сброс активного задания
			# elif 'is_echo' in message['message'] and message['message']['is_echo']:
			# 	user_social_id = int(message['recipient']['id'])

			# 	if 'finish' in message['message']['text']:
			# 		if user_social_id in tokens:
			# 			# send(user_social_id, '', ['Начать'])

	return "Message Processed"


if __name__ == '__main__':
    app.run(port=PORT)