from func.tg_user import client


# print(client.get_dialogs())

# Dialog
for i in client.get_dialogs()[0]:
	x = i.to_dict()['peer']['channel_id']
	print('User / Bot', x)

# Channel
for i in client.get_dialogs()[1]:
	x = i.to_dict()['id']
	print('Channel', x)