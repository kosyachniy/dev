import telebot, urllib

token='417063852:AAFvfJdVGgLv9odlnY_gaiMmV4NIBMlgvOQ'
bot=telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
	bot.send_message(message.chat.id, 'Hi!')

@bot.message_handler(content_types=['document', 'audio', 'photo', 'voice'])
def handle_docs_audio(message):
	bot.send_message(message.chat.id, 'Media!')
	file_info=bot.get_file(message.voice.file_id)
	urllib.request.urlretrieve('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path), '1.oga')

@bot.message_handler(regexp="SOME_REGEXP")
def handle_message(message):
	pass

#@bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])
@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
	bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
	bot.polling(none_stop=True)