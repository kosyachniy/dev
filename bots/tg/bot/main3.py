import time
from multiprocessing import Process

from func.tg_bot import bot, send


@bot.message_handler(commands=['start'])
def handle_start(message):
	send(message.chat.id, 'Hello, world!')


def background_process():
	while True:


		time.sleep(60)


if __name__ == '__main__':
	p = Process(target=background_process)
	p.start()

	bot.polling(none_stop=True)