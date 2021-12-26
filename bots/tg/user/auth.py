import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession
from libdev.cfg import cfg


async def main():
    async with TelegramClient(
        StringSession(), cfg('tg.id'), cfg('tg.hash')
    ) as client:
        print(client.session.save())


asyncio.run(main())
