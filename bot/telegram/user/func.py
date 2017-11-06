from telethon import TelegramClient

import json
with open('set.txt', 'r') as file:
	x = json.loads(file.read())

client = TelegramClient(x['name'], x['id'], x['hash'])
client.connect()

'''
client.sign_in(phone=x['phone'])
user = client.sign_in(code=input('Код: '))
'''
if not client.is_user_authorized():
	client.send_code_request(x['phone'])
	user = client.sign_in(x['phone'], input('Код: '))

#print(user.stringify())
#dialogs, entities = client.get_dialogs(10)
#print(dialogs, entities[0])

for i in client.get_dialogs(10):
	try:
		print(i.id)
	except:
		print('No!')