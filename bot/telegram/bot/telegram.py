#Telegram
from func.data import db, exchangers
import json, telebot

exch = [i[0] for i in exchangers]

with open('data/keys.txt', 'r', encoding='utf-8') as file:
	token = json.loads(file.read())['telegram']['bot']

with open('data/set.txt', 'r', encoding='utf-8') as file:
	s = json.loads(file.read())['write']
	channelid = s['channel']
	twochannel = s['channelen']
	admin = s['admin']

bot = telebot.TeleBot(token)

#Меню
from telebot import types

def keyboard(*cat):
	x = types.ReplyKeyboardMarkup(resize_keyboard=True)
	for j in cat:
		x.add(*[types.KeyboardButton('/' + i) for i in j])
	return x

def send(message='', to=admin, image='', forward=0):
	if not message: return 0
	if type(to) != list:
		to = [to]
	for i in to:
		if not forward:
			if image:
				bot.send_photo(i, open(image, 'rb'), message)
			else:
				if str(i)[0] == '-':
					bot.send_message(i, message)
				else:
					bot.send_message(i, message, reply_markup=keyboard(exch, ['PUMP', 'Информация']))
		else:
			try:
				bot.forward_message(i, forward, message)
			except:
				bot.send_message(i, db['messages'].find_one({'chat': forward, 'message': message})['text'])