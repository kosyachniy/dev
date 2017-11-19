from telethon import TelegramClient

import json
with open('set.txt', 'r') as file:
	x = json.loads(file.read())

client = TelegramClient(x['name'], x['id'], x['hash'], update_workers=4)
client.connect()

if not client.is_user_authorized():
	client.send_code_request(x['phone'])
	client.sign_in(x['phone'], input('Код: '))