from func.tg_bot import *

@bot.message_handler(content_types=["text"])
def text(message):
# Сообщение пользователя
	try:
		bot.send_message(message.chat.id, message.forward_from_chat.id)
		print(message.chat.id, message.forward_from_chat)
	except:
		
# Сообщение чата
		try:
			bot.send_message(message.chat.id, '%d %d' % (message.forward_from_chat.id, message.forward_from_message_id))
			print(message.chat.id, message.forward_from_chat)

# Личное сообщение
		except:
			bot.send_message(message.chat.id, '%d %d' % (message.chat.id, message.message_id))
			print(message.chat.id, message.chat.id)
	
	print('-------------')
	print(message)

bot.polling(none_stop=True)