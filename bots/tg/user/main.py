import asyncio

from lib.tg_user import Telegram


async def main():
    async with Telegram() as tg:
        await tg.send('kosyachniy', 'ola')


if __name__ == '__main__':
    asyncio.run(main())
