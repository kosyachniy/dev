import telegram
import json
import time
from telegram.error import NetworkError, Unauthorized

with open('keys.json', 'r') as file:
	TOKEN = json.loads(file.read())['tg_token']

bot = telegram.Bot(token=TOKEN)


update_id = None

def main():
	global update_id, TOKEN
	bot = telegram.Bot(TOKEN)

	try:
		update_id = bot.get_updates()[0].update_id
	except IndexError:
		update_id = None

	while True:
		try:
			echo(bot)
		except NetworkError:
			time.sleep(1)
		except Unauthorized:
			update_id += 1


def echo(bot):
	global update_id

	for update in bot.get_updates(offset=update_id, timeout=10):

		update_id = update.update_id + 1

		if update.message:
			message = update.message
			user = message.from_user
			print(user, user.to_dict())
			update.message.reply_text(user.id)


if __name__ == '__main__':
	main()