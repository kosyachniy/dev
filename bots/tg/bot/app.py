import json
import time
import urllib
import requests
import random
import string

from func.tg_bot import bot, send


with open('sets.json', 'r') as file:
	sets = json.loads(file.read())
	SERVER_LINK = sets['server']['link']
	CLIENT_LINK = sets['client']['link']

LANGUAGES = ('en', 'ru')
LANGUAGES_NAME = ('English', 'Русский')

LOCALES = {
	'en': {
		'lang': 'Choose your language',
		'intro': 'Hi!\nThis is a Telegram bot.',
		'menu_lang': 'Change language',
		'menu_about': 'About',
		'done': 'Done',
		'success': 'Success!',
		'cancel': 'Cancel',
	},
	'ru': {
		'lang': 'Выберите язык',
		'intro': 'Привет!\nЭто Telegram бот.',
		'menu_lang': 'Изменить язык',
		'menu_about': 'О боте',
		'done': 'Готово',
		'success': 'Успешно!',
		'cancel': 'Отмена',
	},
}


languages = dict()
languages_chosen = dict()
tokens = dict()
ids = dict()


# Генерация токена
ALL_SYMBOLS = string.ascii_lowercase + string.digits
generate = lambda length=32: ''.join(random.choice(ALL_SYMBOLS) for _ in range(length))


# Запрос к API
def api(user_social_id, method, data):
	req = {
		'method': method,
		'params': data,
		'token': tokens[user_social_id],
		'language': LANGUAGES[languages[user_social_id]],
	}

	print('req', user_social_id, req, sep='\t')
	res = requests.post(SERVER_LINK, json=req).json()
	print('res', user_social_id, res, sep='\t')

	return res

# Зарегистрироваться / авторизоваться
def auth(user_social_id, user):
	if user_social_id in ids:
		return {
			'new': False,
		}

	if user_social_id not in languages:
		languages[user_social_id] = 0

	user_new = dict()

	try:
		user_new['name'] = user.first_name if user.first_name else ''
		user_new['surname'] = user.last_name if user.last_name else ''
		user_new['login'] = user.username if user.username else ''
	except:
		pass
		# user_new['name'] = ''
		# user_new['surname'] = ''
		# user_new['login'] = ''
		# user_new['avatar'] = ''

	## Токен
	token = generate()
	tokens[user_social_id] = token

	## Запрос к API
	res = api(user_social_id, 'account.bot', {
		**user_new,
		'social': [{
			'id': 2,
			'user': user_social_id,
		}],
	})

	# Ошибки

	if res['error']:
		print('! Ошибка auth !')
	else:
		res = res['result']

	## Параметры
	ids[user_social_id] = res['id']

	if 'language' in res['social']:
		languages[user_social_id] = res['social']['language']
		languages_chosen[user_social_id] = True

	return res

def get_replica(user_social_id, key):
	return LOCALES[LANGUAGES[languages[user_social_id]]][key]

def get_buttons(user_social_id, keys):
	for i in range(len(keys)):
		for j in range(len(keys[i])):
			keys[i][j] = LOCALES[LANGUAGES[languages[user_social_id]]][keys[i][j]]

	return keys

# ! Метод перевода

@bot.message_handler(commands=['start'])
def handle_start(message):
	auth(message.chat.id, message.from_user)

	send(message.chat.id, get_replica(message.chat.id, 'lang'), [LANGUAGES_NAME])

@bot.message_handler(commands=['help', 'info', 'about', 'menu'])
def handle_start(message):
	auth(message.chat.id, message.from_user)
	send(message.chat.id, get_replica(message.chat.id, 'intro'), get_buttons(message.chat.id, [['menu_lang'], ['menu_about']]))

@bot.message_handler(content_types=['text'])
def handle_message(message):
	# ! Обработка сообщения и пользователя
	auth(message.chat.id, message.from_user)

	# Язык

	if message.text in LANGUAGES_NAME:
		languages[message.chat.id] = LANGUAGES_NAME.index(message.text)
		languages_chosen[message.chat.id] = True

		res = api(message.chat.id, 'account.edit', {
			'social': {
				'id': 2,
				'user': message.chat.id,
				'language': languages[message.chat.id],
			},
		})

	if message.chat.id not in languages_chosen:
		send(message.chat.id, get_replica(message.chat.id, 'lang'), [LANGUAGES_NAME])
		return

	# Кнопки
	## Изменить язык
	if message.text == LOCALES[LANGUAGES[languages[message.chat.id]]]['menu_lang']:
		send(message.chat.id, get_replica(message.chat.id, 'lang'), [LANGUAGES_NAME])
		return

	# Меню
	if message.text == LOCALES[LANGUAGES[languages[message.chat.id]]]['menu_about']:
		send(message.chat.id, get_replica(message.chat.id, 'intro'), get_buttons(message.chat.id, [['menu_lang'], ['menu_about']]))
		return

	send(message.chat.id, message.text, get_buttons(message.chat.id, [['menu_lang'], ['menu_about']]))


if __name__ == '__main__':
	while True:
		try:
			bot.polling(none_stop=True)
		except:
			time.sleep(5)