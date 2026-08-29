#!/usr/bin/env python3
"""Export one Telegram chat, including its downloadable attachments.

This is a standalone exporter.  It deliberately does not import the local
``lib.tg_user.Telegram`` serializer or ``libdev`` configuration helpers.

Required dependency (the repository's old Telethon 1.30 pin is too old for
the current Telegram message/media schema):

    python -m pip install "Telethon>=1.44.0,<2" aiohttp

Examples:

    # TG_ID and TG_HASH may also be stored in a local .env file.
    export TG_ID=12345
    export TG_HASH=0123456789abcdef0123456789abcdef
    python export_chat.py @chat_name
    python export_chat.py -1001234567890 --session-string "$TG_SESSION_STRING"
    python export_chat.py @large_channel --takeout

The result is written to:

    download/<marked-chat-id>/<marked-chat-id>.json
    download/<marked-chat-id>/files/{media,forwarded,avatars,stickers,icons,
                                      reactions,preview,effects,stories,
                                      wallpapers,other,legacy}/*
    download/<marked-chat-id>/media-errors.jsonl  # only when media issues occur

The JSON keeps the legacy ``Telegram.mes2json`` keys and adds normalized
current fields plus the complete raw TL object exposed by the installed
Telethon/negotiated Telegram layer.

Only history and media available to the logged-in user can be exported.
Telegram cannot reconstruct deleted messages, expired/self-destructed media,
secret-chat history, unpurchased paid media, or inaccessible stories.  Saving
protected (``noforwards``) content is intentionally not attempted.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import copy
import datetime as dt
import hashlib
import json
import mimetypes
import os
import random
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional

try:
    import telethon
    import aiohttp
    from telethon import TelegramClient, errors, functions, types, utils
    from telethon.sessions import StringSession
except ImportError as exc:  # pragma: no cover - only used for a friendly CLI error
    raise SystemExit(
        "Telethon and aiohttp are required. Install them with: "
        'python -m pip install "Telethon>=1.44.0,<2" aiohttp'
    ) from exc

try:
    from telethon.tl.alltlobjects import LAYER as TELEGRAM_LAYER
except ImportError:  # Future Telethon versions may move this constant.
    TELEGRAM_LAYER = None


MIN_TELETHON = (1, 44, 0)
MIN_TELEGRAM_LAYER = 227
SCHEMA_NAME = "telegram-chat-export"
SCHEMA_VERSION = 3
HISTORY_PAGE_SIZE = 100  # Telegram list methods normally accept at most 100.
CUSTOM_EMOJI_BATCH_SIZE = 100  # Official limit for getCustomEmojiDocuments.
UNLIMITED_TAKEOUT_FILE_SIZE = (1 << 63) - 1
ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def load_local_env() -> None:
    """Load a nearby .env without overwriting the process environment.

    Keep this standalone exporter dependency-free apart from its Telegram/HTTP
    dependencies. The supported .env syntax covers the conventional
    ``KEY=value`` and ``export KEY=value`` forms, including quoted values.
    """

    candidates = (Path.cwd() / ".env", Path(__file__).resolve().with_name(".env"))
    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except FileNotFoundError:
            continue
        except OSError as exc:
            print(f"Warning: cannot read {path}: {exc}", file=sys.stderr)
            continue

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            key, separator, value = line.partition("=")
            key = key.strip()
            if not separator or not ENV_KEY_RE.fullmatch(key):
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            else:
                value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
            os.environ.setdefault(key, value)
        return


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_datetime(value: Optional[dt.datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def unix_timestamp(value: Optional[dt.datetime]) -> Optional[int]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return int(value.timestamp())


def telethon_version_tuple() -> tuple[int, int, int]:
    numbers = [int(part) for part in re.findall(r"\d+", telethon.__version__)[:3]]
    return tuple((numbers + [0, 0, 0])[:3])  # type: ignore[return-value]


def require_current_telethon() -> None:
    if telethon_version_tuple() < MIN_TELETHON:
        wanted = ".".join(map(str, MIN_TELETHON))
        raise RuntimeError(
            f"Telethon {wanted}+ is required for the current Telegram schema; "
            f"found {telethon.__version__}. Upgrade Telethon before exporting."
        )
    if TELEGRAM_LAYER is None or int(TELEGRAM_LAYER) < MIN_TELEGRAM_LAYER:
        raise RuntimeError(
            f"Telegram schema layer {MIN_TELEGRAM_LAYER}+ is required; "
            f"this Telethon build exposes layer {TELEGRAM_LAYER!r}. Upgrade Telethon."
        )


def tl_name(value: Any) -> str:
    return type(value).__name__ if value is not None else "None"


def json_safe(value: Any) -> Any:
    """Recursively turn TL values into lossless JSON-compatible values."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if value == value and abs(value) != float("inf") else None
    if isinstance(value, bytes):
        return {"_type": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        if isinstance(value, dt.datetime):
            return iso_datetime(value)
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [json_safe(item) for item in value]
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return json_safe(to_dict())
    return str(value)


def peer_id(peer: Any) -> Optional[int]:
    if peer is None:
        return None
    try:
        return int(utils.get_peer_id(peer))
    except (TypeError, ValueError, AttributeError):
        return None


def marked_chat_id(entity: Any) -> int:
    return int(utils.get_peer_id(entity))


def chat_kind(entity: Any) -> str:
    name = tl_name(entity)
    if name == "User":
        return "bot" if getattr(entity, "bot", False) else "private"
    if name in {"Chat", "ChatForbidden"}:
        return "basic_group"
    if name in {"Channel", "ChannelForbidden"}:
        if getattr(entity, "monoforum", False):
            return "monoforum"
        if getattr(entity, "gigagroup", False):
            return "gigagroup"
        if getattr(entity, "megagroup", False):
            return "supergroup"
        return "channel"
    return name


def sanitize_component(
    value: str, fallback: str = "file", max_length: int = 120
) -> str:
    value = Path(value or "").name
    value = re.sub(r"[\x00-\x1f\x7f/\\:]", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    value = re.sub(r"_+", "_", value)
    if not value or value in {".", ".."}:
        value = fallback
    return value[:max_length].rstrip(" .") or fallback


def safe_extension(
    value: Optional[str], mime_type: Optional[str], fallback: str
) -> str:
    raw_value = value or ""
    extension = (
        raw_value.lower()
        if re.fullmatch(r"\.[a-zA-Z0-9]{1,10}", raw_value)
        else Path(raw_value).suffix.lower()
    )
    if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension):
        extension = mimetypes.guess_extension(mime_type or "") or fallback
    if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension.lower()):
        return fallback
    return extension.lower()


def utf16_slice(text: str, offset: int, length: int) -> str:
    """Telegram entity offsets count UTF-16 code units, not Python characters."""
    raw = (text or "").encode("utf-16-le")
    return raw[offset * 2 : (offset + length) * 2].decode("utf-16-le", errors="replace")


def chunks(values: list[int], size: int) -> Iterable[list[int]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def error_text(exc: BaseException) -> str:
    text = re.sub(r"\s+", " ", str(exc)).strip()
    return text[:1000]


def is_file_reference_error(exc: BaseException) -> bool:
    if isinstance(exc, getattr(errors, "FileReferenceExpiredError", ())):
        return True
    if isinstance(exc, getattr(errors, "FilerefUpgradeNeededError", ())):
        return True
    upper = str(exc).upper()
    return "FILE_REFERENCE_" in upper or "FILEREF_" in upper


def file_reference_fingerprint(value: Any) -> Optional[str]:
    """Return a safe identifier for comparing opaque Telegram references."""

    reference = bytes(getattr(value, "file_reference", b"") or b"")
    if reference:
        return hashlib.sha256(reference).hexdigest()[:16]
    profile_photo = getattr(value, "photo", None)
    photo_id = getattr(profile_photo, "photo_id", None)
    if photo_id is not None:
        return hashlib.sha256(f"profile:{photo_id}".encode()).hexdigest()[:16]
    return None


def contact_vcard(media: Any) -> bytes:
    original = getattr(media, "vcard", None)
    if original:
        return str(original).encode("utf-8")
    first = str(getattr(media, "first_name", None) or "").replace(";", "")
    last = str(getattr(media, "last_name", None) or "").replace(";", "")
    phone = str(getattr(media, "phone_number", None) or "")
    return (
        "BEGIN:VCARD\r\n"
        "VERSION:4.0\r\n"
        f"N:{first};{last};;;\r\n"
        f"FN:{first} {last}\r\n"
        f"TEL;TYPE=cell;VALUE=uri:tel:{phone}\r\n"
        "END:VCARD\r\n"
    ).encode("utf-8")


class Pacer:
    """Conservative local pacing; Telegram does not publish fixed quotas."""

    def __init__(
        self,
        history_delay: float,
        metadata_delay: float,
        media_delay: float,
        chunk_delay: float,
        jitter: float,
        flood_reserve: float,
    ) -> None:
        self.history_delay = max(0.0, history_delay)
        self.metadata_delay = max(0.0, metadata_delay)
        self.media_delay = max(0.0, media_delay)
        self.chunk_delay = max(0.0, chunk_delay)
        self.jitter = max(0.0, jitter)
        self.flood_reserve = max(0.0, flood_reserve)

    async def sleep(self, base: float) -> None:
        delay = base + (random.uniform(0.0, self.jitter) if self.jitter else 0.0)
        if delay > 0:
            await asyncio.sleep(delay)

    async def after_history(self) -> None:
        await self.sleep(self.history_delay)

    async def after_metadata(self) -> None:
        await self.sleep(self.metadata_delay)

    async def after_media(self) -> None:
        await self.sleep(self.media_delay)

    async def after_chunk(self) -> None:
        # Telethon invokes an async progress callback after each downloaded
        # part, which lets us add reserve pacing without reimplementing file
        # DC migration, CDN validation, or aligned MTProto chunking.
        await self.sleep(self.chunk_delay)

    async def flood_wait(self, seconds: int, label: str) -> None:
        delay = max(0, seconds) + self.flood_reserve
        if self.jitter:
            delay += random.uniform(0.0, self.jitter)
        print(f"Telegram flood limit for {label}; sleeping {delay:.1f}s", flush=True)
        await asyncio.sleep(delay)


@dataclass
class DownloadTarget:
    obj: Any
    kind: str
    subtype: str
    role: str
    message_id: int
    cache_key: str
    extension: str
    expected_size: Optional[int]
    metadata: dict[str, Any]
    original_name: Optional[str] = None
    thumb: Any = None
    protected: bool = False
    source_chat_id: Optional[int] = None
    source_peer: Any = None
    message_range: Any = None
    dc_id: Optional[int] = None
    refresh_url: Optional[str] = None
    embedded_preview: Optional[bytes] = None
    embedded_preview_info: Optional[dict[str, Any]] = None
    forwarded: bool = False
    category_hint: Optional[str] = None


ATTACHMENT_CATEGORIES = frozenset(
    {
        "media",
        "forwarded",
        "avatars",
        "stickers",
        "icons",
        "reactions",
        "preview",
        "effects",
        "stories",
        "wallpapers",
        "other",
    }
)


def attachment_base_category_values(
    role: str,
    subtype: str,
    category_hint: Optional[str] = None,
    refresh_url: Optional[str] = None,
) -> str:
    """Classify an attachment by semantic purpose before forwarded origin."""

    role = role.lower()
    subtype = subtype.lower()
    if category_hint:
        if category_hint not in ATTACHMENT_CATEGORIES - {"forwarded"}:
            raise ValueError(f"Unsupported attachment category {category_hint!r}")
        # ``other`` is deliberately a weak hint: known semantic asset types
        # nested in a service message (for example a gift sticker) still go
        # to their specific folder. All other context hints are authoritative.
        if category_hint != "other":
            return category_hint
    if role.startswith("message.reaction_custom_emoji."):
        return "reactions"
    if role.startswith("message.effect."):
        return "effects"
    if any(token in role for token in ("avatar", "profile_photo", "peer.photo")):
        return "avatars"
    if subtype == "custom_emoji" or "custom_emoji" in role:
        return "icons"
    if (
        refresh_url
        or "reply_media" in role
        or "video_cover" in role
        or "accessible_preview" in role
        or ".cached_page" in role
    ):
        return "preview"
    if "story" in role:
        return "stories"
    if subtype in {
        "sticker",
        "animated_sticker",
        "video_sticker",
        "premium_sticker_effect",
    }:
        return "stickers"
    if category_hint:
        return category_hint
    return "media"


def attachment_category_values(
    role: str,
    subtype: str,
    forwarded: bool,
    category_hint: Optional[str] = None,
    refresh_url: Optional[str] = None,
) -> str:
    base = attachment_base_category_values(
        role,
        subtype,
        category_hint,
        refresh_url,
    )
    if forwarded and base == "media":
        return "forwarded"
    return base


def attachment_base_category(target: DownloadTarget) -> str:
    return attachment_base_category_values(
        target.role,
        target.subtype,
        target.category_hint,
        target.refresh_url,
    )


def attachment_category(target: DownloadTarget) -> str:
    # Keep semantic asset types together. Only ordinary message attachments
    # split by origin into direct media versus forwarded media.
    return attachment_category_values(
        target.role,
        target.subtype,
        target.forwarded,
        target.category_hint,
        target.refresh_url,
    )


@dataclass
class HistorySource:
    input_peer: Any
    marked_id: int
    label: str
    migration_boundary: Optional[int] = None
    history_peer: Any = None
    parent_peer: Any = None
    topic_peer_id: Optional[int] = None
    topic_top_message: Optional[int] = None
    topic_dialog: Any = None
    topic_entity: Any = None


@dataclass
class ExportStats:
    messages: int = 0
    empty_messages_skipped: int = 0
    history_requests: int = 0
    metadata_requests: int = 0
    flood_waits: int = 0
    transient_retries: int = 0
    file_reference_refreshes: int = 0
    file_reference_refresh_successes: int = 0
    metadata_failures: int = 0
    attachments: dict[str, int] = field(default_factory=dict)
    attachment_categories: dict[str, int] = field(default_factory=dict)
    bytes_downloaded: int = 0

    def observe_attachment(self, record: Mapping[str, Any]) -> None:
        status = str(record.get("status") or "unknown")
        self.attachments[status] = self.attachments.get(status, 0) + 1
        category = record.get("category")
        if category:
            name = str(category)
            self.attachment_categories[name] = (
                self.attachment_categories.get(name, 0) + 1
            )
        if status == "downloaded":
            self.bytes_downloaded += int(record.get("downloaded_size") or 0)


def photo_size_info(size: Any) -> dict[str, Any]:
    size_name = tl_name(size)
    byte_size: Optional[int]
    if size_name == "PhotoSizeProgressive":
        values = getattr(size, "sizes", None) or []
        byte_size = max(values) if values else None
    elif size_name in {"PhotoCachedSize", "PhotoStrippedSize", "PhotoPathSize"}:
        byte_size = len(getattr(size, "bytes", b"") or b"")
    else:
        byte_size = getattr(size, "size", None)
    return {
        "constructor": size_name,
        "type": getattr(size, "type", None),
        "width": getattr(size, "w", None),
        "height": getattr(size, "h", None),
        "size": byte_size,
    }


def best_photo_size(photo: Any) -> Any:
    candidates = []
    for size in getattr(photo, "sizes", None) or []:
        if tl_name(size) in {"PhotoSizeEmpty", "PhotoStrippedSize", "PhotoPathSize"}:
            continue
        info = photo_size_info(size)
        area = int(info.get("width") or 0) * int(info.get("height") or 0)
        candidates.append((area, int(info.get("size") or 0), size))
    if candidates:
        # x/y/w are Telegram's uncropped full-image sizes.  Prefer them over
        # potentially larger-area a/b/c/d crop derivatives.
        uncropped = [
            candidate
            for candidate in candidates
            if getattr(candidate[2], "type", None) in {"x", "y", "w"}
        ]
        return max(uncropped or candidates, key=lambda item: (item[0], item[1]))[2]

    # A cached/stripped image is better than silently losing the attachment.
    fallback = []
    for size in getattr(photo, "sizes", None) or []:
        if tl_name(size) in {"PhotoCachedSize", "PhotoStrippedSize"}:
            fallback.append((len(getattr(size, "bytes", b"") or b""), size))
    if fallback:
        return max(fallback, key=lambda item: item[0])[1]

    video_sizes = [
        size
        for size in (getattr(photo, "video_sizes", None) or [])
        if tl_name(size) == "VideoSize"
    ]
    if video_sizes:
        return max(
            video_sizes,
            key=lambda size: (
                int(getattr(size, "w", 0) or 0) * int(getattr(size, "h", 0) or 0),
                int(getattr(size, "size", 0) or 0),
            ),
        )
    return None


def document_attributes(document: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "filename": None,
        "width": None,
        "height": None,
        "duration": None,
        "title": None,
        "performer": None,
        "voice": False,
        "round": False,
        "animated": False,
        "sticker": False,
        "custom_emoji": False,
        "supports_streaming": False,
        "video_codec": None,
        "sticker_alt": None,
    }
    for attribute in getattr(document, "attributes", None) or []:
        name = tl_name(attribute)
        if name == "DocumentAttributeFilename":
            result["filename"] = getattr(attribute, "file_name", None)
        elif name == "DocumentAttributeVideo":
            result.update(
                width=getattr(attribute, "w", None),
                height=getattr(attribute, "h", None),
                duration=getattr(attribute, "duration", None),
                round=bool(getattr(attribute, "round_message", False)),
                supports_streaming=bool(
                    getattr(attribute, "supports_streaming", False)
                ),
                video_codec=getattr(attribute, "video_codec", None),
            )
        elif name == "DocumentAttributeAudio":
            result.update(
                duration=getattr(attribute, "duration", None),
                title=getattr(attribute, "title", None),
                performer=getattr(attribute, "performer", None),
                voice=bool(getattr(attribute, "voice", False)),
            )
        elif name == "DocumentAttributeImageSize":
            result.update(
                width=getattr(attribute, "w", None),
                height=getattr(attribute, "h", None),
            )
        elif name == "DocumentAttributeAnimated":
            result["animated"] = True
        elif name == "DocumentAttributeSticker":
            result.update(sticker=True, sticker_alt=getattr(attribute, "alt", None))
        elif name == "DocumentAttributeCustomEmoji":
            result["custom_emoji"] = True
    return result


def document_subtype(document: Any, attributes: Mapping[str, Any]) -> str:
    mime = (getattr(document, "mime_type", None) or "").lower()
    if attributes.get("custom_emoji"):
        return "custom_emoji"
    if attributes.get("sticker"):
        if mime == "application/x-tgsticker":
            return "animated_sticker"
        if mime.startswith("video/"):
            return "video_sticker"
        return "sticker"
    if attributes.get("voice"):
        return "voice"
    if attributes.get("round"):
        return "round_video"
    if attributes.get("animated"):
        return "animation"
    if (
        attributes.get("width")
        and attributes.get("height")
        and mime.startswith("video/")
    ):
        return "video"
    if attributes.get("duration") is not None and mime.startswith("audio/"):
        return "audio"
    if mime.startswith("image/"):
        return "image"
    return "file"


def video_quality_key(document: Any) -> tuple[int, int, int, int]:
    attributes = document_attributes(document)
    width = int(attributes.get("width") or 0)
    height = int(attributes.get("height") or 0)
    size = int(getattr(document, "size", 0) or 0)
    return width * height, max(width, height), min(width, height), size


def document_variant(document: Any, selected: bool = False) -> dict[str, Any]:
    attributes = document_attributes(document)
    return {
        "id": getattr(document, "id", None),
        "mime": getattr(document, "mime_type", None),
        "size": getattr(document, "size", None),
        "width": attributes.get("width"),
        "height": attributes.get("height"),
        "duration": attributes.get("duration"),
        "video_codec": attributes.get("video_codec"),
        "selected": selected,
    }


def entity_summary(
    text: str, entities: Iterable[Any], reply_markup: Any
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    links: list[str] = []
    mentions: list[str] = []
    hashtags: list[str] = []
    cashtags: list[str] = []

    for entity in entities or []:
        offset = int(getattr(entity, "offset", 0) or 0)
        length = int(getattr(entity, "length", 0) or 0)
        value = utf16_slice(text or "", offset, length)
        name = tl_name(entity)
        raw = json_safe(entity)
        item = {
            "type": name.removeprefix("MessageEntity"),
            "offset": offset,
            "length": length,
            "text": value,
            "raw": raw,
        }
        items.append(item)

        if name == "MessageEntityTextUrl":
            url = getattr(entity, "url", None)
            if url:
                links.append(url)
        elif name == "MessageEntityUrl" and value:
            links.append(value)
        elif name == "MessageEntityEmail" and value:
            links.append(f"mailto:{value}")
        elif name == "MessageEntityMention" and value:
            mentions.append(value.lstrip("@"))
        elif name in {"MessageEntityMentionName", "InputMessageEntityMentionName"}:
            mentioned = getattr(entity, "user_id", None)
            mentioned_id = peer_id(mentioned) or getattr(
                mentioned, "user_id", mentioned
            )
            if mentioned_id is not None:
                mentions.append(str(mentioned_id))
        elif name == "MessageEntityHashtag" and value:
            hashtags.append(value.lstrip("#").strip())
        elif name == "MessageEntityCashtag" and value:
            cashtags.append(value.lstrip("$").strip())

    buttons: list[Any] = []
    for row in getattr(reply_markup, "rows", None) or []:
        buttons.extend(
            json_safe(button) for button in (getattr(row, "buttons", None) or [])
        )

    return {
        "links": links,
        "cover": None,
        "mentions": mentions,
        "hashtags": hashtags,
        "cashtags": cashtags,
        "markup": items,
        "buttons": buttons,
        "reply_markup": json_safe(reply_markup),
    }


def reaction_summary(message: Any) -> dict[str, Any]:
    reactions = getattr(message, "reactions", None)
    results = list(getattr(reactions, "results", None) or [])
    replies = getattr(message, "replies", None)
    return {
        "views": getattr(message, "views", None),
        "likes": sum(int(getattr(item, "count", 0) or 0) for item in results),
        "reposts": getattr(message, "forwards", None),
        "comments": getattr(replies, "replies", None),
        "results": json_safe(results),
        "recent": json_safe(getattr(reactions, "recent_reactions", None)),
        "top_reactors": json_safe(getattr(reactions, "top_reactors", None)),
        "raw": json_safe(reactions),
    }


def forwarded_summary(message: Any) -> Optional[dict[str, Any]]:
    forwarded = getattr(message, "fwd_from", None)
    if forwarded is None:
        return None
    date = getattr(forwarded, "date", None)
    return {
        "name": (
            getattr(forwarded, "post_author", None)
            or getattr(forwarded, "from_name", None)
        ),
        "author": peer_id(getattr(forwarded, "from_id", None)),
        "message": getattr(forwarded, "channel_post", None),
        "created": unix_timestamp(date),
        "created_iso": iso_datetime(date),
        "saved_from": peer_id(getattr(forwarded, "saved_from_peer", None)),
        "saved_message": getattr(forwarded, "saved_from_msg_id", None),
        "raw": json_safe(forwarded),
    }


def reply_summary(message: Any) -> Optional[dict[str, Any]]:
    reply = getattr(message, "reply_to", None)
    if reply is None:
        return None
    story_id = getattr(reply, "story_id", None)
    source = peer_id(
        getattr(reply, "reply_to_peer_id", None)
        or getattr(reply, "peer", None)
        or getattr(reply, "user_id", None)
    )
    if story_id is not None:
        result: dict[str, Any] = {"type": "story", "source": source, "id": story_id}
    else:
        result = {
            "type": "message",
            "id": getattr(reply, "reply_to_msg_id", None),
            "source": source,
        }
    result.update(
        top_id=getattr(reply, "reply_to_top_id", None),
        forum_topic=bool(getattr(reply, "forum_topic", False)),
        quote=getattr(reply, "quote_text", None),
        quote_offset=getattr(reply, "quote_offset", None),
        quote_entities=json_safe(getattr(reply, "quote_entities", None)),
        todo_item_id=getattr(reply, "todo_item_id", None),
        raw=json_safe(reply),
    )
    return result


def message_type(message: Any) -> str:
    name = tl_name(message)
    if name == "MessageService":
        return "service"
    if name == "MessageEmpty":
        return "empty"
    return "message"


def custom_emoji_ids(value: Any) -> set[int]:
    found: set[int] = set()
    visited: set[int] = set()

    def visit(item: Any) -> None:
        if item is None or isinstance(
            item, (str, int, float, bool, bytes, dt.datetime)
        ):
            return
        object_id = id(item)
        if object_id in visited:
            return
        visited.add(object_id)
        name = tl_name(item)
        if name in {
            "MessageEntityCustomEmoji",
            "ReactionCustomEmoji",
            "TextCustomEmoji",
        }:
            document_id = getattr(item, "document_id", None)
            if document_id is not None:
                found.add(int(document_id))
            return
        field = {
            "KeyboardButtonStyle": "icon",
            "MessageActionTopicCreate": "icon_emoji_id",
            "MessageActionTopicEdit": "icon_emoji_id",
            "WebPageAttributeAiComposeTone": "emoji_id",
        }.get(name)
        if field:
            document_id = getattr(item, field, None)
            if document_id is not None:
                found.add(int(document_id))
        if isinstance(item, (list, tuple, set, frozenset)):
            for child in item:
                visit(child)
            return
        for key, child in vars(item).items() if hasattr(item, "__dict__") else []:
            if not key.startswith("_"):
                visit(child)

    visit(value)
    return found


def message_custom_emoji_ids(message: Any) -> tuple[set[int], set[int]]:
    """Return (icons, reactions) without flattening their semantic purpose."""

    reactions = custom_emoji_ids(getattr(message, "reactions", None))
    icons: set[int] = set()
    for key, value in vars(message).items() if hasattr(message, "__dict__") else []:
        if not key.startswith("_") and key != "reactions":
            icons.update(custom_emoji_ids(value))
    return icons, reactions


def nested_story_media(value: Any) -> list[Any]:
    """Find story references anywhere in a message's current TL graph."""
    found: list[Any] = []
    visited: set[int] = set()

    def visit(item: Any) -> None:
        if item is None or isinstance(
            item, (str, int, float, bool, bytes, dt.datetime)
        ):
            return
        object_id = id(item)
        if object_id in visited:
            return
        visited.add(object_id)
        if tl_name(item) in {"MessageMediaStory", "WebPageAttributeStory"}:
            found.append(item)
        if isinstance(item, (list, tuple, set, frozenset)):
            for child in item:
                visit(child)
            return
        for key, child in vars(item).items() if hasattr(item, "__dict__") else []:
            if not key.startswith("_"):
                visit(child)

    visit(value)
    return found


class AttachmentCollector:
    """Turn all known and nested current media objects into export records."""

    def __init__(
        self,
        message_id: int,
        protected: bool,
        forwarded: bool = False,
        source_chat_id: Optional[int] = None,
        source_peer: Any = None,
        message_range: Any = None,
    ) -> None:
        self.message_id = message_id
        self.protected = protected
        self.forwarded = forwarded
        self.source_chat_id = source_chat_id
        self.source_peer = source_peer
        self.message_range = message_range
        self.targets: list[DownloadTarget] = []
        self.records: list[dict[str, Any]] = []
        self._visited: set[int] = set()

    def metadata_record(
        self,
        media_type: str,
        role: str,
        value: Any,
        status: str = "metadata_only",
        attachment_subtype: Optional[str] = None,
        category_hint: Optional[str] = None,
        **extra: Any,
    ) -> None:
        record = {
            "type": media_type,
            "role": role,
            "status": status,
            **extra,
            "telegram": json_safe(value),
        }
        if attachment_subtype is not None or category_hint is not None:
            record["category"] = attachment_category_values(
                role,
                attachment_subtype or media_type,
                self.forwarded,
                category_hint,
            )
        self.records.append(record)

    def add_photo(
        self,
        photo: Any,
        role: str,
        protected: Optional[bool] = None,
        refresh_url: Optional[str] = None,
        category_hint: Optional[str] = None,
    ) -> None:
        if photo is None or tl_name(photo) in {"PhotoEmpty", "None"}:
            self.metadata_record(
                "image",
                role,
                photo,
                status="unavailable",
                attachment_subtype="image",
                category_hint=category_hint,
                reason="empty_photo",
            )
            return
        size = best_photo_size(photo)
        if size is None:
            self.metadata_record(
                "image",
                role,
                photo,
                status="unavailable",
                attachment_subtype="image",
                category_hint=category_hint,
                reason="no_photo_size",
            )
            return
        selected = photo_size_info(size)
        is_video = tl_name(size) == "VideoSize"
        subtype = "video" if is_video else "image"
        media_id = getattr(photo, "id", None)
        metadata = {
            "type": subtype,
            "role": role,
            "id": media_id,
            "hash": getattr(photo, "access_hash", None),
            "mime": "video/mp4" if is_video else "image/jpeg",
            "size": selected.get("size"),
            "width": selected.get("width"),
            "height": selected.get("height"),
            "selected_quality": selected,
            "variants": [
                photo_size_info(item)
                for item in [
                    *(getattr(photo, "sizes", None) or []),
                    *(getattr(photo, "video_sizes", None) or []),
                ]
            ],
            "telegram": json_safe(photo),
        }
        expected_size = selected.get("size")
        if tl_name(size) == "PhotoStrippedSize":
            # Telethon inflates stripped thumbnail bytes into a JPEG, so the
            # downloaded size cannot equal the compressed TL byte count.
            expected_size = None
        embedded_size = max(
            (
                item
                for item in (getattr(photo, "sizes", None) or [])
                if tl_name(item) in {"PhotoCachedSize", "PhotoStrippedSize"}
                and getattr(item, "bytes", None)
            ),
            key=lambda item: len(bytes(getattr(item, "bytes", b"") or b"")),
            default=None,
        )
        embedded_preview: Optional[bytes] = None
        embedded_preview_info: Optional[dict[str, Any]] = None
        if embedded_size is not None:
            embedded_preview = bytes(getattr(embedded_size, "bytes", b"") or b"")
            if tl_name(embedded_size) == "PhotoStrippedSize":
                try:
                    embedded_preview = utils.stripped_photo_to_jpg(embedded_preview)
                except (IndexError, TypeError, ValueError):
                    embedded_preview = None
            if embedded_preview:
                embedded_preview_info = photo_size_info(embedded_size)
        self.targets.append(
            DownloadTarget(
                obj=photo,
                kind="photo",
                subtype=subtype,
                role=role,
                message_id=self.message_id,
                cache_key=f"photo:{media_id}:{selected.get('type')}",
                extension=".mp4" if is_video else ".jpg",
                expected_size=expected_size,
                metadata=metadata,
                # A type string works for PhotoSizeProgressive too; older
                # Telethon _get_thumb versions do not accept that TL object
                # directly even though they can resolve its type.
                thumb=getattr(size, "type", None),
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                refresh_url=refresh_url,
                embedded_preview=embedded_preview,
                embedded_preview_info=embedded_preview_info,
                category_hint=category_hint,
            )
        )

        # Animated-profile/live-photo previews are a distinct source asset,
        # not a lower-quality replacement for the full still image.
        video_sizes = [
            item
            for item in (getattr(photo, "video_sizes", None) or [])
            if tl_name(item) == "VideoSize"
        ]
        if video_sizes and not is_video:
            video_size = max(
                video_sizes,
                key=lambda item: (
                    int(getattr(item, "w", 0) or 0) * int(getattr(item, "h", 0) or 0),
                    int(getattr(item, "size", 0) or 0),
                ),
            )
            video_info = photo_size_info(video_size)
            self.targets.append(
                DownloadTarget(
                    obj=photo,
                    kind="photo",
                    subtype="animated_photo",
                    role=f"{role}.animated",
                    message_id=self.message_id,
                    cache_key=f"photo:{media_id}:{video_info.get('type')}:video",
                    extension=".mp4",
                    expected_size=video_info.get("size"),
                    metadata={
                        "type": "animated_photo",
                        "role": f"{role}.animated",
                        "id": media_id,
                        "hash": getattr(photo, "access_hash", None),
                        "mime": "video/mp4",
                        "size": video_info.get("size"),
                        "width": video_info.get("width"),
                        "height": video_info.get("height"),
                        "selected_quality": video_info,
                        "telegram": json_safe(photo),
                    },
                    thumb=getattr(video_size, "type", None),
                    protected=self.protected if protected is None else protected,
                    forwarded=self.forwarded,
                    source_chat_id=self.source_chat_id,
                    source_peer=self.source_peer,
                    message_range=self.message_range,
                    refresh_url=refresh_url,
                    embedded_preview=embedded_preview,
                    embedded_preview_info=embedded_preview_info,
                    category_hint=category_hint,
                )
            )

    def add_embedded_photo_size(
        self,
        size: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = "preview",
    ) -> None:
        if tl_name(size) not in {"PhotoCachedSize", "PhotoStrippedSize"}:
            return
        data = bytes(getattr(size, "bytes", b"") or b"")
        if tl_name(size) == "PhotoStrippedSize":
            data = utils.stripped_photo_to_jpg(data)
        if not data:
            return
        digest = hashlib.sha256(data).hexdigest()
        self.targets.append(
            DownloadTarget(
                obj=data,
                kind="bytes",
                subtype="paid_media_preview",
                role=role,
                message_id=self.message_id,
                cache_key=f"embedded:{digest}",
                extension=".jpg",
                expected_size=len(data),
                metadata={
                    "type": "paid_media_preview",
                    "role": role,
                    "mime": "image/jpeg",
                    "size": len(data),
                    "selected_quality": photo_size_info(size),
                    "sha256": digest,
                    "telegram": json_safe(size),
                },
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                category_hint=category_hint,
            )
        )

    def add_document(
        self,
        document: Any,
        role: str,
        *,
        alternatives: Optional[Iterable[Any]] = None,
        protected: Optional[bool] = None,
        refresh_url: Optional[str] = None,
        category_hint: Optional[str] = None,
    ) -> None:
        candidates = [
            item
            for item in [document, *(alternatives or [])]
            if item is not None and tl_name(item) not in {"DocumentEmpty", "None"}
        ]
        if not candidates:
            self.metadata_record(
                "file",
                role,
                document,
                status="unavailable",
                attachment_subtype="file",
                category_hint=category_hint,
                reason="empty_document",
            )
            return

        video_candidates = [
            item for item in candidates if document_attributes(item).get("width")
        ]
        selected_document = (
            max(video_candidates, key=video_quality_key)
            if len(candidates) > 1 and video_candidates
            else candidates[0]
        )
        attributes = document_attributes(selected_document)
        subtype = document_subtype(selected_document, attributes)
        filename = attributes.get("filename")
        mime = getattr(selected_document, "mime_type", None)
        try:
            inferred_extension = utils.get_extension(selected_document)
        except (TypeError, AttributeError):
            inferred_extension = None
        extension = safe_extension(filename or inferred_extension, mime, ".bin")
        media_id = getattr(selected_document, "id", None)
        variants = [
            document_variant(item, selected=getattr(item, "id", None) == media_id)
            for item in candidates
        ]
        metadata = {
            "type": subtype,
            "role": role,
            "id": media_id,
            "hash": getattr(selected_document, "access_hash", None),
            "mime": mime,
            "name": filename,
            "size": getattr(selected_document, "size", None),
            "width": attributes.get("width"),
            "height": attributes.get("height"),
            "duration": attributes.get("duration"),
            "title": attributes.get("title"),
            "performer": attributes.get("performer"),
            "sticker_alt": attributes.get("sticker_alt"),
            "supports_streaming": attributes.get("supports_streaming"),
            "video_codec": attributes.get("video_codec"),
            "variants": variants,
            "telegram": json_safe(selected_document),
        }
        self.targets.append(
            DownloadTarget(
                obj=selected_document,
                kind="document",
                subtype=subtype,
                role=role,
                message_id=self.message_id,
                cache_key=f"document:{media_id}",
                extension=extension,
                expected_size=getattr(selected_document, "size", None),
                metadata=metadata,
                original_name=filename,
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                refresh_url=refresh_url,
                category_hint=category_hint,
            )
        )

        # Premium sticker/custom-emoji effects use document.video_thumbs type
        # "f" and are meaningful assets, unlike ordinary preview thumbnails.
        effects = [
            item
            for item in (getattr(selected_document, "video_thumbs", None) or [])
            if tl_name(item) == "VideoSize" and getattr(item, "type", None) == "f"
        ]
        if effects:
            effect = max(effects, key=lambda item: int(getattr(item, "size", 0) or 0))
            location = types.InputDocumentFileLocation(
                id=int(selected_document.id),
                access_hash=int(selected_document.access_hash),
                file_reference=selected_document.file_reference,
                thumb_size="f",
            )
            effect_size = int(getattr(effect, "size", 0) or 0) or None
            self.targets.append(
                DownloadTarget(
                    obj=location,
                    kind="file_location",
                    subtype="premium_sticker_effect",
                    role=f"{role}.premium_effect",
                    message_id=self.message_id,
                    cache_key=f"document:{media_id}:effect:f",
                    extension=".tgs",
                    expected_size=effect_size,
                    metadata={
                        "type": "premium_sticker_effect",
                        "role": f"{role}.premium_effect",
                        "id": media_id,
                        "mime": "application/x-tgsticker",
                        "size": effect_size,
                        "selected_quality": photo_size_info(effect),
                        "telegram": json_safe(effect),
                    },
                    protected=self.protected if protected is None else protected,
                    forwarded=self.forwarded,
                    source_chat_id=self.source_chat_id,
                    source_peer=self.source_peer,
                    message_range=self.message_range,
                    dc_id=getattr(selected_document, "dc_id", None),
                    refresh_url=refresh_url,
                    category_hint=category_hint,
                )
            )

    def add_web_document(
        self,
        document: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = None,
    ) -> None:
        url = getattr(document, "url", None)
        mime = getattr(document, "mime_type", None)
        size = getattr(document, "size", None)
        digest = hashlib.sha256((url or repr(document)).encode("utf-8")).hexdigest()[
            :20
        ]
        extension = safe_extension(url, mime, ".bin")
        metadata = {
            "type": "web_file",
            "role": role,
            "url": url,
            "mime": mime,
            "size": size,
            "telegram": json_safe(document),
        }
        self.targets.append(
            DownloadTarget(
                obj=document,
                kind="web_document",
                subtype="web_file",
                role=role,
                message_id=self.message_id,
                cache_key=f"web:{digest}",
                extension=extension,
                expected_size=size,
                metadata=metadata,
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                category_hint=category_hint,
            )
        )

    def add_contact(
        self,
        media: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = None,
    ) -> None:
        metadata = {
            "type": "contact",
            "role": role,
            "name": " ".join(
                filter(
                    None,
                    [
                        getattr(media, "first_name", None),
                        getattr(media, "last_name", None),
                    ],
                )
            ),
            "phone": getattr(media, "phone_number", None),
            "user_id": getattr(media, "user_id", None),
            "vcard": getattr(media, "vcard", None),
            "telegram": json_safe(media),
        }
        self.targets.append(
            DownloadTarget(
                obj=media,
                kind="contact",
                subtype="contact",
                role=role,
                message_id=self.message_id,
                cache_key=(
                    f"contact:{self.source_chat_id}:{self.message_id}:{len(self.targets)}"
                ),
                extension=".vcf",
                expected_size=None,
                metadata=metadata,
                original_name=metadata["name"] or metadata["phone"],
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                category_hint=category_hint,
            )
        )

    def collect_story(
        self,
        story: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = "stories",
    ) -> None:
        name = tl_name(story)
        if name != "StoryItem":
            self.metadata_record(
                "story",
                role,
                story,
                status="unavailable",
                attachment_subtype="story",
                category_hint=category_hint,
                reason=name,
            )
            return
        story_protected = (self.protected if protected is None else protected) or bool(
            getattr(story, "noforwards", False)
        )
        self.collect_media(
            getattr(story, "media", None),
            f"{role}.media",
            protected=story_protected,
            category_hint=category_hint,
        )
        music = getattr(story, "music", None)
        if music is not None:
            self.add_document(
                music,
                f"{role}.music",
                protected=story_protected,
                category_hint=category_hint,
            )
        for key, child in vars(story).items() if hasattr(story, "__dict__") else []:
            if not key.startswith("_") and key not in {"media", "music"}:
                self.discover(
                    child,
                    f"{role}.{key}",
                    protected=story_protected,
                    category_hint=category_hint,
                )

    def discover(
        self,
        value: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = None,
    ) -> None:
        if value is None or isinstance(
            value, (str, int, float, bool, bytes, dt.datetime)
        ):
            return
        object_id = id(value)
        if object_id in self._visited:
            return
        self._visited.add(object_id)
        name = tl_name(value)
        active_protection = self.protected if protected is None else protected
        if name == "Photo":
            self.add_photo(
                value,
                role,
                protected=active_protection,
                category_hint=category_hint,
            )
            return
        if name == "Document":
            self.add_document(
                value,
                role,
                protected=active_protection,
                category_hint=category_hint,
            )
            return
        if name in {"WebDocument", "WebDocumentNoProxy"}:
            self.add_web_document(
                value,
                role,
                protected=active_protection,
                category_hint=category_hint,
            )
            return
        if name.startswith("MessageMedia"):
            self.collect_media(
                value,
                role,
                protected=active_protection,
                category_hint=category_hint,
            )
            return
        if name == "MessageExtendedMedia":
            self.collect_media(
                getattr(value, "media", None),
                f"{role}.media",
                protected=active_protection,
                category_hint=category_hint,
            )
            return
        if name == "MessageExtendedMediaPreview":
            self.metadata_record(
                "paid_media_preview",
                role,
                value,
                status="unavailable",
                attachment_subtype="paid_media_preview",
                category_hint="preview",
                reason="paid_media_not_purchased",
            )
            self.add_embedded_photo_size(
                getattr(value, "thumb", None),
                f"{role}.accessible_preview",
                protected=active_protection,
                category_hint="preview",
            )
            return
        if name.startswith("StoryItem"):
            self.collect_story(
                value,
                role,
                protected=active_protection,
                category_hint=category_hint or "stories",
            )
            return
        if isinstance(value, (list, tuple, set, frozenset)):
            for index, child in enumerate(value):
                self.discover(
                    child,
                    f"{role}.{index}",
                    protected=active_protection,
                    category_hint=category_hint,
                )
            return
        for key, child in vars(value).items() if hasattr(value, "__dict__") else []:
            if not key.startswith("_"):
                self.discover(
                    child,
                    f"{role}.{key}",
                    protected=active_protection,
                    category_hint=category_hint,
                )

    def collect_media(
        self,
        media: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = None,
    ) -> None:
        if media is None:
            return
        name = tl_name(media)
        active_protection = self.protected if protected is None else protected

        if name == "MessageMediaPhoto":
            self.add_photo(
                getattr(media, "photo", None),
                f"{role}.photo",
                protected=active_protection,
                category_hint=category_hint,
            )
            live_video = getattr(media, "video", None)
            if live_video is not None:
                self.add_document(
                    live_video,
                    f"{role}.live_photo_video",
                    protected=active_protection,
                    category_hint=category_hint,
                )
            return

        if name == "MessageMediaDocument":
            self.add_document(
                getattr(media, "document", None),
                f"{role}.document",
                alternatives=getattr(media, "alt_documents", None) or [],
                protected=active_protection,
                category_hint=category_hint,
            )
            cover = getattr(media, "video_cover", None)
            if cover is not None:
                self.add_photo(
                    cover,
                    f"{role}.video_cover",
                    protected=active_protection,
                    category_hint=category_hint,
                )
            return

        if name == "MessageMediaContact":
            self.add_contact(
                media,
                role,
                protected=active_protection,
                category_hint=category_hint,
            )
            return

        if name in {"MessageMediaGeo", "MessageMediaGeoLive", "MessageMediaVenue"}:
            geo = getattr(media, "geo", None)
            self.metadata_record(
                "geo",
                role,
                media,
                latitude=getattr(geo, "lat", None),
                longitude=getattr(geo, "long", None),
                title=getattr(media, "title", None),
                address=getattr(media, "address", None),
                period=getattr(media, "period", None),
            )
            return

        if name == "MessageMediaWebPage":
            webpage = getattr(media, "webpage", None)
            refresh_url = getattr(webpage, "url", None)
            self.metadata_record(
                "web",
                role,
                media,
                link=getattr(webpage, "url", None),
                title=getattr(webpage, "title", None),
            )
            if tl_name(webpage) == "WebPage":
                webpage_photo = getattr(webpage, "photo", None)
                if webpage_photo is not None:
                    self.add_photo(
                        webpage_photo,
                        f"{role}.photo",
                        protected=active_protection,
                        refresh_url=refresh_url,
                        category_hint="preview",
                    )
                webpage_document = getattr(webpage, "document", None)
                if webpage_document is not None:
                    self.add_document(
                        webpage_document,
                        f"{role}.document",
                        protected=active_protection,
                        refresh_url=refresh_url,
                        category_hint="preview",
                    )
                self.discover(
                    getattr(webpage, "cached_page", None),
                    f"{role}.cached_page",
                    active_protection,
                    category_hint="preview",
                )
                self.discover(
                    getattr(webpage, "attributes", None),
                    f"{role}.attributes",
                    active_protection,
                    category_hint="preview",
                )
            return

        if name == "MessageMediaGame":
            game = getattr(media, "game", None)
            self.metadata_record(
                "game", role, media, title=getattr(game, "title", None)
            )
            self.discover(
                game,
                f"{role}.game",
                active_protection,
                category_hint="preview",
            )
            return

        if name == "MessageMediaInvoice":
            self.metadata_record(
                "payment",
                role,
                media,
                title=getattr(media, "title", None),
                data=getattr(media, "description", None),
                currency=getattr(media, "currency", None),
                total_amount=getattr(media, "total_amount", None),
            )
            self.discover(
                getattr(media, "photo", None),
                f"{role}.photo",
                active_protection,
                category_hint="preview",
            )
            self.discover(
                getattr(media, "extended_media", None),
                f"{role}.extended_media",
                active_protection,
                category_hint="preview",
            )
            return

        if name == "MessageMediaPaidMedia":
            self.metadata_record(
                "paid_media",
                role,
                media,
                stars_amount=getattr(media, "stars_amount", None),
            )
            for index, extended in enumerate(
                getattr(media, "extended_media", None) or []
            ):
                self.discover(
                    extended,
                    f"{role}.{index}",
                    active_protection,
                    category_hint=category_hint,
                )
            return

        if name == "MessageMediaPoll":
            poll = getattr(media, "poll", None)
            self.metadata_record(
                "poll",
                role,
                media,
                title=json_safe(getattr(poll, "question", None)),
                answers=json_safe(getattr(poll, "answers", None)),
            )
            self.discover(
                getattr(media, "attached_media", None),
                f"{role}.attached_media",
                active_protection,
                category_hint=category_hint,
            )
            for index, answer in enumerate(getattr(poll, "answers", None) or []):
                self.discover(
                    getattr(answer, "media", None),
                    f"{role}.answer.{index}",
                    active_protection,
                    category_hint=category_hint,
                )
            results = getattr(media, "results", None)
            self.discover(
                getattr(results, "solution_media", None),
                f"{role}.solution",
                active_protection,
                category_hint=category_hint,
            )
            return

        if name == "MessageMediaStory":
            story = getattr(media, "story", None)
            status = "metadata_only" if story is not None else "unavailable"
            self.metadata_record(
                "story",
                role,
                media,
                status=status,
                attachment_subtype=("story" if status == "unavailable" else None),
                category_hint=("stories" if status == "unavailable" else None),
                source=peer_id(getattr(media, "peer", None)),
                id=getattr(media, "id", None),
                mention=bool(getattr(media, "via_mention", False)),
                reason=None if story is not None else "story_not_returned_or_expired",
            )
            if story is not None:
                self.collect_story(
                    story,
                    f"{role}.story",
                    protected=active_protection,
                    category_hint=category_hint or "stories",
                )
            return

        metadata_types = {
            "MessageMediaDice": "dice",
            "MessageMediaGiveaway": "giveaway",
            "MessageMediaGiveawayResults": "giveaway_results",
            "MessageMediaToDo": "todo",
            "MessageMediaVideoStream": "video_stream",
            "MessageMediaUnsupported": "unsupported",
            "MessageMediaEmpty": "empty",
        }
        if name in metadata_types:
            status = (
                "not_downloadable"
                if name == "MessageMediaVideoStream"
                else "metadata_only"
            )
            self.metadata_record(metadata_types[name], role, media, status=status)
            return

        # Future MessageMedia constructors remain visible in JSON, and any
        # nested Photo/Document values are still found without a code update.
        self.metadata_record(name, role, media, status="metadata_only")
        for key, child in vars(media).items() if hasattr(media, "__dict__") else []:
            if not key.startswith("_"):
                self.discover(
                    child,
                    f"{role}.{key}",
                    active_protection,
                    category_hint=category_hint,
                )

    def collect_message(self, message: Any, emoji_documents: Mapping[int, Any]) -> None:
        self.collect_media(getattr(message, "media", None), "message.media")
        reply = getattr(message, "reply_to", None)
        self.collect_media(
            getattr(reply, "reply_media", None),
            "message.reply_media",
            category_hint="preview",
        )
        action = getattr(message, "action", None)
        action_name = tl_name(action)
        if action_name in {
            "MessageActionChatEditPhoto",
            "MessageActionSuggestProfilePhoto",
        }:
            action_category = "avatars"
        elif action_name == "MessageActionSetChatWallPaper":
            action_category = "wallpapers"
        else:
            action_category = "other"
        self.discover(
            action,
            "message.action",
            category_hint=action_category,
        )
        self.discover(
            getattr(message, "rich_message", None),
            "message.rich_message",
            category_hint="preview",
        )

        icon_ids, reaction_ids = message_custom_emoji_ids(message)
        for purpose, document_ids in (
            ("custom_emoji", icon_ids),
            ("reaction_custom_emoji", reaction_ids),
        ):
            for document_id in sorted(document_ids):
                role = f"message.{purpose}.{document_id}"
                document = emoji_documents.get(document_id)
                if document is None:
                    self.metadata_record(
                        "custom_emoji",
                        role,
                        None,
                        status="unavailable",
                        attachment_subtype="custom_emoji",
                        category_hint=(
                            "reactions"
                            if purpose == "reaction_custom_emoji"
                            else "icons"
                        ),
                        id=document_id,
                        reason="custom_emoji_document_not_returned",
                    )
                else:
                    self.add_document(
                        document,
                        role,
                        protected=self.protected,
                        category_hint=(
                            "reactions"
                            if purpose == "reaction_custom_emoji"
                            else "icons"
                        ),
                    )


class JsonExportWriter:
    def __init__(
        self, final_path: Path, header: Mapping[str, Any], overwrite: bool
    ) -> None:
        self.final_path = final_path
        self.partial_path = final_path.with_suffix(final_path.suffix + ".part")
        if final_path.exists() and not overwrite:
            raise FileExistsError(
                f"{final_path} already exists; use --overwrite to replace it after a complete export"
            )
        self.partial_path.unlink(missing_ok=True)
        self.file = self.partial_path.open("w", encoding="utf-8")
        self.first = True
        self.file.write("{\n")
        for key, value in header.items():
            self.file.write(json.dumps(str(key), ensure_ascii=False))
            self.file.write(": ")
            self.file.write(
                json.dumps(json_safe(value), ensure_ascii=False, separators=(",", ":"))
            )
            self.file.write(",\n")
        self.file.write('"messages": [\n')

    def write_message(self, message: Mapping[str, Any]) -> None:
        if not self.first:
            self.file.write(",\n")
        self.file.write(
            json.dumps(json_safe(message), ensure_ascii=False, separators=(",", ":"))
        )
        self.first = False

    def finish(
        self,
        peers: Mapping[str, Any],
        peer_avatars: Iterable[Mapping[str, Any]],
        summary: Mapping[str, Any],
    ) -> None:
        self.file.write("\n],\n")
        self.file.write('"peers": ')
        self.file.write(
            json.dumps(json_safe(peers), ensure_ascii=False, separators=(",", ":"))
        )
        self.file.write(",\n")
        self.file.write('"peer_avatars": ')
        self.file.write(
            json.dumps(
                json_safe(list(peer_avatars)),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        self.file.write(",\n")
        self.file.write('"summary": ')
        self.file.write(
            json.dumps(json_safe(summary), ensure_ascii=False, separators=(",", ":"))
        )
        self.file.write("\n}\n")
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()
        os.replace(self.partial_path, self.final_path)

    def close_incomplete(self) -> None:
        if not self.file.closed:
            self.file.flush()
            self.file.close()


class ChatExporter:
    def __init__(
        self,
        base_client: TelegramClient,
        entity: Any,
        input_peer: Any,
        output_dir: Path,
        args: argparse.Namespace,
    ) -> None:
        self.base_client = base_client
        self.entity = entity
        self.input_peer = input_peer
        self.chat_id = marked_chat_id(entity)
        self.output_dir = output_dir
        self.files_dir = output_dir / "files"
        self.error_log_path = output_dir / "media-errors.jsonl"
        self.args = args
        self.pacer = Pacer(
            args.history_delay,
            args.metadata_delay,
            args.media_delay,
            args.chunk_delay,
            args.jitter,
            args.flood_reserve,
        )
        self.entity_protected = bool(getattr(entity, "noforwards", False))
        self.chat_protected = self.entity_protected
        self.private_protection_my = False
        self.private_protection_peer = False
        self.history_sources = [
            HistorySource(
                input_peer=input_peer, marked_id=self.chat_id, label="selected_chat"
            )
        ]
        self.history_complete = True
        self.history_limitations: list[str] = []
        self.migration: Optional[dict[str, Any]] = None
        self.monoforum_scope: Optional[str] = None
        self.monoforum_admin_export = False
        self.search_own_messages = False
        self.stats = ExportStats()
        self.media_cache: dict[str, dict[str, Any]] = {}
        self.media_asset_cache: dict[str, dict[str, Any]] = {}
        self.migrated_legacy_files: set[Path] = set()
        self.referenced_files: set[str] = set()
        self.emoji_documents: dict[int, Any] = {}
        self.unresolved_emoji: set[int] = set()
        self.story_cache: dict[tuple[Optional[int], int], Any] = {}
        self.unresolved_stories: set[tuple[Optional[int], int]] = set()
        self.available_effects_loaded = False
        self.message_effects: dict[int, dict[str, Any]] = {}
        self.seen_message_ids: set[tuple[int, int]] = set()
        self.peers: dict[str, Any] = {str(self.chat_id): json_safe(entity)}
        self.peer_entities: dict[int, Any] = {self.chat_id: entity}
        self.peer_avatar_records: list[dict[str, Any]] = []

    async def rpc(self, factory: Callable[[], Any], label: str) -> Any:
        attempts = 0
        while True:
            try:
                return await factory()
            except (errors.FloodWaitError, errors.FloodPremiumWaitError) as exc:
                self.stats.flood_waits += 1
                await self.pacer.flood_wait(int(getattr(exc, "seconds", 0)), label)
            except (
                errors.ServerError,
                errors.TimedOutError,
                asyncio.TimeoutError,
                OSError,
            ) as exc:
                attempts += 1
                self.stats.transient_retries += 1
                if attempts > self.args.retries:
                    raise
                delay = min(60.0, 2.0**attempts) + random.uniform(0.0, self.args.jitter)
                print(
                    f"Transient {type(exc).__name__} during {label}; retrying in {delay:.1f}s",
                    flush=True,
                )
                await asyncio.sleep(delay)

    def remember_peers(self, response: Any) -> None:
        for entity in [
            *(getattr(response, "users", None) or []),
            *(getattr(response, "chats", None) or []),
        ]:
            marked_id = peer_id(entity)
            if marked_id is not None:
                self.peers.setdefault(str(marked_id), json_safe(entity))
                if (
                    marked_id not in self.peer_entities
                    or getattr(entity, "photo", None) is not None
                ):
                    self.peer_entities[marked_id] = entity

    async def prepare(self) -> None:
        """Resolve protection and migration metadata before opening takeout."""
        name = tl_name(self.entity)
        if name == "User":
            result = await self.rpc(
                lambda: self.base_client(
                    functions.users.GetFullUserRequest(id=self.input_peer)
                ),
                "private-chat metadata",
            )
            self.stats.metadata_requests += 1
            self.remember_peers(result)
            full_user = getattr(result, "full_user", None)
            self.private_protection_my = bool(
                getattr(full_user, "noforwards_my_enabled", False)
            )
            self.private_protection_peer = bool(
                getattr(full_user, "noforwards_peer_enabled", False)
            )
            self.chat_protected = (
                self.chat_protected
                or self.private_protection_my
                or self.private_protection_peer
            )
            await self.pacer.after_metadata()
            return

        if name in {"Channel", "ChannelForbidden"}:
            try:
                result = await self.rpc(
                    lambda: self.base_client(
                        functions.channels.GetFullChannelRequest(
                            channel=self.input_peer
                        )
                    ),
                    "channel metadata",
                )
            except errors.ChannelPrivateError:
                # Telegram's official export fallback can recover only this
                # user's own messages in an inaccessible/left private channel.
                self.search_own_messages = True
                self.history_complete = False
                self.history_limitations.append(
                    "The channel became private/inaccessible; only this user's own messages could be searched."
                )
                await self.pacer.after_metadata()
                return
            self.stats.metadata_requests += 1
            self.remember_peers(result)
            full_chat = getattr(result, "full_chat", None)
            if getattr(self.entity, "monoforum", False):
                rights = getattr(self.entity, "admin_rights", None)
                self.monoforum_admin_export = bool(
                    getattr(self.entity, "creator", False)
                    or getattr(rights, "manage_direct_messages", False)
                )
                self.monoforum_scope = (
                    "all_accessible_topics"
                    if self.monoforum_admin_export
                    else "own_topic_only"
                )
                if not self.monoforum_admin_export:
                    self.history_limitations.append(
                        "This account cannot manage monoforum direct messages; Telegram exposes only its own topic."
                    )
            old_chat_id = getattr(full_chat, "migrated_from_chat_id", None)
            if old_chat_id is not None:
                old_peer = types.InputPeerChat(int(old_chat_id))
                old_marked_id = int(utils.get_peer_id(types.PeerChat(int(old_chat_id))))
                boundary = getattr(full_chat, "migrated_from_max_id", None)
                self.history_sources.append(
                    HistorySource(
                        input_peer=old_peer,
                        marked_id=old_marked_id,
                        label="migrated_from_basic_group",
                        migration_boundary=int(boundary)
                        if boundary is not None
                        else None,
                    )
                )
                self.migration = {
                    "from_chat_id": old_marked_id,
                    "to_chat_id": self.chat_id,
                    "from_max_message_id": boundary,
                }
            await self.pacer.after_metadata()
            return

        if name in {"Chat", "ChatForbidden"}:
            migrated_to = getattr(self.entity, "migrated_to", None)
            if migrated_to is not None:
                current_entity = await self.rpc(
                    lambda: self.base_client.get_entity(migrated_to),
                    "migrated supergroup metadata",
                )
                self.stats.metadata_requests += 1
                current_peer = await self.base_client.get_input_entity(current_entity)
                current_marked_id = marked_chat_id(current_entity)
                self.entity_protected = self.entity_protected or bool(
                    getattr(current_entity, "noforwards", False)
                )
                self.chat_protected = self.chat_protected or self.entity_protected
                self.peers.setdefault(str(current_marked_id), json_safe(current_entity))
                self.peer_entities.setdefault(current_marked_id, current_entity)
                old_source = self.history_sources[0]
                old_source.label = "migrated_from_basic_group"
                self.history_sources = [
                    HistorySource(
                        input_peer=current_peer,
                        marked_id=current_marked_id,
                        label="migrated_to_supergroup",
                    ),
                    old_source,
                ]
                self.migration = {
                    "from_chat_id": self.chat_id,
                    "to_chat_id": current_marked_id,
                    "from_max_message_id": None,
                }
                await self.pacer.after_metadata()

    async def resolve_custom_emojis(self, api: Any, messages: Iterable[Any]) -> None:
        wanted: set[int] = set()
        for message in messages:
            wanted.update(custom_emoji_ids(message))
        pending = sorted(wanted - self.emoji_documents.keys() - self.unresolved_emoji)
        for batch in chunks(pending, CUSTOM_EMOJI_BATCH_SIZE):
            try:
                documents = await self.rpc(
                    lambda batch=batch: api(
                        functions.messages.GetCustomEmojiDocumentsRequest(
                            document_id=batch
                        )
                    ),
                    "custom emoji lookup",
                )
                self.stats.metadata_requests += 1
                returned = {int(document.id): document for document in documents}
                self.emoji_documents.update(returned)
                self.unresolved_emoji.update(set(batch) - returned.keys())
            except (
                errors.RPCError,
                asyncio.TimeoutError,
                OSError,
                ValueError,
                TypeError,
            ) as exc:
                print(f"Custom emoji lookup failed: {error_text(exc)}", flush=True)
                self.stats.metadata_failures += 1
                self.unresolved_emoji.update(batch)
            await self.pacer.after_metadata()

    async def load_available_effects(self, api: Any, force: bool = False) -> bool:
        if self.available_effects_loaded and not force:
            return True
        loaded = False
        try:
            response = await self.rpc(
                lambda: api(functions.messages.GetAvailableEffectsRequest(hash=0)),
                "message effect lookup",
            )
            self.stats.metadata_requests += 1
            if tl_name(response) == "AvailableEffectsNotModified":
                raise RuntimeError(
                    "Telegram returned no message-effect catalog for hash=0"
                )
            documents = {
                int(document.id): document
                for document in (getattr(response, "documents", None) or [])
            }
            effects: dict[int, dict[str, Any]] = {}
            for effect in getattr(response, "effects", None) or []:
                assets = []
                for role, field_name in (
                    ("static_icon", "static_icon_id"),
                    ("sticker", "effect_sticker_id"),
                    ("animation", "effect_animation_id"),
                ):
                    document_id = getattr(effect, field_name, None)
                    if document_id is not None and int(document_id) in documents:
                        assets.append((role, documents[int(document_id)]))
                effects[int(effect.id)] = {
                    "definition": effect,
                    "assets": assets,
                }
            self.message_effects = effects
            self.available_effects_loaded = True
            loaded = True
        except (errors.RPCError, asyncio.TimeoutError, OSError, RuntimeError) as exc:
            self.stats.metadata_failures += 1
            print(f"Message effect lookup failed: {error_text(exc)}", flush=True)
        finally:
            await self.pacer.after_metadata()
        return loaded

    async def resolve_message_effects(self, api: Any, messages: Iterable[Any]) -> None:
        if any(getattr(message, "effect", None) is not None for message in messages):
            await self.load_available_effects(api)

    def collect_message_effect(
        self,
        collector: AttachmentCollector,
        message: Any,
    ) -> None:
        effect_id = getattr(message, "effect", None)
        if effect_id is None:
            return
        effect = self.message_effects.get(int(effect_id))
        if effect is None:
            collector.metadata_record(
                "message_effect",
                "message.effect",
                None,
                status="unavailable",
                attachment_subtype="message_effect",
                category_hint="effects",
                id=effect_id,
                reason="message_effect_catalog_entry_not_returned",
            )
            return
        collector.metadata_record(
            "message_effect",
            "message.effect",
            effect["definition"],
            id=effect_id,
        )
        for role, document in effect["assets"]:
            start = len(collector.targets)
            collector.add_document(
                document,
                f"message.effect.{role}",
                protected=collector.protected,
            )
            for target in collector.targets[start:]:
                target.metadata["effect_id"] = effect_id

    async def list_monoforum_topics(self, api: Any) -> list[HistorySource]:
        """Enumerate every admin-visible direct-message topic in a monoforum."""
        topics: list[HistorySource] = []
        seen: set[int] = set()
        offset_date: Optional[dt.datetime] = None
        offset_id = 0
        previous_boundary: Optional[tuple[Optional[dt.datetime], int]] = None

        while True:
            response = await self.rpc(
                lambda: api(
                    functions.messages.GetSavedDialogsRequest(
                        offset_date=offset_date,
                        offset_id=offset_id,
                        offset_peer=types.InputPeerEmpty(),
                        limit=HISTORY_PAGE_SIZE,
                        hash=0,
                        exclude_pinned=None,
                        parent_peer=self.input_peer,
                    )
                ),
                "monoforum topic list",
            )
            self.stats.metadata_requests += 1
            await self.pacer.after_metadata()

            dialogs = list(getattr(response, "dialogs", None) or [])
            if not dialogs:
                if tl_name(response) == "SavedDialogsNotModified":
                    raise RuntimeError(
                        "Telegram returned an unenumerable monoforum topic list"
                    )
                break

            entities = {
                peer_id(entity): entity
                for entity in [
                    *(getattr(response, "users", None) or []),
                    *(getattr(response, "chats", None) or []),
                ]
                if peer_id(entity) is not None
            }
            self.remember_peers(response)
            top_messages = {
                int(message.id): message
                for message in (getattr(response, "messages", None) or [])
                if int(getattr(message, "id", 0) or 0) > 0
            }
            last_boundary: Optional[tuple[Optional[dt.datetime], int]] = None

            for dialog in dialogs:
                if tl_name(dialog) != "MonoForumDialog":
                    continue
                topic_id = peer_id(getattr(dialog, "peer", None))
                if topic_id is None:
                    raise RuntimeError(
                        "Telegram returned a monoforum topic without a peer ID"
                    )
                entity = entities.get(topic_id)
                if entity is None:
                    raise RuntimeError(
                        f"Telegram omitted the entity/access hash for monoforum topic {topic_id}"
                    )
                topic_peer = utils.get_input_peer(entity)
                top_message_id = int(getattr(dialog, "top_message", 0) or 0)
                top_message = top_messages.get(top_message_id)
                top_date = getattr(top_message, "date", None)
                if topic_id not in seen:
                    seen.add(topic_id)
                    topics.append(
                        HistorySource(
                            input_peer=self.input_peer,
                            marked_id=self.chat_id,
                            label="monoforum_topic",
                            history_peer=topic_peer,
                            parent_peer=self.input_peer,
                            topic_peer_id=topic_id,
                            topic_top_message=top_message_id,
                            topic_dialog=dialog,
                            topic_entity=entity,
                        )
                    )
                if top_message_id > 0 and top_date is not None:
                    last_boundary = (top_date, top_message_id)

            if (
                len(dialogs) < HISTORY_PAGE_SIZE
                or tl_name(response) != "SavedDialogsSlice"
            ):
                break
            if last_boundary is None or last_boundary == previous_boundary:
                raise RuntimeError("Monoforum topic pagination stopped advancing")
            previous_boundary = last_boundary
            offset_date, offset_id = last_boundary

        return topics

    async def hydrate_stories(self, api: Any, message: Any) -> None:
        grouped: dict[tuple[Optional[int], int], list[Any]] = {}
        for media in nested_story_media(message):
            if getattr(media, "story", None) is not None:
                continue
            story_id = int(getattr(media, "id", 0) or 0)
            key = (peer_id(getattr(media, "peer", None)), story_id)
            if story_id <= 0:
                continue
            if key in self.story_cache:
                media.story = self.story_cache[key]
                continue
            if key in self.unresolved_stories:
                continue
            grouped.setdefault(key, []).append(media)

        for (_marked_peer, story_id), references in grouped.items():
            media = references[0]
            try:
                # Resolve through the active API proxy so any cache miss is
                # also wrapped by invokeWithTakeout in takeout mode.
                story_peer = await self.rpc(
                    lambda media=media: api.get_input_entity(
                        getattr(media, "peer", None)
                    ),
                    "story peer resolution",
                )
                await self.pacer.after_metadata()
                result = await self.rpc(
                    lambda story_peer=story_peer, story_id=story_id: api(
                        functions.stories.GetStoriesByIDRequest(
                            peer=story_peer,
                            id=[story_id],
                        )
                    ),
                    "story lookup",
                )
                self.stats.metadata_requests += 1
                for story in getattr(result, "stories", None) or []:
                    if int(getattr(story, "id", 0) or 0) == story_id:
                        key = (_marked_peer, story_id)
                        self.story_cache[key] = story
                        for reference in references:
                            reference.story = story
                        break
                else:
                    self.unresolved_stories.add((_marked_peer, story_id))
            except (
                errors.RPCError,
                asyncio.TimeoutError,
                OSError,
                ValueError,
                TypeError,
            ) as exc:
                # The attachment record explicitly says that an expired or
                # inaccessible story was unavailable.
                print(f"Story {story_id} is unavailable: {error_text(exc)}", flush=True)
                self.unresolved_stories.add((_marked_peer, story_id))
            finally:
                # Pace failed/empty lookups too; a run of expired stories must
                # not become an unthrottled request burst.
                await self.pacer.after_metadata()

    def target_filename(self, target: DownloadTarget, ordinal: int) -> str:
        if target.kind == "profile_photo":
            owner = sanitize_component(
                str(target.metadata.get("owner_type") or "peer"), "peer", 24
            )
            photo_id = target.metadata.get("id")
            return f"{target.source_chat_id}_{photo_id}_{owner}_avatar.jpg"
        if target.original_name:
            original = sanitize_component(target.original_name, target.subtype)
            stem = sanitize_component(Path(original).stem, target.subtype, 40)
        else:
            stem = sanitize_component(target.role.replace(".", "_"), target.subtype, 40)
        media_id = target.metadata.get("id")
        id_part = f"_{media_id}" if media_id is not None else ""
        source_part = str(
            target.source_chat_id if target.source_chat_id is not None else self.chat_id
        )
        return f"{source_part}_{target.message_id}_{ordinal:02d}{id_part}_{stem}{target.extension}"

    def save_embedded_preview(
        self, target: DownloadTarget, final_path: Path
    ) -> Optional[dict[str, Any]]:
        if not target.embedded_preview:
            return None
        preview_path = final_path.with_name(f"{final_path.stem}_embedded_preview.jpg")
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        partial_path = preview_path.with_suffix(preview_path.suffix + ".part")
        partial_path.write_bytes(target.embedded_preview)
        os.replace(partial_path, preview_path)
        relative_path = preview_path.relative_to(self.output_dir).as_posix()
        self.referenced_files.add(relative_path)
        return {
            "status": "downloaded_embedded_preview",
            "category": attachment_category(target),
            "file": relative_path,
            "downloaded_size": len(target.embedded_preview),
            "quality": target.embedded_preview_info,
        }

    def log_media_issue(
        self,
        target: DownloadTarget,
        record: Mapping[str, Any],
        relative_path: str,
    ) -> None:
        entry = {
            "at": iso_datetime(utc_now()),
            "chat_id": self.chat_id,
            "source_chat_id": target.source_chat_id,
            "message_id": target.message_id,
            "role": target.role,
            "category": record.get("category"),
            "kind": target.kind,
            "cache_key": target.cache_key,
            "media_id": target.metadata.get("id"),
            "source_url": target.refresh_url,
            "intended_file": relative_path,
            "status": record.get("status"),
            "reason": record.get("reason"),
            "error_type": record.get("error_type"),
            "error": record.get("error"),
            "attempts": record.get("attempts"),
            "file_reference_refresh": record.get("file_reference_refresh"),
            "fallback": record.get("fallback"),
        }
        with self.error_log_path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(json_safe(entry), ensure_ascii=False) + "\n")

    async def refresh_target(
        self,
        api: Any,
        target: DownloadTarget,
        diagnostic: dict[str, Any],
    ) -> Optional[DownloadTarget]:
        diagnostic.update(
            strategy="source_refetch",
            file_reference_before=file_reference_fingerprint(target.obj),
            steps=[],
        )
        try:
            if target.kind == "profile_photo":
                fresh_entity = await self.rpc(
                    lambda: self.base_client.get_entity(
                        target.source_peer or target.obj
                    ),
                    f"refresh peer avatar {target.source_chat_id}",
                )
                await self.pacer.after_metadata()
                diagnostic["steps"].append(
                    {
                        "method": "get_entity",
                        "response_type": tl_name(fresh_entity),
                    }
                )
                refreshed = copy.copy(target)
                refreshed.obj = fresh_entity
                return refreshed
            if target.refresh_url:
                preview = await self.rpc(
                    lambda: self.base_client(
                        functions.messages.GetWebPagePreviewRequest(
                            message=target.refresh_url
                        )
                    ),
                    f"refresh web preview for message {target.message_id}",
                )
                self.stats.metadata_requests += 1
                await self.pacer.after_metadata()
                preview_media = getattr(preview, "media", None)
                webpage = getattr(preview_media, "webpage", None)
                diagnostic["steps"].append(
                    {
                        "method": "messages.getWebPagePreview",
                        "media_type": tl_name(preview_media),
                        "webpage_type": tl_name(webpage),
                    }
                )
                if tl_name(webpage) == "WebPage":
                    collector = AttachmentCollector(
                        target.message_id,
                        target.protected,
                        forwarded=target.forwarded,
                        source_chat_id=target.source_chat_id,
                        source_peer=target.source_peer,
                        message_range=target.message_range,
                    )
                    collector.collect_media(preview_media, "message.media")
                    candidate = next(
                        (
                            item
                            for item in collector.targets
                            if item.cache_key == target.cache_key
                        ),
                        None,
                    )
                    if candidate is not None:
                        return candidate

            if "story" in target.role.lower():
                # Force stories.getStoriesByID to supply a new file_reference
                # instead of reusing the in-run hydrated StoryItem cache.
                self.story_cache.clear()
                self.unresolved_stories.clear()
            if target.role.startswith("message.effect."):
                if not await self.load_available_effects(api, force=True):
                    return None
                effect_id = int(target.metadata.get("effect_id") or 0)
                effect = self.message_effects.get(effect_id)
                if effect is None:
                    return None
                collector = AttachmentCollector(
                    target.message_id,
                    target.protected,
                    forwarded=target.forwarded,
                    source_chat_id=target.source_chat_id,
                    source_peer=target.source_peer,
                    message_range=target.message_range,
                )
                for role, document in effect["assets"]:
                    start = len(collector.targets)
                    collector.add_document(
                        document,
                        f"message.effect.{role}",
                        protected=target.protected,
                    )
                    for candidate in collector.targets[start:]:
                        candidate.metadata["effect_id"] = effect_id
                return next(
                    (
                        item
                        for item in collector.targets
                        if item.cache_key == target.cache_key
                    ),
                    None,
                )
            if target.role.startswith(
                ("message.custom_emoji.", "message.reaction_custom_emoji.")
            ):
                document_id = int(target.metadata.get("id") or 0)
                documents = await self.rpc(
                    lambda: api(
                        functions.messages.GetCustomEmojiDocumentsRequest(
                            document_id=[document_id]
                        )
                    ),
                    f"refresh custom emoji {document_id}",
                )
                self.stats.metadata_requests += 1
                await self.pacer.after_metadata()
                if not documents:
                    return None
                document = documents[0]
                self.emoji_documents[document_id] = document
                collector = AttachmentCollector(
                    target.message_id,
                    target.protected,
                    forwarded=target.forwarded,
                    source_chat_id=target.source_chat_id,
                    source_peer=target.source_peer,
                    message_range=target.message_range,
                )
                collector.add_document(
                    document, target.role, protected=target.protected
                )
                return next(
                    (
                        item
                        for item in collector.targets
                        if item.cache_key == target.cache_key
                    ),
                    None,
                )

            source_peer = target.source_peer or self.input_peer
            input_message = types.InputMessageID(int(target.message_id))
            if tl_name(source_peer) == "InputPeerChannel":
                query: Any = functions.channels.GetMessagesRequest(
                    channel=utils.get_input_channel(source_peer),
                    id=[input_message],
                )
            else:
                query = functions.messages.GetMessagesRequest(id=[input_message])
            if target.message_range is not None:
                query = functions.InvokeWithMessagesRangeRequest(
                    range=target.message_range,
                    query=query,
                )
            response = await self.rpc(
                lambda: api(query),
                f"refresh message {target.message_id}",
            )
            self.stats.metadata_requests += 1
            await self.pacer.after_metadata()
            diagnostic["steps"].append(
                {
                    "method": (
                        "channels.getMessages"
                        if tl_name(source_peer) == "InputPeerChannel"
                        else "messages.getMessages"
                    ),
                    "response_type": tl_name(response),
                }
            )
            fresh = next(iter(getattr(response, "messages", None) or []), None)
            if fresh is None:
                return None
            await self.hydrate_stories(api, fresh)
            collector = AttachmentCollector(
                target.message_id,
                target.protected,
                forwarded=target.forwarded,
                source_chat_id=target.source_chat_id,
                source_peer=source_peer,
                message_range=target.message_range,
            )
            collector.collect_message(fresh, self.emoji_documents)
            self.collect_message_effect(collector, fresh)
            for candidate in collector.targets:
                if candidate.cache_key == target.cache_key:
                    return candidate
        except (
            errors.RPCError,
            asyncio.TimeoutError,
            OSError,
            ValueError,
            TypeError,
        ) as exc:
            diagnostic.update(
                result="refresh_error",
                error_type=type(exc).__name__,
                error=error_text(exc),
            )
            return None
        diagnostic.setdefault("result", "source_no_longer_returns_media")
        return None

    async def download_target(
        self, api: Any, target: DownloadTarget, ordinal: int
    ) -> dict[str, Any]:
        record = copy.deepcopy(target.metadata)
        category = attachment_category(target)
        record["category"] = category
        if target.protected:
            record.update(status="protected", reason="telegram_content_protection")
            return record

        if self.args.max_file_size and target.expected_size is not None:
            if int(target.expected_size) > self.args.max_file_size:
                record.update(
                    status="skipped_limit",
                    reason="larger_than_max_file_size",
                    max_file_size=self.args.max_file_size,
                )
                return record

        filename = self.target_filename(target, ordinal)
        final_path = self.files_dir / category / filename
        final_path.parent.mkdir(parents=True, exist_ok=True)
        relative_path = final_path.relative_to(self.output_dir).as_posix()
        cache_slot = f"{category}\0{target.cache_key}"

        def usable_file(path: Path) -> bool:
            if path.is_symlink() or not path.is_file():
                return False
            size = path.stat().st_size
            return (
                target.expected_size is None and size > 0
            ) or size == target.expected_size

        def remember_asset(cache: dict[str, Any]) -> None:
            self.media_cache[cache_slot] = cache
            self.media_asset_cache.setdefault(target.cache_key, cache)

        def clone_file(source: Path, destination: Path) -> None:
            temporary = destination.with_suffix(destination.suffix + ".reuse.part")
            temporary.unlink(missing_ok=True)
            try:
                os.link(source, temporary)
            except OSError:
                shutil.copy2(source, temporary)
            os.replace(temporary, destination)

        cached = self.media_cache.get(cache_slot)
        if cached:
            cached_path = self.output_dir / str(cached["file"])
            if usable_file(cached_path):
                self.referenced_files.add(str(cached["file"]))
                record.update(
                    status="reused",
                    file=cached["file"],
                    downloaded_size=cached["downloaded_size"],
                    reused_from=cached.get("first_message"),
                )
                return record

        if usable_file(final_path):
            existing_size = final_path.stat().st_size
            cache = {
                "file": relative_path,
                "downloaded_size": existing_size,
                "first_message": target.message_id,
            }
            remember_asset(cache)
            self.referenced_files.add(relative_path)
            record.update(status="existing", **cache)
            return record

        # Preserve crash consistency with an older completed JSON: clone its
        # flat file now and let post-publication pruning remove the old link.
        for legacy_path in (
            self.files_dir / filename,
            self.files_dir / "legacy" / filename,
        ):
            if usable_file(legacy_path):
                clone_file(legacy_path, final_path)
                self.migrated_legacy_files.add(legacy_path)
                cache = {
                    "file": relative_path,
                    "downloaded_size": final_path.stat().st_size,
                    "first_message": target.message_id,
                }
                remember_asset(cache)
                self.referenced_files.add(relative_path)
                record.update(
                    status="existing",
                    migrated_from=legacy_path.relative_to(
                        self.output_dir
                    ).as_posix(),
                    **cache,
                )
                return record

        asset = self.media_asset_cache.get(target.cache_key)
        if asset:
            asset_path = self.output_dir / str(asset["file"])
            if usable_file(asset_path):
                clone_file(asset_path, final_path)
                cache = {
                    "file": relative_path,
                    "downloaded_size": final_path.stat().st_size,
                    "first_message": target.message_id,
                }
                remember_asset(cache)
                self.referenced_files.add(relative_path)
                record.update(
                    status="reused",
                    reused_from=asset.get("first_message"),
                    reused_asset_from=asset["file"],
                    **cache,
                )
                return record

        partial_path = final_path.with_suffix(final_path.suffix + ".part")
        current_target = target
        attempts = 0
        reference_refreshes: list[dict[str, Any]] = []
        while True:
            partial_path.unlink(missing_ok=True)
            try:

                async def pace_chunk(_downloaded: int, _total: int) -> None:
                    await self.pacer.after_chunk()

                if current_target.kind == "bytes":
                    partial_path.write_bytes(bytes(current_target.obj))
                    result: Any = str(partial_path)
                elif current_target.kind == "contact":
                    partial_path.write_bytes(contact_vcard(current_target.obj))
                    result = str(partial_path)
                elif current_target.kind == "profile_photo":
                    result = await self.base_client.download_profile_photo(
                        current_target.obj,
                        file=str(partial_path),
                        download_big=True,
                    )
                elif current_target.kind == "web_document":
                    timeout = aiohttp.ClientTimeout(
                        total=None,
                        sock_connect=60,
                        sock_read=60,
                    )
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(
                            current_target.obj.url,
                            headers={"Accept-Encoding": "identity"},
                        ) as response:
                            response.raise_for_status()
                            with partial_path.open("wb") as output:
                                async for chunk in response.content.iter_chunked(
                                    512 * 1024
                                ):
                                    output.write(chunk)
                                    await self.pacer.after_chunk()
                    result = str(partial_path)
                elif current_target.kind == "file_location":
                    await api.download_file(
                        current_target.obj,
                        file=str(partial_path),
                        file_size=current_target.expected_size,
                        progress_callback=pace_chunk,
                        dc_id=current_target.dc_id,
                    )
                    result = str(partial_path)
                else:
                    result = await api.download_media(
                        current_target.obj,
                        file=str(partial_path),
                        thumb=current_target.thumb,
                        progress_callback=pace_chunk,
                    )
                if result is None or not partial_path.is_file():
                    raise RuntimeError("Telegram returned no downloadable file")
                actual_size = partial_path.stat().st_size
                if (
                    current_target.expected_size is not None
                    and actual_size != current_target.expected_size
                ):
                    raise RuntimeError(
                        f"downloaded {actual_size} bytes, expected {current_target.expected_size}"
                    )
                if actual_size == 0:
                    raise RuntimeError("downloaded file is empty")
                os.replace(partial_path, final_path)
                cache = {
                    "file": relative_path,
                    "downloaded_size": actual_size,
                    "first_message": target.message_id,
                }
                remember_asset(cache)
                self.referenced_files.add(relative_path)
                record.update(status="downloaded", **cache)
                if attempts:
                    record["attempts"] = attempts
                if reference_refreshes:
                    record["file_reference_refresh"] = reference_refreshes
                print(f"Downloaded {relative_path} ({actual_size} bytes)", flush=True)
                if target.kind != "contact":
                    await self.pacer.after_media()
                return record

            except (errors.FloodWaitError, errors.FloodPremiumWaitError) as exc:
                self.stats.flood_waits += 1
                await self.pacer.flood_wait(
                    int(getattr(exc, "seconds", 0)), f"media {target.role}"
                )
            except Exception as exc:
                attempts += 1
                if is_file_reference_error(exc):
                    diagnostic: dict[str, Any] = {
                        "attempt": len(reference_refreshes) + 1,
                        "trigger_error_type": type(exc).__name__,
                    }
                    if len(reference_refreshes) >= 2:
                        diagnostic.update(
                            result="refresh_limit_reached",
                            file_reference_before=file_reference_fingerprint(
                                current_target.obj
                            ),
                            steps=[],
                        )
                        refreshed = None
                    else:
                        self.stats.file_reference_refreshes += 1
                        refreshed = await self.refresh_target(
                            api, current_target, diagnostic
                        )
                    if refreshed is not None:
                        before = diagnostic.get("file_reference_before")
                        after = file_reference_fingerprint(refreshed.obj)
                        diagnostic["file_reference_after"] = after
                        if after is not None and after != before:
                            diagnostic["result"] = "refreshed"
                            self.stats.file_reference_refresh_successes += 1
                            reference_refreshes.append(diagnostic)
                            current_target = refreshed
                            print(
                                f"Refreshed expired file reference for message "
                                f"{target.message_id} {target.role}; retrying immediately",
                                flush=True,
                            )
                            continue
                        diagnostic["result"] = "unchanged_file_reference"
                    else:
                        diagnostic.setdefault(
                            "result", "source_no_longer_returns_media"
                        )
                    reference_refreshes.append(diagnostic)
                    partial_path.unlink(missing_ok=True)
                    refresh_failed = diagnostic.get("result") == "refresh_error"
                    fallback = self.save_embedded_preview(target, final_path)
                    record.update(
                        status="failed" if refresh_failed else "unavailable",
                        reason=(
                            "file_reference_refresh_failed"
                            if refresh_failed
                            else "expired_file_reference_not_refreshable"
                        ),
                        error_type=type(exc).__name__,
                        error=error_text(exc),
                        attempts=attempts,
                        file_reference_refresh=reference_refreshes,
                    )
                    if fallback is not None:
                        record["fallback"] = fallback
                    self.log_media_issue(target, record, relative_path)
                    print(
                        f"Unavailable {target.role} in message {target.message_id}: "
                        + (
                            "refresh request failed"
                            if refresh_failed
                            else "Telegram no longer returns a fresh file reference"
                        )
                        + (
                            f"; saved embedded preview to {fallback['file']}"
                            if fallback is not None
                            else ""
                        ),
                        file=sys.stderr,
                        flush=True,
                    )
                    if target.kind != "contact":
                        await self.pacer.after_media()
                    return record
                if target.kind == "profile_photo" and isinstance(exc, RuntimeError):
                    partial_path.unlink(missing_ok=True)
                    record.update(
                        status="unavailable",
                        reason="profile_photo_not_returned",
                        error_type=type(exc).__name__,
                        error=error_text(exc),
                        attempts=attempts,
                    )
                    self.log_media_issue(target, record, relative_path)
                    await self.pacer.after_media()
                    return record
                retryable = isinstance(
                    exc,
                    (
                        errors.ServerError,
                        errors.TimedOutError,
                        asyncio.TimeoutError,
                        ConnectionError,
                        OSError,
                        RuntimeError,
                        aiohttp.ClientError,
                    ),
                )
                if retryable and attempts <= self.args.retries:
                    self.stats.transient_retries += 1
                    delay = min(60.0, 2.0**attempts) + random.uniform(
                        0.0, self.args.jitter
                    )
                    print(
                        f"Download retry {attempts}/{self.args.retries} for {target.role} "
                        f"after {type(exc).__name__}; sleeping {delay:.1f}s",
                        flush=True,
                    )
                    await asyncio.sleep(delay)
                    continue
                partial_path.unlink(missing_ok=True)
                record.update(
                    status="failed",
                    error_type=type(exc).__name__,
                    error=error_text(exc),
                    attempts=attempts,
                )
                self.log_media_issue(target, record, relative_path)
                print(
                    f"Failed {target.role}: {error_text(exc)}",
                    file=sys.stderr,
                    flush=True,
                )
                if target.kind != "contact":
                    await self.pacer.after_media()
                return record

    def prune_stale_files(self) -> int:
        if not self.args.overwrite or self.args.keep_stale_files:
            return 0
        removed = 0
        try:
            paths = sorted(
                self.files_dir.rglob("*"),
                key=lambda path: len(path.parts),
                reverse=True,
            )
        except OSError as exc:
            print(f"Could not inspect stale files: {error_text(exc)}", file=sys.stderr)
            return 0
        for path in paths:
            try:
                if path.is_dir() and not path.is_symlink():
                    try:
                        path.rmdir()
                    except OSError:
                        pass
                    continue
                relative = path.relative_to(self.output_dir).as_posix()
                if relative not in self.referenced_files:
                    path.unlink()
                    removed += 1
            except OSError as exc:
                print(
                    f"Could not prune stale file {path}: {error_text(exc)}",
                    file=sys.stderr,
                )
        return removed

    def remove_migrated_legacy_files(self) -> int:
        if self.args.keep_stale_files:
            return 0
        removed = 0
        for path in self.migrated_legacy_files:
            try:
                if path.parent in {
                    self.files_dir,
                    self.files_dir / "legacy",
                } and path.is_file():
                    path.unlink()
                    removed += 1
            except OSError as exc:
                print(
                    f"Could not remove migrated legacy file {path}: {error_text(exc)}",
                    file=sys.stderr,
                )
        return removed

    def archive_unclassified_legacy_files(self) -> int:
        """Move unmatched old flat files aside without deleting their data."""

        if self.args.keep_stale_files:
            return 0
        archived = 0
        legacy_dir = self.files_dir / "legacy"
        for path in list(self.files_dir.iterdir()):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                legacy_dir.mkdir(parents=True, exist_ok=True)
                destination = legacy_dir / path.name
                suffix = 1
                while destination.exists():
                    destination = legacy_dir / f"{path.stem}_{suffix}{path.suffix}"
                    suffix += 1
                os.replace(path, destination)
                archived += 1
            except OSError as exc:
                print(
                    f"Could not archive legacy file {path}: {error_text(exc)}",
                    file=sys.stderr,
                )
        return archived

    async def download_peer_avatars(self, api: Any) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for marked_id, entity in sorted(self.peer_entities.items()):
            photo = getattr(entity, "photo", None)
            photo_id = getattr(photo, "photo_id", None)
            if photo_id is None or tl_name(photo) in {
                "UserProfilePhotoEmpty",
                "ChatPhotoEmpty",
                "None",
            }:
                continue
            target = DownloadTarget(
                obj=entity,
                kind="profile_photo",
                subtype="avatar",
                role="peer.avatar",
                message_id=0,
                cache_key=f"avatar:{marked_id}:{photo_id}:big",
                extension=".jpg",
                expected_size=None,
                metadata={
                    "type": "avatar",
                    "role": "peer.avatar",
                    "id": photo_id,
                    "owner_id": marked_id,
                    "owner_type": tl_name(entity),
                    "owner_name": utils.get_display_name(entity),
                    "telegram": json_safe(photo),
                },
                source_chat_id=marked_id,
                category_hint="avatars",
            )
            record = await self.download_target(api, target, 1)
            records.append(record)
            self.stats.observe_attachment(record)
        return records

    async def attachment_records(
        self,
        api: Any,
        message: Any,
        source: HistorySource,
        message_range: Any,
    ) -> list[dict[str, Any]]:
        protected = self.entity_protected or bool(getattr(message, "noforwards", False))
        if tl_name(self.entity) == "User":
            protected = protected or (
                self.private_protection_my
                if bool(getattr(message, "out", False))
                else self.private_protection_peer
            )
        else:
            protected = protected or self.chat_protected
        collector = AttachmentCollector(
            int(message.id),
            protected,
            forwarded=getattr(message, "fwd_from", None) is not None,
            source_chat_id=source.marked_id,
            source_peer=source.input_peer,
            message_range=message_range,
        )
        collector.collect_message(message, self.emoji_documents)
        self.collect_message_effect(collector, message)
        records = list(collector.records)
        for ordinal, target in enumerate(collector.targets, start=1):
            records.append(await self.download_target(api, target, ordinal))
        for record in records:
            self.stats.observe_attachment(record)
        return records

    def serialize_message(
        self,
        message: Any,
        attachments: list[dict[str, Any]],
        source: HistorySource,
    ) -> dict[str, Any]:
        text = getattr(message, "message", None)
        date = getattr(message, "date", None)
        edit_date = getattr(message, "edit_date", None)
        return {
            # Legacy-compatible core fields.
            "data": text,
            "source": peer_id(getattr(message, "peer_id", None)),
            "author": peer_id(getattr(message, "from_id", None)),
            "message": getattr(message, "id", None),
            "reactions": reaction_summary(message),
            "entities": entity_summary(
                text or "",
                getattr(message, "entities", None) or [],
                getattr(message, "reply_markup", None),
            ),
            "attachments": attachments,
            "forwarded": forwarded_summary(message),
            "replied": reply_summary(message),
            "created": unix_timestamp(date),
            # Current normalized fields.
            "type": message_type(message),
            "history_source": source.marked_id,
            "monoforum_topic": (
                {
                    "peer_id": source.topic_peer_id,
                    "top_message": source.topic_top_message,
                }
                if source.history_peer is not None
                else None
            ),
            "created_iso": iso_datetime(date),
            "edited": unix_timestamp(edit_date),
            "edited_iso": iso_datetime(edit_date),
            "saved_peer": peer_id(getattr(message, "saved_peer_id", None)),
            "album_id": getattr(message, "grouped_id", None),
            "via_bot_id": getattr(message, "via_bot_id", None),
            "via_business_bot_id": getattr(message, "via_business_bot_id", None),
            "guestchat_via_from": peer_id(getattr(message, "guestchat_via_from", None)),
            "post_author": getattr(message, "post_author", None),
            "ttl_period": getattr(message, "ttl_period", None),
            "effect_id": getattr(message, "effect", None),
            "quick_reply_shortcut_id": getattr(
                message, "quick_reply_shortcut_id", None
            ),
            "paid_message_stars": getattr(message, "paid_message_stars", None),
            "suggested_post": json_safe(getattr(message, "suggested_post", None)),
            "factcheck": json_safe(getattr(message, "factcheck", None)),
            "service_action": json_safe(getattr(message, "action", None)),
            "flags": {
                key: bool(getattr(message, key, False))
                for key in (
                    "out",
                    "mentioned",
                    "media_unread",
                    "silent",
                    "post",
                    "from_scheduled",
                    "pinned",
                    "noforwards",
                    "invert_media",
                    "offline",
                    "video_processing_pending",
                )
            },
            # Complete TL object, including fields added after this script.
            "raw": json_safe(message),
        }

    async def history_ranges(self, api: Any, use_takeout_ranges: bool) -> list[Any]:
        if not use_takeout_ranges:
            return [None]
        result = await self.rpc(
            lambda: api(functions.messages.GetSplitRangesRequest()),
            "takeout split ranges",
        )
        self.stats.metadata_requests += 1
        await self.pacer.after_metadata()
        ranges = list(result)
        ranges.sort(key=lambda item: int(getattr(item, "max_id", 0) or 0), reverse=True)
        return ranges or [None]

    async def history_page(
        self,
        api: Any,
        source: HistorySource,
        message_range: Any,
        offset_id: int,
    ) -> Any:
        if source.history_peer is not None:
            query: Any = functions.messages.GetSavedHistoryRequest(
                peer=source.history_peer,
                parent_peer=source.parent_peer,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=HISTORY_PAGE_SIZE,
                max_id=0,
                min_id=0,
                hash=0,
            )
        elif self.search_own_messages:
            query = functions.messages.SearchRequest(
                peer=source.input_peer,
                q="",
                from_id=types.InputPeerSelf(),
                filter=types.InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=offset_id,
                add_offset=0,
                limit=HISTORY_PAGE_SIZE,
                max_id=0,
                min_id=0,
                hash=0,
            )
        else:
            query = functions.messages.GetHistoryRequest(
                peer=source.input_peer,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=HISTORY_PAGE_SIZE,
                max_id=0,
                min_id=0,
                hash=0,
            )
        request = (
            functions.InvokeWithMessagesRangeRequest(range=message_range, query=query)
            if message_range is not None
            else query
        )
        response = await self.rpc(lambda: api(request), "message history")
        self.stats.history_requests += 1
        return response

    async def export(self, api: Any, use_takeout_ranges: bool) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        final_path = self.output_dir / f"{self.chat_id}.json"
        started = utc_now()
        if self.monoforum_admin_export:
            self.history_sources = await self.list_monoforum_topics(api)
        header = {
            "schema": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "telegram_layer": TELEGRAM_LAYER,
            "telethon_version": telethon.__version__,
            "exported_at": iso_datetime(started),
            "order": (
                "monoforum_topic_api_order_then_message_newest_to_oldest"
                if self.monoforum_admin_export
                else "newest_to_oldest_by_history_source"
            ),
            "chat": {
                "id": self.chat_id,
                "type": chat_kind(self.entity),
                "title": utils.get_display_name(self.entity),
                "username": getattr(self.entity, "username", None),
                "protected_content": self.chat_protected,
                "migration": self.migration,
                "monoforum_scope": self.monoforum_scope,
                "history_sources": [
                    {
                        "id": source.marked_id,
                        "label": source.label,
                        "migration_boundary": source.migration_boundary,
                        "topic_peer_id": source.topic_peer_id,
                        "topic_top_message": source.topic_top_message,
                        "topic_dialog": json_safe(source.topic_dialog),
                        "topic_entity": json_safe(source.topic_entity),
                    }
                    for source in self.history_sources
                ],
                "raw": json_safe(self.entity),
            },
        }
        writer = JsonExportWriter(final_path, header, self.args.overwrite)
        self.error_log_path.unlink(missing_ok=True)
        try:
            ranges = await self.history_ranges(api, use_takeout_ranges)
            for source_index, source in enumerate(self.history_sources, start=1):
                for range_index, message_range in enumerate(ranges, start=1):
                    offset_id = 0
                    while True:
                        response = await self.history_page(
                            api, source, message_range, offset_id
                        )
                        self.remember_peers(response)
                        # Pace every successful history request, including an
                        # empty takeout range.
                        await self.pacer.after_history()
                        page = list(getattr(response, "messages", None) or [])
                        if not page:
                            break

                        page_ids = [
                            int(item.id)
                            for item in page
                            if int(getattr(item, "id", 0) or 0) > 0
                        ]
                        if not page_ids:
                            self.stats.empty_messages_skipped += len(page)
                            break
                        next_offset = min(page_ids)
                        if offset_id and next_offset >= offset_id:
                            raise RuntimeError(
                                f"Telegram history pagination stopped advancing at message {offset_id}"
                            )

                        new_messages = []
                        for message in page:
                            message_id = int(getattr(message, "id", 0) or 0)
                            if message_id <= 0 or tl_name(message) == "MessageEmpty":
                                self.stats.empty_messages_skipped += 1
                                continue
                            message_key = (source.marked_id, message_id)
                            if message_key not in self.seen_message_ids:
                                self.seen_message_ids.add(message_key)
                                new_messages.append(message)

                        # Hydration may introduce story caption/reaction custom
                        # emoji IDs, so it must happen before emoji resolution.
                        for message in new_messages:
                            await self.hydrate_stories(api, message)
                        await self.resolve_custom_emojis(api, new_messages)
                        await self.resolve_message_effects(api, new_messages)
                        for message in new_messages:
                            attachments = await self.attachment_records(
                                api,
                                message,
                                source,
                                message_range,
                            )
                            writer.write_message(
                                self.serialize_message(message, attachments, source)
                            )
                            self.stats.messages += 1
                            if (
                                self.args.log_every
                                and self.stats.messages % self.args.log_every == 0
                            ):
                                print(
                                    f"Exported {self.stats.messages} messages "
                                    f"(source {source_index}/{len(self.history_sources)}, "
                                    f"range {range_index}/{len(ranges)}, next offset {next_offset})",
                                    flush=True,
                                )

                        offset_id = next_offset

            self.peer_avatar_records = await self.download_peer_avatars(api)
            finished = utc_now()
            failed = self.stats.attachments.get("failed", 0)
            skipped = self.stats.attachments.get("skipped_limit", 0)
            protected = self.stats.attachments.get("protected", 0)
            unavailable = self.stats.attachments.get("unavailable", 0)
            complete_accessible = (
                self.history_complete
                and self.stats.metadata_failures == 0
                and failed == 0
                and skipped == 0
            )
            fully_complete = complete_accessible and protected == 0 and unavailable == 0
            summary = {
                "complete": fully_complete,
                "complete_accessible": complete_accessible,
                "history_complete": self.history_complete,
                "monoforum_scope": self.monoforum_scope,
                "messages": self.stats.messages,
                "empty_messages_skipped": self.stats.empty_messages_skipped,
                "history_requests": self.stats.history_requests,
                "metadata_requests": self.stats.metadata_requests,
                "flood_waits": self.stats.flood_waits,
                "transient_retries": self.stats.transient_retries,
                "file_reference_refreshes": self.stats.file_reference_refreshes,
                "file_reference_refresh_successes": (
                    self.stats.file_reference_refresh_successes
                ),
                "metadata_failures": self.stats.metadata_failures,
                "attachments": dict(sorted(self.stats.attachments.items())),
                "attachment_categories": dict(
                    sorted(self.stats.attachment_categories.items())
                ),
                "bytes_downloaded": self.stats.bytes_downloaded,
                "started_at": iso_datetime(started),
                "finished_at": iso_datetime(finished),
                "duration_seconds": round((finished - started).total_seconds(), 3),
                "limitations": [
                    "Only history and files currently accessible to this user account are exportable.",
                    "Deleted or expired content and secret-chat history cannot be recovered.",
                    "Protected content, locked paid media, and live streams are recorded but not downloaded.",
                    *self.history_limitations,
                ],
            }
            # Publish the new JSON before pruning.  If serialization/fsync/
            # replace fails, the previous completed JSON and its files remain
            # a consistent archive.
            writer.finish(self.peers, self.peer_avatar_records, summary)
            stale_files_removed = self.remove_migrated_legacy_files()
            legacy_files_archived = 0
            if fully_complete:
                stale_files_removed += self.prune_stale_files()
            else:
                legacy_files_archived = self.archive_unclassified_legacy_files()
            print(
                f"Finished: {self.stats.messages} messages -> {final_path} "
                f"({failed} failed downloads, {stale_files_removed} stale files pruned, "
                f"{legacy_files_archived} unmatched legacy files archived)",
                flush=True,
            )
            return summary
        except BaseException:
            writer.close_incomplete()
            print(
                f"Incomplete JSON kept at {writer.partial_path}",
                file=sys.stderr,
                flush=True,
            )
            raise


def parse_chat_reference(value: str) -> Any:
    stripped = value.strip()
    if stripped.startswith("chat="):
        stripped = stripped.removeprefix("chat=").strip()
    return int(stripped) if re.fullmatch(r"[+-]?\d+", stripped) else stripped


async def preflight_call(
    factory: Callable[[], Any],
    args: argparse.Namespace,
    label: str,
) -> Any:
    attempts = 0
    while True:
        try:
            return await factory()
        except (errors.FloodWaitError, errors.FloodPremiumWaitError) as exc:
            delay = (
                int(getattr(exc, "seconds", 0))
                + args.flood_reserve
                + random.uniform(0.0, args.jitter)
            )
            print(
                f"Telegram flood limit for {label}; sleeping {delay:.1f}s", flush=True
            )
            await asyncio.sleep(delay)
        except (
            errors.ServerError,
            errors.TimedOutError,
            asyncio.TimeoutError,
            OSError,
        ):
            attempts += 1
            if attempts > args.retries:
                raise
            await asyncio.sleep(
                min(60.0, 2.0**attempts) + random.uniform(0.0, args.jitter)
            )


async def resolve_selected_chat(
    client: TelegramClient, args: argparse.Namespace
) -> Any:
    reference = parse_chat_reference(args.chat)
    try:
        return await preflight_call(
            lambda: client.get_entity(reference),
            args,
            "selected-chat resolution",
        )
    except (ValueError, TypeError):
        pass

    inferred_peer: Any = None
    if isinstance(reference, int):
        real_id, inferred_peer = utils.resolve_id(reference)
        peer_kind = args.peer_kind
        if peer_kind == "auto":
            peer_kind = {
                types.PeerUser: "user",
                types.PeerChat: "chat",
                types.PeerChannel: "channel",
            }[inferred_peer]
        if peer_kind == "chat":
            return await preflight_call(
                lambda: client.get_entity(types.InputPeerChat(real_id)),
                args,
                "basic-chat resolution",
            )
        if args.access_hash is None:
            input_peer = None
        elif peer_kind == "user":
            input_peer = types.InputPeerUser(real_id, args.access_hash)
        else:
            input_peer = types.InputPeerChannel(real_id, args.access_hash)
        if input_peer is not None:
            return await preflight_call(
                lambda: client.get_entity(input_peer),
                args,
                "numeric-peer resolution",
            )

    if isinstance(reference, int):
        # StringSession does not persist an entity cache. A conservative dialog
        # scan can recover the required per-account access hash without guessing.
        offset_date: Optional[dt.datetime] = None
        offset_id = 0
        offset_peer: Any = types.InputPeerEmpty()
        ignore_pinned = False
        while True:
            dialogs = await preflight_call(
                lambda: client.get_dialogs(
                    limit=HISTORY_PAGE_SIZE,
                    offset_date=offset_date,
                    offset_id=offset_id,
                    offset_peer=offset_peer,
                    ignore_pinned=ignore_pinned,
                ),
                args,
                "dialog scan",
            )
            for dialog in dialogs:
                if marked_chat_id(dialog.entity) == reference:
                    return dialog.entity
            if len(dialogs) < HISTORY_PAGE_SIZE:
                break
            last = dialogs[-1]
            last_message = getattr(last, "message", None)
            if last_message is None:
                break
            next_boundary = (
                getattr(last_message, "date", None),
                int(getattr(last_message, "id", 0) or 0),
                last.input_entity,
            )
            if next_boundary[1] <= 0 or (
                next_boundary[0] == offset_date and next_boundary[1] == offset_id
            ):
                break
            offset_date, offset_id, offset_peer = next_boundary
            ignore_pinned = True
            delay = args.metadata_delay + random.uniform(0.0, args.jitter)
            if delay > 0:
                await asyncio.sleep(delay)

        if inferred_peer is types.PeerChannel:
            offset = 0
            while True:
                result = await preflight_call(
                    lambda offset=offset: client(
                        functions.channels.GetLeftChannelsRequest(offset=offset)
                    ),
                    args,
                    "left-channel scan",
                )
                chats = list(getattr(result, "chats", None) or [])
                for chat in chats:
                    if marked_chat_id(chat) == reference:
                        return chat
                if not chats or tl_name(result) != "ChatsSlice":
                    break
                offset += len(chats)
                delay = args.metadata_delay + random.uniform(0.0, args.jitter)
                if delay > 0:
                    await asyncio.sleep(delay)

    raise ValueError(
        f"Cannot resolve chat {args.chat!r}. Use a username/link, ensure the chat is in "
        "this account's dialogs, or pass --access-hash and --peer-kind."
    )


def takeout_flags(
    entity: Any,
    max_file_size: int,
    history_sources: Iterable[HistorySource],
) -> dict[str, Any]:
    kind = chat_kind(entity)
    source_names = {tl_name(source.input_peer) for source in history_sources}
    return {
        "contacts": False,
        "users": kind in {"private", "bot"},
        "chats": kind == "basic_group" or "InputPeerChat" in source_names,
        # Telegram asks for megagroups together with basic groups so migrated
        # group history remains available in the takeout session.
        "megagroups": kind in {"basic_group", "supergroup", "gigagroup", "monoforum"},
        "channels": kind in {"channel", "monoforum"},
        "files": True,
        "max_file_size": max_file_size or UNLIMITED_TAKEOUT_FILE_SIZE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download one complete accessible Telegram chat to JSON and files/.",
        # ArgumentDefaultsHelpFormatter would print TG_PHONE/TG_SESSION from
        # the environment and leak credentials into help output and logs.
        formatter_class=argparse.HelpFormatter,
    )
    parser.add_argument(
        "chat",
        help="@username, t.me link, 'me', or Telegram marked chat ID (chat=ID is accepted)",
    )
    parser.add_argument("--api-id", type=int, default=os.getenv("TG_ID"))
    parser.add_argument("--api-hash", default=os.getenv("TG_HASH"))
    parser.add_argument(
        "--phone",
        default=os.getenv("TG_PHONE"),
        help="Used only when login is required",
    )
    parser.add_argument(
        "--session",
        default=os.getenv("TG_SESSION_FILE", "telegram-export"),
        help="SQLite session name/path when --session-string is not supplied",
    )
    parser.add_argument(
        "--session-string",
        default=os.getenv("TG_SESSION"),
        help="Telethon StringSession; prefer TG_SESSION_STRING so it is not in shell history",
    )
    parser.add_argument("--output", type=Path, default=Path("download"))
    parser.add_argument(
        "--access-hash",
        type=int,
        help="Only needed for an uncached numeric user/channel ID",
    )
    parser.add_argument(
        "--peer-kind",
        choices=("auto", "user", "chat", "channel"),
        default="auto",
        help="How to interpret a numeric ID (basic chats do not need --access-hash)",
    )
    parser.add_argument(
        "--takeout",
        action="store_true",
        help="Use Telegram's export session and split ranges (may require a security wait)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Atomically replace an existing JSON export",
    )
    parser.add_argument(
        "--keep-stale-files",
        action="store_true",
        help="With --overwrite, do not prune files unreferenced by the new JSON",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=0,
        metavar="BYTES",
        help="Skip larger files; 0 means no exporter-imposed limit",
    )
    parser.add_argument(
        "--history-delay",
        type=float,
        default=3.5,
        help="Reserve delay after each 100-message history page",
    )
    parser.add_argument(
        "--metadata-delay",
        type=float,
        default=1.0,
        help="Reserve delay after story/custom-emoji/split-range requests",
    )
    parser.add_argument(
        "--media-delay",
        type=float,
        default=0.75,
        help="Reserve delay between sequential attachment downloads",
    )
    parser.add_argument(
        "--chunk-delay",
        type=float,
        default=0.15,
        help="Reserve delay after each Telethon media download part",
    )
    parser.add_argument(
        "--jitter", type=float, default=0.5, help="Random extra seconds added to delays"
    )
    parser.add_argument(
        "--flood-reserve",
        type=float,
        default=5.0,
        help="Extra seconds added to Telegram's exact FLOOD_WAIT value",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=6,
        help="Retries for transient RPC/download failures",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=100,
        help="Print progress every N messages; 0 disables",
    )
    return parser


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.api_id is None or not args.api_hash:
        parser.error("--api-id/TG_ID and --api-hash/TG_HASH are required")
    try:
        args.api_id = int(args.api_id)
    except (TypeError, ValueError):
        parser.error("--api-id/TG_ID must be an integer")
    for name in (
        "history_delay",
        "metadata_delay",
        "media_delay",
        "chunk_delay",
        "jitter",
        "flood_reserve",
    ):
        if getattr(args, name) < 0:
            parser.error(f"--{name.replace('_', '-')} cannot be negative")
    if args.retries < 0 or args.max_file_size < 0 or args.log_every < 0:
        parser.error("--retries, --max-file-size and --log-every cannot be negative")


async def async_main(args: argparse.Namespace) -> int:
    require_current_telethon()
    session: Any = (
        StringSession(args.session_string) if args.session_string else args.session
    )
    client = TelegramClient(
        session,
        args.api_id,
        args.api_hash,
        request_retries=5,
        connection_retries=5,
        retry_delay=2,
        auto_reconnect=True,
        flood_sleep_threshold=0,  # All flood waits are handled with reserve above.
    )

    await client.start(phone=args.phone)
    try:
        me = await client.get_me()
        if getattr(me, "bot", False):
            raise RuntimeError(
                "Full messages.getHistory export requires a Telegram user session; bot sessions are unsupported."
            )
        entity = await resolve_selected_chat(client, args)
        input_peer = await preflight_call(
            lambda: client.get_input_entity(entity),
            args,
            "selected-chat input-peer resolution",
        )
        chat_id = marked_chat_id(entity)
        output_dir = args.output.expanduser().resolve() / str(chat_id)
        exporter = ChatExporter(client, entity, input_peer, output_dir, args)
        await exporter.prepare()

        if args.takeout:
            try:
                async with client.takeout(
                    finalize=True,
                    **takeout_flags(
                        entity, args.max_file_size, exporter.history_sources
                    ),
                ) as takeout:
                    summary = await exporter.export(takeout, use_takeout_ranges=True)
                    takeout.success = bool(summary["complete_accessible"])
            except errors.TakeoutInitDelayError as exc:
                ready = utc_now() + dt.timedelta(seconds=int(exc.seconds))
                print(
                    "Telegram requires a takeout security wait of "
                    f"{exc.seconds}s. Re-run after {iso_datetime(ready)}, or omit --takeout "
                    "to use conservatively paced normal history calls.",
                    file=sys.stderr,
                )
                return 3
        else:
            summary = await exporter.export(client, use_takeout_ranges=False)
        return 0 if summary["complete_accessible"] else 2
    finally:
        await client.disconnect()


def main() -> int:
    load_local_env()
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args, parser)
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print(
            "Export interrupted; downloaded files and the .json.part file were kept.",
            file=sys.stderr,
        )
        return 130
    except Exception as exc:
        print(
            f"Export failed: {type(exc).__name__}: {error_text(exc)}", file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
