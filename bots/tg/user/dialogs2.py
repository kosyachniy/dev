import json
import asyncio

from telethon import TelegramClient, events


with open('keys.json', 'r') as file:
	x = json.loads(file.read())['tg']


async def send(client, name, cont):
	entity = await client.get_entity(name)
	await client.send_message(entity, cont)


async def main():
	async with TelegramClient('main{}'.format(x['id']), x['id'], x['hash']) as client:
		dialogs = await client.get_dialogs()
		for dialog in dialogs:
			print(
				dialog.name, " " * (40 - len(dialog.name)),
				"\t", dialog.entity.__class__.__name__, " " * (10 - len(dialog.entity.__class__.__name__)),
				"\t", dialog.entity.id,
				f"({-dialog.entity.id})" if dialog.entity.__class__.__name__ in ('Chat',) else "",
				"\t", dialog.entity.migrated_to.channel_id if hasattr(dialog.entity, 'migrated_to') and dialog.entity.migrated_to else "",
				f"(-100{dialog.entity.migrated_to.channel_id})" if hasattr(dialog.entity, 'migrated_to') and dialog.entity.migrated_to else "",
			)


if __name__ == '__main__':
	# await main() # for Jupyter Notebook
	asyncio.run(main())