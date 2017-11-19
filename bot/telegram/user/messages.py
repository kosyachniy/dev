from func import *

'''
total, messages, senders = client.get_message_history(136563129)
for i in messages:
	print(i.message)
'''

total, messages, senders = client.get_message_history(-1001143136828)
for i in messages:
	print(i.message)