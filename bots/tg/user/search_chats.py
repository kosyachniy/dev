"""Find known Telegram chats by title without downloading the dialog list.

    python search_chats.py "part of the chat name"

Uses the same libdev tg.id, tg.hash and tg.session settings as chats.py.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from telethon import TelegramClient, errors, functions, types, utils
from telethon.sessions import StringSession


def validate_search(query, limit):
    query = query.strip()
    if not query:
        raise ValueError("The search string must not be empty.")
    if not 1 <= limit <= 100:
        raise ValueError("The limit must be between 1 and 100.")
    return query


def describe_entity(entity):
    if isinstance(entity, (types.Chat, types.ChatForbidden)):
        kind = "chat"
    elif isinstance(entity, (types.Channel, types.ChannelForbidden)):
        kind = "channel"
    else:
        kind = "bot" if getattr(entity, "bot", False) else "user"
    migrated = getattr(entity, "migrated_to", None)
    return {
        "id": entity.id,
        "login": getattr(entity, "username", None),
        "name": utils.get_display_name(entity),
        "entity": kind,
        "last_message": None,
        "marked_id": utils.get_peer_id(entity),
        "migrated_to": migrated.channel_id if migrated else None,
    }


def rpc_error_text(exc):
    if isinstance(exc, errors.FloodWaitError):
        return f"Telegram requires a wait of {exc.seconds} seconds. Retry after that."
    if isinstance(exc, errors.QueryTooShortError):
        return "Telegram rejected the search string as too short. Use a longer name."
    return str(exc)


async def search_chats(client, query, limit=50, last_message=True):
    """Return chat records using one search and at most one metadata request.

    my_results contains known peers; results contains global/public matches.
    Telegram controls matching and may cap results, so this is not exhaustive.
    """
    query = validate_search(query, limit)
    found = await client(functions.contacts.SearchRequest(q=query, limit=limit))
    entities = {
        utils.get_peer_id(entity): entity for entity in [*found.chats, *found.users]
    }
    rows = []
    peers = []
    seen = set()
    for peer in found.my_results:
        peer_id = utils.get_peer_id(peer)
        if peer_id in seen or peer_id not in entities:
            continue
        seen.add(peer_id)
        entity = entities[peer_id]
        rows.append(describe_entity(entity))
        if last_message:
            # Convert the returned entity locally: resolving a bare ID through
            # client.get_input_entity() can fall back to fetching all dialogs.
            try:
                peers.append(types.InputDialogPeer(utils.get_input_peer(entity)))
            except (TypeError, ValueError):
                print(
                    f"Latest message unavailable for {peer_id}: "
                    "Telegram did not return a usable input peer.",
                    file=sys.stderr,
                )
        if len(rows) >= limit:
            break

    if peers:
        try:
            details = await client(functions.messages.GetPeerDialogsRequest(peers))
        except errors.RPCError as exc:
            # Keep the IDs and titles even when metadata is inaccessible or
            # rate limited. Never fall back to scanning dialogs or retrying.
            print(
                f"Latest message IDs unavailable: {rpc_error_text(exc)}",
                file=sys.stderr,
            )
        else:
            latest = {
                utils.get_peer_id(dialog.peer): dialog.top_message or None
                for dialog in details.dialogs
            }
            for row in rows:
                row["last_message"] = latest.get(row["marked_id"])
    return rows


def format_chats(rows):
    lines = [
        f"{'Name':45}\t{'Login':25}\t{'Entity':10}\t"
        "ID (marked ID)\tMigrated to\tLast message"
    ]
    for row in rows:
        migrated = row["migrated_to"]
        migrated_text = (
            f"{migrated}({utils.get_peer_id(types.PeerChannel(migrated))})"
            if migrated is not None
            else ""
        )
        name = row["name"].replace("\n", " ").replace("\r", " ").replace("\t", " ")
        lines.append(
            f"{name:45}\t{row['login'] or '':25}\t{row['entity']:10}\t"
            f"{row['id']}({row['marked_id']})\t{migrated_text}\t"
            f"{row['last_message'] if row['last_message'] is not None else ''}"
        )
    return "\n".join(lines) + "\n"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Chat title or part of it")
    parser.add_argument(
        "--limit", type=int, default=50,
        help="Maximum results, 1–100 (default: 50)",
    )
    parser.add_argument("--output", type=Path, default=Path("chats_search.txt"))
    parser.add_argument(
        "--no-last-message", action="store_true",
        help="Skip the metadata request; use only one search request",
    )
    args = parser.parse_args(argv)
    try:
        args.query = validate_search(args.query, args.limit)
    except ValueError as exc:
        parser.error(str(exc))
    return args


async def main(args):
    from libdev.cfg import cfg

    async with TelegramClient(
        StringSession(cfg("tg.session")),
        cfg("tg.id"),
        cfg("tg.hash"),
        flood_sleep_threshold=0,
        request_retries=0,
        raise_last_call_error=True,
        receive_updates=False,
    ) as client:
        rows = await search_chats(
            client, args.query, args.limit, last_message=not args.no_last_message
        )
    text = format_chats(rows)
    print(text, end="")
    args.output.write_text(text, encoding="utf-8")
    if not rows:
        print(
            "Telegram returned no known chats. Try a more distinctive part of "
            "the current title; server search is not exhaustive.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    try:
        asyncio.run(main(parse_args()))
    except errors.RPCError as exc:
        print(rpc_error_text(exc), file=sys.stderr)
        sys.exit(1)
