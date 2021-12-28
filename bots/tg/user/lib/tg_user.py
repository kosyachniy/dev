"""
Functionality for working with users on Telegram
"""

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import (
    MessageEntityTextUrl, MessageEntityHashtag, MessageEntityCashtag,
    MessageEntityMention,
)
from libdev.cfg import cfg


def _clear_tags(tag):
    if tag[0] in {'#', '$'}:
        tag = tag[1:]
    return tag.strip()


class Telegram:
    def __init__(self):
        self.client = TelegramClient(
            StringSession(cfg('tg.session')), cfg('tg.id'), cfg('tg.hash')
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

        if entity['_'] == 'PeerChat':
            return int(f"-{entity['chat_id']}")

        if entity['_'] == 'PeerChannel':
            return int(f"-100{entity['channel_id']}")

        return entity['user_id']

    def mes2json(self, message):
        return {
            'data': message.message,
            'source': self.get_entity_id(message.peer_id),
            'author': self.get_entity_id(message.from_id),
            'message': message.id,
            'reactions': {
                'views': message.views or [],
                'likes': [],
                'reposts': [],
                'comments': [],
            },
            'entities': {
                'links': [
                    link.url
                    for link in message.entities or []
                    if type(link) == MessageEntityTextUrl
                ],
                'cover': None,
                'mentions': [
                    message.message[mention.offset+1:mention.offset+mention.length]
                    for mention in message.entities or []
                    if type(mention) == MessageEntityMention
                ],
                'hashtags': [
                    _clear_tags(message.message[tag.offset:tag.offset+tag.length])
                    for tag in message.entities or []
                    if type(tag) == MessageEntityHashtag
                ],
                'cashtags': [
                    _clear_tags(message.message[tag.offset:tag.offset+tag.length])
                    for tag in message.entities or []
                    if type(tag) == MessageEntityCashtag
                ],
                'markup': [],
                'buttons': [],
            },
            'attachments': {
                'links': [],
                'images': [],
                'videos': [],
                'files': [],
                'forwarded': message.fwd_from and {
                    'name': message.fwd_from.post_author,
                    'author': self.get_entity_id(message.fwd_from.from_id),
                    'message': message.fwd_from.channel_post,
                    'created': int(message.fwd_from.date.timestamp()),
                },
                'replied': message.reply_to and message.reply_to.reply_to_msg_id,
            },
            'created': int(message.date.timestamp()),
        }

    async def send(self, name, cont):
        entity = await self.client.get_entity(name)
        await self.client.send_message(entity, cont)


__all__ = (
    'Telegram',
    'events',
)
