from telethon import TelegramClient

import json
with open('set.txt', 'r') as file:
	x = json.loads(file.read())

client = TelegramClient(x['name'], x['id'], x['hash'])
client.connect()
'''
client.sign_in(phone=x['telephone'])
me = client.sign_in(code=input('Код: '))
'''
client.send_code_request(x['phone'])
user = client.sign_in(x['phone'], input('Код: '))
