"""
Functionality for working with users on Telegram
"""

import asyncio
import datetime

from telethon import TelegramClient
import telethon.errors
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import (
    MessageEntityTextUrl,
    MessageEntityHashtag,
    MessageEntityCashtag,
    MessageEntityMention,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaContact,
    MessageMediaWebPage,
    MessageMediaVenue,
    MessageMediaGeo,
    MessageMediaGeoLive,
    MessageMediaGame,
    MessageMediaInvoice,
    MessageMediaPoll,
    MessageMediaUnsupported,
    MessageMediaDice,
    MessageMediaStory,
)
from libdev.cfg import cfg


def _clear_tags(tag):
    if tag[0] in {"#", "$"}:
        tag = tag[1:]
    return tag.strip()


class Telegram:
    def __init__(self):
        self.client = TelegramClient(
            StringSession(cfg("tg.session")), cfg("tg.id"), cfg("tg.hash")
        )

    async def __aenter__(self):
        await self.client.connect()
        return self

    async def __aexit__(self, exception_type, exception_val, trace):
        await self.client.disconnect()

    @staticmethod
    def get_entity_id(peer):
        if peer is None:
            return None

        entity = peer.to_dict()

        if entity["_"] == "PeerChat":
            return int(f"-{entity['chat_id']}")

        if entity["_"] == "PeerChannel":
            return int(f"-100{entity['channel_id']}")

        return entity["user_id"]

    @staticmethod
    def get_media(media):
        if isinstance(media, MessageMediaPhoto):
            # TODO: load
            img = media.photo.to_dict() if media.photo else {}
            return dict(
                type="image",
                id=img.get("id"),  # NOTE: expired photo
                hash=img.get("access_hash"),
            )

        if isinstance(media, MessageMediaDocument):
            # TODO: load
            doc = media.document.to_dict() if media.document else {}
            return dict(
                type="file",
                id=doc.get("id"),
                hash=doc.get("access_hash"),
                mime=doc.get("mime_type"),
            )

        if isinstance(media, MessageMediaGeo):
            return dict(
                type="geo",
                lat=media.geo.lat,
                long=media.geo.long,
            )

        if isinstance(media, MessageMediaGeoLive):
            return dict(
                type="geo",
                lat=media.geo.lat,
                long=media.geo.long,
                period=media.period,
            )

        if isinstance(media, MessageMediaVenue):
            return dict(
                type="geo",
                title=media.venue.title,
                address=media.venue.address,
            )

        if isinstance(media, MessageMediaContact):
            return dict(
                type="contact",
                name=media.first_name,
                phone=media.phone_number,
            )

        if isinstance(media, MessageMediaWebPage):
            web = media.webpage.to_dict()
            return dict(
                type="web",
                link=web.get("url"),
            )

        if isinstance(media, MessageMediaGame):
            return dict(
                type="game",
                link=media.game.title,
            )

        if isinstance(media, MessageMediaInvoice):
            return dict(
                type="payment",
                title=media.title,
                data=media.description,
            )

        if isinstance(media, MessageMediaPoll):
            return dict(
                type="poll",
                title=media.poll.question,
                data=[answer.text for answer in media.poll.answers],
            )

        if isinstance(media, MessageMediaDice):
            return dict(
                type="dice",
                emoji=media.emoticon,
                data=media.value,
            )

        if isinstance(media, MessageMediaStory):
            return dict(
                type="story",
                source=media.user_id,
                id=media.id,
                mention=media.via_mention,
            )

        elif isinstance(media, MessageMediaUnsupported):
            print(media)
            return None

        else:
            print(type(media), media)
            print(dir(media))
            print(media.to_dict())
            return None

    @classmethod
    def mes2json(cls, message):
        reply = None
        if message.reply_to:
            if "story_id" in message.reply_to.to_dict():
                reply = {
                    "type": "story",
                    "source": message.reply_to.user_id,
                    "id": message.reply_to.story_id,
                }
            else:
                reply = {
                    "type": "message",
                    "id": message.reply_to.reply_to_msg_id,
                }

        return {
            "data": message.message,
            "source": cls.get_entity_id(message.peer_id),
            "author": cls.get_entity_id(message.from_id),
            "message": message.id,
            "reactions": {
                "views": message.views or [],
                "likes": [],
                "reposts": [],
                "comments": [],
            },
            "entities": {
                "links": [
                    link.url
                    for link in message.entities or []
                    if type(link) == MessageEntityTextUrl
                ],
                "cover": None,
                "mentions": [
                    message.message[
                        mention.offset + 1 : mention.offset + mention.length
                    ]
                    for mention in message.entities or []
                    if type(mention) == MessageEntityMention
                ],
                "hashtags": [
                    _clear_tags(message.message[tag.offset : tag.offset + tag.length])
                    for tag in message.entities or []
                    if type(tag) == MessageEntityHashtag
                ],
                "cashtags": [
                    _clear_tags(message.message[tag.offset : tag.offset + tag.length])
                    for tag in message.entities or []
                    if type(tag) == MessageEntityCashtag
                ],
                "markup": [],
                "buttons": [],
            },
            "attachments": (
                [
                    cls.get_media(message.media),
                ]
                if message.media
                else []
            ),
            "forwarded": message.fwd_from
            and {
                "name": message.fwd_from.post_author,
                "author": cls.get_entity_id(message.fwd_from.from_id),
                "message": message.fwd_from.channel_post,
                "created": int(message.fwd_from.date.timestamp()),
            },
            "replied": reply,
            "created": int(message.date.timestamp()),
        }

    async def send(self, name, cont):
        entity = await self.client.get_entity(name)
        await self.client.send_message(entity, cont)

    async def forward(self, target, source, message):
        target = await self.client.get_entity(target)
        source = await self.client.get_entity(source)
        await self.client.forward_messages(
            entity=target,
            messages=message,
            from_peer=source,
        )


client = Telegram()


def _format_channel(entity):
    return {
        "id": int(f"-100{entity.full_chat.id}"),
        "login": entity.chats[0].username,
        "url": f"https://t.me/{entity.chats[0].username}",
        "title": entity.chats[0].title,
        "followers": entity.full_chat.participants_count,
    }


def _format_post(post):
    likes = (
        sum(reaction.count for reaction in post.reactions.results)
        if post.reactions
        else 0
    )
    comments = post.replies.replies if post.replies else 0
    reposts = post.forwards or 0
    return {
        "id": post.id,
        "views": post.views,
        "likes": likes,
        "comments": comments,
        "reposts": reposts,
        "engagement": likes + comments + reposts,
    }


async def get_channel(entity):
    await client.start()
    entity = await client.get_entity(entity)
    full_channel = await client(GetFullChannelRequest(channel=entity))
    return _format_channel(full_channel)


async def get_posts(entity_id, date):
    await client.start()
    posts = await client.get_messages(entity_id, limit=100)
    return [_format_post(post) for post in posts if post.date.date() == date]


async def get_stat(entity_id, date=datetime.datetime.now().date()):
    try:
        data = await get_channel(entity_id)
    except telethon.errors.rpcerrorlist.FloodWaitError:
        await asyncio.sleep(60)  # FIXME: depends on FloodWaitError
        data = await get_channel(entity_id)
    data["posts"] = 0
    data["views"] = 0
    data["likes"] = 0
    data["comments"] = 0
    data["engagement"] = 0
    data["best_post"] = None
    current_engagement = 0

    for post in await get_posts(entity_id, date):
        data["posts"] += 1
        data["views"] += post["views"]
        data["likes"] += post["likes"]
        data["comments"] += post["comments"]
        data["engagement"] += post["engagement"]

        if data["best_post"] is None or post["engagement"] > current_engagement:
            data["best_post"] = f"https://t.me/{data['login']}/{post['id']}"
            current_engagement = post["engagement"]

    return data
