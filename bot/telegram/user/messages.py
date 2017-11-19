from func import *
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

'''
total, messages, senders = client.get_message_history(136563129)
for i in messages:
	print(i.message)
'''

'''
total, messages, senders = client.get_message_history(-1001143136828)
for i in messages:
	print(i.message)
'''

'''
total, messages, senders = client.get_message_history(PeerUser(user_id=136563129))
for i in messages:
	print(i.message)
'''


#-1001143136828, access_hash=1243590961638105134 #client.get_entity(1143136828) #1143136828, 1243590961638105134 #-1001143136828 #1143136828 #client.get_entity(-1001143136828)
total, messages, senders = client.get_message_history(-1001143136828)
for i in messages:
	print(i.message)


'''
print(dir(PeerChannel(channel_id=-1001143136828)))
print(PeerChannel(channel_id=-1001143136828).pretty_format)


print(dir(client.get_entity(-1001143136828)))
print(client.get_entity(-1001143136828))
'''
'''
for i in client.get_entity(-1001143136828):
	print(i)
 #'-1001143136828')))
 '''

'''
id = -1128386214 #input()

for i in client.get_message_history(id)[1]:
	print(i.message)
'''