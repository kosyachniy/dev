import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from libdev.cfg import cfg


LIMIT = None
FILTER = None  # ""


async def chats(client, limit=None):
    dialogs = await client.get_dialogs()
    chats = []

    for i, dialog in enumerate(dialogs):
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
        if hasattr(dialog.entity, "username") and dialog.entity.username:
            login = dialog.entity.username
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
        print(
            dialog.name,
            " " * (45 - len(dialog.name)),
            "\t",
            login or "",
            " " * (25 - len(login or "")),
            "\t",
            entity,
            " " * (10 - len(entity)),
            "\t",
            dialog.entity.id,
            (
                f"(-{dialog.entity.id})"
                if entity == "chat"
                else (f"(-100{dialog.entity.id})" if entity == "channel" else "")
            ),
            "\t",
            (
                dialog.entity.migrated_to.channel_id
                if (hasattr(dialog.entity, "migrated_to") and dialog.entity.migrated_to)
                else ""
            ),
            (
                f"(-100{dialog.entity.migrated_to.channel_id})"
                if (hasattr(dialog.entity, "migrated_to") and dialog.entity.migrated_to)
                else ""
            ),
        )

    return chats


async def main():
    async with TelegramClient(
        # f"main{cfg('tg.id')}",
        StringSession(cfg("tg.session")),
        cfg("tg.id"),
        cfg("tg.hash"),
    ) as client:
        await chats(client, LIMIT)


if __name__ == "__main__":
    # await main() # for Jupyter Notebook
    asyncio.run(main())
