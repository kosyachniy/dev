import json

# from telethon import TelegramClient
from telethon.sync import TelegramClient


with open('keys.json', 'r') as file:
	x = json.loads(file.read())['tg']

# client = TelegramClient('main', x['id'], x['hash'], update_workers=4).start()
client = TelegramClient('main{}'.format(x['id']), x['id'], x['hash']).start() # , update_workers=4


# import json
# import asyncio

# from telethon import TelegramClient, events


# with open('keys.json', 'r') as file:
# 	x = json.loads(file.read())['tg']


# async def send(client, name, cont):
# 	entity = await client.get_entity(name)
# 	await client.send_message(entity, cont)


# async def main():
# 	async with TelegramClient('main{}'.format(x['id']), x['id'], x['hash']) as client:
# 		print(client.get_dialogs())


# if __name__ == '__main__':
# 	# await main() # for Jupyter Notebook
# 	asyncio.run(main())