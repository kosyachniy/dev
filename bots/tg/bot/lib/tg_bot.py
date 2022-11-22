import json

import telebot


with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tg']['token']

bot = telebot.TeleBot(token)


def keyboard(rows):
	if rows == []:
		return telebot.types.ReplyKeyboardRemove()

	if rows in (None, [], [[]]):
		return rows

	buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	for cols in rows:
		buttons.add(*[telebot.types.KeyboardButton(col) for col in cols])

	return buttons

def send(user, text='', buttons=None, image=None): # users=[], forward=None, next_message=func
	# ! Если пустой buttons - убирать кнопки (но не None)

	if not image:
		return bot.send_message(
			user,
			text,
			reply_markup=keyboard(buttons),
		)

	else:
		return bot.send_photo(
			user,
			open(image, 'rb'),
			text,
			reply_markup=keyboard(buttons),
		)

	# return bot.forward_message(user, forward, text)