import asyncio

from lib.tg import tg


FILE = 'https://web.chill.services/load/0000000001dlxvdo.jpg'
# FILE = 'https://cv.chill.services/load/0000000005pbimvr.jpeg'


async def main():
    await tg.send(136563129, "Текст", files=FILE)


asyncio.run(main())
