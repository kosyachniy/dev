from func.tg_user import client
from telethon.tl.functions.messages import ForwardMessagesRequest


client.send_message(136563129, '456')

#ForwardMessagesRequest(-1001143136828, 1, randint(1,100000), 136563129))
'''
ForwardMessagesRequest(
    from_peer=get_input_peer(entities[1]),
    id=[msg.id],
    random_id=[generate_random_long()],
    to_peer=get_input_peer(entities[2])
))
'''