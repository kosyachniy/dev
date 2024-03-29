import asyncio

from lib.tg_user import Telegram, events, get_stat


async def main():
    print(await get_stat('hnklny'))

    async with Telegram() as tg:
        await tg.send('kosyachniy', 'ola')

        @tg.client.on(events.NewMessage)
        async def handler(update):
            print(update)
            print(tg.mes2json(update.message))

        await tg.client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
