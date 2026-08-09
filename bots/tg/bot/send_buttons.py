import asyncio

from lib.tg import tg


async def main():
    await tg.send(136563129, "buttons", buttons=[
        {'name': 'user ID', 'data': 'tg://user?id=136563129'},
        {'name': 'user login', 'data': 'https://t.me/kosyachniy'},
    ])


asyncio.run(main())
