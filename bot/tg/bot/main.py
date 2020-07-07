import time
import urllib
import requests

from func.tg_bot import bot, keyboard


LANGUAGES = ('en', 'ru')

LOCALES = {
	'en': {
		'intro': 'Hi!',
	},
	'ru': {
		'intro': 'Хай!',
	},
}


languages = dict()


def auth(user_social_id):
	if user_social_id not in languages:
		languages[user_social_id] = 0

def send(user_social_id, text='', buttons=[], image=None): # users=[], forward=None
	if not image:
		return bot.send_message(
			user_social_id,
			text,
			reply_markup=keyboard(buttons) if len(buttons) else None
		)

	else:
		return bot.send_photo(
			user_social_id,
			open(image, 'rb'),
			text,
			reply_markup=keyboard(buttons) if len(buttons) else None
		)

	# return bot.forward_message(user_social_id, forward, text)

def get_replica(user_social_id, key):
	return LOCALES[LANGUAGES[languages[user_social_id]]][key]


@bot.message_handler(commands=['start', 'help', 'info', 'about', 'menu'])
def handle_start(message):
	auth(message.chat.id)
	send(message.chat.id, get_replica(message.chat.id, 'intro'))

# @bot.message_handler(content_types=['document', 'audio', 'photo'])
# def handle_attachments(message):
# 	bot.send_message(message.chat.id, 'Медиа')

@bot.message_handler(content_types=['voice'])
def handle_attachments(message):
	file_info = bot.get_file(message.voice.file_id)
	name = 'load/%d-%f.oga' % (message.chat.id, time.time())
	urllib.request.urlretrieve('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path), name)

# @bot.message_handler(regexp="SOME_REGEXP")
# def handle_reg(message):
# 	pass

@bot.message_handler(commands=['about', 'author'])
def about(message):
	bot.send_message(message.chat.id, 'Author: Poloz Alexey\npolozhev@mail.ru')

#@bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])

@bot.message_handler(content_types=["text"])
def handle_message(message):
	with open('re.png', 'rb') as file:
		bot.send_photo(message.chat.id, file, 'Подпись к фото')

@bot.message_handler(content_types=['text'])
def handle_message(message):
	auth(message.chat.id)

	x = send(message.chat.id, message.text, [['Вариант 1', 'Вариант 2'], ['Назад']])
	bot.register_next_step_handler(x, next_message)

def next_message(message):
	bot.send_message(message.chat.id, 'Текст')


if __name__ == '__main__':
	while True:
		try:
			bot.polling(none_stop=True)
		except requests.exceptions.ReadTimeout:
			time.sleep(5)