import json

import telebot


with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tg']['token']

bot = telebot.TeleBot(token)


def send(to, text, img=None, attempt=1):
	try:
		if img:
			with open(img, 'rb') as file:
				mes = bot.send_photo(to, file, text, parse_mode='Markdown')
		else:
			mes = bot.send_message(to, text, parse_mode= 'Markdown', disable_web_page_preview=True)

		return mes

	except:
		print('! ERROR TELEGRAM SEND ! №{}'.format(attempt))
		print(text)

		if attempt == 1:
			return send(to, text, img, 2)

		raise Exception('Telegram send message')

def delete(to, message, attempt=1):
	try:
		bot.delete_message(to, message)

	except:
		print('! ERROR TELEGRAM DEL ! №{}'.format(attempt))

		if attempt == 1:
			return delete(to, message, 2)

		raise Exception('Telegram del message')

def edit(to, message, text):
	bot.edit_message_text(chat_id=to, message_id=message, text=text)