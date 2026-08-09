from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputPeerUser
import asyncio
from libdev.cfg import cfg


BOT_ID = 8127764238
BOT_HASH = None  # access_hash из User(...)

BOT_PEER = InputPeerUser(user_id=BOT_ID, access_hash=BOT_HASH)

client = TelegramClient(
    StringSession(cfg("tg.session")),
    cfg("tg.id"),
    cfg("tg.hash"),
)


async def main():
    await client.start()  # авторизация юзера

    async for msg in client.iter_messages(BOT_PEER):
        sender = msg.sender_id or "бот/система"
        print(f"[{msg.id}] {sender}: {msg.text or ''}")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
