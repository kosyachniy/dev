import json

from telethon import TelegramClient


with open('keys.json', 'r') as file:
	x = json.loads(file.read())['tg']

client = TelegramClient('main', x['id'], x['hash'], update_workers=4).start()