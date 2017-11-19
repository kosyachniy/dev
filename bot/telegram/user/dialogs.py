from func import *

print(client.get_dialogs())

#Dialog
for i in client.get_dialogs()[0]:
	x = i.to_dict()['peer']['channel_id']
	print('User / Bot', x)

#Channel
for i in client.get_dialogs()[1]:
	x = i.to_dict()['id']
	print('Channel', x)


'''
print(client.get_dialogs()[1])
for i in client.get_dialogs()[0]:
	print(i)
	x = i.to_dict()['peer']
	print(x)
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