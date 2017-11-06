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
	client.sign_in(x['phone'], input('Код: '))

#print(user.stringify())
#dialogs, entities = client.get_dialogs(10)
#print(dialogs, entities[0])

#print(client.get_message_history())

'''
for i in client.get_message_history(136563129)[1]: #get_message_history #get_input_entity #get_entity
	print(i.message)
'''

for i in client.get_dialogs()[0]:
	x = i.to_dict()['peer']
	x = [x[i] for i in x][0]
	print(x)
	try:
		for i in client.get_message_history(x)[1]:
			print(i.message)
	except:
		pass
	print('-----')