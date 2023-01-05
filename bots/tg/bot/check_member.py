import asyncio

from lib.tg import tg


CHAT = -1001390390608 # retestme -1001142824902
USERS = (5861445313,) # (373406030, 136563129, 1229366790)


async def check_entry(chat, user):
    try:
        user_type = (await tg.bot.get_chat_member(chat, user)).status
        # print(user_type)
        if user_type in ('creator', 'administrator', 'member'):
            return True
        return False
    except Exception as e:
        print(e)
        return False

async def main():
    for user in USERS:
        print(user, end=' ')
        print('YNEOS'[not await check_entry(CHAT, user)::2])


if __name__ == '__main__':
    asyncio.run(main())
