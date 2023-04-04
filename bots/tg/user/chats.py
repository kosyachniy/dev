import asyncio

from telethon import TelegramClient

from libdev.cfg import cfg


async def chats(client, limit=None):
    dialogs = await client.get_dialogs()
    chats = []

    for i, dialog in enumerate(dialogs):
        if i == limit:
            break

        chats.append({
            'id': dialog.entity.id,
            'name': dialog.name,
            'entity': dialog.entity.__class__.__name__,
            'last_message': dialog.message.id,
        })
        print(
            dialog.name, " " * (40 - len(dialog.name)),
            "\t", dialog.entity.__class__.__name__, " " * (10 - len(dialog.entity.__class__.__name__)),
            "\t", dialog.entity.id,
            f"(-{dialog.entity.id})" if dialog.entity.__class__.__name__ in ('Chat',) else f"(-100{dialog.entity.id})" if dialog.entity.__class__.__name__ in ('Channel',) else "",
            "\t", dialog.entity.migrated_to.channel_id if hasattr(dialog.entity, 'migrated_to') and dialog.entity.migrated_to else "",
            f"(-100{dialog.entity.migrated_to.channel_id})" if hasattr(dialog.entity, 'migrated_to') and dialog.entity.migrated_to else "",
        )

    return chats


async def main():
    async with TelegramClient(f"main{cfg('tg.id')}", cfg('tg.id'), cfg('tg.hash')) as client:
        print(await chats(client))


if __name__ == '__main__':
    # await main() # for Jupyter Notebook
    asyncio.run(main())
