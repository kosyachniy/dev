import telebot
import numpy as np

token='417063852:AAFvfJdVGgLv9odlnY_gaiMmV4NIBMlgvOQ'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
	bot.send_message(message.chat.id, 'Hi!')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
	t=message.text.split('\n')
	try:
		x_shape = tuple(map(int, t[0].split()))
		X = np.fromiter(map(int, t[1].split()), np.int).reshape(x_shape)
		y_shape = tuple(map(int, t[2].split()))
		Y = np.fromiter(map(int, t[3].split()), np.int).reshape(y_shape)
		if x_shape[1]==y_shape[1]:
			te=''
			for i in X.dot(Y.T):
				for j in i:
					te+=str(j)+' '
				te+='\n'
			bot.send_message(message.chat.id, te)
		else:
			bot.send_message(message.chat.id, 'matrix shapes do not match')
	except:
		bot.send_message(message.chat.id, 'Error!')

if __name__ == '__main__':
	bot.polling(none_stop=True)
