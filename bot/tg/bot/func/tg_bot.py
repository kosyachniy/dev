import json

import telebot


with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tg']['token']

bot = telebot.TeleBot(token)


# Меню
def keyboard(rows):
	buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	for cols in rows:
		buttons.add(*[telebot.types.KeyboardButton(col) for col in cols])

	return buttons