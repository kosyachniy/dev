import json

# from telethon import TelegramClient
from telethon.sync import TelegramClient


with open('keys.json', 'r') as file:
	x = json.loads(file.read())['tg']

# client = TelegramClient('main', x['id'], x['hash'], update_workers=4).start()
client = TelegramClient('main{}'.format(x['id']), x['id'], x['hash']).start() # , update_workers=4