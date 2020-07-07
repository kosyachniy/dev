import json

import telebot


with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tg']['token']

bot = telebot.TeleBot(token)


def keyboard(rows):
	buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	for cols in rows:
		buttons.add(*[telebot.types.KeyboardButton(col) for col in cols])

	return buttons

def send(user, text='', buttons=[], image=None): # users=[], forward=None, next_message=None
	if not image:
		return bot.send_message(
			user,
			text,
			reply_markup=keyboard(buttons) if len(buttons) else None
		)

	else:
		return bot.send_photo(
			user,
			open(image, 'rb'),
			text,
			reply_markup=keyboard(buttons) if len(buttons) else None
		)

	# return bot.forward_message(user, forward, text)