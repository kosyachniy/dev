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
    python export_chat_2.py @chat_name
    python export_chat_2.py -1001234567890 --session-string "$TG_SESSION_STRING"
    python export_chat_2.py @large_channel --takeout

The result is written to:

    download/<marked-chat-id>/<marked-chat-id>.jsonl
    download/<marked-chat-id>/<marked-chat-id>.metadata.json
    download/<marked-chat-id>/files/{media,forwarded,avatars,stickers,icons,
                                      reactions,preview,effects,stories,
                                      wallpapers,other}/*
    download/<marked-chat-id>/media-errors.jsonl  # only when media issues occur

The JSONL contains one message object per physical line, globally ordered from
oldest to newest.  The companion metadata JSON contains schema, chat, peer,
avatar, export-summary, and file-integrity information. Message objects keep
compact core fields and normalized current fields without a raw Telegram TL
copy. ``data`` is the visible text assembled from the message, RichMessage,
link-preview text, and Instant View article with MarkdownV2 formatting markers
but without MarkdownV2 escape backslashes. Every
structured/non-text value (including RichMessage structure, articles, entities,
keyboards, service actions, to-do lists, polls, locations, previews, and media)
lives exclusively in ``attachments``. Semantic attachment descriptors retain
their normalized content; physical assets expose one selected rendition and
its saved local file. File-carrying Telegram wrappers are folded into that one
concrete attachment, so they never create a second generic photo/document/
contact entry. Public attachments omit internal download routing fields such as
role and category. Link/reply previews save still images only: a Telegram video
preview is represented by its largest available JPEG thumbnail, never by the
full video. All absolute times are integer Unix seconds, and recursively empty
optional values are omitted. Poll option tokens are retained;
other opaque binary and authorization-capability tokens are represented by
SHA-256 and byte size instead of copying potentially sensitive payload bytes.

Re-running the same command against a valid JSONL/metadata pair performs an
incremental update: it checks each chat/topic history boundary, processes only
higher-ID messages, and preserves/reuses existing media.  Use ``--overwrite``
to rebuild all message state, including edits, deletions, and changed reactions.

Only history and media available to the logged-in user can be exported.
Telegram cannot reconstruct deleted messages, expired/self-destructed media,
secret-chat history, unpurchased paid media, or inaccessible stories.  Saving
protected (``noforwards``) content is intentionally not attempted. Telegram's
``MessageEmpty`` placeholders are skipped because they contain no message date
or content; their IDs still advance history pagination safely.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import copy
import datetime as dt
import hashlib
import heapq
import html
import inspect
import json
import mimetypes
import os
import random
import re
import shutil
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Mapping, Optional, cast
from urllib.parse import urlsplit, urlunsplit

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
SUPPORTED_TELEGRAM_LAYER = 227
SCHEMA_NAME = "telegram-chat-export"
SCHEMA_VERSION = 14
HISTORY_PAGE_SIZE = 100  # Telegram list methods normally accept at most 100.
CUSTOM_EMOJI_BATCH_SIZE = 100  # Official limit for getCustomEmojiDocuments.
UNLIMITED_TAKEOUT_FILE_SIZE = (1 << 63) - 1
ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
LOG_URL_RE = re.compile(r"https?://[^\s'\"<>]+", re.IGNORECASE)
SUPPORTED_MESSAGE_FIELDS = frozenset(
    {
        "id",
        "peer_id",
        "date",
        "message",
        "out",
        "mentioned",
        "media_unread",
        "silent",
        "post",
        "from_scheduled",
        "legacy",
        "edit_hide",
        "pinned",
        "noforwards",
        "invert_media",
        "offline",
        "video_processing_pending",
        "paid_suggested_post_stars",
        "paid_suggested_post_ton",
        "from_id",
        "from_boosts_applied",
        "from_rank",
        "saved_peer_id",
        "fwd_from",
        "via_bot_id",
        "via_business_bot_id",
        "guestchat_via_from",
        "reply_to",
        "media",
        "reply_markup",
        "entities",
        "views",
        "forwards",
        "replies",
        "edit_date",
        "post_author",
        "grouped_id",
        "reactions",
        "restriction_reason",
        "ttl_period",
        "quick_reply_shortcut_id",
        "effect",
        "factcheck",
        "report_delivery_until_date",
        "paid_message_stars",
        "suggested_post",
        "schedule_repeat_period",
        "summary_from_language",
        "rich_message",
    }
)
SUPPORTED_MESSAGE_SERVICE_FIELDS = frozenset(
    {
        "id",
        "peer_id",
        "date",
        "action",
        "out",
        "mentioned",
        "media_unread",
        "reactions_are_possible",
        "silent",
        "post",
        "legacy",
        "from_id",
        "saved_peer_id",
        "reply_to",
        "reactions",
        "ttl_period",
    }
)
SUPPORTED_MESSAGE_EMPTY_FIELDS = frozenset({"id", "peer_id"})
SUPPORTED_MESSAGE_MEDIA_CONSTRUCTORS = frozenset(
    {
        "MessageMediaContact",
        "MessageMediaDice",
        "MessageMediaDocument",
        "MessageMediaEmpty",
        "MessageMediaGame",
        "MessageMediaGeo",
        "MessageMediaGeoLive",
        "MessageMediaGiveaway",
        "MessageMediaGiveawayResults",
        "MessageMediaInvoice",
        "MessageMediaPaidMedia",
        "MessageMediaPhoto",
        "MessageMediaPoll",
        "MessageMediaStory",
        "MessageMediaToDo",
        "MessageMediaUnsupported",
        "MessageMediaVenue",
        "MessageMediaVideoStream",
        "MessageMediaWebPage",
    }
)
SUPPORTED_MESSAGE_ACTION_CONSTRUCTORS = frozenset(
    {
        "MessageActionBoostApply",
        "MessageActionBotAllowed",
        "MessageActionChangeCreator",
        "MessageActionChannelCreate",
        "MessageActionChannelMigrateFrom",
        "MessageActionChatAddUser",
        "MessageActionChatCreate",
        "MessageActionChatDeletePhoto",
        "MessageActionChatDeleteUser",
        "MessageActionChatEditPhoto",
        "MessageActionChatEditTitle",
        "MessageActionChatJoinedByLink",
        "MessageActionChatJoinedByRequest",
        "MessageActionChatMigrateTo",
        "MessageActionConferenceCall",
        "MessageActionContactSignUp",
        "MessageActionCustomAction",
        "MessageActionEmpty",
        "MessageActionGameScore",
        "MessageActionGeoProximityReached",
        "MessageActionGiftCode",
        "MessageActionGiftPremium",
        "MessageActionGiftStars",
        "MessageActionGiftTon",
        "MessageActionGiveawayLaunch",
        "MessageActionGiveawayResults",
        "MessageActionGroupCall",
        "MessageActionGroupCallScheduled",
        "MessageActionHistoryClear",
        "MessageActionInviteToGroupCall",
        "MessageActionManagedBotCreated",
        "MessageActionNewCreatorPending",
        "MessageActionNoForwardsRequest",
        "MessageActionNoForwardsToggle",
        "MessageActionPaidMessagesPrice",
        "MessageActionPaidMessagesRefunded",
        "MessageActionPaymentRefunded",
        "MessageActionPaymentSent",
        "MessageActionPaymentSentMe",
        "MessageActionPhoneCall",
        "MessageActionPinMessage",
        "MessageActionPollAppendAnswer",
        "MessageActionPollDeleteAnswer",
        "MessageActionPrizeStars",
        "MessageActionRequestedPeer",
        "MessageActionRequestedPeerSentMe",
        "MessageActionScreenshotTaken",
        "MessageActionSecureValuesSent",
        "MessageActionSecureValuesSentMe",
        "MessageActionSetChatTheme",
        "MessageActionSetChatWallPaper",
        "MessageActionSetMessagesTTL",
        "MessageActionStarGift",
        "MessageActionStarGiftPurchaseOffer",
        "MessageActionStarGiftPurchaseOfferDeclined",
        "MessageActionStarGiftUnique",
        "MessageActionSuggestBirthday",
        "MessageActionSuggestProfilePhoto",
        "MessageActionSuggestedPostApproval",
        "MessageActionSuggestedPostRefund",
        "MessageActionSuggestedPostSuccess",
        "MessageActionTodoAppendTasks",
        "MessageActionTodoCompletions",
        "MessageActionTopicCreate",
        "MessageActionTopicEdit",
        "MessageActionWebViewDataSent",
        "MessageActionWebViewDataSentMe",
    }
)


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


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def unix_timestamp(value: Optional[dt.datetime]) -> Optional[int]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return int(value.timestamp())


def file_sha256(path: Path) -> str:
    """Return the SHA-256 of a saved attachment without loading it in memory."""

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def telethon_version_tuple() -> tuple[int, int, int]:
    numbers = [int(part) for part in re.findall(r"\d+", telethon.__version__)[:3]]
    return tuple((numbers + [0, 0, 0])[:3])  # type: ignore[return-value]


def raw_tl_constructor(patched_type: type[Any]) -> type[Any]:
    """Return the generated TL base hidden behind Telethon's message patch."""

    constructor_id = getattr(patched_type, "CONSTRUCTOR_ID", None)
    for candidate in patched_type.__mro__:
        if (
            candidate.__module__ == "telethon.tl.types"
            and getattr(candidate, "CONSTRUCTOR_ID", None) == constructor_id
        ):
            return candidate
    raise RuntimeError(
        f"Cannot locate the raw TL constructor for {patched_type.__name__}"
    )


def require_current_telethon() -> None:
    if telethon_version_tuple() < MIN_TELETHON:
        wanted = ".".join(map(str, MIN_TELETHON))
        raise RuntimeError(
            f"Telethon {wanted}+ is required for the current Telegram schema; "
            f"found {telethon.__version__}. Upgrade Telethon before exporting."
        )
    if TELEGRAM_LAYER is None or int(TELEGRAM_LAYER) != SUPPORTED_TELEGRAM_LAYER:
        raise RuntimeError(
            f"Telegram schema layer {SUPPORTED_TELEGRAM_LAYER} is required by "
            f"this normalized export schema; this Telethon build exposes layer "
            f"{TELEGRAM_LAYER!r}. Update the exporter before using a different layer."
        )
    for message_type, expected_fields in (
        (types.Message, SUPPORTED_MESSAGE_FIELDS),
        (types.MessageService, SUPPORTED_MESSAGE_SERVICE_FIELDS),
        (types.MessageEmpty, SUPPORTED_MESSAGE_EMPTY_FIELDS),
    ):
        raw_type = raw_tl_constructor(message_type)
        message_fields = frozenset(inspect.signature(raw_type).parameters)
        if message_fields != expected_fields:
            added = sorted(message_fields - expected_fields)
            removed = sorted(expected_fields - message_fields)
            raise RuntimeError(
                f"This Telethon {message_type.__name__} shape is not covered by "
                f"the normalized export schema (added={added}, removed={removed}). "
                "Update the exporter before running it so message content is not "
                "silently lost."
            )
    for prefix, expected in (
        ("MessageMedia", SUPPORTED_MESSAGE_MEDIA_CONSTRUCTORS),
        ("MessageAction", SUPPORTED_MESSAGE_ACTION_CONSTRUCTORS),
    ):
        current = frozenset(
            name
            for name, constructor in vars(types).items()
            if name.startswith(prefix)
            and inspect.isclass(constructor)
            and constructor.__name__ == name
        )
        if current != expected:
            added = sorted(current - expected)
            removed = sorted(expected - current)
            raise RuntimeError(
                f"This Telethon {prefix} set is not covered by the normalized "
                f"export schema (added={added}, removed={removed}). Update the "
                "exporter before running it."
            )


def tl_name(value: Any) -> str:
    return type(value).__name__ if value is not None else "None"


def json_safe(value: Any) -> Any:
    """Recursively turn TL values into JSON-compatible values."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if value == value and abs(value) != float("inf") else None
    if isinstance(value, bytes):
        return {"_type": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, dt.datetime):
        return unix_timestamp(value)
    if isinstance(value, dt.date):
        return unix_timestamp(
            dt.datetime.combine(value, dt.time.min, tzinfo=dt.timezone.utc)
        )
    if isinstance(value, dt.time):
        raise TypeError(
            "A time without a date cannot be serialized as a Unix timestamp"
        )
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


JSON_OMIT = object()


def sparse_json(value: Any) -> Any:
    """Return JSON-compatible data without recursively empty optional values."""

    def compact(item: Any) -> Any:
        if item is None or item == "":
            return JSON_OMIT
        if isinstance(item, Mapping):
            # Empty bytes are default TL values, not useful payloads.
            if item.get("_type") == "bytes" and not item.get("base64"):
                return JSON_OMIT
            mapping_result: dict[str, Any] = {}
            for key, child in item.items():
                compacted = compact(child)
                if compacted is not JSON_OMIT:
                    mapping_result[str(key)] = compacted
            if not mapping_result:
                return JSON_OMIT
            # Most discriminator-only TL constructors are meaningful events
            # (for example ReactionPaid or MessageActionPinMessage), so retain
            # them. Only explicit Empty constructors and the reactions
            # container with no remaining reaction data are defaults.
            if set(mapping_result) == {"_"} and (
                str(mapping_result["_"]).endswith("Empty")
                or mapping_result["_"] == "MessageReactions"
            ):
                return JSON_OMIT
            return mapping_result
        if isinstance(item, list):
            list_result: list[Any] = []
            for child in item:
                compacted = compact(child)
                if compacted is not JSON_OMIT:
                    list_result.append(compacted)
            return list_result if list_result else JSON_OMIT
        return item

    compacted = compact(json_safe(value))
    return {} if compacted is JSON_OMIT else compacted


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


def chunks(values: list[int], size: int) -> Iterable[list[int]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def safe_url_for_log(value: Optional[str]) -> Optional[str]:
    """Keep a URL useful for diagnostics without credentials or signed values."""

    if not value:
        return None
    raw = str(value)
    try:
        parsed = urlsplit(raw)
        host = parsed.hostname
        port = parsed.port
    except (TypeError, ValueError):
        digest = hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]
        return f"[redacted-url:{digest}]"
    if parsed.scheme.lower() not in {"http", "https"} or not host:
        digest = hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]
        return f"[redacted-url:{digest}]"
    safe_host = f"[{host}]" if ":" in host else host
    if port is not None:
        safe_host = f"{safe_host}:{port}"
    return urlunsplit((parsed.scheme.lower(), safe_host, parsed.path, "", ""))


def sanitize_log_text(value: str) -> str:
    return LOG_URL_RE.sub(
        lambda match: safe_url_for_log(match.group(0)) or "[redacted-url]",
        value,
    )


def error_text(exc: BaseException) -> str:
    text = re.sub(r"\s+", " ", str(exc)).strip()
    text = sanitize_log_text(text)
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

FILE_ATTACHMENT_FIELDS = (
    "type",
    "id",
    "hash",
    "access_hash",
    "mime",
    "file_name",
    "title",
    "sticker_alt",
    "video_codec",
    "file",
    "created",
)
PUBLIC_ATTACHMENT_FIELDS = (
    "type",
    "content",
    "status",
    "reason",
    *FILE_ATTACHMENT_FIELDS[1:],
)
PUBLIC_ATTACHMENT_FIELD_SET = frozenset(PUBLIC_ATTACHMENT_FIELDS)
SUCCESS_ATTACHMENT_STATUSES = frozenset(
    {"downloaded", "existing", "metadata_only", "reused"}
)


def public_attachment_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Project an internal semantic/file record to the public manifest."""

    projected = {
        field_name: record.get(field_name) for field_name in PUBLIC_ATTACHMENT_FIELDS
    }
    if projected.get("status") in SUCCESS_ATTACHMENT_STATUSES:
        projected["status"] = None
    return sparse_json(projected)


def public_peer_avatar_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Project an internal avatar download record without routing metadata."""

    projected = dict(record)
    for field_name in (
        "role",
        "roles",
        "category",
        "downloaded_size",
        "first_message",
        "reused_from",
        "reused_asset_from",
    ):
        projected.pop(field_name, None)
    if projected.get("status") in SUCCESS_ATTACHMENT_STATUSES:
        projected.pop("status", None)
    return sparse_json(projected)


def file_attachment_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Stable compact physical-asset projection used by cache identities."""

    return sparse_json(
        {field_name: record.get(field_name) for field_name in FILE_ATTACHMENT_FIELDS}
    )


def media_asset_identity(asset_key: str, record: Mapping[str, Any]) -> str:
    """Bind an internal cache key to the exact compact saved-file record."""

    payload = {
        "asset_key": asset_key,
        "attachment": file_attachment_record(record),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    if role == "message.effect" or role.startswith("message.effect."):
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
    topic_entity: Any = None


def history_source_metadata(source: HistorySource) -> dict[str, Any]:
    """Describe a history stream without persisting private unsent drafts."""

    return sparse_json(
        {
            "id": source.marked_id,
            "label": source.label,
            "migration_boundary": source.migration_boundary,
            "topic_peer_id": source.topic_peer_id,
            "topic_top_message": source.topic_top_message,
            "topic_entity": json_safe(source.topic_entity),
        }
    )


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


def best_static_photo_size(sizes: Iterable[Any]) -> Any:
    candidates = []
    all_sizes = list(sizes)
    for size in all_sizes:
        if tl_name(size) not in {"PhotoSize", "PhotoSizeProgressive"}:
            continue
        info = photo_size_info(size)
        area = int(info.get("width") or 0) * int(info.get("height") or 0)
        candidates.append((area, int(info.get("size") or 0), size))
    if candidates:
        # Telegram's a/b/c/d renditions are server-cropped thumbnails. Select
        # the maximum full-image rendition first so a square crop never beats
        # the actual photo merely because its pixel area is larger.
        full_image_candidates = [
            candidate
            for candidate in candidates
            if getattr(candidate[2], "type", None) in {"s", "m", "x", "y", "w"}
        ]
        return max(
            full_image_candidates or candidates,
            key=lambda item: (item[0], item[1]),
        )[2]

    # A cached/stripped image is better than silently losing the attachment.
    fallback = []
    for size in all_sizes:
        if tl_name(size) in {"PhotoCachedSize", "PhotoStrippedSize"}:
            fallback.append((len(getattr(size, "bytes", b"") or b""), size))
    if fallback:
        return max(fallback, key=lambda item: item[0])[1]

    return None


def best_photo_size(photo: Any, *, allow_video: bool = True) -> Any:
    static_size = best_static_photo_size(getattr(photo, "sizes", None) or [])
    if static_size is not None or not allow_video:
        return static_size

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
            result["sticker_alt"] = getattr(attribute, "alt", None)
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


def select_document_rendition(
    document: Any, alternatives: Optional[Iterable[Any]] = None
) -> Any:
    """Select the one document rendition used by both JSON and downloading."""

    candidates = [
        item
        for item in [document, *(alternatives or [])]
        if item is not None and tl_name(item) not in {"DocumentEmpty", "None"}
    ]
    if not candidates:
        return document
    video_candidates = [
        item for item in candidates if document_attributes(item).get("width")
    ]
    if len(candidates) > 1 and video_candidates:
        return max(video_candidates, key=video_quality_key)
    return candidates[0]


CONTENT_TRANSPORT_FIELDS = frozenset(
    {
        "access_hash",
        "alt_documents",
        "dc_id",
        "file_reference",
        "iv",
        "key",
        "sizes",
        "thumb",
        "thumbs",
        "video_sizes",
        "video_thumbs",
    }
)
CONTENT_REDACTED_PREFIXES = (
    "SecureCredentials",
    "SecureData",
    "SecureFile",
    "SecureSecret",
    "SecureValue",
    "EncryptedFile",
    "InputSecureFile",
)
CONTENT_EMPTY_CONSTRUCTORS = frozenset(
    {"MessageActionEmpty", "MessageMediaEmpty", "ReactionEmpty", "TextEmpty"}
)
CONTENT_TYPE_PREFIXES = (
    "InputMessageEntity",
    "MessageExtendedMedia",
    "MessageAction",
    "MessageEntity",
    "MessageMedia",
    "MessagePeer",
    "PageListOrderedItem",
    "PageListItem",
    "PageBlock",
    "WebPageAttribute",
    "KeyboardButton",
    "ReplyKeyboard",
    "ReactionNotificationsFrom",
    "Reaction",
)
CONTENT_FIELD_RENAMES = {
    ("GeoPoint", "lat"): "latitude",
    ("GeoPoint", "long"): "longitude",
    ("MessageActionCustomAction", "message"): "text",
    ("MessageActionTodoAppendTasks", "list"): "items",
    ("MessageMediaInvoice", "receipt_msg_id"): "receipt_id",
    ("MessageMediaPaidMedia", "extended_media"): "items",
    ("MessageMediaToDo", "todo"): "list",
    ("MessageMediaStory", "peer"): "source",
    ("MessageReactions", "recent_reactions"): "recent",
    ("PageBlockOrderedList", "type"): "numbering_type",
    ("PageListOrderedItemBlocks", "type"): "numbering_type",
    ("PageListOrderedItemText", "type"): "numbering_type",
    ("PollAnswer", "date"): "created",
    ("PollResults", "results"): "answers",
    ("PrivacyValueAllowChatParticipants", "chats"): "raw_chat_ids",
    ("PrivacyValueDisallowChatParticipants", "chats"): "raw_chat_ids",
    ("ReactionEmoji", "emoticon"): "emoji",
    ("RichMessage", "part"): "partial",
    ("Page", "part"): "partial",
    ("StoryItem", "date"): "created",
    ("StoryItem", "expire_date"): "expires",
    ("StoryItem", "edited"): "is_edited",
    ("StoryItem", "from_id"): "author",
    ("StoryItemSkipped", "date"): "created",
    ("StoryItemSkipped", "expire_date"): "expires",
    ("TodoCompletion", "date"): "created",
    ("TodoCompletion", "id"): "item_id",
    ("TodoList", "list"): "items",
    ("WebPage", "cached_page"): "article",
    ("WebPage", "type"): "page_type",
    ("StoryFwdHeader", "from_"): "source",
}
CONTENT_HASH_FIELDS = frozenset({("FactCheck", "hash")})
CONTENT_OMITTED_FIELD_PAIRS = frozenset({("MessageReplies", "replies_pts")})
CONTENT_SENSITIVE_TEXT_FIELDS = frozenset(
    {("MessageActionStarGift", "prepaid_upgrade_hash")}
)
CONTENT_BINARY_FIELDS = frozenset(
    {
        ("PollAnswer", "option"),
        ("PollAnswerVoters", "option"),
    }
)
CONTENT_CHANNEL_ID_FIELDS = frozenset(
    {
        ("MediaAreaChannelPost", "channel_id"),
        ("MessageActionChatMigrateTo", "channel_id"),
        ("MessageMediaGiveaway", "channels"),
        ("MessageMediaGiveawayResults", "channel_id"),
        ("MessageReplies", "channel_id"),
        ("RequestedPeerChannel", "channel_id"),
    }
)
CONTENT_CHAT_ID_FIELDS = frozenset(
    {
        ("MessageActionChannelMigrateFrom", "chat_id"),
        ("RequestedPeerChat", "chat_id"),
    }
)
MAX_CONTENT_DEPTH = 128
MAX_CONTENT_NODES = 100_000
_OPTIONAL_FALSE_FIELDS: dict[type[Any], frozenset[str]] = {}


def encoded_binary_content(value: Any) -> Any:
    """Encode a known semantic byte token, omitting an empty default token."""

    if not isinstance(value, bytes) or not value:
        return JSON_OMIT
    return {
        "encoding": "base64",
        "data": base64.b64encode(value).decode("ascii"),
    }


def snake_case(value: str) -> str:
    first = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first).lower()
    return result.replace("to_do", "todo")


def content_type_name(constructor: str) -> str:
    special = {
        "Page": "article",
        "RichMessage": "rich_message",
        "TextWithEntities": "text_with_entities",
    }
    if constructor in special:
        return special[constructor]
    value = constructor
    for prefix in CONTENT_TYPE_PREFIXES:
        if value.startswith(prefix) and len(value) > len(prefix):
            value = value[len(prefix) :]
            break
    return snake_case(value)


def optional_false_fields(value: Any) -> frozenset[str]:
    value_type = type(value)
    cached = _OPTIONAL_FALSE_FIELDS.get(value_type)
    if cached is not None:
        return cached
    try:
        parameters = inspect.signature(value_type).parameters
    except (TypeError, ValueError):
        cached = frozenset()
    else:
        cached = frozenset(
            name
            for name, parameter in parameters.items()
            if parameter.default is None
        )
    _OPTIONAL_FALSE_FIELDS[value_type] = cached
    return cached


def compact_peer_reference(value: Any) -> Any:
    marked = peer_id(value)
    if marked is not None:
        return marked
    raw_id = getattr(value, "user_id", None)
    if raw_id is None:
        raw_id = getattr(value, "chat_id", None)
    if raw_id is None:
        raw_id = getattr(value, "channel_id", None)
    return int(raw_id) if type(raw_id) is int else None


def compact_entity_reference(value: Any) -> dict[str, Any]:
    try:
        marked = marked_chat_id(value)
    except (TypeError, ValueError, AttributeError):
        raw_id = getattr(value, "id", None)
        marked = int(raw_id) if type(raw_id) is int else None
    return sparse_json(
        {
            "type": chat_kind(value),
            "id": marked,
            "title": utils.get_display_name(value),
            "username": getattr(value, "username", None),
        }
    )


def compact_media_reference(value: Any) -> Any:
    name = tl_name(value)
    if name == "Photo":
        return sparse_json(
            {
                "type": "photo",
                "id": getattr(value, "id", None),
                "created": unix_timestamp(getattr(value, "date", None)),
            }
        )
    if name == "PhotoEmpty":
        return sparse_json(
            {"type": "photo", "id": getattr(value, "id", None), "unavailable": True}
        )
    if name == "Document":
        attributes = document_attributes(value)
        return sparse_json(
            {
                "type": document_subtype(value, attributes),
                "id": getattr(value, "id", None),
                "mime": getattr(value, "mime_type", None),
                "file_name": attributes.get("filename"),
                "title": attributes.get("title"),
                "sticker_alt": attributes.get("sticker_alt"),
                "video_codec": attributes.get("video_codec"),
                "created": unix_timestamp(getattr(value, "date", None)),
            }
        )
    if name == "DocumentEmpty":
        return sparse_json(
            {"type": "file", "id": getattr(value, "id", None), "unavailable": True}
        )
    if name in {"WebDocument", "WebDocumentNoProxy"}:
        attributes = document_attributes(value)
        return sparse_json(
            {
                "type": "web_file",
                "mime": getattr(value, "mime_type", None),
                "file_name": attributes.get("filename"),
                "title": attributes.get("title"),
                "sticker_alt": attributes.get("sticker_alt"),
                "video_codec": attributes.get("video_codec"),
            }
        )
    if name in {"InputDocument", "InputDocumentEmpty"}:
        return sparse_json(
            {"type": "file", "id": getattr(value, "id", None)}
        )
    if name in {"InputPhoto", "InputPhotoEmpty"}:
        return sparse_json(
            {"type": "photo", "id": getattr(value, "id", None)}
        )
    return JSON_OMIT


def normalized_content(value: Any) -> Any:
    """Project a Telegram content subtree to sparse, transport-free JSON."""

    active: set[int] = set()
    node_count = 0

    def binary_value(item: bytes, allowed: bool) -> Any:
        if not item:
            return JSON_OMIT
        if allowed:
            return encoded_binary_content(item)
        return {
            "type": "binary",
            "hash": hashlib.sha256(item).hexdigest(),
            "size": len(item),
            "redacted": True,
        }

    def marked_bare_peer_id(item: Any, *, channel: bool) -> Any:
        def mark(raw_id: Any) -> Any:
            if type(raw_id) is not int or raw_id <= 0:
                return JSON_OMIT
            peer = types.PeerChannel(raw_id) if channel else types.PeerChat(raw_id)
            return peer_id(peer)

        if isinstance(item, (list, tuple, set, frozenset)):
            values = [mark(raw_id) for raw_id in item]
            values = [raw_id for raw_id in values if raw_id is not JSON_OMIT]
            return values if values else JSON_OMIT
        return mark(item)

    def normalize(
        item: Any,
        depth: int = 0,
        binary_context: Optional[tuple[str, str]] = None,
    ) -> Any:
        nonlocal node_count
        if item is None:
            return JSON_OMIT
        if isinstance(item, (str, int, bool)):
            return item
        if isinstance(item, float):
            return item if item == item and abs(item) != float("inf") else JSON_OMIT
        if isinstance(item, bytes):
            return binary_value(item, binary_context in CONTENT_BINARY_FIELDS)
        if isinstance(item, dt.datetime):
            return unix_timestamp(item)
        if isinstance(item, dt.date):
            return unix_timestamp(
                dt.datetime.combine(item, dt.time.min, tzinfo=dt.timezone.utc)
            )
        if isinstance(item, dt.time):
            raise TypeError(
                "A time without a date cannot be serialized as a Unix timestamp"
            )
        if isinstance(item, Path):
            return item.as_posix()

        if depth > MAX_CONTENT_DEPTH:
            raise ValueError(
                f"Telegram content exceeds the supported nesting depth "
                f"({MAX_CONTENT_DEPTH})"
            )
        object_id = id(item)
        if object_id in active:
            constructor = tl_name(item)
            if isinstance(item, Mapping):
                constructor = str(item.get("_") or constructor)
            return sparse_json(
                {
                    "type": "cycle_reference",
                    "content_type": content_type_name(constructor),
                }
            )
        node_count += 1
        if node_count > MAX_CONTENT_NODES:
            raise ValueError(
                f"Telegram content exceeds the supported node count "
                f"({MAX_CONTENT_NODES})"
            )
        active.add(object_id)
        try:
            return normalize_complex(item, depth, binary_context)
        finally:
            active.remove(object_id)

    def normalize_complex(
        item: Any,
        depth: int,
        binary_context: Optional[tuple[str, str]],
    ) -> Any:
        if isinstance(item, (list, tuple, set, frozenset)):
            list_result = []
            for child in item:
                normalized = normalize(child, depth + 1, binary_context)
                if normalized is not JSON_OMIT:
                    list_result.append(normalized)
            return list_result if list_result else JSON_OMIT

        constructor = ""
        fields: Mapping[str, Any]
        original = None
        if isinstance(item, Mapping):
            constructor = str(item.get("_") or "")
            fields = item
        else:
            constructor = tl_name(item)
            original = item
            media_reference = compact_media_reference(item)
            if media_reference is not JSON_OMIT:
                return media_reference
            if constructor.startswith(("PhotoSize", "VideoSize")):
                return JSON_OMIT
            if constructor.startswith(CONTENT_REDACTED_PREFIXES):
                return {"type": content_type_name(constructor), "redacted": True}
            if constructor.startswith(("Peer", "InputPeer", "InputUser")):
                compact = compact_peer_reference(item)
                return compact if compact is not None else JSON_OMIT
            if constructor in {
                "User",
                "UserEmpty",
                "UserFull",
                "Chat",
                "ChatEmpty",
                "ChatForbidden",
                "Channel",
                "ChannelForbidden",
            }:
                return compact_entity_reference(item)
            if constructor in {"UserProfilePhoto", "ChatPhoto"}:
                return sparse_json(
                    {
                        "type": "profile_photo",
                        "id": getattr(item, "photo_id", None),
                    }
                )
            if constructor in {"UserProfilePhotoEmpty", "ChatPhotoEmpty"}:
                return JSON_OMIT
            try:
                fields = {
                    key: child
                    for key, child in vars(item).items()
                    if not key.startswith("_")
                }
            except TypeError:
                to_dict = getattr(item, "to_dict", None)
                if not callable(to_dict):
                    return str(item)
                converted = to_dict()
                if not isinstance(converted, Mapping):
                    return normalize(converted, depth + 1)
                fields = converted
                constructor = str(converted.get("_") or constructor)

        if constructor in CONTENT_EMPTY_CONSTRUCTORS:
            return JSON_OMIT
        if constructor.startswith(CONTENT_REDACTED_PREFIXES):
            return {"type": content_type_name(constructor), "redacted": True}

        if constructor == "MessageExtendedMedia":
            return normalize(fields.get("media"), depth + 1)
        if constructor == "MessageExtendedMediaPreview":
            return sparse_json(
                {
                    "type": "paid_media_preview",
                    "width": fields.get("w"),
                    "height": fields.get("h"),
                    "video_duration": fields.get("video_duration"),
                }
            )
        if constructor == "MessageMediaDocument":
            fields = dict(fields)
            fields["document"] = select_document_rendition(
                fields.get("document"), fields.get("alt_documents") or []
            )
            fields.pop("alt_documents", None)
        if constructor == "MessageMediaPoll":
            poll = normalize(fields.get("poll"), depth + 1)
            result = dict(poll) if isinstance(poll, Mapping) else {"type": "poll"}
            result["type"] = "poll"
            results = normalize(fields.get("results"), depth + 1)
            if isinstance(results, Mapping):
                results = dict(results)
                results.pop("type", None)
            if results is not JSON_OMIT and results:
                result["results"] = results
            attached_media = normalize(fields.get("attached_media"), depth + 1)
            if attached_media is not JSON_OMIT:
                result["attached_media"] = attached_media
            return sparse_json(result)
        if constructor == "MessageMediaPaidMedia":
            items = normalize(fields.get("extended_media"), depth + 1)
            return sparse_json(
                {
                    "type": "paid_media",
                    "stars_amount": fields.get("stars_amount"),
                    "items": None if items is JSON_OMIT else items,
                }
            )
        if constructor == "MessageMediaToDo":
            todo = normalize(fields.get("todo"), depth + 1)
            result = dict(todo) if isinstance(todo, Mapping) else {}
            result["type"] = "todo"
            completions = normalize(fields.get("completions"), depth + 1)
            if completions is not JSON_OMIT:
                result["completions"] = completions
            return sparse_json(result)
        if constructor == "MessageMediaWebPage":
            webpage = normalize(fields.get("webpage"), depth + 1)
            result = dict(webpage) if isinstance(webpage, Mapping) else {}
            for field_name in (
                "force_large_media",
                "force_small_media",
                "manual",
                "safe",
            ):
                if fields.get(field_name):
                    result[field_name] = True
            return sparse_json(result)

        result: dict[str, Any] = {}
        if constructor:
            result["type"] = content_type_name(constructor)
        optional_false = optional_false_fields(original) if original is not None else ()
        for key, child in fields.items():
            key = str(key)
            if key == "_" or key in CONTENT_TRANSPORT_FIELDS:
                continue
            if (constructor, key) in CONTENT_OMITTED_FIELD_PAIRS:
                continue
            if key == "hash" and (constructor, key) not in CONTENT_HASH_FIELDS:
                continue
            if constructor == "MessageMediaContact" and key == "vcard":
                continue
            if child is False and key in optional_false:
                continue
            pair = (constructor, key)
            if pair in CONTENT_CHANNEL_ID_FIELDS:
                normalized = marked_bare_peer_id(child, channel=True)
            elif pair in CONTENT_CHAT_ID_FIELDS:
                normalized = marked_bare_peer_id(child, channel=False)
            elif pair in CONTENT_SENSITIVE_TEXT_FIELDS and isinstance(child, str):
                if not child:
                    continue
                encoded = child.encode("utf-8")
                normalized = {
                    "type": "token",
                    "hash": hashlib.sha256(encoded).hexdigest(),
                    "size": len(encoded),
                    "redacted": True,
                }
            else:
                normalized = normalize(child, depth + 1, pair)
            if normalized is JSON_OMIT:
                continue
            output_key = CONTENT_FIELD_RENAMES.get((constructor, key), key)
            if output_key == "type":
                output_key = "value_type"
            result[output_key] = normalized
        return result if result else JSON_OMIT

    normalized = normalize(value)
    return {} if normalized is JSON_OMIT else sparse_json(normalized)


PHYSICAL_REFERENCE_TYPES = frozenset(
    {
        "animation",
        "animated_photo",
        "animated_sticker",
        "audio",
        "custom_emoji",
        "file",
        "image",
        "photo",
        "profile_photo",
        "round_video",
        "sticker",
        "video",
        "video_sticker",
        "voice",
        "web_file",
    }
)
PHYSICAL_REFERENCE_FIELDS = frozenset(
    {
        "type",
        "id",
        "mime",
        "file_name",
        "title",
        "sticker_alt",
        "video_codec",
        "created",
        "unavailable",
    }
)
NESTED_ATTACHMENT_FIELDS = frozenset(
    {"attached_media", "extended_media", "media", "solution_media"}
)


def strip_physical_attachment_content(value: Any) -> Any:
    """Remove asset/nested-media payloads represented by separate attachments."""

    def strip(item: Any) -> Any:
        if isinstance(item, Mapping):
            if (
                item.get("type") in PHYSICAL_REFERENCE_TYPES
                and set(map(str, item)) <= PHYSICAL_REFERENCE_FIELDS
            ):
                return JSON_OMIT
            result: dict[str, Any] = {}
            for key, child in item.items():
                key = str(key)
                if key in NESTED_ATTACHMENT_FIELDS:
                    continue
                stripped = strip(child)
                if stripped is not JSON_OMIT:
                    result[key] = stripped
            return result if result else JSON_OMIT
        if isinstance(item, list):
            list_result = [
                stripped
                for child in item
                if (stripped := strip(child)) is not JSON_OMIT
            ]
            return list_result if list_result else JSON_OMIT
        return item

    stripped = strip(value)
    return {} if stripped is JSON_OMIT else sparse_json(stripped)


def carrier_attachment_content(media: Any) -> dict[str, Any]:
    """Return only nonredundant context for a file-carrying media wrapper."""

    normalized = normalized_content(media)
    if not isinstance(normalized, Mapping):
        return {}
    stripped = strip_physical_attachment_content(normalized)
    if not isinstance(stripped, Mapping):
        return {}
    content = dict(stripped)
    content.pop("type", None)
    name = tl_name(media)
    if name == "MessageMediaDocument":
        # These flags only repeat the concrete attachment subtype.
        for field_name in ("round", "video", "voice"):
            content.pop(field_name, None)
    elif name == "MessageMediaContact":
        # The compact record already exposes the Telegram user as id. Keep
        # structured name/phone fields alongside the saved vCard.
        content.pop("user_id", None)
    return sparse_json(content)


MARKDOWN_V2_RESERVED_RE = re.compile(r"([\\_*\[\]()~`>#+\-=|{}.!])")
SAFE_RICH_LINK_SCHEMES = frozenset({"http", "https", "mailto", "tel", "tg"})


@dataclass(frozen=True)
class MarkdownPart:
    text: str
    atomic: bool = False
    non_linkable: bool = False


@dataclass(frozen=True)
class RenderedText:
    plain: str = ""
    markdown_v2: str = ""
    atomic: bool = False
    non_linkable: bool = False
    parts: tuple[MarkdownPart, ...] = ()


def rendered_parts(value: RenderedText) -> list[MarkdownPart]:
    if value.parts:
        return list(value.parts)
    if not value.markdown_v2:
        return []
    return [MarkdownPart(value.markdown_v2, value.atomic, value.non_linkable)]


def merge_markdown_parts(values: Iterable[MarkdownPart]) -> tuple[MarkdownPart, ...]:
    merged: list[MarkdownPart] = []
    for value in values:
        if not value.text:
            continue
        if (
            merged
            and merged[-1].atomic == value.atomic
            and merged[-1].non_linkable == value.non_linkable
        ):
            previous = merged[-1]
            boundary = (
                "\r"
                if previous.text.endswith("_") and value.text.startswith("_")
                else ""
            )
            merged[-1] = MarkdownPart(
                previous.text + boundary + value.text,
                value.atomic,
                value.non_linkable,
            )
        else:
            merged.append(value)
    return tuple(merged)


def rendered_from_parts(plain: str, values: Iterable[MarkdownPart]) -> RenderedText:
    parts = merge_markdown_parts(values)
    return RenderedText(
        plain,
        "".join(part.text for part in parts),
        any(part.atomic for part in parts),
        any(part.non_linkable for part in parts),
        parts,
    )


def markdown_v2_escape(value: str) -> str:
    return MARKDOWN_V2_RESERVED_RE.sub(r"\\\1", value)


def markdown_v2_without_escapes(value: str) -> str:
    """Convert strict Telegram markup to readable, unescaped stored markup.

    Stored ``data`` uses the requested ``**bold**`` spelling. Literal stars
    are distinguishable here because the strict renderer escaped them first.
    Code bodies and link targets are copied without treating their stars as
    bold delimiters.
    """

    result: list[str] = []
    position = 0
    escapable = frozenset(r"\_*[]()~`>#+-=|{}.!")
    inline_code = False
    fenced_code = False
    link_target = False
    while position < len(value):
        character = value[position]
        if (
            character == "\\"
            and position + 1 < len(value)
            and value[position + 1] in escapable
        ):
            result.append(value[position + 1])
            position += 2
            continue
        if (
            character == "\r"
            and not inline_code
            and not fenced_code
            and not link_target
            and position > 0
            and position + 1 < len(value)
            and value[position - 1] == "_"
            and value[position + 1] == "_"
        ):
            # The strict Telegram dialect inserts CR only to disambiguate
            # nested/adjacent underscore delimiters. It is not source text.
            position += 1
            continue
        if link_target:
            result.append(character)
            if character == ")":
                link_target = False
            position += 1
            continue
        if not inline_code and value.startswith("```", position):
            fenced_code = not fenced_code
            result.append("```")
            position += 3
            continue
        if not fenced_code and character == "`":
            inline_code = not inline_code
            result.append(character)
            position += 1
            continue
        if (
            not inline_code
            and not fenced_code
            and not link_target
            and value.startswith("](", position)
        ):
            result.append("](")
            link_target = True
            position += 2
            continue
        if (
            character == "*"
            and not inline_code
            and not fenced_code
            and not link_target
        ):
            result.append("**")
            position += 1
            continue
        result.append(character)
        position += 1
    return "".join(result)


def markdown_v2_code(value: str) -> str:
    return value.replace("\\", "\\\\").replace("`", "\\`")


def markdown_v2_link_target(value: str) -> str:
    return value.replace("\\", "\\\\").replace(")", "\\)")


def markdown_v2_link(label: str, target: str) -> str:
    try:
        scheme = urlsplit(target).scheme.lower()
    except ValueError:
        scheme = ""
    if scheme not in SAFE_RICH_LINK_SCHEMES:
        return label
    return f"[{label}]({markdown_v2_link_target(target)})"


def has_url_scheme(value: str) -> bool:
    try:
        return bool(urlsplit(value).scheme)
    except ValueError:
        return False


def join_rendered(values: Iterable[RenderedText], separator: str) -> RenderedText:
    visible = [value for value in values if value.plain != ""]
    parts: list[MarkdownPart] = []
    for index, value in enumerate(visible):
        if index:
            parts.append(MarkdownPart(separator))
        parts.extend(rendered_parts(value))
    return rendered_from_parts(
        separator.join(value.plain for value in visible),
        parts,
    )


def styled_rendered(value: RenderedText, marker: str) -> RenderedText:
    if not value.plain:
        return value
    styled: list[MarkdownPart] = []
    pending: list[MarkdownPart] = []

    def flush_pending() -> None:
        if not pending:
            return
        markdown = "".join(part.text for part in pending)
        opening_break = ""
        closing_break = ""
        # Telegram resolves ambiguous adjacent italic/underline underscores by
        # ignoring a carriage return placed between their delimiters.
        if marker == "_":
            opening_break = "\r" if markdown.startswith("__") else ""
            closing_break = "\r" if markdown.endswith("__") else ""
        elif marker == "__":
            opening_break = "\r" if markdown.startswith("_") else ""
            closing_break = "\r" if markdown.endswith("_") else ""
        styled.append(
            MarkdownPart(
                f"{marker}{opening_break}{markdown}{closing_break}{marker}",
                non_linkable=any(part.non_linkable for part in pending),
            )
        )
        pending.clear()

    for part in rendered_parts(value):
        if part.atomic:
            flush_pending()
            styled.append(part)
        else:
            pending.append(part)
    flush_pending()
    return rendered_from_parts(value.plain, styled)


def linked_rendered(value: RenderedText, target: str) -> RenderedText:
    try:
        scheme = urlsplit(target).scheme.lower()
    except ValueError:
        scheme = ""
    if scheme not in SAFE_RICH_LINK_SCHEMES:
        return value
    linked: list[MarkdownPart] = []
    for part in rendered_parts(value):
        if part.atomic or part.non_linkable:
            linked.append(part)
        else:
            linked.append(
                MarkdownPart(
                    markdown_v2_link(part.text, target),
                    non_linkable=True,
                )
            )
    return rendered_from_parts(value.plain, linked)


def quoted_markdown_v2(value: str, collapsed: bool = False) -> str:
    quoted = "\n".join(f">{line}" for line in value.split("\n"))
    return f"{quoted}||" if collapsed else quoted


def render_rich_text(
    value: Any,
    _active_styles: frozenset[str] = frozenset(),
) -> RenderedText:
    name = tl_name(value)
    if value is None or name in {"None", "TextEmpty"}:
        return RenderedText()
    if isinstance(value, str):
        return RenderedText(value, markdown_v2_escape(value))
    if name == "TextPlain":
        text = str(getattr(value, "text", None) or "")
        return RenderedText(text, markdown_v2_escape(text))
    if name == "TextConcat":
        return join_rendered(
            (
                render_rich_text(item, _active_styles)
                for item in getattr(value, "texts", None) or []
            ),
            "",
        )
    if name == "TextImage":
        return RenderedText()
    if name == "TextMath":
        source = str(getattr(value, "source", None) or "")
        return RenderedText(
            source,
            f"`{markdown_v2_code(source)}`" if source else "",
            bool(source),
        )
    if name == "TextCustomEmoji":
        alt = str(getattr(value, "alt", None) or "")
        document_id = getattr(value, "document_id", None)
        markdown = markdown_v2_escape(alt)
        if alt and type(document_id) is int:
            markdown = f"![{markdown}](tg://emoji?id={document_id})"
        return RenderedText(alt, markdown, False, bool(markdown and document_id))

    styles = {
        "TextBold": ("bold", "*"),
        "TextItalic": ("italic", "_"),
        "TextUnderline": ("underline", "__"),
        "TextStrike": ("strike", "~"),
        "TextSpoiler": ("spoiler", "||"),
    }
    if name in styles:
        style, marker = styles[name]
        child = render_rich_text(
            getattr(value, "text", None),
            _active_styles | {style},
        )
        return child if style in _active_styles else styled_rendered(child, marker)

    child = render_rich_text(getattr(value, "text", None), _active_styles)
    if name == "TextFixed":
        return RenderedText(
            child.plain,
            f"`{markdown_v2_code(child.plain)}`" if child.plain else "",
            bool(child.plain),
        )
    if name == "TextUrl":
        return linked_rendered(
            child,
            str(getattr(value, "url", None) or ""),
        )
    if name == "TextEmail":
        email = str(getattr(value, "email", None) or "")
        return linked_rendered(child, f"mailto:{email}")
    if name == "TextPhone":
        phone = str(getattr(value, "phone", None) or "")
        return linked_rendered(child, f"tel:{phone}")
    if name == "TextMentionName":
        user_id = getattr(value, "user_id", None)
        return linked_rendered(child, f"tg://user?id={user_id}")
    if name == "TextAutoUrl":
        target = child.plain
        if target and not has_url_scheme(target):
            target = f"https://{target}"
        return linked_rendered(child, target)
    if name == "TextAutoEmail":
        return linked_rendered(child, f"mailto:{child.plain}")
    if name == "TextAutoPhone":
        return linked_rendered(child, f"tel:{child.plain}")
    return child


@dataclass
class _EntitySpan:
    start: int
    end: int
    entity: Any
    order: int = 0
    children: list["_EntitySpan"] = field(default_factory=list)


def utf16_python_index(text: str, offset: int) -> Optional[int]:
    if offset < 0:
        return None
    units = 0
    for index, character in enumerate(text):
        if units == offset:
            return index
        units += 2 if ord(character) > 0xFFFF else 1
        if units > offset:
            return None
    return len(text) if units == offset else None


def entity_user_id(entity: Any) -> Optional[int]:
    value = getattr(entity, "user_id", None)
    if type(value) is int:
        return value
    marked = peer_id(value)
    if marked is not None:
        return abs(marked)
    raw = getattr(value, "user_id", None)
    return int(raw) if type(raw) is int else None


def render_text_with_entities(text: str, entities: Iterable[Any]) -> RenderedText:
    spans: list[_EntitySpan] = []
    for order, entity in enumerate(entities or []):
        offset = getattr(entity, "offset", None)
        length = getattr(entity, "length", None)
        if type(offset) is not int or type(length) is not int or length <= 0:
            continue
        start = utf16_python_index(text, offset)
        end = utf16_python_index(text, offset + length)
        if start is None or end is None or start >= end:
            continue
        spans.append(_EntitySpan(start, end, entity, order))

    spans.sort(key=lambda span: (span.start, -span.end, span.order))
    roots: list[_EntitySpan] = []
    stack: list[_EntitySpan] = []
    for span in spans:
        while stack and span.start >= stack[-1].end:
            stack.pop()
        if stack and span.end > stack[-1].end:
            # Crossing Telegram spans cannot be represented in Markdown. Drop
            # only this decoration and preserve every source character.
            continue
        (stack[-1].children if stack else roots).append(span)
        stack.append(span)

    entity_styles = {
        "MessageEntityBold": "bold",
        "MessageEntityItalic": "italic",
        "MessageEntityUnderline": "underline",
        "MessageEntityStrike": "strike",
        "MessageEntitySpoiler": "spoiler",
    }

    def render_range(
        start: int,
        end: int,
        children: list[_EntitySpan],
        active_styles: frozenset[str] = frozenset(),
    ) -> RenderedText:
        position = start
        rendered: list[MarkdownPart] = []
        for child in children:
            if child.start < position or child.end > end:
                continue
            rendered.append(
                MarkdownPart(markdown_v2_escape(text[position : child.start]))
            )
            rendered.extend(rendered_parts(render_span(child, active_styles)))
            position = child.end
        rendered.append(MarkdownPart(markdown_v2_escape(text[position:end])))
        return rendered_from_parts(text[start:end], rendered)

    def render_span(
        span: _EntitySpan,
        active_styles: frozenset[str],
    ) -> RenderedText:
        entity = span.entity
        name = tl_name(entity)
        raw = text[span.start : span.end]
        if name == "MessageEntityCode":
            return RenderedText(raw, f"`{markdown_v2_code(raw)}`", bool(raw))
        if name == "MessageEntityPre":
            language = str(getattr(entity, "language", None) or "")
            language = language if re.fullmatch(r"[A-Za-z0-9_+-]{1,32}", language) else ""
            prefix = f"```{language}\n" if language else "```\n"
            return RenderedText(
                raw,
                f"{prefix}{markdown_v2_code(raw)}\n```",
                bool(raw),
            )

        style = entity_styles.get(name)
        child_styles = active_styles | {style} if style else active_styles
        inner = render_range(span.start, span.end, span.children, child_styles)
        if name == "MessageEntityBold":
            return inner if style in active_styles else styled_rendered(inner, "*")
        if name == "MessageEntityItalic":
            return inner if style in active_styles else styled_rendered(inner, "_")
        if name == "MessageEntityUnderline":
            return inner if style in active_styles else styled_rendered(inner, "__")
        if name == "MessageEntityStrike":
            return inner if style in active_styles else styled_rendered(inner, "~")
        if name == "MessageEntitySpoiler":
            return inner if style in active_styles else styled_rendered(inner, "||")
        if name == "MessageEntityTextUrl":
            return linked_rendered(
                inner,
                str(getattr(entity, "url", None) or ""),
            )
        if name == "MessageEntityUrl":
            target = raw if has_url_scheme(raw) else f"https://{raw}"
            return linked_rendered(inner, target)
        if name == "MessageEntityEmail":
            return linked_rendered(inner, f"mailto:{raw}")
        if name == "MessageEntityPhone":
            return linked_rendered(inner, f"tel:{raw}")
        if name in {"MessageEntityMentionName", "InputMessageEntityMentionName"}:
            user_id = entity_user_id(entity)
            return (
                linked_rendered(inner, f"tg://user?id={user_id}")
                if user_id is not None
                else inner
            )
        if name == "MessageEntityCustomEmoji":
            document_id = getattr(entity, "document_id", None)
            if type(document_id) is not int:
                return inner
            return RenderedText(
                inner.plain,
                f"![{inner.markdown_v2}](tg://emoji?id={document_id})",
                False,
                True,
            )
        if name == "MessageEntityBlockquote":
            if inner.atomic:
                return inner
            return RenderedText(
                inner.plain,
                quoted_markdown_v2(
                    inner.markdown_v2,
                    collapsed=bool(getattr(entity, "collapsed", False)),
                ),
                non_linkable=inner.non_linkable,
            )
        return inner

    return render_range(0, len(text), roots)


class _VisibleHTMLParser(HTMLParser):
    _SUPPRESSED_TAGS = frozenset({"head", "script", "style", "template", "noscript"})
    _PREFORMATTED_TAGS = frozenset({"pre", "textarea"})
    _BLOCK_TAGS = frozenset(
        {
            "address",
            "article",
            "aside",
            "blockquote",
            "div",
            "dl",
            "fieldset",
            "figcaption",
            "figure",
            "footer",
            "form",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "header",
            "hgroup",
            "li",
            "main",
            "nav",
            "ol",
            "p",
            "section",
            "table",
            "tr",
            "ul",
        }
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[tuple[str, bool]] = []
        self.suppressed_depth = 0
        self.preformatted_depth = 0

    def append(self, value: str, *, preserve: bool = False) -> None:
        if not value:
            return
        if self.parts and self.parts[-1][1] == preserve:
            previous, _ = self.parts[-1]
            self.parts[-1] = (previous + value, preserve)
        else:
            self.parts.append((value, preserve))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if tag in self._SUPPRESSED_TAGS:
            self.suppressed_depth += 1
            return
        if self.suppressed_depth:
            return
        if tag in self._PREFORMATTED_TAGS:
            self.append("\n")
            self.preformatted_depth += 1
            return
        if tag in {"br", "hr"}:
            self.append("\n")
        elif tag in self._BLOCK_TAGS:
            self.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.suppressed_depth:
            if tag in self._SUPPRESSED_TAGS:
                self.suppressed_depth -= 1
            return
        if tag in self._PREFORMATTED_TAGS:
            self.preformatted_depth = max(0, self.preformatted_depth - 1)
            self.append("\n")
            return
        if tag in self._BLOCK_TAGS:
            self.append("\n")
        elif tag in {"td", "th"}:
            self.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.suppressed_depth:
            self.append(data, preserve=bool(self.preformatted_depth))


def visible_html_text(value: str) -> str:
    parser = _VisibleHTMLParser()
    try:
        parser.feed(value)
        parser.close()
    except (AssertionError, ValueError):
        value = re.sub(
            r"(?is)<(head|script|style|template|noscript)\b[^>]*>.*?</\1\s*>",
            "",
            value,
        )
        return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()

    normalized: list[tuple[str, bool]] = []
    for text, preserve in parser.parts:
        if not preserve:
            text = re.sub(r"[ \t\f\v]+", " ", text)
            text = re.sub(r" *\n(?: *\n)* *", "\n", text)
        if text:
            normalized.append((text, preserve))
    if normalized and not normalized[0][1]:
        normalized[0] = (normalized[0][0].lstrip(), False)
    if normalized and not normalized[-1][1]:
        normalized[-1] = (normalized[-1][0].rstrip(), False)
    return "".join(text for text, _preserve in normalized)


def render_page_caption(value: Any) -> RenderedText:
    if value is None:
        return RenderedText()
    return join_rendered(
        (
            render_rich_text(getattr(value, "text", None)),
            render_rich_text(getattr(value, "credit", None)),
        ),
        "\n",
    )


def render_page_blocks(values: Iterable[Any]) -> RenderedText:
    return join_rendered((render_page_block(value) for value in values or []), "\n\n")


def render_page_list_item(value: Any, index: int, ordered: bool) -> RenderedText:
    name = tl_name(value)
    if name.endswith("Text"):
        body = render_rich_text(getattr(value, "text", None))
    else:
        body = render_page_blocks(getattr(value, "blocks", None) or [])
    if not body.plain:
        return body
    checkbox = ""
    if getattr(value, "checkbox", False):
        checkbox = "[x] " if getattr(value, "checked", False) else "[ ] "
    if ordered:
        explicit = getattr(value, "num", None)
        number = explicit or getattr(value, "value", None) or index
        prefix = f"{number}. {checkbox}"
        markdown_prefix = markdown_v2_escape(prefix)
    else:
        prefix = f"- {checkbox}"
        markdown_prefix = markdown_v2_escape(prefix)
    return RenderedText(prefix + body.plain, markdown_prefix + body.markdown_v2)


def render_page_block(value: Any) -> RenderedText:
    name = tl_name(value)
    if value is None or name in {
        "None",
        "PageBlockUnsupported",
        "PageBlockDivider",
        "PageBlockAnchor",
    }:
        return RenderedText()

    text = render_rich_text(getattr(value, "text", None))
    if name in {
        "PageBlockTitle",
        "PageBlockHeader",
        "PageBlockSubheader",
        "PageBlockKicker",
        "PageBlockHeading1",
        "PageBlockHeading2",
        "PageBlockHeading3",
        "PageBlockHeading4",
        "PageBlockHeading5",
        "PageBlockHeading6",
    }:
        return text
    if name in {"PageBlockSubtitle", "PageBlockFooter"}:
        return text
    if name in {"PageBlockParagraph", "PageBlockThinking"}:
        return text
    if name == "PageBlockAuthorDate":
        return render_rich_text(getattr(value, "author", None))
    if name == "PageBlockPreformatted":
        plain = text.plain
        language = str(getattr(value, "language", None) or "")
        language = language if re.fullmatch(r"[A-Za-z0-9_+-]{1,32}", language) else ""
        prefix = f"```{language}\n" if language else "```\n"
        return RenderedText(
            plain,
            f"{prefix}{markdown_v2_code(plain)}\n```" if plain else "",
            bool(plain),
        )
    if name in {"PageBlockBlockquote", "PageBlockPullquote"}:
        rendered = join_rendered(
            (
                text,
                render_rich_text(getattr(value, "caption", None)),
            ),
            "\n",
        )
        if rendered.atomic:
            return rendered
        return RenderedText(
            rendered.plain,
            quoted_markdown_v2(rendered.markdown_v2) if rendered.plain else "",
            non_linkable=rendered.non_linkable,
        )
    if name == "PageBlockBlockquoteBlocks":
        rendered = join_rendered(
            (
                render_page_blocks(getattr(value, "blocks", None) or []),
                render_rich_text(getattr(value, "caption", None)),
            ),
            "\n",
        )
        if rendered.atomic:
            return rendered
        return RenderedText(
            rendered.plain,
            quoted_markdown_v2(rendered.markdown_v2) if rendered.plain else "",
            non_linkable=rendered.non_linkable,
        )
    if name in {"PageBlockPhoto", "PageBlockVideo", "PageBlockAudio", "PageBlockMap", "InputPageBlockMap"}:
        return render_page_caption(getattr(value, "caption", None))
    if name == "PageBlockCover":
        return render_page_block(getattr(value, "cover", None))
    if name == "PageBlockEmbed":
        embedded = visible_html_text(str(getattr(value, "html", None) or ""))
        return join_rendered(
            (
                render_page_caption(getattr(value, "caption", None)),
                RenderedText(embedded, markdown_v2_escape(embedded)),
            ),
            "\n",
        )
    if name == "PageBlockEmbedPost":
        author = str(getattr(value, "author", None) or "")
        return join_rendered(
            (
                RenderedText(author, markdown_v2_escape(author)),
                render_page_blocks(getattr(value, "blocks", None) or []),
                render_page_caption(getattr(value, "caption", None)),
            ),
            "\n",
        )
    if name in {"PageBlockCollage", "PageBlockSlideshow"}:
        return join_rendered(
            (
                render_page_blocks(getattr(value, "items", None) or []),
                render_page_caption(getattr(value, "caption", None)),
            ),
            "\n",
        )
    if name == "PageBlockChannel":
        title = utils.get_display_name(getattr(value, "channel", None))
        return RenderedText(title, markdown_v2_escape(title))
    if name == "PageBlockList":
        return join_rendered(
            (
                render_page_list_item(item, index, False)
                for index, item in enumerate(getattr(value, "items", None) or [], 1)
            ),
            "\n",
        )
    if name == "PageBlockOrderedList":
        items = list(getattr(value, "items", None) or [])
        raw_start = getattr(value, "start", None)
        if getattr(value, "reversed", False):
            start = int(raw_start) if type(raw_start) is int else len(items)
            numbers = range(start, start - len(items), -1)
        else:
            start = int(raw_start) if type(raw_start) is int else 1
            numbers = range(start, start + len(items))
        return join_rendered(
            (
                render_page_list_item(item, number, True)
                for item, number in zip(items, numbers)
            ),
            "\n",
        )
    if name == "PageBlockTable":
        rows: list[RenderedText] = []
        for row in getattr(value, "rows", None) or []:
            cells: list[RenderedText] = []
            for cell in getattr(row, "cells", None) or []:
                rendered = render_rich_text(getattr(cell, "text", None))
                cells.append(rendered)
            rows.append(
                RenderedText(
                    " | ".join(cell.plain for cell in cells if cell.plain),
                    " \\| ".join(
                        cell.markdown_v2 for cell in cells if cell.plain
                    ),
                )
            )
        return join_rendered(
            (
                render_rich_text(getattr(value, "title", None)),
                join_rendered(rows, "\n"),
            ),
            "\n",
        )
    if name == "PageBlockDetails":
        return join_rendered(
            (
                render_rich_text(getattr(value, "title", None)),
                render_page_blocks(getattr(value, "blocks", None) or []),
            ),
            "\n",
        )
    if name == "PageBlockRelatedArticles":
        articles: list[RenderedText] = []
        for article in getattr(value, "articles", None) or []:
            title = str(getattr(article, "title", None) or "")
            title_rendered = RenderedText(title, markdown_v2_escape(title))
            url = str(getattr(article, "url", None) or "")
            if title and url:
                title_rendered = linked_rendered(title_rendered, url)
            fields = [
                title_rendered,
                RenderedText(
                    str(getattr(article, "description", None) or ""),
                    markdown_v2_escape(str(getattr(article, "description", None) or "")),
                ),
                RenderedText(
                    str(getattr(article, "author", None) or ""),
                    markdown_v2_escape(str(getattr(article, "author", None) or "")),
                ),
            ]
            articles.append(join_rendered(fields, " — "))
        return join_rendered(
            (
                render_rich_text(getattr(value, "title", None)),
                join_rendered(articles, "\n"),
            ),
            "\n",
        )
    if name in {"PageBlockMath"}:
        source = str(getattr(value, "source", None) or "")
        return RenderedText(
            source,
            f"`{markdown_v2_code(source)}`" if source else "",
            bool(source),
        )
    return text


def render_rich_message(value: Any) -> RenderedText:
    return render_page_blocks(getattr(value, "blocks", None) or [])


def render_page(value: Any) -> RenderedText:
    return render_page_blocks(getattr(value, "blocks", None) or [])


def rendered_message_content(message: Any) -> RenderedText:
    segments: list[RenderedText] = []
    positions: dict[str, list[int]] = {}
    source_occurrences: dict[tuple[str, str], int] = {}

    def add(segment: RenderedText, source: str) -> None:
        if segment.plain == "":
            return
        source_key = (source, segment.plain)
        occurrence = source_occurrences.get(source_key, 0)
        source_occurrences[source_key] = occurrence + 1
        matching_positions = positions.setdefault(segment.plain, [])
        if occurrence >= len(matching_positions):
            matching_positions.append(len(segments))
            segments.append(segment)
            return
        existing_index = matching_positions[occurrence]
        existing = segments[existing_index]
        if (
            existing.markdown_v2 == markdown_v2_escape(existing.plain)
            and segment.markdown_v2 != markdown_v2_escape(segment.plain)
        ):
            segments[existing_index] = RenderedText(
                existing.plain,
                segment.markdown_v2,
            )

    text = str(getattr(message, "message", None) or "")
    if text:
        add(
            render_text_with_entities(
                text,
                getattr(message, "entities", None) or [],
            ),
            "message",
        )
    rich_message = getattr(message, "rich_message", None)
    for block in getattr(rich_message, "blocks", None) or []:
        add(render_page_block(block), "rich_message")

    media = getattr(message, "media", None)
    webpage = getattr(media, "webpage", None) if tl_name(media) == "MessageMediaWebPage" else None
    page = getattr(webpage, "cached_page", None)
    if webpage is not None:
        for field_name in ("site_name", "title", "description", "author"):
            value = str(getattr(webpage, field_name, None) or "")
            if value:
                add(
                    RenderedText(value, markdown_v2_escape(value)),
                    f"webpage.{field_name}",
                )
    for block in getattr(page, "blocks", None) or []:
        add(render_page_block(block), "cached_page")

    return join_rendered(segments, "\n\n")


def reaction_summary(message: Any) -> dict[str, Any]:
    reactions = getattr(message, "reactions", None)
    results = [
        item
        for item in (getattr(reactions, "results", None) or [])
        if tl_name(getattr(item, "reaction", None)) != "ReactionEmpty"
        and int(getattr(item, "count", 0) or 0) > 0
    ]
    replies = getattr(message, "replies", None)
    normalized = normalized_content(reactions)
    reaction_data = dict(normalized) if isinstance(normalized, Mapping) else {}
    reaction_data.pop("type", None)
    for field_name in ("results", "recent"):
        rows = reaction_data.get(field_name)
        if not isinstance(rows, list):
            continue
        meaningful = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            reaction = row.get("reaction")
            if not isinstance(reaction, Mapping):
                continue
            if field_name == "results" and int(row.get("count") or 0) <= 0:
                continue
            meaningful.append(row)
        if meaningful:
            reaction_data[field_name] = meaningful
        else:
            reaction_data.pop(field_name, None)
    top_reactors = reaction_data.get("top_reactors")
    if isinstance(top_reactors, list):
        top_reactors = [
            row
            for row in top_reactors
            if isinstance(row, Mapping) and int(row.get("count") or 0) > 0
        ]
        if top_reactors:
            reaction_data["top_reactors"] = top_reactors
        else:
            reaction_data.pop("top_reactors", None)
    if not any(
        reaction_data.get(field_name)
        for field_name in ("results", "recent", "top_reactors")
    ):
        for field_name in ("min", "can_see_list", "reactions_as_tags"):
            reaction_data.pop(field_name, None)
    return {
        "views": getattr(message, "views", None),
        "likes": (
            sum(int(getattr(item, "count", 0) or 0) for item in results)
            if results
            else None
        ),
        "reposts": getattr(message, "forwards", None),
        "comments": getattr(replies, "replies", None),
        **reaction_data,
    }


def forwarded_header_data(forwarded: Any) -> Optional[dict[str, Any]]:
    if forwarded is None:
        return None
    saved_from = sparse_json(
        {
            "peer": peer_id(getattr(forwarded, "saved_from_peer", None)),
            "id": getattr(forwarded, "saved_from_msg_id", None),
            "author": peer_id(getattr(forwarded, "saved_from_id", None)),
            "name": getattr(forwarded, "saved_from_name", None),
            "created": unix_timestamp(getattr(forwarded, "saved_date", None)),
        }
    )
    return {
        "source": peer_id(getattr(forwarded, "from_id", None)),
        "source_name": getattr(forwarded, "from_name", None),
        "source_id": getattr(forwarded, "channel_post", None),
        "post_author": getattr(forwarded, "post_author", None),
        "created": unix_timestamp(getattr(forwarded, "date", None)),
        "imported": True if getattr(forwarded, "imported", False) else None,
        "saved_out": True if getattr(forwarded, "saved_out", False) else None,
        "saved_from": saved_from,
        "psa_type": getattr(forwarded, "psa_type", None),
    }


def forwarded_summary(message: Any) -> Optional[dict[str, Any]]:
    return forwarded_header_data(getattr(message, "fwd_from", None))


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
    poll_option = encoded_binary_content(getattr(reply, "poll_option", None))
    result.update(
        top_id=getattr(reply, "reply_to_top_id", None),
        scheduled=True if getattr(reply, "reply_to_scheduled", False) else None,
        forum_topic=True if getattr(reply, "forum_topic", False) else None,
        quoted=True if getattr(reply, "quote", False) else None,
        ephemeral=True if getattr(reply, "reply_to_ephemeral", False) else None,
        reply_from=forwarded_header_data(getattr(reply, "reply_from", None)),
        quote_text=getattr(reply, "quote_text", None),
        quote_offset=getattr(reply, "quote_offset", None),
        todo_item_id=getattr(reply, "todo_item_id", None),
        poll_option=None if poll_option is JSON_OMIT else poll_option,
    )
    return result


def thread_summary(message: Any) -> Any:
    replies = normalized_content(getattr(message, "replies", None))
    if isinstance(replies, Mapping):
        result = dict(replies)
        result.pop("type", None)
        return result
    return replies


def suggested_post_data(value: Any) -> Any:
    if value is None:
        return None
    if getattr(value, "accepted", False):
        state = "accepted"
    elif getattr(value, "rejected", False):
        state = "rejected"
    else:
        state = "pending"
    return sparse_json(
        {
            "state": state,
            "price": normalized_content(getattr(value, "price", None)),
            "schedule_date": unix_timestamp(getattr(value, "schedule_date", None)),
        }
    )


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
        self._record_keys: set[str] = set()

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
        record: dict[str, Any] = {
            "type": media_type,
            "role": role,
            "status": status,
            "category": attachment_category_values(
                role,
                attachment_subtype or media_type,
                self.forwarded,
                category_hint,
            ),
        }
        if attachment_subtype is not None:
            record["_physical"] = True
        content: dict[str, Any] = {}
        normalized = normalized_content(value)
        if isinstance(normalized, Mapping):
            normalized = dict(normalized)
            normalized.pop("type", None)
            for field_name in FILE_ATTACHMENT_FIELDS[1:]:
                if normalized.get(field_name) is not None:
                    record[field_name] = normalized.pop(field_name)
            content.update(normalized)
        elif normalized:
            content["value"] = normalized
        supplied_content = extra.pop("content", None)
        if isinstance(supplied_content, Mapping):
            content.update(supplied_content)
        elif supplied_content not in (None, "", [], {}):
            content["value"] = supplied_content
        for field_name in PUBLIC_ATTACHMENT_FIELDS:
            if field_name in {"content", "role", "roles"}:
                continue
            if field_name in extra:
                record[field_name] = extra.pop(field_name)
        content.update(extra)
        if status == "unavailable" and attachment_subtype is not None:
            # The status already expresses this for empty physical media.
            content.pop("unavailable", None)
        if content:
            record["content"] = sparse_json(content)
        self.records.append(record)

    def semantic_record(
        self,
        value: Any,
        role: str,
        *,
        type_override: Optional[str] = None,
        category_hint: Optional[str] = None,
        status: str = "metadata_only",
        reason: Optional[str] = None,
        omit_fields: Iterable[str] = (),
        content_type_field: Optional[str] = None,
    ) -> None:
        normalized = normalized_content(value)
        if not normalized:
            return
        if isinstance(normalized, Mapping):
            payload: Any = dict(normalized)
            normalized_type = payload.pop("type", None)
            for field_name in omit_fields:
                payload.pop(field_name, None)
            if (
                content_type_field
                and normalized_type
                and normalized_type != type_override
            ):
                payload[content_type_field] = normalized_type
        else:
            payload = normalized
            normalized_type = None
        attachment_type = type_override or normalized_type or content_type_name(
            tl_name(value)
        )
        payload = strip_physical_attachment_content(payload)
        record = sparse_json(
            {
                "type": attachment_type,
                "role": role,
                "category": attachment_category_values(
                    role,
                    str(attachment_type),
                    self.forwarded,
                    category_hint,
                ),
                "content": payload,
                "status": status,
                "reason": reason,
            }
        )
        if not record:
            return
        key = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if key not in self._record_keys:
            self._record_keys.add(key)
            self.records.append(record)

    def add_photo(
        self,
        photo: Any,
        role: str,
        protected: Optional[bool] = None,
        refresh_url: Optional[str] = None,
        category_hint: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[Mapping[str, Any]] = None,
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
                content=content,
            )
            return
        preview_only = category_hint == "preview" or refresh_url is not None
        size = best_photo_size(photo, allow_video=not preview_only)
        if size is None:
            self.metadata_record(
                "image",
                role,
                photo,
                status="unavailable",
                attachment_subtype="image",
                category_hint=category_hint,
                reason="no_photo_size",
                content=content,
            )
            return
        selected = photo_size_info(size)
        is_video = tl_name(size) == "VideoSize"
        subtype = "video" if is_video else "image"
        media_id = getattr(photo, "id", None)
        metadata = {
            "type": subtype,
            "id": media_id,
            "access_hash": getattr(photo, "access_hash", None),
            "mime": "video/mp4" if is_video else "image/jpeg",
            "title": title,
            "created": unix_timestamp(getattr(photo, "date", None)),
        }
        if content:
            metadata["content"] = sparse_json(dict(content))
        expected_size = selected.get("size")
        if tl_name(size) == "PhotoStrippedSize":
            # Telethon inflates stripped thumbnail bytes into a JPEG, so the
            # downloaded size cannot equal the compressed TL byte count.
            expected_size = None
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
        if video_sizes and not is_video and not preview_only:
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
                        "id": media_id,
                        "access_hash": getattr(photo, "access_hash", None),
                        "mime": "video/mp4",
                        "title": title,
                        "created": unix_timestamp(getattr(photo, "date", None)),
                    },
                    thumb=getattr(video_size, "type", None),
                    protected=self.protected if protected is None else protected,
                    forwarded=self.forwarded,
                    source_chat_id=self.source_chat_id,
                    source_peer=self.source_peer,
                    message_range=self.message_range,
                    refresh_url=refresh_url,
                    category_hint=category_hint,
                )
            )

    def add_embedded_photo_size(
        self,
        size: Any,
        role: str,
        protected: Optional[bool] = None,
        category_hint: Optional[str] = "preview",
        content: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        if tl_name(size) not in {"PhotoCachedSize", "PhotoStrippedSize"}:
            return False
        data = bytes(getattr(size, "bytes", b"") or b"")
        if tl_name(size) == "PhotoStrippedSize":
            try:
                data = utils.stripped_photo_to_jpg(data)
            except (IndexError, TypeError, ValueError):
                return False
        if not data:
            return False
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
                metadata=sparse_json(
                    {
                        "type": "paid_media_preview",
                        "mime": "image/jpeg",
                        "content": dict(content) if content else None,
                    }
                ),
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                category_hint=category_hint,
            )
        )
        return True

    def add_document(
        self,
        document: Any,
        role: str,
        *,
        alternatives: Optional[Iterable[Any]] = None,
        protected: Optional[bool] = None,
        refresh_url: Optional[str] = None,
        category_hint: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if category_hint == "preview" or refresh_url is not None:
            self.add_document_preview_image(
                document,
                role,
                alternatives=alternatives,
                protected=protected,
                refresh_url=refresh_url,
                title=title,
                content=content,
            )
            return
        selected_document = select_document_rendition(document, alternatives)
        if selected_document is None or tl_name(selected_document) in {
            "DocumentEmpty",
            "None",
        }:
            self.metadata_record(
                "file",
                role,
                document,
                status="unavailable",
                attachment_subtype="file",
                category_hint=category_hint,
                reason="empty_document",
                content=content,
            )
            return
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
        metadata = {
            "type": subtype,
            "id": media_id,
            "access_hash": getattr(selected_document, "access_hash", None),
            "mime": mime,
            "file_name": filename,
            "title": title or attributes.get("title"),
            "sticker_alt": attributes.get("sticker_alt"),
            "video_codec": attributes.get("video_codec"),
            "created": unix_timestamp(getattr(selected_document, "date", None)),
        }
        if content:
            metadata["content"] = sparse_json(dict(content))
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
            effect = max(
                effects,
                key=lambda item: (
                    int(getattr(item, "w", 0) or 0)
                    * int(getattr(item, "h", 0) or 0),
                    int(getattr(item, "size", 0) or 0),
                ),
            )
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
                        "id": media_id,
                        "access_hash": getattr(
                            selected_document, "access_hash", None
                        ),
                        "mime": "application/x-tgsticker",
                        "title": title or attributes.get("title"),
                        "sticker_alt": attributes.get("sticker_alt"),
                        "created": unix_timestamp(
                            getattr(selected_document, "date", None)
                        ),
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

    def add_document_preview_image(
        self,
        document: Any,
        role: str,
        *,
        alternatives: Optional[Iterable[Any]] = None,
        protected: Optional[bool] = None,
        refresh_url: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        """Save one still document thumbnail without fetching the document."""

        alternative_list = list(alternatives or [])
        preferred = select_document_rendition(document, alternative_list)
        candidates: list[Any] = []
        seen_candidates: set[int] = set()
        for candidate in (preferred, document, *alternative_list):
            if candidate is None or tl_name(candidate) != "Document":
                continue
            identity = id(candidate)
            if identity in seen_candidates:
                continue
            seen_candidates.add(identity)
            candidates.append(candidate)
        selected_document = None
        size = None
        for candidate in candidates:
            candidate_size = best_static_photo_size(
                getattr(candidate, "thumbs", None) or []
            )
            if candidate_size is not None:
                selected_document = candidate
                size = candidate_size
                break
        if selected_document is None or size is None:
            return False
        selected = photo_size_info(size)
        thumb_type = getattr(size, "type", None)
        if not isinstance(thumb_type, str) or not thumb_type:
            return False

        media_id = getattr(selected_document, "id", None)
        access_hash = getattr(selected_document, "access_hash", None)
        file_reference = getattr(selected_document, "file_reference", None)
        metadata = {
            "type": "image",
            "id": media_id,
            "access_hash": access_hash,
            "mime": "image/jpeg",
            "title": title or document_attributes(selected_document).get("title"),
            "created": unix_timestamp(getattr(selected_document, "date", None)),
        }
        if content:
            metadata["content"] = sparse_json(dict(content))

        size_name = tl_name(size)
        expected_size = int(selected.get("size") or 0) or None
        if size_name in {"PhotoCachedSize", "PhotoStrippedSize"}:
            data = bytes(getattr(size, "bytes", b"") or b"")
            if size_name == "PhotoStrippedSize":
                try:
                    data = utils.stripped_photo_to_jpg(data)
                except (IndexError, TypeError, ValueError):
                    return False
            if not data:
                return False
            target_object: Any = data
            target_kind = "bytes"
            expected_size = len(data)
        else:
            if (
                type(media_id) is not int
                or type(access_hash) is not int
                or not isinstance(file_reference, bytes)
            ):
                return False
            target_object = types.InputDocumentFileLocation(
                id=media_id,
                access_hash=access_hash,
                file_reference=file_reference,
                thumb_size=thumb_type,
            )
            target_kind = "file_location"

        self.targets.append(
            DownloadTarget(
                obj=target_object,
                kind=target_kind,
                subtype="image",
                role=f"{role}.thumbnail",
                message_id=self.message_id,
                cache_key=f"document:{media_id}:thumb:{thumb_type}",
                extension=".jpg",
                expected_size=expected_size,
                metadata=metadata,
                thumb=thumb_type,
                protected=self.protected if protected is None else protected,
                forwarded=self.forwarded,
                source_chat_id=self.source_chat_id,
                source_peer=self.source_peer,
                message_range=self.message_range,
                dc_id=getattr(selected_document, "dc_id", None),
                refresh_url=refresh_url,
                category_hint="preview",
            )
        )
        return True

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
        access_hash = getattr(document, "access_hash", None)
        attributes = document_attributes(document)
        preview_only = category_hint == "preview"
        if preview_only and document_subtype(document, attributes) != "image":
            return
        subtype = "image" if preview_only else "web_file"
        file_name = attributes.get("filename")
        # WebDocument access_hash identifies Telegram-proxied content. A
        # WebDocumentNoProxy URL may be mutable, so scope it to this message
        # instead of reusing potentially stale same-size bytes later.
        identity_values = [url, access_hash, size, mime]
        if access_hash is None:
            identity_values.extend([self.source_chat_id, self.message_id])
        digest = hashlib.sha256(
            json.dumps(identity_values, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:24]
        extension = safe_extension(file_name or url, mime, ".bin")
        metadata = {
            "type": subtype,
            "access_hash": access_hash,
            "mime": mime,
            "file_name": file_name,
            "title": attributes.get("title"),
            "sticker_alt": attributes.get("sticker_alt"),
            "video_codec": attributes.get("video_codec"),
        }
        self.targets.append(
            DownloadTarget(
                obj=document,
                kind="web_document",
                subtype=subtype,
                role=role,
                message_id=self.message_id,
                cache_key=f"web:{digest}",
                extension=extension,
                expected_size=size,
                metadata=metadata,
                original_name=file_name,
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
        content: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if category_hint == "preview":
            return
        content_hash = hashlib.sha256(contact_vcard(media)).hexdigest()[:24]
        metadata = {
            "type": "contact",
            "id": getattr(media, "user_id", None),
            "mime": "text/vcard",
            "title": " ".join(
                filter(
                    None,
                    [
                        getattr(media, "first_name", None),
                        getattr(media, "last_name", None),
                    ],
                )
            ),
        }
        if content:
            metadata["content"] = sparse_json(dict(content))
        self.targets.append(
            DownloadTarget(
                obj=media,
                kind="contact",
                subtype="contact",
                role=role,
                message_id=self.message_id,
                cache_key=(
                    f"contact:{self.source_chat_id}:{self.message_id}:{content_hash}"
                ),
                extension=".vcf",
                expected_size=None,
                metadata=metadata,
                original_name=(
                    metadata["title"] or getattr(media, "phone_number", None)
                ),
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
            if category_hint == "preview":
                self.add_document_preview_image(
                    music,
                    f"{role}.music",
                    protected=story_protected,
                )
            else:
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
        try:
            self._discover_value(value, role, protected, category_hint)
        finally:
            self._visited.discard(object_id)

    def _discover_value(
        self,
        value: Any,
        role: str,
        protected: Optional[bool],
        category_hint: Optional[str],
    ) -> None:
        name = tl_name(value)
        active_protection = self.protected if protected is None else protected
        if name in {"Photo", "PhotoEmpty"}:
            self.add_photo(
                value,
                role,
                protected=active_protection,
                category_hint=category_hint,
            )
            return
        if name in {"Document", "DocumentEmpty"}:
            if category_hint == "preview":
                self.add_document_preview_image(
                    value,
                    role,
                    protected=active_protection,
                )
            else:
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
            preview_content = sparse_json(
                {
                    "width": getattr(value, "w", None),
                    "height": getattr(value, "h", None),
                    "video_duration": getattr(value, "video_duration", None),
                }
            )
            preview_added = self.add_embedded_photo_size(
                getattr(value, "thumb", None),
                f"{role}.accessible_preview",
                protected=active_protection,
                category_hint="preview",
                content=preview_content,
            )
            if not preview_added:
                self.metadata_record(
                    "paid_media_preview",
                    role,
                    value,
                    status="unavailable",
                    attachment_subtype="paid_media_preview",
                    category_hint="preview",
                    reason="paid_media_not_purchased",
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
        if name == "MessageMediaEmpty":
            return
        active_protection = self.protected if protected is None else protected
        semantic_category = category_hint
        semantic_status = "metadata_only"
        semantic_reason = None
        semantic_type = None
        omit_fields: tuple[str, ...] = ()
        if name == "MessageMediaWebPage":
            semantic_category = "preview"
            semantic_type = "link_preview"
            omit_fields = ("article",)
        elif name == "MessageMediaPaidMedia":
            omit_fields = ("items",)
        elif name == "MessageMediaStory":
            semantic_category = "stories"
            if getattr(media, "story", None) is None:
                semantic_status = "unavailable"
                semantic_reason = "story_not_returned_or_expired"
        elif name == "MessageMediaVideoStream":
            semantic_status = "not_downloadable"
        elif name == "MessageMediaUnsupported":
            semantic_status = "unsupported"
        if name not in {
            "MessageMediaPhoto",
            "MessageMediaDocument",
            "MessageMediaContact",
        }:
            self.semantic_record(
                media,
                role,
                type_override=semantic_type,
                category_hint=semantic_category,
                status=semantic_status,
                reason=semantic_reason,
                omit_fields=omit_fields,
                content_type_field=(
                    "webpage_type" if name == "MessageMediaWebPage" else None
                ),
            )

        if name == "MessageMediaPhoto":
            self.add_photo(
                getattr(media, "photo", None),
                f"{role}.photo",
                protected=active_protection,
                category_hint=category_hint,
                content=carrier_attachment_content(media),
            )
            live_video = getattr(media, "video", None)
            if live_video is not None and category_hint != "preview":
                self.add_document(
                    live_video,
                    f"{role}.live_photo_video",
                    protected=active_protection,
                    category_hint=category_hint,
                )
            return

        if name == "MessageMediaDocument":
            if category_hint == "preview":
                cover = getattr(media, "video_cover", None)
                if (
                    cover is not None
                    and best_photo_size(cover, allow_video=False) is not None
                ):
                    self.add_photo(
                        cover,
                        f"{role}.video_cover",
                        protected=active_protection,
                        category_hint="preview",
                        content=carrier_attachment_content(media),
                    )
                else:
                    self.add_document_preview_image(
                        getattr(media, "document", None),
                        f"{role}.document",
                        alternatives=getattr(media, "alt_documents", None) or [],
                        protected=active_protection,
                        content=carrier_attachment_content(media),
                    )
                return
            self.add_document(
                getattr(media, "document", None),
                f"{role}.document",
                alternatives=getattr(media, "alt_documents", None) or [],
                protected=active_protection,
                category_hint=category_hint,
                content=carrier_attachment_content(media),
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
                content=carrier_attachment_content(media),
            )
            return

        if name in {"MessageMediaGeo", "MessageMediaGeoLive", "MessageMediaVenue"}:
            return

        if name == "MessageMediaWebPage":
            webpage = getattr(media, "webpage", None)
            refresh_url = getattr(webpage, "url", None)
            if tl_name(webpage) == "WebPage":
                webpage_photo = getattr(webpage, "photo", None)
                if (
                    webpage_photo is not None
                    and best_photo_size(webpage_photo, allow_video=False) is not None
                ):
                    self.add_photo(
                        webpage_photo,
                        f"{role}.photo",
                        protected=active_protection,
                        refresh_url=refresh_url,
                        category_hint="preview",
                        title=getattr(webpage, "title", None),
                    )
                else:
                    self.add_document_preview_image(
                        getattr(webpage, "document", None),
                        f"{role}.document",
                        protected=active_protection,
                        refresh_url=refresh_url,
                        title=getattr(webpage, "title", None),
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
            self.discover(
                game,
                f"{role}.game",
                active_protection,
                category_hint="preview",
            )
            return

        if name == "MessageMediaInvoice":
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
            if story is not None:
                self.collect_story(
                    story,
                    f"{role}.story",
                    protected=active_protection,
                    category_hint=category_hint or "stories",
                )
            return

        if name in {
            "MessageMediaDice",
            "MessageMediaGiveaway",
            "MessageMediaGiveawayResults",
            "MessageMediaToDo",
            "MessageMediaVideoStream",
            "MessageMediaUnsupported",
        }:
            return

        raise RuntimeError(
            f"Unsupported Telegram media constructor {name!r}; update the "
            "current-layer exporter before continuing"
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
        self.semantic_record(
            action,
            "message.action",
            category_hint=action_category,
        )
        self.discover(
            action,
            "message.action",
            category_hint=action_category,
        )
        rich_message = getattr(message, "rich_message", None)
        self.semantic_record(
            rich_message,
            "message.rich_message",
            type_override="rich_message",
            category_hint="other",
        )
        self.discover(
            rich_message,
            "message.rich_message",
        )
        media = getattr(message, "media", None)
        webpage = (
            getattr(media, "webpage", None)
            if tl_name(media) == "MessageMediaWebPage"
            else None
        )
        article = getattr(webpage, "cached_page", None)
        self.semantic_record(
            article,
            "message.media.webpage.article",
            type_override="article",
            category_hint="preview",
        )
        self.semantic_record(
            getattr(message, "factcheck", None),
            "message.fact_check",
            type_override="fact_check",
            category_hint="other",
        )
        suggested_post = getattr(message, "suggested_post", None)
        if suggested_post is not None:
            self.semantic_record(
                suggested_post_data(suggested_post),
                "message.suggested_post",
                type_override="suggested_post",
                category_hint="other",
            )
        self.semantic_record(
            getattr(message, "entities", None) or [],
            "message.entities",
            type_override="text_entities",
            category_hint="other",
        )
        reply_markup = getattr(message, "reply_markup", None)
        self.semantic_record(
            reply_markup,
            "message.reply_markup",
            category_hint="other",
        )
        self.discover(reply_markup, "message.reply_markup", category_hint="other")
        self.semantic_record(
            getattr(reply, "quote_entities", None) or [],
            "message.reply_quote_entities",
            type_override="text_entities",
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


CheckpointKey = tuple[int, int]


@dataclass
class ExistingExportState:
    metadata: dict[str, Any]
    message_count: int
    byte_size: int
    sha256: str
    checkpoints: dict[CheckpointKey, int]
    first_created_epoch: Optional[int]
    last_created_epoch: Optional[int]
    has_undated_messages: bool
    peers: dict[str, Any]
    peer_avatars: list[dict[str, Any]]
    media_assets: dict[str, dict[str, Any]]


def checkpoint_key_from_source(source: HistorySource) -> CheckpointKey:
    return int(source.marked_id), int(source.topic_peer_id or 0)


def attachment_asset_key(record: Mapping[str, Any]) -> Optional[str]:
    value = record.get("asset_key")
    return str(value) if value else None


def is_current_attachment_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return (
        not path.is_absolute()
        and ".." not in path.parts
        and len(path.parts) >= 3
        and path.parts[0] == "files"
        and path.parts[1] in ATTACHMENT_CATEGORIES
    )


def effective_message_history_source(
    message: Mapping[str, Any],
) -> Optional[int]:
    """Resolve an omitted row history source from its semantic source."""

    value = (
        message.get("history_source")
        if "history_source" in message
        else message.get("source")
    )
    return value if type(value) is int and value != 0 else None


def validate_message_contract(message: Mapping[str, Any]) -> None:
    """Enforce invariants required by the current JSONL message schema."""

    pending: list[tuple[str, Any]] = [("message", message)]
    while pending:
        path, value = pending.pop()
        if isinstance(value, Mapping):
            for key, child in value.items():
                field = str(key)
                child_path = f"{path}.{field}"
                if field == "raw" or field.startswith("_"):
                    raise ValueError(f"{child_path} is not allowed")
                if field.endswith("_iso"):
                    raise ValueError(f"{child_path} is not allowed")
                pending.append((child_path, child))
        elif isinstance(value, list):
            pending.extend(
                (f"{path}[{index}]", child) for index, child in enumerate(value)
            )
        elif isinstance(value, (bytes, dt.datetime, dt.date, dt.time)):
            raise ValueError(f"{path} is not JSON-normalized")
        elif callable(getattr(value, "to_dict", None)):
            raise ValueError(f"{path} contains a Telegram object")

    message_id = message.get("id")
    if type(message_id) is not int or message_id <= 0:
        raise ValueError("id must be a positive integer")
    if "message" in message:
        raise ValueError("top-level message is not allowed; use id")

    for field_name in ("source", "author"):
        value = message.get(field_name)
        if type(value) is not int or value == 0:
            raise ValueError(f"{field_name} must be a non-zero integer")

    if "history_source" in message:
        history_source = message.get("history_source")
        if type(history_source) is not int or history_source == 0:
            raise ValueError("history_source must be a non-zero integer or omitted")
        if history_source == message.get("source"):
            raise ValueError("history_source must be omitted when it equals source")
    topic = message.get("monoforum_topic")
    if topic is not None:
        if not isinstance(topic, Mapping):
            raise ValueError("monoforum_topic must be an object or null")
        topic_peer_id = topic.get("peer_id")
        if type(topic_peer_id) is not int or topic_peer_id == 0:
            raise ValueError("monoforum_topic.peer_id must be a non-zero integer")
        top_message = topic.get("top_message")
        if top_message is not None and (
            type(top_message) is not int or top_message <= 0
        ):
            raise ValueError(
                "monoforum_topic.top_message must be a positive integer or null"
            )

    for field_name in ("created", "edited"):
        value = message.get(field_name)
        if value is not None and type(value) is not int:
            raise ValueError(f"{field_name} must be an integer timestamp or null")

    data = message.get("data")
    if data is not None and not isinstance(data, str):
        raise ValueError("data must be an unescaped MarkdownV2 string or null")
    if "formatted" in message:
        raise ValueError("top-level formatted is not allowed; keep text in data")
    report_delivery_until = message.get("report_delivery_until")
    if report_delivery_until is not None and type(report_delivery_until) is not int:
        raise ValueError(
            "report_delivery_until must be an integer timestamp or null"
        )

    forwarded = message.get("forwarded")
    if forwarded is not None:
        if not isinstance(forwarded, Mapping):
            raise ValueError("forwarded must be an object or null")
        forwarded_created = forwarded.get("created")
        if forwarded_created is not None and type(forwarded_created) is not int:
            raise ValueError("forwarded.created must be an integer timestamp or null")

    attachments = message.get("attachments")
    if attachments is not None and not isinstance(attachments, list):
        raise ValueError("attachments must be a list or null")
    for attachment in attachments or []:
        if not isinstance(attachment, Mapping):
            raise ValueError("attachment entries must be objects")
        unexpected_fields = set(attachment) - PUBLIC_ATTACHMENT_FIELD_SET
        if unexpected_fields:
            raise ValueError(
                "attachment entries contain unsupported fields: "
                + ", ".join(sorted(map(str, unexpected_fields)))
            )
        if not isinstance(attachment.get("type"), str) or not attachment.get("type"):
            raise ValueError("attachment.type must be a non-empty string")
        content = attachment.get("content")
        if content is not None and not isinstance(content, (Mapping, list)):
            raise ValueError("attachment.content must be an object or list")
        status = attachment.get("status")
        if status is not None and status not in {
            "failed",
            "not_downloadable",
            "protected",
            "skipped_limit",
            "unavailable",
            "unsupported",
        }:
            raise ValueError("attachment.status is unsupported")
        reason = attachment.get("reason")
        if reason is not None and (not isinstance(reason, str) or not reason):
            raise ValueError("attachment.reason must be a non-empty string or null")
        if reason is not None and status is None:
            raise ValueError("attachment.reason requires attachment.status")
        file_value = attachment.get("file")
        if file_value is not None:
            if not is_current_attachment_path(file_value):
                raise ValueError("attachment.file must be inside a current files category")
            attachment_hash = attachment.get("hash")
            if not isinstance(attachment_hash, str) or not re.fullmatch(
                r"[0-9a-f]{64}", attachment_hash
            ):
                raise ValueError("saved file attachments require a SHA-256 hash")
            if status is not None:
                raise ValueError("saved file attachments cannot have an error status")
        attachment_created = attachment.get("created")
        if attachment_created is not None and type(attachment_created) is not int:
            raise ValueError("attachment.created must be an integer timestamp or null")


def normalize_existing_file_record(
    record: Mapping[str, Any],
    output_dir: Path,
) -> Optional[dict[str, Any]]:
    """Return a cache record only for a regular file inside ``files/``."""

    relative_value = record.get("file")
    if not is_current_attachment_path(relative_value):
        return None
    relative_path = Path(str(relative_value))
    if relative_path.is_absolute():
        return None
    files_dir = output_dir / "files"
    candidate = output_dir / relative_path
    try:
        output_resolved = output_dir.resolve()
        files_resolved = files_dir.resolve()
        if files_dir.is_symlink() or not files_dir.is_dir():
            return None
        files_resolved.relative_to(output_resolved)
        candidate_resolved = candidate.resolve(strict=True)
        candidate_resolved.relative_to(files_resolved)
        normalized_relative = candidate_resolved.relative_to(output_resolved)
    except (FileNotFoundError, OSError, ValueError):
        return None
    if candidate.is_symlink() or not candidate.is_file():
        return None
    normalized = dict(record)
    normalized["file"] = normalized_relative.as_posix()
    normalized["downloaded_size"] = candidate.stat().st_size
    return normalized


def parse_checkpoint_metadata(value: Any) -> dict[CheckpointKey, int]:
    if not isinstance(value, list):
        raise ValueError("history_checkpoints must be a list")
    checkpoints: dict[CheckpointKey, int] = {}
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("history checkpoint entries must be objects")
        history_source = item.get("history_source")
        topic_peer_id_value = item.get("topic_peer_id")
        max_message_id = item.get("max_message_id")
        if type(history_source) is not int or history_source == 0:
            raise ValueError("history checkpoint source must be a non-zero integer")
        if topic_peer_id_value is not None and (
            type(topic_peer_id_value) is not int or topic_peer_id_value == 0
        ):
            raise ValueError("history checkpoint topic must be null or non-zero integer")
        if type(max_message_id) is not int or max_message_id <= 0:
            raise ValueError("history checkpoint message IDs must be positive integers")
        topic_peer_id = topic_peer_id_value or 0
        key = (history_source, topic_peer_id)
        if key in checkpoints:
            raise ValueError("history checkpoint keys must be unique")
        checkpoints[key] = max_message_id
    return checkpoints


def load_existing_export(
    messages_path: Path,
    metadata_path: Path,
    overwrite: bool,
    expected_chat_id: int,
) -> Optional[ExistingExportState]:
    if overwrite:
        return None
    messages_exists = messages_path.exists()
    metadata_exists = metadata_path.exists()
    if not messages_exists and not metadata_exists:
        return None
    if messages_exists != metadata_exists:
        raise FileExistsError(
            "The existing JSONL export pair is incomplete; use --overwrite to "
            "rebuild it"
        )
    if (
        messages_path.is_symlink()
        or metadata_path.is_symlink()
        or not messages_path.is_file()
        or not metadata_path.is_file()
    ):
        raise RuntimeError(
            "Existing export files must be regular, non-symbolic-link files"
        )

    try:
        metadata_value = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Cannot read existing export metadata {metadata_path}: {error_text(exc)}"
        ) from exc
    if not isinstance(metadata_value, dict):
        raise RuntimeError(f"Existing metadata {metadata_path} is not a JSON object")
    if metadata_value.get("schema") != SCHEMA_NAME:
        raise RuntimeError(
            f"Unsupported existing export schema {metadata_value.get('schema')!r}"
        )
    schema_version_value = metadata_value.get("schema_version")
    if type(schema_version_value) is not int:
        raise RuntimeError("Existing export schema version is not an integer")
    if schema_version_value != SCHEMA_VERSION:
        raise RuntimeError(
            f"Existing export schema version {schema_version_value} is unsupported; "
            f"this exporter requires version {SCHEMA_VERSION}; use --overwrite "
            "to rebuild it"
        )
    if metadata_value.get("attachment_hash_algorithm") != "sha256":
        raise RuntimeError("Existing export uses an unsupported attachment hash")
    if metadata_value.get("messages_file") != messages_path.name:
        raise RuntimeError("Existing metadata points to a different messages file")
    if metadata_value.get("messages_format") != "jsonl":
        raise RuntimeError("Existing messages file is not declared as JSONL")
    if metadata_value.get("messages_order") != "oldest_to_newest_by_created_at":
        raise RuntimeError("Existing JSONL does not use the required chronological order")
    if metadata_value.get("order") != metadata_value["messages_order"]:
        raise RuntimeError("Existing metadata order fields do not match")
    if type(metadata_value.get("exported_at")) is not int:
        raise RuntimeError("Existing metadata field exported_at is invalid")
    if not isinstance(metadata_value.get("telethon_version"), str):
        raise RuntimeError("Existing metadata field telethon_version is invalid")
    telegram_layer = metadata_value.get("telegram_layer")
    if (
        type(telegram_layer) is not int
        or telegram_layer != SUPPORTED_TELEGRAM_LAYER
    ):
        raise RuntimeError(
            "Existing metadata uses a different Telegram schema layer"
        )
    chat_value = metadata_value.get("chat")
    if (
        not isinstance(chat_value, Mapping)
        or type(chat_value.get("id")) is not int
        or chat_value.get("id") != expected_chat_id
    ):
        raise RuntimeError("Existing metadata belongs to a different Telegram chat")
    if "monoforum_scope" not in chat_value or not isinstance(
        chat_value.get("history_sources"), list
    ):
        raise RuntimeError("Existing chat metadata is missing current schema fields")

    expected_count_value = metadata_value.get("messages_count")
    expected_bytes_value = metadata_value.get("messages_bytes")
    expected_sha256 = metadata_value.get("messages_sha256")
    if type(expected_count_value) is not int or expected_count_value < 0:
        raise RuntimeError("Existing JSONL message count is invalid")
    if type(expected_bytes_value) is not int or expected_bytes_value < 0:
        raise RuntimeError("Existing JSONL byte count is invalid")
    if not isinstance(expected_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", expected_sha256
    ):
        raise RuntimeError("Existing JSONL SHA-256 is invalid")
    expected_count = expected_count_value
    expected_bytes = expected_bytes_value
    actual_bytes = messages_path.stat().st_size
    if actual_bytes != expected_bytes:
        raise RuntimeError(
            f"Existing JSONL size is {actual_bytes}, expected {expected_bytes}; "
            "use --overwrite to rebuild it"
        )

    raw_checkpoints = metadata_value.get("history_checkpoints")
    try:
        stored_checkpoints = parse_checkpoint_metadata(raw_checkpoints)
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            f"Invalid existing history checkpoints: {error_text(exc)}"
        ) from exc

    for field_name in ("messages_first_created", "messages_last_created"):
        field_value = metadata_value.get(field_name)
        if field_name not in metadata_value or (
            field_value is not None and type(field_value) is not int
        ):
            raise RuntimeError(f"Existing metadata field {field_name} is invalid")
    if type(metadata_value.get("messages_have_undated")) is not bool:
        raise RuntimeError(
            "Existing metadata field messages_have_undated is invalid"
        )
    media_assets_value = metadata_value.get("media_assets")
    if not isinstance(media_assets_value, Mapping) or any(
        not isinstance(asset_key, str) or not isinstance(asset, Mapping)
        for asset_key, asset in media_assets_value.items()
    ):
        raise RuntimeError("Existing metadata field media_assets is invalid")
    if any(
        asset.get("file") and not is_current_attachment_path(asset["file"])
        for asset in media_assets_value.values()
    ):
        raise RuntimeError("Existing media asset paths do not match current schema")
    if any(
        asset.get("file")
        and (
            not isinstance(asset.get("hash"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", str(asset.get("hash")))
            or not isinstance(asset.get("identity"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", str(asset.get("identity")))
        )
        for asset in media_assets_value.values()
    ):
        raise RuntimeError(
            "Existing media assets must include SHA-256 hashes and identities"
        )
    if not isinstance(metadata_value.get("peers"), Mapping):
        raise RuntimeError("Existing metadata field peers is invalid")
    if not isinstance(metadata_value.get("peer_avatars"), list):
        raise RuntimeError("Existing metadata field peer_avatars is invalid")
    summary_value = metadata_value.get("summary")
    if not isinstance(summary_value, Mapping):
        raise RuntimeError("Existing metadata field summary is invalid")
    started_at = summary_value.get("started_at")
    finished_at = summary_value.get("finished_at")
    duration_seconds = summary_value.get("duration_seconds")
    if (
        type(summary_value.get("messages")) is not int
        or summary_value.get("messages") != expected_count
        or any(
            type(summary_value.get(field_name)) is not bool
            for field_name in (
                "complete",
                "complete_accessible",
                "history_complete",
            )
        )
    ):
        raise RuntimeError("Existing export summary does not match current schema")
    if (
        type(started_at) is not int
        or type(finished_at) is not int
        or finished_at < started_at
    ):
        raise RuntimeError("Existing export summary timestamps are invalid")
    if type(duration_seconds) is int:
        duration_value = float(duration_seconds)
    elif type(duration_seconds) is float:
        duration_value = duration_seconds
    else:
        raise RuntimeError("Existing export summary duration is invalid")
    if duration_value < 0:
        raise RuntimeError("Existing export summary duration is invalid")

    output_dir = messages_path.parent
    # Current-schema metadata is the checkpoint and media index. The writer
    # still verifies the JSONL byte size, line count, and SHA-256 while copying
    # it into the safe publication file before any new rows are appended.
    media_assets: dict[str, dict[str, Any]] = {}
    for asset_key, asset in media_assets_value.items():
        if not asset.get("file"):
            continue
        normalized_asset = normalize_existing_file_record(asset, output_dir)
        if normalized_asset is not None:
            media_assets[str(asset_key)] = normalized_asset

    peers_value = metadata_value.get("peers")
    peers = dict(peers_value) if isinstance(peers_value, Mapping) else {}
    avatar_value = metadata_value.get("peer_avatars")
    peer_avatars: list[dict[str, Any]] = []
    for item in avatar_value or []:
        if not isinstance(item, Mapping):
            raise RuntimeError("Existing peer avatar entries must be objects")
        avatar_created = item.get("created")
        if avatar_created is not None and type(avatar_created) is not int:
            raise RuntimeError(
                "Peer avatar created must be an integer timestamp or null"
            )
        if item.get("file"):
            if not is_current_attachment_path(item["file"]):
                raise RuntimeError(
                    "Peer avatar file paths must use a category under files/"
                )
            if attachment_asset_key(item) is None:
                raise RuntimeError("File-backed peer avatars must include asset_key")
            if not isinstance(item.get("hash"), str) or not re.fullmatch(
                r"[0-9a-f]{64}", str(item.get("hash"))
            ):
                raise RuntimeError("File-backed peer avatars must include SHA-256")
            normalized_avatar = normalize_existing_file_record(item, output_dir)
            if normalized_avatar is None:
                continue
            avatar = normalized_avatar
        else:
            avatar = dict(item)
        peer_avatars.append(avatar)
        asset_key = attachment_asset_key(avatar)
        if not avatar.get("file") or not asset_key:
            continue
        media_assets.setdefault(
            asset_key,
            {
                "file": avatar["file"],
                "hash": avatar["hash"],
                "identity": media_asset_identity(asset_key, avatar),
                "downloaded_size": avatar["downloaded_size"],
                "first_message": 0,
            },
        )
    return ExistingExportState(
        metadata=metadata_value,
        message_count=expected_count,
        byte_size=actual_bytes,
        sha256=expected_sha256,
        checkpoints=stored_checkpoints,
        first_created_epoch=metadata_value["messages_first_created"],
        last_created_epoch=metadata_value["messages_last_created"],
        has_undated_messages=metadata_value["messages_have_undated"],
        peers=peers,
        peer_avatars=peer_avatars,
        media_assets=media_assets,
    )


def recover_pending_export_publication(
    messages_path: Path,
    metadata_path: Path,
) -> bool:
    """Restore the previous pair before inspecting incremental state."""

    messages_backup_path = messages_path.with_name(
        f".{messages_path.name}.publish-backup"
    )
    metadata_backup_path = metadata_path.with_name(
        f".{metadata_path.name}.publish-backup"
    )
    marker_path = messages_path.with_name(
        f".{messages_path.stem}.publish-in-progress.json"
    )
    marker_partial_path = marker_path.with_suffix(marker_path.suffix + ".part")
    if not marker_path.exists():
        return False
    try:
        state = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Cannot read export publication journal {marker_path}: "
            f"{error_text(exc)}"
        ) from exc
    required_keys = (
        "messages_had_previous",
        "metadata_had_previous",
    )
    if not isinstance(state, Mapping) or any(
        key not in state or type(state[key]) is not bool for key in required_keys
    ):
        raise RuntimeError(f"Invalid export publication journal {marker_path}")
    pairs = (
        (
            messages_path,
            messages_backup_path,
            state["messages_had_previous"],
        ),
        (
            metadata_path,
            metadata_backup_path,
            state["metadata_had_previous"],
        ),
    )
    for final_path, backup_path, had_previous in pairs:
        if had_previous:
            if backup_path.exists():
                os.replace(backup_path, final_path)
            elif not final_path.exists():
                raise RuntimeError(
                    f"Cannot restore missing prior export file {final_path}"
                )
        else:
            final_path.unlink(missing_ok=True)
            backup_path.unlink(missing_ok=True)
    marker_path.unlink(missing_ok=True)
    marker_partial_path.unlink(missing_ok=True)
    try:
        directory_fd = os.open(messages_path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError:
        pass
    print(
        f"Recovered the previous complete export after an interrupted "
        f"publication in {messages_path.parent}",
        file=sys.stderr,
        flush=True,
    )
    return True


class JsonlExportWriter:
    """Stream chronological messages into an atomically published JSONL pair."""

    def __init__(
        self,
        messages_path: Path,
        metadata_path: Path,
        header: Mapping[str, Any],
        overwrite: bool,
        existing: Optional[ExistingExportState] = None,
    ) -> None:
        if overwrite and existing is not None:
            raise ValueError("Full overwrite cannot also use incremental state")
        self.messages_path = messages_path
        self.metadata_path = metadata_path
        self.messages_partial_path = messages_path.with_suffix(
            messages_path.suffix + ".part"
        )
        self.metadata_partial_path = metadata_path.with_suffix(
            metadata_path.suffix + ".part"
        )
        self.messages_backup_path = messages_path.with_name(
            f".{messages_path.name}.publish-backup"
        )
        self.metadata_backup_path = metadata_path.with_name(
            f".{metadata_path.name}.publish-backup"
        )
        self.publication_marker_path = messages_path.with_name(
            f".{messages_path.stem}.publish-in-progress.json"
        )
        self.publication_marker_partial_path = self.publication_marker_path.with_suffix(
            self.publication_marker_path.suffix + ".part"
        )
        self.header = dict(header)
        self.existing = existing
        self.checkpoints = dict(existing.checkpoints) if existing else {}
        self.message_count = 0
        self.byte_size = 0
        self.digest = hashlib.sha256()
        self.first_created_epoch = existing.first_created_epoch if existing else None
        self.last_created_epoch = existing.last_created_epoch if existing else None
        self.has_undated_messages = (
            existing.has_undated_messages if existing else False
        )
        self.last_order_key: Optional[tuple[int, int]] = None
        if existing is not None and existing.message_count:
            if existing.has_undated_messages:
                self.last_order_key = (1, 0)
            elif existing.last_created_epoch is not None:
                self.last_order_key = (0, existing.last_created_epoch)
            else:
                raise RuntimeError("Existing non-empty JSONL has no ordering boundary")
        self.closed = False
        self.published = False

        self.recover_incomplete_publication()
        for stale_backup in (
            self.messages_backup_path,
            self.metadata_backup_path,
        ):
            stale_backup.unlink(missing_ok=True)

        completed_paths = [messages_path, metadata_path]
        existing_paths = [path for path in completed_paths if path.exists()]
        if existing_paths and not overwrite and self.existing is None:
            names = ", ".join(path.name for path in existing_paths)
            raise FileExistsError(
                f"Export output already exists ({names}); use --overwrite to "
                "replace it after a complete export"
            )

        for path in (
            self.messages_partial_path,
            self.metadata_partial_path,
            self.publication_marker_partial_path,
        ):
            path.unlink(missing_ok=True)

        self.output = self.messages_partial_path.open("wb")
        if existing is not None:
            try:
                self.copy_and_validate_existing(existing)
            except BaseException:
                self.output.close()
                self.closed = True
                self.messages_partial_path.unlink(missing_ok=True)
                raise

    def copy_and_validate_existing(self, existing: ExistingExportState) -> None:
        """Copy the prior JSONL and rederive all state used to resume it."""

        checkpoints: dict[CheckpointKey, int] = {}
        media_assets = dict(existing.media_assets)
        referenced_media_files: dict[str, str] = {}
        referenced_media_records: dict[str, list[dict[str, Any]]] = {}
        verified_file_hashes: dict[str, str] = {}
        first_created_epoch: Optional[int] = None
        last_created_epoch: Optional[int] = None
        has_undated = False
        previous_order_key: Optional[tuple[int, int]] = None
        copied_count = 0

        def verified_file_hash(relative_file: str) -> str:
            actual = verified_file_hashes.get(relative_file)
            if actual is None:
                actual = file_sha256(self.messages_path.parent / relative_file)
                verified_file_hashes[relative_file] = actual
            return actual

        with self.messages_path.open("rb") as previous:
            for line_number, line in enumerate(previous, start=1):
                self.output.write(line)
                self.digest.update(line)
                self.byte_size += len(line)
                copied_count += 1
                if not line.endswith(b"\n"):
                    raise RuntimeError(
                        f"Existing JSONL line {line_number} has no terminating newline"
                    )
                try:
                    message = json.loads(line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise RuntimeError(
                        f"Invalid existing JSONL message on line {line_number}: "
                        f"{error_text(exc)}"
                    ) from exc
                if not isinstance(message, Mapping):
                    raise RuntimeError(
                        f"Existing JSONL line {line_number} is not a message object"
                    )

                try:
                    validate_message_contract(message)
                    message_id = message.get("id")
                    history_source = effective_message_history_source(message)
                    if type(message_id) is not int or message_id <= 0:
                        raise ValueError("message ID must be a positive integer")
                    if history_source is None:
                        raise ValueError(
                            "history_source/source must resolve to a non-zero integer"
                        )
                    topic = message.get("monoforum_topic")
                    if topic is not None and not isinstance(topic, Mapping):
                        raise ValueError("monoforum_topic must be an object or null")
                    topic_peer_id = (
                        topic.get("peer_id") if isinstance(topic, Mapping) else 0
                    )
                    if topic is not None and (
                        type(topic_peer_id) is not int or topic_peer_id == 0
                    ):
                        raise ValueError(
                            "monoforum topic peer_id must be a non-zero integer"
                        )
                    checkpoint_key = (history_source, int(topic_peer_id or 0))
                    if message_id <= checkpoints.get(checkpoint_key, 0):
                        raise ValueError(
                            "message IDs must increase within each history source"
                        )
                    checkpoints[checkpoint_key] = message_id

                    created = message.get("created")
                    if created is not None and type(created) is not int:
                        raise ValueError(
                            "created must be an integer timestamp or null"
                        )
                    order_key = (1, 0) if created is None else (0, created)
                    if (
                        previous_order_key is not None
                        and order_key < previous_order_key
                    ):
                        raise ValueError(
                            "messages must be ordered oldest-to-newest by created"
                        )
                    previous_order_key = order_key
                    if created is None:
                        has_undated = True
                    else:
                        first_created_epoch = (
                            created
                            if first_created_epoch is None
                            else min(first_created_epoch, created)
                        )
                        last_created_epoch = (
                            created
                            if last_created_epoch is None
                            else max(last_created_epoch, created)
                        )

                    attachments = message.get("attachments") or []
                    if not isinstance(attachments, list):
                        raise ValueError("attachments must be a list")
                    for attachment in attachments:
                        if not isinstance(attachment, Mapping):
                            raise ValueError("attachment entries must be objects")
                        unexpected_fields = (
                            set(attachment) - PUBLIC_ATTACHMENT_FIELD_SET
                        )
                        if unexpected_fields:
                            raise ValueError(
                                "attachment entries contain unsupported fields: "
                                + ", ".join(sorted(map(str, unexpected_fields)))
                            )
                        if not isinstance(attachment.get("type"), str) or not str(
                            attachment["type"]
                        ):
                            raise ValueError("attachment type must be a non-empty string")
                        if not attachment.get("file"):
                            continue
                        if not is_current_attachment_path(attachment["file"]):
                            raise ValueError(
                                "attachment files must use a category under files/"
                            )
                        attachment_hash = attachment.get("hash")
                        if not isinstance(attachment_hash, str) or not re.fullmatch(
                            r"[0-9a-f]{64}", attachment_hash
                        ):
                            raise ValueError(
                                "saved attachments must include a SHA-256 hash"
                            )
                        normalized = normalize_existing_file_record(
                            attachment,
                            self.messages_path.parent,
                        )
                        if normalized is None:
                            raise ValueError(
                                "saved attachment file is missing or unsafe"
                            )
                        relative_file = str(normalized["file"])
                        if verified_file_hash(relative_file) != attachment_hash:
                            raise ValueError(
                                "saved attachment content does not match its hash"
                            )
                        previous_hash = referenced_media_files.setdefault(
                            relative_file,
                            attachment_hash,
                        )
                        if previous_hash != attachment_hash:
                            raise ValueError(
                                "attachments disagree about a saved file hash"
                            )
                        referenced_media_records.setdefault(relative_file, []).append(
                            public_attachment_record(attachment)
                        )
                except (TypeError, ValueError) as exc:
                    raise RuntimeError(
                        f"Invalid existing JSONL message on line {line_number}: "
                        f"{error_text(exc)}"
                    ) from exc

        for avatar in existing.peer_avatars:
            if not avatar.get("file"):
                continue
            avatar_hash = avatar.get("hash")
            if not isinstance(avatar_hash, str) or not re.fullmatch(
                r"[0-9a-f]{64}", avatar_hash
            ):
                raise RuntimeError("Saved peer avatars must include a SHA-256 hash")
            avatar_file = str(avatar["file"])
            if verified_file_hash(avatar_file) != avatar_hash:
                raise RuntimeError("Saved peer avatar content has a wrong SHA-256")
            referenced_media_files[avatar_file] = avatar_hash
            referenced_media_records.setdefault(avatar_file, []).append(
                public_attachment_record(avatar)
            )

        for asset_key, asset in media_assets.items():
            relative_file = str(asset.get("file") or "")
            asset_hash = asset.get("hash")
            identity = asset.get("identity")
            identity_matches = isinstance(identity, str) and any(
                media_asset_identity(str(asset_key), attachment) == identity
                for attachment in referenced_media_records.get(relative_file, [])
            )
            if (
                not relative_file
                or not isinstance(asset_hash, str)
                or not re.fullmatch(r"[0-9a-f]{64}", asset_hash)
                or referenced_media_files.get(relative_file) != asset_hash
                or not identity_matches
            ):
                raise RuntimeError(
                    f"Media cache entry {asset_key!r} is not backed by a saved "
                    "attachment"
                )

        if (
            copied_count != existing.message_count
            or self.byte_size != existing.byte_size
            or self.digest.hexdigest() != existing.sha256
        ):
            raise RuntimeError(
                "Existing JSONL count/checksum does not match its metadata"
            )
        if (
            checkpoints != existing.checkpoints
            or first_created_epoch != existing.first_created_epoch
            or last_created_epoch != existing.last_created_epoch
            or has_undated != existing.has_undated_messages
        ):
            raise RuntimeError(
                "Existing JSONL resume state does not match its metadata; use "
                "--overwrite to rebuild it"
            )

        self.message_count = copied_count
        self.checkpoints = checkpoints
        self.first_created_epoch = first_created_epoch
        self.last_created_epoch = last_created_epoch
        self.has_undated_messages = has_undated
        self.last_order_key = previous_order_key

    def fsync_output_directory(self) -> None:
        try:
            directory_fd = os.open(self.messages_path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            # Some platforms/filesystems do not support fsync on directories.
            pass

    def publication_state(self) -> dict[str, bool]:
        return {
            "messages_had_previous": self.messages_path.exists(),
            "metadata_had_previous": self.metadata_path.exists(),
        }

    def write_publication_marker(self, state: Mapping[str, bool]) -> None:
        with self.publication_marker_partial_path.open(
            "w", encoding="utf-8"
        ) as output:
            json.dump(dict(state), output, separators=(",", ":"))
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(
            self.publication_marker_partial_path,
            self.publication_marker_path,
        )
        self.fsync_output_directory()

    def rollback_publication(self, state: Mapping[str, Any]) -> None:
        pairs = (
            (
                self.messages_path,
                self.messages_backup_path,
                bool(state.get("messages_had_previous")),
            ),
            (
                self.metadata_path,
                self.metadata_backup_path,
                bool(state.get("metadata_had_previous")),
            ),
        )
        for final_path, backup_path, had_previous in pairs:
            if had_previous:
                if backup_path.exists():
                    os.replace(backup_path, final_path)
                elif not final_path.exists():
                    raise RuntimeError(
                        f"Cannot restore missing prior export file {final_path}"
                    )
                # No backup plus an existing final means publication stopped
                # before this prior file was moved; leave it intact.
            else:
                final_path.unlink(missing_ok=True)
                backup_path.unlink(missing_ok=True)
        self.publication_marker_path.unlink(missing_ok=True)
        self.publication_marker_partial_path.unlink(missing_ok=True)
        self.fsync_output_directory()

    def recover_incomplete_publication(self) -> None:
        recover_pending_export_publication(
            self.messages_path,
            self.metadata_path,
        )

    def publish_pair(self) -> None:
        state = self.publication_state()
        self.write_publication_marker(state)
        try:
            if state["messages_had_previous"]:
                os.replace(self.messages_path, self.messages_backup_path)
            if state["metadata_had_previous"]:
                os.replace(self.metadata_path, self.metadata_backup_path)
            os.replace(self.messages_partial_path, self.messages_path)
            os.replace(self.metadata_partial_path, self.metadata_path)
            self.fsync_output_directory()
            self.publication_marker_path.unlink()
            self.fsync_output_directory()
            self.published = True
        except BaseException as publish_exc:
            try:
                self.rollback_publication(state)
            except BaseException as rollback_exc:
                raise RuntimeError(
                    f"Export publication failed ({error_text(publish_exc)}) and "
                    f"rollback also failed ({error_text(rollback_exc)}); inspect "
                    f"{self.publication_marker_path} before retrying"
                ) from publish_exc
            raise

        for backup_path in (
            self.messages_backup_path,
            self.metadata_backup_path,
        ):
            try:
                backup_path.unlink(missing_ok=True)
            except OSError as exc:
                print(
                    f"Could not remove publication backup {backup_path}: "
                    f"{error_text(exc)}",
                    file=sys.stderr,
                )

    def write_message(
        self,
        message: Mapping[str, Any],
    ) -> None:
        if self.closed:
            raise RuntimeError("Cannot write to a closed JSONL export")
        validate_message_contract(message)
        created = message.get("created")
        created_epoch = created if type(created) is int else None
        self.ensure_order(created_epoch)
        order_key = (1, 0) if created_epoch is None else (0, created_epoch)
        message_id = int(message.get("id") or 0)
        history_source = effective_message_history_source(message)
        if history_source is None:
            raise RuntimeError(
                "Message history_source/source does not identify a history stream"
            )
        topic = message.get("monoforum_topic")
        topic_peer_id = (
            int(topic.get("peer_id") or 0) if isinstance(topic, Mapping) else 0
        )
        checkpoint_key = (history_source, topic_peer_id)
        previous_message_id = self.checkpoints.get(checkpoint_key, 0)
        if message_id <= previous_message_id:
            raise RuntimeError(
                f"Message ID {message_id} does not advance history checkpoint "
                f"{checkpoint_key} after {previous_message_id}"
            )
        self.checkpoints[checkpoint_key] = message_id
        if created_epoch is None:
            self.has_undated_messages = True
        else:
            self.first_created_epoch = (
                created_epoch
                if self.first_created_epoch is None
                else min(self.first_created_epoch, created_epoch)
            )
            self.last_created_epoch = (
                created_epoch
                if self.last_created_epoch is None
                else max(self.last_created_epoch, created_epoch)
            )
        line = (
            json.dumps(
                sparse_json(message),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        self.output.write(line)
        self.digest.update(line)
        self.byte_size += len(line)
        self.message_count += 1
        self.last_order_key = order_key

    def ensure_order(self, created_epoch: Optional[int]) -> None:
        order_key = (1, 0) if created_epoch is None else (0, created_epoch)
        if self.last_order_key is not None and order_key < self.last_order_key:
            raise RuntimeError(
                "Telegram returned a new message older than the JSONL tail; "
                "cannot append while preserving oldest-to-newest order"
            )

    def messages_state(self) -> dict[str, Any]:
        return {
            "file": self.messages_path.name,
            "format": "jsonl",
            "order": "oldest_to_newest_by_created_at",
            "count": self.message_count,
            "bytes": self.byte_size,
            "sha256": self.digest.hexdigest(),
            "first_created": self.first_created_epoch,
            "last_created": self.last_created_epoch,
            "have_undated": self.has_undated_messages,
            "history_checkpoints": [
                {
                    "history_source": history_source,
                    "topic_peer_id": topic_peer_id or None,
                    "max_message_id": max_message_id,
                }
                for (history_source, topic_peer_id), max_message_id in sorted(
                    self.checkpoints.items()
                )
            ],
        }

    def write_metadata_partial(
        self,
        messages: Mapping[str, Any],
        peers: Mapping[str, Any],
        peer_avatars: Iterable[Mapping[str, Any]],
        media_assets: Mapping[str, Mapping[str, Any]],
        summary: Mapping[str, Any],
    ) -> None:
        metadata = {
            **self.header,
            "messages_file": messages["file"],
            "messages_format": messages["format"],
            "messages_order": messages["order"],
            "messages_count": messages["count"],
            "messages_bytes": messages["bytes"],
            "messages_sha256": messages["sha256"],
            "messages_first_created": messages["first_created"],
            "messages_last_created": messages["last_created"],
            "messages_have_undated": messages["have_undated"],
            "history_checkpoints": messages["history_checkpoints"],
            "peers": json_safe(peers),
            "peer_avatars": json_safe(list(peer_avatars)),
            "media_assets": json_safe(media_assets),
            "summary": json_safe(summary),
        }
        with self.metadata_partial_path.open("w", encoding="utf-8") as output:
            json.dump(
                json_safe(metadata),
                output,
                ensure_ascii=False,
                indent=2,
            )
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())

    def finish(
        self,
        peers: Mapping[str, Any],
        peer_avatars: Iterable[Mapping[str, Any]],
        media_assets: Mapping[str, Mapping[str, Any]],
        summary: Mapping[str, Any],
    ) -> None:
        if self.closed:
            raise RuntimeError("JSONL export writer is already closed")
        self.output.flush()
        os.fsync(self.output.fileno())
        self.output.close()
        self.closed = True
        messages = self.messages_state()
        expected_count = int(summary.get("messages") or 0)
        if int(messages["count"]) != expected_count:
            raise RuntimeError(
                f"JSONL message count {messages['count']} does not match "
                f"export summary {expected_count}"
            )
        self.write_metadata_partial(
            messages,
            peers,
            peer_avatars,
            media_assets,
            summary,
        )

        # Journal and roll back the two-file replacement as a unit if either
        # rename fails. The metadata checksum remains the consumer-side
        # completion check for an unexpected process or machine stop.
        self.publish_pair()

    def close_incomplete(self) -> None:
        if not self.closed:
            try:
                self.output.flush()
                self.output.close()
            except Exception:
                pass
            finally:
                self.closed = True

    def incomplete_paths(self) -> list[Path]:
        return [
            path
            for path in (
                self.messages_partial_path,
                self.metadata_partial_path,
                self.publication_marker_partial_path,
                self.publication_marker_path,
                self.messages_backup_path,
                self.metadata_backup_path,
            )
            if path.exists()
        ]


class ChatExporter:
    def __init__(
        self,
        base_client: TelegramClient,
        self_entity: Any,
        entity: Any,
        input_peer: Any,
        output_dir: Path,
        args: argparse.Namespace,
    ) -> None:
        self.base_client = base_client
        self.self_id = marked_chat_id(self_entity)
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
        self.referenced_files: set[str] = set()
        self.emoji_documents: dict[int, Any] = {}
        self.unresolved_emoji: set[int] = set()
        self.story_cache: dict[tuple[Optional[int], int], Any] = {}
        self.unresolved_stories: set[tuple[Optional[int], int]] = set()
        self.available_effects_loaded = False
        self.message_effects: dict[int, dict[str, Any]] = {}
        self.webfile_dc_id: Optional[int] = None
        self.peers: dict[str, Any] = {
            str(self.chat_id): json_safe(entity),
            str(self.self_id): json_safe(self_entity),
        }
        self.peer_entities: dict[int, Any] = {
            self.chat_id: entity,
            self.self_id: self_entity,
        }
        self.peer_avatar_records: list[dict[str, Any]] = []
        self.existing_export: Optional[ExistingExportState] = None
        self.incremental = False
        self.existing_avatar_keys: set[tuple[int, int]] = set()

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

    async def get_webfile_dc_id(self) -> int:
        if self.webfile_dc_id is None:
            config = await self.rpc(
                lambda: self.base_client(functions.help.GetConfigRequest()),
                "Telegram web-file data center lookup",
            )
            self.stats.metadata_requests += 1
            await self.pacer.after_metadata()
            self.webfile_dc_id = int(config.webfile_dc_id)
        return self.webfile_dc_id

    def remember_peers(self, response: Any) -> None:
        for entity in [
            *(getattr(response, "users", None) or []),
            *(getattr(response, "chats", None) or []),
        ]:
            marked_id = peer_id(entity)
            if marked_id is not None:
                self.peers[str(marked_id)] = json_safe(entity)
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

    def log_media_issue(
        self,
        target: DownloadTarget,
        record: Mapping[str, Any],
        relative_path: str,
    ) -> None:
        entry = {
            "at": unix_timestamp(utc_now()),
            "chat_id": self.chat_id,
            "source_chat_id": target.source_chat_id,
            "message_id": target.message_id,
            "role": target.role,
            "category": record.get("category"),
            "kind": target.kind,
            "cache_key": target.cache_key,
            "media_id": target.metadata.get("id"),
            "source_url": safe_url_for_log(target.refresh_url),
            "intended_file": relative_path,
            "status": record.get("status"),
            "reason": record.get("reason"),
            "error_type": record.get("error_type"),
            "error": record.get("error"),
            "attempts": record.get("attempts"),
            "file_reference_refresh": record.get("file_reference_refresh"),
        }
        with self.error_log_path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(sparse_json(entry), ensure_ascii=False) + "\n")

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
            refresh_url = target.refresh_url
            if refresh_url:
                preview = await self.rpc(
                    lambda: self.base_client(
                        functions.messages.GetWebPagePreviewRequest(
                            message=refresh_url
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
                input_channel = utils.get_input_channel(source_peer)
                if input_channel is None:
                    raise RuntimeError(
                        f"Could not refresh channel message {target.message_id}: "
                        "source peer has no input-channel representation"
                    )
                query: Any = functions.channels.GetMessagesRequest(
                    channel=input_channel,
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
        record["asset_key"] = target.cache_key
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
            cache["identity"] = media_asset_identity(
                target.cache_key,
                {**record, **cache},
            )
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
                if not cached.get("hash"):
                    cached["hash"] = file_sha256(cached_path)
                self.referenced_files.add(str(cached["file"]))
                record.update(
                    status="reused",
                    file=cached["file"],
                    hash=cached["hash"],
                    downloaded_size=cached["downloaded_size"],
                    reused_from=cached.get("first_message"),
                )
                return record

        if usable_file(final_path):
            existing_size = final_path.stat().st_size
            cache = {
                "file": relative_path,
                "hash": file_sha256(final_path),
                "downloaded_size": existing_size,
                "first_message": target.message_id,
            }
            remember_asset(cache)
            self.referenced_files.add(relative_path)
            record.update(status="existing", **cache)
            return record

        asset = self.media_asset_cache.get(target.cache_key)
        if asset:
            asset_path = self.output_dir / str(asset["file"])
            if usable_file(asset_path):
                clone_file(asset_path, final_path)
                cloned_hash = file_sha256(final_path)
                if asset.get("hash") and asset["hash"] != cloned_hash:
                    final_path.unlink(missing_ok=True)
                    self.media_asset_cache.pop(target.cache_key, None)
                    print(
                        f"Ignored corrupt cached media {asset['file']} for "
                        f"{target.role}; downloading it again",
                        file=sys.stderr,
                        flush=True,
                    )
                else:
                    cache = {
                        "file": relative_path,
                        "hash": cloned_hash,
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
                    if tl_name(current_target.obj) == "WebDocumentNoProxy":
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
                    else:
                        # Ordinary WebDocument URLs must be fetched through
                        # Telegram; only WebDocumentNoProxy authorizes a direct
                        # request to the origin server.
                        location = types.InputWebFileLocation(
                            url=current_target.obj.url,
                            access_hash=int(current_target.obj.access_hash),
                        )
                        offset = 0
                        request_size = 512 * 1024
                        webfile_dc_id = await self.get_webfile_dc_id()
                        home_dc_id = int(
                            getattr(self.base_client.session, "dc_id", 0) or 0
                        )
                        sender = (
                            None
                            if home_dc_id == webfile_dc_id
                            else await self.base_client._borrow_exported_sender(
                                webfile_dc_id
                            )
                        )
                        try:
                            with partial_path.open("wb") as output:
                                while True:
                                    request = functions.upload.GetWebFileRequest(
                                        location=location,
                                        offset=offset,
                                        limit=request_size,
                                    )
                                    response = (
                                        await self.base_client(request)
                                        if sender is None
                                        else await self.base_client._call(
                                            sender,
                                            request,
                                        )
                                    )
                                    chunk = bytes(
                                        getattr(response, "bytes", b"") or b""
                                    )
                                    if not chunk:
                                        break
                                    output.write(chunk)
                                    offset += len(chunk)
                                    await self.pacer.after_chunk()
                                    if len(chunk) < request_size or (
                                        current_target.expected_size is not None
                                        and offset >= current_target.expected_size
                                    ):
                                        break
                        finally:
                            if sender is not None:
                                await self.base_client._return_exported_sender(sender)
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
                    "hash": file_sha256(final_path),
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
                    self.log_media_issue(target, record, relative_path)
                    print(
                        f"Unavailable {target.role} in message {target.message_id}: "
                        + (
                            "refresh request failed"
                            if refresh_failed
                            else "Telegram no longer returns a fresh file reference"
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
                    reason="download_failed",
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
            if (int(marked_id), int(photo_id)) in self.existing_avatar_keys:
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
                    "mime": "image/jpeg",
                    "owner_id": marked_id,
                    "owner_type": tl_name(entity),
                    "owner_name": utils.get_display_name(entity),
                },
                source_chat_id=marked_id,
                category_hint="avatars",
            )
            internal = await self.download_target(api, target, 1)
            self.stats.observe_attachment(internal)
            records.append(public_peer_avatar_record(internal))
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
        records: list[dict[str, Any]] = []

        def append_public(record: Mapping[str, Any]) -> None:
            public = public_attachment_record(record)
            if public:
                records.append(public)

        prepared_records: list[dict[str, Any]] = []
        physical_record_keys: set[str] = set()
        for record in collector.records:
            prepared = dict(record)
            is_physical = bool(prepared.pop("_physical", False))
            if is_physical:
                identity = json.dumps(
                    public_attachment_record(prepared),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                if identity in physical_record_keys:
                    continue
                physical_record_keys.add(identity)
            prepared_records.append(prepared)
        for record in prepared_records:
            self.stats.observe_attachment(record)
            append_public(record)
        unique_targets: list[DownloadTarget] = []
        target_keys: set[tuple[str, str]] = set()
        for target in collector.targets:
            identity = (attachment_category(target), target.cache_key)
            if identity in target_keys:
                continue
            target_keys.add(identity)
            unique_targets.append(target)
        for ordinal, target in enumerate(unique_targets, start=1):
            internal = await self.download_target(api, target, ordinal)
            self.stats.observe_attachment(internal)
            append_public(internal)
        return records

    def serialize_message(
        self,
        message: Any,
        attachments: list[dict[str, Any]],
        source: HistorySource,
    ) -> dict[str, Any]:
        date = getattr(message, "date", None)
        edit_date = getattr(message, "edit_date", None)
        rendered = rendered_message_content(message)
        message_source = peer_id(getattr(message, "peer_id", None))
        if message_source is None or message_source == 0:
            message_source = int(source.marked_id)
        sender_id = getattr(message, "sender_id", None)
        author = (
            int(sender_id)
            if type(sender_id) is int and sender_id != 0
            else peer_id(getattr(message, "from_id", None))
        )
        if author is None or author == 0:
            author = (
                self.self_id
                if bool(getattr(message, "out", False))
                else message_source
            )
        flags = {
            key: True
            for key in (
                "out",
                "mentioned",
                "media_unread",
                "silent",
                "post",
                "from_scheduled",
                "edit_hide",
                "pinned",
                "noforwards",
                "invert_media",
                "offline",
                "video_processing_pending",
                "paid_suggested_post_stars",
                "paid_suggested_post_ton",
                "reactions_are_possible",
            )
            if bool(getattr(message, key, False))
        }
        if bool(getattr(message, "legacy", False)):
            flags["telegram_legacy"] = True
        serialized = {
            # Compact core fields.
            "data": markdown_v2_without_escapes(rendered.markdown_v2),
            "source": message_source,
            "author": author,
            "id": getattr(message, "id", None),
            "reactions": reaction_summary(message),
            "thread": thread_summary(message),
            "attachments": attachments,
            "forwarded": forwarded_summary(message),
            "replied": reply_summary(message),
            "created": unix_timestamp(date),
            # Current normalized fields.
            "type": message_type(message),
            "monoforum_topic": (
                {
                    "peer_id": source.topic_peer_id,
                    "top_message": source.topic_top_message,
                }
                if source.history_peer is not None
                else None
            ),
            "edited": unix_timestamp(edit_date),
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
            "from_boosts_applied": getattr(message, "from_boosts_applied", None),
            "from_rank": getattr(message, "from_rank", None),
            "restriction_reasons": normalized_content(
                getattr(message, "restriction_reason", None)
            ),
            "report_delivery_until": unix_timestamp(
                getattr(message, "report_delivery_until_date", None)
            ),
            "schedule_repeat_period": getattr(
                message, "schedule_repeat_period", None
            ),
            "summary_from_language": getattr(
                message, "summary_from_language", None
            ),
            "flags": flags,
        }
        if source.marked_id != message_source:
            serialized["history_source"] = source.marked_id
        return serialized

    async def history_ranges(self, api: Any, use_takeout_ranges: bool) -> list[Any]:
        if not use_takeout_ranges:
            return [None]
        result = await self.rpc(
            lambda: api(functions.messages.GetSplitRangesRequest()),
            "takeout split ranges",
        )
        self.stats.metadata_requests += 1
        await self.pacer.after_metadata()
        # Telegram prescribes using these opaque partitions in returned order
        # and restarting ordinary history offsets for every partition.
        return list(result) or [None]

    async def history_page(
        self,
        api: Any,
        source: HistorySource,
        message_range: Any,
        offset_id: int,
        *,
        ascending: bool = False,
        limit: int = HISTORY_PAGE_SIZE,
    ) -> Any:
        add_offset = -limit if ascending else 0
        if source.history_peer is not None:
            query: Any = functions.messages.GetSavedHistoryRequest(
                peer=source.history_peer,
                parent_peer=source.parent_peer,
                offset_id=offset_id,
                offset_date=None,
                add_offset=add_offset,
                limit=limit,
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
                add_offset=add_offset,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0,
            )
        else:
            query = functions.messages.GetHistoryRequest(
                peer=source.input_peer,
                offset_id=offset_id,
                offset_date=None,
                add_offset=add_offset,
                limit=limit,
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

    async def source_range_high_watermarks(
        self,
        api: Any,
        source: HistorySource,
        ranges: list[Any],
    ) -> list[tuple[Any, int, int]]:
        """Capture the actual newest source message inside each API partition."""

        if (
            len(ranges) == 1
            and ranges[0] is None
            and source.topic_top_message is not None
        ):
            top_message = int(source.topic_top_message)
            return [(None, top_message, 1)] if top_message > 0 else []

        snapshots: list[tuple[Any, int, int]] = []
        for range_index, message_range in enumerate(ranges, start=1):
            offset_id = 0
            while True:
                response = await self.history_page(
                    api,
                    source,
                    message_range,
                    offset_id,
                    limit=HISTORY_PAGE_SIZE,
                )
                self.remember_peers(response)
                await self.pacer.after_history()
                messages = list(getattr(response, "messages", None) or [])
                if not messages:
                    break
                newest_id = max(
                    (
                        int(getattr(message, "id", 0) or 0)
                        for message in messages
                        if tl_name(message) != "MessageEmpty"
                    ),
                    default=0,
                )
                if newest_id > 0:
                    snapshots.append((message_range, newest_id, range_index))
                    break
                placeholder_ids = [
                    int(getattr(message, "id", 0) or 0)
                    for message in messages
                    if int(getattr(message, "id", 0) or 0) > 0
                ]
                if not placeholder_ids:
                    break
                next_offset = min(placeholder_ids)
                if offset_id and next_offset >= offset_id:
                    raise RuntimeError(
                        "Telegram history placeholder scan stopped advancing"
                    )
                offset_id = next_offset
        return snapshots

    async def iter_source_messages_ascending(
        self,
        api: Any,
        source: HistorySource,
        range_snapshots: list[tuple[Any, int, int]],
        checkpoint: int,
        created_cutoff_epoch: int,
    ) -> AsyncIterator[tuple[Any, Any, int, int]]:
        """Yield one logical history oldest-first inside this run's snapshot."""

        previous_order_key: Optional[tuple[int, int]] = None
        last_seen_message_id = checkpoint
        for message_range, high_watermark, range_index in range_snapshots:
            # MessageRange.min_id/max_id belong to Telegram's opaque export
            # partitioning. History offsets remain local to this source.
            lower_bound = checkpoint
            upper_bound = high_watermark
            if upper_bound <= lower_bound:
                continue

            # Telegram offsets are exclusive. In reverse iteration the first
            # raw request starts at boundary + 1 and uses a negative add_offset.
            offset_id = lower_bound + 1
            while offset_id <= upper_bound:
                response = await self.history_page(
                    api,
                    source,
                    message_range,
                    offset_id,
                    ascending=True,
                )
                self.remember_peers(response)
                await self.pacer.after_history()
                raw_page = list(getattr(response, "messages", None) or [])
                if not raw_page:
                    break

                page_ids = [
                    int(getattr(message, "id", 0) or 0)
                    for message in raw_page
                    if int(getattr(message, "id", 0) or 0) > 0
                ]
                if not page_ids:
                    self.stats.empty_messages_skipped += len(raw_page)
                    break
                highest_id = max(page_ids)
                if highest_id <= lower_bound:
                    break
                # The server vector is newest-first by date. Official clients
                # reverse it for output, then continue after the first positive
                # ID. MessageEmpty placeholders still advance the cursor even
                # though they have neither a timestamp nor content to export.
                cursor_id = next(
                    int(getattr(message, "id", 0) or 0)
                    for message in raw_page
                    if int(getattr(message, "id", 0) or 0) > 0
                )
                next_offset = cursor_id + 1
                if next_offset <= offset_id:
                    raise RuntimeError(
                        f"Telegram ascending history pagination stopped advancing "
                        f"at message {offset_id}"
                    )

                page: list[Any] = []
                for message in reversed(raw_page):
                    message_id = int(getattr(message, "id", 0) or 0)
                    if message_id <= 0 or tl_name(message) == "MessageEmpty":
                        self.stats.empty_messages_skipped += 1
                        continue
                    if message_id <= lower_bound or message_id > upper_bound:
                        continue
                    if message_id <= last_seen_message_id:
                        continue
                    created_epoch = unix_timestamp(getattr(message, "date", None))
                    order_key = (
                        (1, 0) if created_epoch is None else (0, created_epoch)
                    )
                    if (
                        previous_order_key is not None
                        and order_key < previous_order_key
                    ):
                        raise RuntimeError(
                            "Telegram returned a logical history out of chronological "
                            "order; direct JSONL streaming is unsafe"
                        )
                    previous_order_key = order_key
                    last_seen_message_id = message_id
                    # High-water IDs are obtained one source at a time. Apply
                    # one shared created-time cutoff as well, so a message that
                    # arrives while later sources are being inspected cannot
                    # make the next incremental run older than this run's tail.
                    if (
                        created_epoch is not None
                        and created_epoch > created_cutoff_epoch
                    ):
                        continue
                    page.append(message)

                for message in page:
                    await self.hydrate_stories(api, message)
                await self.resolve_custom_emojis(api, page)
                await self.resolve_message_effects(api, page)
                for message in page:
                    yield message, message_range, range_index, next_offset

                if (
                    highest_id >= upper_bound
                    or isinstance(response, types.messages.Messages)
                ):
                    break
                offset_id = next_offset

    async def export(self, api: Any, use_takeout_ranges: bool) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        messages_path = self.output_dir / f"{self.chat_id}.jsonl"
        metadata_path = self.output_dir / f"{self.chat_id}.metadata.json"
        recover_pending_export_publication(messages_path, metadata_path)
        started = utc_now()
        created_cutoff_epoch = int(started.timestamp())
        if self.monoforum_admin_export:
            self.history_sources = await self.list_monoforum_topics(api)
        self.existing_export = load_existing_export(
            messages_path,
            metadata_path,
            self.args.overwrite,
            self.chat_id,
        )
        self.incremental = self.existing_export is not None
        if self.existing_export is not None:
            previous_chat = self.existing_export.metadata.get("chat")
            previous_scope = (
                previous_chat.get("monoforum_scope")
                if isinstance(previous_chat, Mapping)
                else None
            )
            if previous_scope != self.monoforum_scope:
                raise RuntimeError(
                    "The accessible monoforum scope changed; use --overwrite "
                    "to rebuild history without duplicates or gaps"
                )
            previous_summary = self.existing_export.metadata.get("summary")
            previous_history_complete = bool(
                previous_summary.get("history_complete", True)
                if isinstance(previous_summary, Mapping)
                else True
            )
            if not previous_history_complete and self.history_complete:
                raise RuntimeError(
                    "Telegram history access expanded since the previous limited "
                    "export; use --overwrite to backfill older messages"
                )
            current_peers = dict(self.peers)
            self.peers = {
                **self.existing_export.peers,
                **current_peers,
            }
            self.peer_avatar_records = list(self.existing_export.peer_avatars)
            self.media_asset_cache.update(self.existing_export.media_assets)
            for avatar in self.peer_avatar_records:
                owner_id = avatar.get("owner_id")
                photo_id = avatar.get("id")
                relative = avatar.get("file")
                if owner_id is None or photo_id is None or not relative:
                    continue
                avatar_path = self.output_dir / str(relative)
                if avatar_path.is_file() and not avatar_path.is_symlink():
                    self.existing_avatar_keys.add((int(owner_id), int(photo_id)))
        header = {
            "schema": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "attachment_hash_algorithm": "sha256",
            "telegram_layer": TELEGRAM_LAYER,
            "telethon_version": telethon.__version__,
            "exported_at": unix_timestamp(started),
            "order": "oldest_to_newest_by_created_at",
            "chat": {
                "id": self.chat_id,
                "type": chat_kind(self.entity),
                "title": utils.get_display_name(self.entity),
                "username": getattr(self.entity, "username", None),
                "protected_content": self.chat_protected,
                "migration": self.migration,
                "monoforum_scope": self.monoforum_scope,
                "history_sources": [
                    history_source_metadata(source)
                    for source in self.history_sources
                ],
            },
        }
        writer = JsonlExportWriter(
            messages_path,
            metadata_path,
            header,
            self.args.overwrite,
            existing=self.existing_export,
        )
        if self.existing_export is not None:
            # Validation may repair the cache to another surviving categorized
            # copy of the same asset.
            self.media_asset_cache.update(self.existing_export.media_assets)
        if not self.incremental:
            self.error_log_path.unlink(missing_ok=True)
        try:
            ranges = await self.history_ranges(api, use_takeout_ranges)
            iterators: dict[
                int,
                AsyncIterator[tuple[Any, Any, int, int]],
            ] = {}
            sources_by_index: dict[int, HistorySource] = {}
            heap: list[tuple[int, int, int, int, Any, Any, int, int]] = []

            async def push_next(source_index: int) -> None:
                iterator = iterators[source_index]
                try:
                    message, message_range, range_index, next_offset = await anext(
                        iterator
                    )
                except StopAsyncIteration:
                    return
                created_epoch = unix_timestamp(getattr(message, "date", None))
                undated, created_value = (
                    (1, 0) if created_epoch is None else (0, created_epoch)
                )
                heapq.heappush(
                    heap,
                    (
                        undated,
                        created_value,
                        source_index,
                        int(getattr(message, "id", 0) or 0),
                        message,
                        message_range,
                        range_index,
                        next_offset,
                    ),
                )

            for source_index, source in enumerate(self.history_sources, start=1):
                source_key = checkpoint_key_from_source(source)
                source_checkpoint = (
                    self.existing_export.checkpoints.get(source_key, 0)
                    if self.existing_export is not None
                    else 0
                )
                range_snapshots = await self.source_range_high_watermarks(
                    api,
                    source,
                    ranges,
                )
                if not any(
                    high_watermark > source_checkpoint
                    for _message_range, high_watermark, _range_index in range_snapshots
                ):
                    continue
                sources_by_index[source_index] = source
                iterators[source_index] = self.iter_source_messages_ascending(
                    api,
                    source,
                    range_snapshots,
                    source_checkpoint,
                    created_cutoff_epoch,
                )
                await push_next(source_index)

            while heap:
                (
                    undated,
                    created_value,
                    source_index,
                    _message_id,
                    message,
                    message_range,
                    range_index,
                    next_offset,
                ) = heapq.heappop(heap)
                source = sources_by_index[source_index]
                created_epoch = None if undated else created_value
                writer.ensure_order(created_epoch)
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
                await push_next(source_index)

            new_avatar_records = await self.download_peer_avatars(api)
            merged_avatars: dict[tuple[Any, ...], dict[str, Any]] = {}
            for avatar in [*self.peer_avatar_records, *new_avatar_records]:
                identity = (
                    avatar.get("owner_id"),
                    avatar.get("id"),
                )
                merged_avatars[identity] = avatar
            self.peer_avatar_records = list(merged_avatars.values())
            finished = utc_now()
            failed = self.stats.attachments.get("failed", 0)
            skipped = self.stats.attachments.get("skipped_limit", 0)
            protected = self.stats.attachments.get("protected", 0)
            unavailable = self.stats.attachments.get("unavailable", 0)
            previous_summary_value = (
                self.existing_export.metadata.get("summary")
                if self.existing_export is not None
                else None
            )
            previous_summary = (
                previous_summary_value
                if isinstance(previous_summary_value, Mapping)
                else {}
            )
            previous_complete_accessible = bool(
                previous_summary.get("complete_accessible", True)
            )
            previous_fully_complete = bool(previous_summary.get("complete", True))
            previous_history_complete = bool(
                previous_summary.get("history_complete", True)
            )
            current_complete_accessible = (
                self.history_complete
                and self.stats.metadata_failures == 0
                and failed == 0
                and skipped == 0
            )
            current_fully_complete = (
                current_complete_accessible
                and protected == 0
                and unavailable == 0
            )
            complete_accessible = (
                previous_complete_accessible and current_complete_accessible
            )
            fully_complete = previous_fully_complete and current_fully_complete
            combined_history_complete = (
                previous_history_complete and self.history_complete
            )
            existing_messages = (
                self.existing_export.message_count
                if self.existing_export is not None
                else 0
            )
            total_messages = existing_messages + self.stats.messages
            previous_limitations = previous_summary.get("limitations") or []
            limitations = list(
                dict.fromkeys(
                    [
                        *(
                            str(item)
                            for item in previous_limitations
                            if item is not None
                        ),
                        "Only history and files currently accessible to this user account are exportable.",
                        "Deleted or expired content and secret-chat history cannot be recovered.",
                        "Undated, content-free MessageEmpty placeholders are skipped while still advancing history pagination.",
                        "Protected content, locked paid media, and live streams are recorded but not downloaded.",
                        "Raw Telegram TL message copies are intentionally omitted.",
                        "Encrypted Telegram Passport and secure-value payload bodies are redacted.",
                        "Opaque binary bot, payment, callback, game, and authorization-capability tokens are represented by SHA-256 and byte size; poll option tokens are retained.",
                        "Incremental updates add higher-ID messages only; edits, deletions, and reaction changes on existing messages require --overwrite.",
                        *self.history_limitations,
                    ]
                )
            )
            summary = {
                "complete": fully_complete,
                "complete_accessible": complete_accessible,
                "history_complete": combined_history_complete,
                "monoforum_scope": self.monoforum_scope,
                "mode": "incremental" if self.incremental else "full",
                "messages": total_messages,
                "messages_existing": existing_messages,
                "messages_added": self.stats.messages,
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
                "attachment_stats_scope": "current_run_new_messages_and_avatars",
                "started_at": unix_timestamp(started),
                "finished_at": unix_timestamp(finished),
                "duration_seconds": round((finished - started).total_seconds(), 3),
                "limitations": limitations,
            }
            # Publish both message JSONL and its metadata completion marker
            # before pruning. A failed write leaves attachments untouched.
            writer.finish(
                self.peers,
                self.peer_avatar_records,
                self.media_asset_cache,
                summary,
            )
            stale_files_removed = 0
            if not self.incremental and fully_complete:
                stale_files_removed = self.prune_stale_files()
            print(
                f"Finished: added {self.stats.messages} messages "
                f"({total_messages} total) -> {messages_path} "
                f"(metadata: {metadata_path.name}; "
                f"{failed} failed downloads, "
                f"{stale_files_removed} stale files pruned)",
                flush=True,
            )
            return summary
        except BaseException:
            writer.close_incomplete()
            incomplete = ", ".join(
                str(path) for path in writer.incomplete_paths()
            ) or "no partial artifact"
            print(
                f"Incomplete export work kept at: {incomplete}",
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
        description=(
            "Download or incrementally update one Telegram chat as chronological "
            "JSONL, metadata JSON, and files/."
        ),
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
        default=os.getenv("TG_SESSION_STRING") or os.getenv("TG_SESSION"),
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
        help="Ignore incremental checkpoints and rebuild the complete export",
    )
    parser.add_argument(
        "--keep-stale-files",
        action="store_true",
        help="With --overwrite, do not prune files unreferenced by the new export",
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
    if args.api_id is None:
        parser.error("--api-id or TG_ID is required")
    if not args.api_hash:
        parser.error("--api-hash or TG_HASH is required")
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

    await cast(Awaitable[Any], client.start(phone=args.phone))
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
        exporter = ChatExporter(client, me, entity, input_peer, output_dir, args)
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
                    f"{exc.seconds}s. Re-run after Unix timestamp "
                    f"{unix_timestamp(ready)}, or omit --takeout "
                    "to use conservatively paced normal history calls.",
                    file=sys.stderr,
                )
                return 3
        else:
            summary = await exporter.export(client, use_takeout_ranges=False)
        return 0 if summary["complete_accessible"] else 2
    finally:
        await cast(Awaitable[Any], client.disconnect())


def main() -> int:
    load_local_env()
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args, parser)
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print(
            "Export interrupted; downloaded files and JSONL work files were kept.",
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
