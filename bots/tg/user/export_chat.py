import asyncio
import json

from libdev.cfg import cfg
from telethon import TelegramClient
from telethon.sessions import StringSession

from lib.tg_user import Telegram


CHAT = 1229366790

ITER_LIMIT = 100
LIMIT = None
DELAY = 15
FILE = f"{CHAT}.json"
LOGS = False


async def main():
    async with TelegramClient(
        StringSession(cfg("tg.session")),
        cfg("tg.id"),
        cfg("tg.hash"),
    ) as client:
        total = 0
        previous = None

        while True:
            count = 0

            async for message in client.iter_messages(
                CHAT,
                limit=ITER_LIMIT,
                max_id=previous or -1,
            ):
                count += 1
                total += 1

                # try:
                data = Telegram.mes2json(message)
                # except Exception as e:
                #     print(e)
                #     print(message)
                #     print("-" * 100)
                #     await asyncio.sleep(300)
                #     previous = data["message"]
                #     continue

                previous = data["message"]

                with open(FILE, "a") as file:
                    print(json.dumps(data, ensure_ascii=False), file=file)

                if LOGS:
                    print(f"#{total}: {previous}")
                    print(json.dumps(data, ensure_ascii=False, indent="\t"))
                    print("-" * 100)

                # await asyncio.sleep(DELAY)

            if ITER_LIMIT and count < ITER_LIMIT:
                break
            if LIMIT and total >= LIMIT:
                break

            await asyncio.sleep(DELAY)

        print(f"Total: {total} messages")


if __name__ == "__main__":
    asyncio.run(main())
