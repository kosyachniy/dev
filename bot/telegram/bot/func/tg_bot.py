import telebot, json

with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tg']['token']
bot = telebot.TeleBot(token)

# Меню
def keyboard(key):
	x = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	for j in key:
		x.add(*[telebot.types.KeyboardButton(i) for i in j])
	return x