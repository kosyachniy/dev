#!/usr/bin/env python3
"""Convert one VK archive conversation folder to Telegram-style JSONL.

Python 3.9+; no third-party packages or VK credentials required.

    python vk/user/export_chat.py vk/user/213802528
    python vk/user/export_chat.py vk/user/213802528 -o /tmp/chat.jsonl

Reads every messages*.html page and writes <folder>.jsonl alongside the folder,
oldest first. Uses the same compact fields as tg/user/export_chat_2.py: data,
source, author, id, attachments, created, type, edited, and flags.out. Empty
optional values are omitted. Source is the numeric conversation folder name;
the archive owner's ID comes from the base64-encoded jd metadata.

VK's displayed dates have no timezone. --timezone defaults to Europe/Moscow,
including its historical UTC offsets. Override it if the archive uses another
timezone. Dates become integer Unix seconds.

Attachment descriptions, URLs, and forwarded-message counts are retained in
attachments[].content. URLs are not downloaded; missing attachment details are
marked unavailable. No file paths, hashes, or forwarded bodies are fabricated.
The original HTML files are untouched. A successful run atomically replaces
the JSONL; malformed pages and conflicting duplicate IDs abort the export.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import codecs
import datetime as dt
import json
import mimetypes
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


MONTHS = {
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "мая": 5,
    "июн": 6, "июл": 7, "авг": 8, "сен": 9, "сент": 9,
    "окт": 10, "ноя": 11, "дек": 12,
}
DATE_RE = re.compile(
    r"(\d{1,2})\s+([а-яё]+)\.?\s+(\d{4})\s+в\s+"
    r"(\d{1,2}):(\d{2})(?::(\d{2}))?", re.IGNORECASE
)
ATTACHMENT_TYPES = {
    "фотография": "image",
    "файл": "file",
    "видеозапись": "video",
    "аудиозапись": "audio",
    "голосовое сообщение": "voice",
    "стикер": "sticker",
    "звонок": "phone_call",
    "ссылка": "link_preview",
    "запись на стене": "wall_post",
    "подарок": "gift",
    "карта": "geo",
}
VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    children: list[Any] = field(default_factory=list)

    def has_class(self, name: str) -> bool:
        return name in self.attrs.get("class", "").split()

    def find(self, class_name: str) -> Iterator[Element]:
        for child in self.children:
            if isinstance(child, Element):
                if child.has_class(class_name):
                    yield child
                yield from child.find(class_name)


class ArchiveParser(HTMLParser):
    """Small HTML tree so attachment/header text cannot leak into message text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element("root", {})
        self.stack = [self.root]
        self.metadata: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Any]]) -> None:
        node = Element(tag, {k: v for k, v in attrs if v is not None})
        self.stack[-1].children.append(node)
        if tag == "meta" and node.attrs.get("name") == "jd":
            self.metadata.append(node.attrs.get("content", ""))
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Any]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if len(self.stack) == 1 or self.stack[-1].tag != tag:
            raise ValueError(f"unexpected closing HTML tag </{tag}>")
        self.stack.pop()

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)

    def close(self) -> None:
        super().close()
        if len(self.stack) != 1:
            raise ValueError(f"incomplete HTML: unclosed <{self.stack[-1].tag}>")


def render(node: Any, *, markdown: bool = False) -> str:
    if isinstance(node, str):
        return node
    if node.tag in {"script", "style"} or any(
        node.has_class(c) for c in ("kludges", "attachment", "message-edited")
    ):
        return ""
    if node.tag == "br":
        return "\n"
    if node.tag == "img":
        return node.attrs.get("alt", "")
    text = "".join(render(child, markdown=markdown) for child in node.children)
    if markdown and text:
        if node.tag == "a" and node.attrs.get("href"):
            url = node.attrs["href"]
            return text if text == url else f"[{text}]({url})"
        marker = {
            "b": "*", "strong": "*", "i": "_", "em": "_", "u": "__",
            "s": "~", "del": "~", "code": "`", "pre": "```",
        }.get(node.tag)
        if marker:
            return f"{marker}{text}{marker}"
    return text


def read_page(path: Path) -> ArchiveParser:
    raw = path.read_bytes()
    charset = re.search(br"charset\s*=\s*[\"']?([a-zA-Z0-9_-]+)", raw[:4096])
    if raw.startswith(codecs.BOM_UTF8):
        encoding = "utf-8-sig"
    elif charset:
        encoding = charset[1].decode("ascii")
    else:
        try:
            raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "cp1251"
    parser = ArchiveParser()
    parser.feed(raw.decode(encoding))
    parser.close()
    return parser


def archive_owner(metadata: list[str]) -> int | None:
    owners = set()
    for encoded in metadata:
        try:
            value = json.loads(base64.b64decode(
                encoded + "=" * (-len(encoded) % 4), validate=True
            ))
            owner = value["user_id"]
            if type(owner) is not int or owner <= 0:
                raise ValueError("user_id must be a positive integer")
            owners.add(owner)
        except (ValueError, KeyError, TypeError, binascii.Error) as exc:
            raise ValueError("invalid jd owner metadata; supply --self-id") from exc
    if len(owners) > 1:
        raise ValueError("conflicting archive owners in jd metadata")
    return next(iter(owners), None)


def timestamp(text: str, timezone: ZoneInfo) -> int:
    match = DATE_RE.fullmatch(text.strip())
    if not match:
        raise ValueError(f"unsupported VK date: {text!r}")
    day, month, year, hour, minute, second = match.groups()
    month_number = MONTHS.get(month.lower())
    if month_number is None:
        raise ValueError(f"unsupported VK month: {month!r}")
    return int(dt.datetime(
        int(year), month_number, int(day), int(hour), int(minute),
        int(second or 0), tzinfo=timezone,
    ).timestamp())


def author_id(header: Element, owner: int | None) -> int:
    name = render(header).rsplit(",", 1)[0].strip()
    if name == "Вы":
        if owner is None:
            raise ValueError("cannot identify 'Вы': missing jd metadata; supply --self-id")
        return owner
    for child in header.children:
        if not isinstance(child, Element) or child.tag != "a":
            continue
        url = urlsplit(child.attrs.get("href", ""))
        if url.hostname not in {"vk.com", "vk.ru", "www.vk.com", "www.vk.ru", "m.vk.com", "m.vk.ru"}:
            continue
        match = re.fullmatch(r"/(id|club|public)(\d+)/?", url.path)
        if match:
            value = int(match[2])
            if value:
                return value if match[1] == "id" else -value
    raise ValueError("cannot identify message author from header profile link")


def attachment_record(node: Element) -> dict[str, Any]:
    descriptions = list(node.find("attachment__description"))
    description = "\n".join(render(d).strip() for d in descriptions).strip()
    content: dict[str, Any] = {}
    if description:
        content["description"] = description
    links = list(node.find("attachment__link"))
    urls = list(dict.fromkeys(link.attrs["href"] for link in links if link.attrs.get("href")))
    if urls:
        if len(urls) == 1:
            content["url"] = urls[0]
        else:
            content["urls"] = urls
    label = description.lower().replace("ё", "е")
    forwarded = re.fullmatch(r"(\d+) прикрепленн\w* сообщени\w*", label)
    kind = ATTACHMENT_TYPES.get(label, "unknown")
    if forwarded:
        kind = "forwarded_messages"
        content["count"] = int(forwarded[1])
    record: dict[str, Any] = {"type": kind}
    if content:
        record["content"] = content
    if not urls:
        record.update(status="unavailable", reason="attachment_details_not_in_backup")
    elif kind in {"image", "video", "audio", "voice", "file"}:
        mime, _ = mimetypes.guess_type(urlsplit(urls[0]).path)
        if mime:
            record["mime"] = mime
    return record


def message_record(node: Element, source: int, owner: int | None, timezone: ZoneInfo) -> dict[str, Any]:
    message_id = int(node.attrs["data-id"])
    if message_id <= 0:
        raise ValueError("message data-id must be a positive integer")
    if list(node.find("message")):
        raise ValueError("nested messages are not supported by this archive format")
    headers = [c for c in node.children if isinstance(c, Element) and c.has_class("message__header")]
    bodies = [c for c in node.children if isinstance(c, Element) and not c.has_class("message__header")]
    if len(headers) != 1 or len(bodies) != 1:
        raise ValueError("expected one message header and one body")
    header = headers[0]
    _, separator, date = render(header).rpartition(",")
    if not separator:
        raise ValueError("missing message date in header")
    author = author_id(header, owner)
    row: dict[str, Any] = {}
    data = render(bodies[0], markdown=True)
    if data:
        row["data"] = data
    row.update(source=source, author=author, id=message_id)
    attachments = [attachment_record(a) for a in node.find("attachment")]
    if attachments:
        row["attachments"] = attachments
    row.update(created=timestamp(date, timezone), type="message")
    for edited in header.find("message-edited"):
        if edited.attrs.get("title"):
            row["edited"] = timestamp(edited.attrs["title"], timezone)
        else:
            raise ValueError("edit marker has no timestamp")
    if author == owner:
        row["flags"] = {"out": True}
    return row


def export_chat(folder: Path, output: Path | None = None, *, source_id: int | None = None,
                self_id: int | None = None, timezone: str = "Europe/Moscow") -> dict[str, Any]:
    folder = folder.resolve()
    if not folder.is_dir():
        raise ValueError(f"not a conversation folder: {folder}")
    if source_id is None:
        try:
            source_id = int(folder.name)
        except ValueError as exc:
            raise ValueError("folder name must be a numeric VK peer ID; supply --source-id") from exc
    if type(source_id) is not int or source_id == 0:
        raise ValueError("source ID must be a non-zero integer")
    if self_id is not None and (type(self_id) is not int or self_id <= 0):
        raise ValueError("self ID must be a positive integer")
    zone = ZoneInfo(timezone)
    pages = sorted(folder.glob("messages*.html"), key=lambda p: (
        int(re.search(r"\d+", p.stem)[0]) if re.search(r"\d+", p.stem) else -1, p.name,
    ))
    if not pages:
        raise ValueError(f"no messages*.html pages found in {folder}")
    output = Path(output).absolute() if output is not None else folder.with_name(folder.name + ".jsonl")
    if output.suffix.lower() != ".jsonl":
        raise ValueError("output must have the .jsonl extension")
    if output.is_symlink() or output.resolve() in {p.resolve() for p in pages}:
        raise ValueError("output must not replace a source page or symbolic link")

    rows: dict[int, dict[str, Any]] = {}
    origins: dict[int, str] = {}
    owner = self_id
    duplicates = 0
    for path in pages:
        try:
            page = read_page(path)
            page_owner = archive_owner(page.metadata) if self_id is None else self_id
            if owner is not None and page_owner is not None and owner != page_owner:
                raise ValueError("conflicting archive owners across pages")
            owner = owner if owner is not None else page_owner
            nodes = list(page.root.find("message"))
            if not nodes:
                raise ValueError("page contains no messages")
            for node in nodes:
                try:
                    row = message_record(node, source_id, owner, zone)
                except (ValueError, KeyError) as exc:
                    raise ValueError(f"message {node.attrs.get('data-id', '?')}: {exc}") from exc
                message_id = row["id"]
                if message_id in rows:
                    if rows[message_id] != row:
                        raise ValueError(f"conflicting message {message_id}, first seen in {origins[message_id]}")
                    duplicates += 1
                else:
                    rows[message_id] = row
                    origins[message_id] = path.name
        except (ValueError, LookupError, OSError) as exc:
            raise ValueError(f"{path.name}: {exc}") from exc

    ordered = sorted(rows.values(), key=lambda row: (row["created"], row["id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=output.parent, prefix=f".{output.name}.",
                                         suffix=".tmp", delete=False) as destination:
            temporary = Path(destination.name)
            for row in ordered:
                destination.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {"output": output, "pages": len(pages), "messages": len(rows),
            "duplicates": duplicates, "attachments": sum(len(r.get("attachments", [])) for r in ordered)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path, help="VK conversation folder containing messages*.html")
    parser.add_argument("-o", "--output", type=Path, help="destination .jsonl (default: alongside the folder)")
    parser.add_argument("--source-id", type=int, help="conversation peer ID (default: folder name)")
    parser.add_argument("--self-id", type=int, help="archive owner ID (default: HTML jd metadata)")
    parser.add_argument("--timezone", default="Europe/Moscow", help="IANA timezone for archive dates (default: Europe/Moscow)")
    args = parser.parse_args()
    try:
        result = export_chat(args.folder, args.output, source_id=args.source_id,
                             self_id=args.self_id, timezone=args.timezone)
    except (ValueError, OSError, ZoneInfoNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Exported {result['messages']} messages and {result['attachments']} attachments "
          f"from {result['pages']} pages to {result['output']} "
          f"({result['duplicates']} identical duplicates skipped). Timezone: {args.timezone}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
