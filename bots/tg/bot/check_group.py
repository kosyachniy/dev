import asyncio

import aiogram

from lib.tg import tg


async def get_entity(name):
    try:
        entity = await tg.bot.get_chat(name)
    except aiogram.utils.exceptions.ChatNotFound:
        print("❌")
        return

    # print(dir(entity))
    print(entity.as_json())
    print("ID", entity.id)
    print("Type", entity.type)  # channel / supergroup
    print("Title", entity.title)
    print("Name", entity.full_name)
    print(entity.first_name)
    print(entity.last_name)
    print("Login", entity.username)
    print("Link", await entity.get_url())
    print("Invite link", entity.invite_link)
    print("Description", entity.description)
    print("Bio", entity.bio)
    print("Photo", entity.photo)

async def main():
    while True:
        await get_entity(input())


if __name__ == '__main__':
    asyncio.run(main())
