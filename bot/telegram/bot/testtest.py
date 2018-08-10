import telebot

token = '649651643:AAFnMsAYmwMJBITc90DmQ44J8tjhTT0mPpo'
bot = telebot.TeleBot(token)

def keyboard(key):
	x = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	for j in key:
		x.add(*[telebot.types.KeyboardButton(i) for i in j])
	return x


@bot.message_handler(commands=['start', 'help', 'info'])
def startfunc(message):
	bot.send_message(message.chat.id, 'Привет)')

@bot.message_handler(content_types=["text"])
def newfunc(message):
	if message.text == 'Расписание':
		photo = open('1.png', 'rb')
		bot.send_photo(message.chat.id, photo, 'Расписание')
	else:
		bot.send_message(message.chat.id, message.text, reply_markup = keyboard([['Раписание']]))


if __name__ == '__main__':
	bot.polling(none_stop=True)