from telethon import TelegramClient
import time

import json
with open('set.txt', 'r') as file:
	x = json.loads(file.read())

client = TelegramClient(x['name'], x['id'], x['hash'], update_workers=4)
client.connect()

if not client.is_user_authorized():
	client.send_code_request(x['phone'])
	client.sign_in(x['phone'], input('Код: '))

#print(dir(client))

def mess(cont):
	print(cont.status)
	time.sleep(2)
	#print(dir(cont))
	#print(cont.to_dict())
	'''
	if 'status' not in dir(cont):
		print(cont.stringify().title())
	'''

while True:
	client.add_update_handler(mess)

'''
for i in client.get_dialogs()[0]:
	x = i.to_dict()['peer']
	if 'user_id' in x:
		j = x['user_id']
		print('User / Bot', j)
		for u in client.get_message_history(j)[1]:
			print(u.message)
	else:
		j = x['channel_id']
		print('Channel', j)
	print('-----')
'''