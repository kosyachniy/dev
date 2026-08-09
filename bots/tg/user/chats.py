import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from libdev.cfg import cfg


LIMIT = 30  # None
FILTER = None  # ""
# USER_SESSION = ""


async def chats(client, limit=None):
    dialogs = await client.get_dialogs()
    chats = []
    text = ""

    for i, dialog in enumerate(dialogs):
        # print("!", i)

        if i == limit:
            break
        if FILTER is not None and (
            FILTER != dialog.name if FILTER in {""} else FILTER not in dialog.name
        ):
            continue

        # Entity
        if dialog.entity.__class__.__name__ == "Chat":
            entity = "chat"
        elif dialog.entity.__class__.__name__ == "Channel":
            entity = "channel"
        else:
            entity = "user"

        # Login
        extra = None
        if hasattr(dialog.entity, "username") and dialog.entity.username:
            login = dialog.entity.username
            if login.lower()[-3:] == "bot":
                entity = "bot"
                extra = await client.get_entity(f"@{login}")
        else:
            login = None

        chats.append(
            {
                "id": dialog.entity.id,
                "login": login,
                "name": dialog.name,
                "entity": entity,
                "last_message": dialog.message.id,
            }
        )
        text_row = "".join(
            [
                str(dialog.name),
                " " * (45 - len(dialog.name)),
                "\t",
                login or "",
                " " * (25 - len(login or "")),
                "\t",
                str(entity),
                " " * (10 - len(entity)),
                "\t",
                str(dialog.entity.id),
                (
                    f"(-{dialog.entity.id})"
                    if entity == "chat"
                    else (f"(-100{dialog.entity.id})" if entity == "channel" else "")
                ),
                "\t",
                (
                    str(dialog.entity.migrated_to.channel_id)
                    if (
                        hasattr(dialog.entity, "migrated_to")
                        and dialog.entity.migrated_to
                    )
                    else ""
                ),
                (
                    f"(-100{dialog.entity.migrated_to.channel_id})"
                    if (
                        hasattr(dialog.entity, "migrated_to")
                        and dialog.entity.migrated_to
                    )
                    else ""
                ),
                str(extra),
                "\n",
            ]
        )
        print(text_row, end="")
        text += text_row

    return chats, text


async def main():
    async with TelegramClient(
        # f"main{cfg('tg.id')}",
        StringSession(cfg("TG_SESSION")),  # USER_SESSION
        cfg("tg.id"),
        cfg("tg.hash"),
    ) as client:
        _, text = await chats(client, LIMIT)
        print(text)
        # with open("chats.txt", "w") as file:
        #     print(text, file=file)


if __name__ == "__main__":
    # await main() # for Jupyter Notebook
    asyncio.run(main())
