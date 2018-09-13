from func.tg_bot import *
import urllib, time

@bot.message_handler(commands=['start', 'help', 'info'])
def handle_start(message):
	bot.send_message(message.chat.id, 'Хай!')

@bot.message_handler(content_types=['document', 'audio', 'photo'])
def handle_attachments(message):
	bot.send_message(message.chat.id, 'Медиа')

@bot.message_handler(content_types=['voice'])
def handle_attachments(message):
	file_info = bot.get_file(message.voice.file_id)
	name = 'load/%d-%f.oga' % (message.chat.id, time.time())
	urllib.request.urlretrieve('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path), name)

# @bot.message_handler(regexp="SOME_REGEXP")
# def handle_reg(message):
# 	pass

@bot.message_handler(commands=['about', 'author'])
def about(message):
	bot.send_message(message.chat.id, 'Author: Poloz Alexey\npolozhev@mail.ru')

#@bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])

@bot.message_handler(content_types=["text"])
def handle_message(message):
	with open('re.png', 'rb') as file:
		bot.send_photo(message.chat.id, file, 'Подпись к фото')

	x = bot.send_message(message.chat.id, message.text, reply_markup=keyboard([['Вариант 1', 'Вариант 2'], ['Назад']]))
	bot.register_next_step_handler(x, next_message)

def next_message(message):
	bot.send_message(message.chat.id, 'Текст')

# def send(message='', to=admin, image='', forward=0):
# 	if not message: return 0
# 	if type(to) != list:
# 		to = [to]
# 	for i in to:
# 		if not forward:
# 			if image:
# 				bot.send_photo(i, open(image, 'rb'), message)
# 			else:
# 				if str(i)[0] == '-':
# 					bot.send_message(i, message)
# 				else:
# 					bot.send_message(i, message, reply_markup=keyboard(exch, ['PUMP', 'Информация']))
# 		else:
# 			try:
# 				bot.forward_message(i, forward, message)
# 			except:
# 				bot.send_message(i, db['messages'].find_one({'chat': forward, 'message': message})['text'])

if __name__ == '__main__':
	bot.polling(none_stop=True)