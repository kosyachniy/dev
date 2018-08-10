import telebot

token = '502642950:AAHAItidjsCnjzPfwOtB6__fQpw0aWFF5ME'
bot = telebot.TeleBot(token)

def keyboard(key):
	x = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	for j in key:
		x.add(*[telebot.types.KeyboardButton(i) for i in j])
	return x


@bot.message_handler(commands=['start', 'help', 'info'])
def rere(message):
	bot.send_message(message.chat.id, 'Hi!', reply_markup=keyboard([['Расписание']]))

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
	if message.text == 'Расписание':
		bot.send_photo(message.chat.id, open('1.png', 'rb'), 'Эт расписание')
	else:
		bot.send_message(message.chat.id, message.text, reply_markup=keyboard([['Расписание']]))


if __name__ == '__main__':
	bot.polling(none_stop=True)