from func.tg_user import client


'''
total, messages, senders = client.get_message_history(136563129)
for i in messages:
	print(i.message)
'''

from_id = -1001143136828

total, messages, senders = client.get_message_history(client.get_entity(from_id))
for i in messages:
	print(i.message)