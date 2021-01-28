from func.tg_user import client


dialogs = client.get_dialogs()

for i in dialogs:
	print(i.name, i.entity.id)

# #Dialog
# for i in client.get_dialogs()[0]:
# 	x = i.to_dict()['peer']['channel_id']
# 	print('User / Bot', x)

# #Channel
# for i in client.get_dialogs()[1]:
# 	x = i.to_dict()['id']
# 	print('Channel', dir(x))
# 	print('---')
# 	break