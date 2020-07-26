import json

from pymessenger.bot import Bot


with open('keys.json', 'r') as file:
	ACCESS_TOKEN = json.loads(file.read())['facebook']['token']


bot = Bot(ACCESS_TOKEN)

def send(user_social_id, text, keyboard=[]):
	# if len(keyboard):
	# 	bot.send_button_message(user_social_id, text, keyboard)
	# else:
	bot.send_text_message(user_social_id, text)