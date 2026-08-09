import asyncio

from tgio import Telegram


TOKEN = ""
CHAT = 136563129
TEXT = "test"


async def main():
    tg = Telegram(TOKEN)
    res = await tg.send(CHAT, TEXT)
    print(res)


asyncio.run(main())
