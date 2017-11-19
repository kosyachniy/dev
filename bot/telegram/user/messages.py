from func import *

'''
total, messages, senders = client.get_message_history(136563129)
for i in messages:
	print(i.message)
'''

total, messages, senders = client.get_message_history('-1001143136828')
for i in messages:
	print(i.message)


'''
id = -1128386214 #input()

for i in client.get_message_history(id)[1]:
	print(i.message)
'''