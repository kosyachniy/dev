import json, telebot

with open('set.txt', 'r') as file:
	token = json.loads(file.read())['token']
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def text(message):
	bot.send_message(message.chat.id, message.forward_from_chat['id'])
	print(message.chat.id, message.forward_from_chat)

bot.polling(none_stop=True)