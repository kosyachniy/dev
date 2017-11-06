import telebot

token='417063852:AAFvfJdVGgLv9odlnY_gaiMmV4NIBMlgvOQ'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
	bot.send_message(message.chat.id, 'Hi!')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
	f=open('load/1.jpg', 'rb')
	bot.send_photo(message.chat.id, f)

if __name__ == '__main__':
	bot.polling(none_stop=True)
