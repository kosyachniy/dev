import json, telebot

with open('set.txt', 'r') as file:
	token = json.loads(file.read())['token']
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def text(message):
	try:
		bot.send_message(message.chat.id, message.forward_from.id)
		print(message.chat.id, message.forward_from)
	except:
		try:
			bot.send_message(message.chat.id, '%d %d' % (message.forward_from_chat.id, message.forward_from_message_id))
			print(message.chat.id, message.forward_from_chat)
		except:
			bot.send_message(message.chat.id, '%d %d' % (message.chat.id, message.message_id))
			print(message.chat.id, message.chat.id)
	
	print('-------------')
	print(message)

bot.polling(none_stop=True)