import asyncio
import contextlib
import datetime as dt
import inspect
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, get_args

from telethon import types
from telethon.tl.types import messages as message_types

import export_chat_2 as export


class ExportSchemaTests(unittest.TestCase):
    def assert_normalized(self, value):
        self.assertFalse(callable(getattr(value, "to_dict", None)))
        self.assertNotIsInstance(value, (bytes, dt.date, dt.time))
        if isinstance(value, dict):
            for key, child in value.items():
                self.assertNotEqual(key, "raw")
                self.assertFalse(key.startswith("_"), key)
                self.assertFalse(key.endswith("_iso"), key)
                self.assertIsNotNone(child, key)
                self.assertNotEqual(child, "", key)
                if isinstance(child, (dict, list)):
                    self.assertTrue(child, key)
                self.assert_normalized(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_normalized(child)

    @staticmethod
    def source(peer_id=7):
        return export.HistorySource(
            types.InputPeerUser(peer_id, 0), peer_id, "test"
        )

    def serialize(self, message):
        exporter: Any = object.__new__(export.ChatExporter)
        exporter.self_id = 99
        collector = export.AttachmentCollector(
            int(message.id),
            False,
            source_chat_id=7,
        )
        collector.collect_message(message, {})
        attachments = [
            export.public_attachment_record(record)
            for record in collector.records
            if export.public_attachment_record(record)
        ]
        row = export.sparse_json(
            exporter.serialize_message(message, attachments, self.source())
        )
        export.validate_message_contract(row)
        self.assertFalse(
            "history_source" in row and row["history_source"] == row["source"]
        )
        self.assert_normalized(row)
        return row

    def emit_attachments(self, message):
        exporter: Any = object.__new__(export.ChatExporter)
        exporter.entity = types.User(7)
        exporter.entity_protected = False
        exporter.private_protection_my = False
        exporter.private_protection_peer = False
        exporter.chat_protected = False
        exporter.emoji_documents = {}
        exporter.stats = export.ExportStats()
        exporter.collect_message_effect = lambda _collector, _message: None

        async def fake_download(_api, target, ordinal):
            category = export.attachment_category(target)
            return {
                **target.metadata,
                "category": category,
                "status": "downloaded",
                "file": (
                    f"files/{category}/attachment-{ordinal}{target.extension}"
                ),
                "hash": "0" * 64,
                "downloaded_size": target.expected_size or 1,
            }

        exporter.download_target = fake_download
        emitted = asyncio.run(
            exporter.attachment_records(None, message, self.source(), None)
        )
        for attachment in emitted:
            self.assertTrue(
                {"role", "roles", "category"}.isdisjoint(attachment),
                attachment,
            )
        export.validate_message_contract(
            {
                "id": int(message.id),
                "source": 7,
                "author": 7,
                "created": 1,
                "attachments": emitted,
            }
        )
        return emitted, exporter

    def test_current_message_fields_are_all_accounted_for(self):
        for message_type, expected_fields in (
            (types.Message, export.SUPPORTED_MESSAGE_FIELDS),
            (types.MessageService, export.SUPPORTED_MESSAGE_SERVICE_FIELDS),
            (types.MessageEmpty, export.SUPPORTED_MESSAGE_EMPTY_FIELDS),
        ):
            self.assertEqual(
                frozenset(
                    inspect.signature(
                        export.raw_tl_constructor(message_type)
                    ).parameters
                ),
                expected_fields,
            )
        export.require_current_telethon()

        for prefix, expected in (
            ("MessageMedia", export.SUPPORTED_MESSAGE_MEDIA_CONSTRUCTORS),
            ("MessageAction", export.SUPPORTED_MESSAGE_ACTION_CONSTRUCTORS),
        ):
            current = frozenset(
                name
                for name, constructor in vars(types).items()
                if name.startswith(prefix)
                and inspect.isclass(constructor)
                and constructor.__name__ == name
            )
            self.assertEqual(current, expected)

    def test_every_current_content_constructor_normalizes(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        text = types.TextWithEntities("text", [])
        geo = types.GeoPoint(2.0, 1.0, 3)
        poll = types.Poll(1, text, [], 9)
        todo = types.TodoList(text, [])
        media = {
            "MessageMediaContact": types.MessageMediaContact(
                "+1", "First", "Last", "BEGIN:VCARD", 1
            ),
            "MessageMediaDice": types.MessageMediaDice(4, "🎲"),
            "MessageMediaDocument": types.MessageMediaDocument(
                document=types.DocumentEmpty(1)
            ),
            "MessageMediaEmpty": types.MessageMediaEmpty(),
            "MessageMediaGame": types.MessageMediaGame(
                types.Game(1, 2, "game", "Game", "Description", types.PhotoEmpty(3))
            ),
            "MessageMediaGeo": types.MessageMediaGeo(geo),
            "MessageMediaGeoLive": types.MessageMediaGeoLive(geo, 60),
            "MessageMediaGiveaway": types.MessageMediaGiveaway([8], 2, now),
            "MessageMediaGiveawayResults": types.MessageMediaGiveawayResults(
                8, 10, 1, 0, [7], now
            ),
            "MessageMediaInvoice": types.MessageMediaInvoice(
                "Title", "Description", "USD", 100, "start"
            ),
            "MessageMediaPaidMedia": types.MessageMediaPaidMedia(
                5, [types.MessageExtendedMediaPreview(w=100, h=200)]
            ),
            "MessageMediaPhoto": types.MessageMediaPhoto(photo=types.PhotoEmpty(1)),
            "MessageMediaPoll": types.MessageMediaPoll(poll, types.PollResults()),
            "MessageMediaStory": types.MessageMediaStory(types.PeerChannel(8), 1),
            "MessageMediaToDo": types.MessageMediaToDo(todo),
            "MessageMediaUnsupported": types.MessageMediaUnsupported(),
            "MessageMediaVenue": types.MessageMediaVenue(
                geo, "Venue", "Address", "provider", "id", "type"
            ),
            "MessageMediaVideoStream": types.MessageMediaVideoStream(
                types.InputGroupCall(1, 2)
            ),
            "MessageMediaWebPage": types.MessageMediaWebPage(types.WebPageEmpty(1)),
        }
        self.assertEqual(frozenset(media), export.SUPPORTED_MESSAGE_MEDIA_CONSTRUCTORS)
        for name, value in media.items():
            result = export.normalized_content(value)
            collector = export.AttachmentCollector(1, False, source_chat_id=7)
            collector.collect_media(value, "message.media")
            descriptors = [
                export.public_attachment_record(record)
                for record in collector.records
            ]
            descriptors.extend(
                export.public_attachment_record(target.metadata)
                for target in collector.targets
            )
            if name == "MessageMediaEmpty":
                self.assertEqual(result, {})
                self.assertEqual(descriptors, [])
            else:
                self.assertTrue(result.get("type"), name)
                self.assert_normalized(result)
                self.assertTrue(descriptors, name)
                self.assert_normalized(descriptors)
                for descriptor in descriptors:
                    self.assertTrue(
                        {"role", "roles", "category"}.isdisjoint(descriptor),
                        (name, descriptor),
                    )

        for name in export.SUPPORTED_MESSAGE_ACTION_CONSTRUCTORS:
            constructor = getattr(types, name)
            value = constructor.__new__(constructor)
            expected_fields = set()
            for field_name, parameter in inspect.signature(constructor).parameters.items():
                annotation = str(parameter.annotation).lower()
                if "list[" in annotation:
                    field_value = [1]
                elif "datetime.datetime" in annotation:
                    field_value = now
                elif "bytes" in annotation:
                    field_value = b"opaque"
                elif "bool" in annotation:
                    field_value = True
                elif "float" in annotation:
                    field_value = 1.5
                elif "int" in annotation:
                    field_value = 1
                else:
                    field_value = "value"
                setattr(value, field_name, field_value)
                expected_fields.add(
                    export.CONTENT_FIELD_RENAMES.get(
                        (name, field_name), field_name
                    )
                )
            result = export.normalized_content(value)
            collector = export.AttachmentCollector(1, False, source_chat_id=7)
            collector.semantic_record(
                value,
                "message.action",
                category_hint="other",
            )
            if name == "MessageActionEmpty":
                self.assertEqual(result, {})
                self.assertEqual(collector.records, [])
                continue
            self.assertEqual(result.get("type"), export.content_type_name(name))
            self.assertTrue(expected_fields.issubset(result), name)
            self.assert_normalized(result)
            self.assertEqual(len(collector.records), 1, name)
            self.assertEqual(
                export.public_attachment_record(collector.records[0])["type"],
                export.content_type_name(name),
            )

        for alias_name, expected_count in (
            ("TypePageBlock", 39),
            ("TypeRichText", 29),
            ("TypePageListItem", 2),
            ("TypePageListOrderedItem", 2),
            ("TypeKeyboardButton", 18),
            ("TypeMessageEntity", 25),
            ("TypeReaction", 4),
        ):
            constructors = get_args(getattr(types, alias_name))
            self.assertEqual(len(constructors), expected_count)
            for constructor in constructors:
                value = constructor.__new__(constructor)
                expected_fields = set()
                for field_name, parameter in inspect.signature(
                    constructor
                ).parameters.items():
                    annotation = str(parameter.annotation).lower()
                    if "list[" in annotation:
                        field_value = [1]
                    elif "datetime.datetime" in annotation:
                        field_value = now
                    elif "bytes" in annotation:
                        field_value = b"opaque"
                    elif "bool" in annotation:
                        field_value = True
                    elif "float" in annotation:
                        field_value = 1.5
                    elif "int" in annotation:
                        field_value = 1
                    else:
                        field_value = "value"
                    setattr(value, field_name, field_value)
                    output_name = export.CONTENT_FIELD_RENAMES.get(
                        (constructor.__name__, field_name), field_name
                    )
                    expected_fields.add(
                        "value_type" if output_name == "type" else output_name
                    )
                result = export.normalized_content(value)
                if constructor.__name__ in {"ReactionEmpty", "TextEmpty"}:
                    self.assertEqual(result, {})
                    continue
                self.assertTrue(result.get("type"), constructor.__name__)
                self.assertTrue(
                    expected_fields.issubset(result), constructor.__name__
                )
                self.assert_normalized(result)

    def test_every_rich_text_and_page_block_renders_to_strings(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        leaf = types.TextPlain("visible")
        rich_values = []
        for constructor in get_args(types.TypeRichText):
            name = constructor.__name__
            if name == "TextEmpty":
                value = constructor()
            elif name == "TextPlain":
                value = constructor("visible")
            elif name == "TextConcat":
                value = constructor([leaf, types.TextPlain(" second")])
            elif name == "TextUrl":
                value = constructor(leaf, "https://example.com/a_(b)", 1)
            elif name == "TextEmail":
                value = constructor(leaf, "mail@example.com")
            elif name == "TextPhone":
                value = constructor(leaf, "+123")
            elif name == "TextImage":
                value = constructor(1, 10, 10)
            elif name == "TextAnchor":
                value = constructor(leaf, "anchor")
            elif name == "TextMath":
                value = constructor("x+y")
            elif name == "TextCustomEmoji":
                value = constructor(1, "🙂")
            elif name == "TextMentionName":
                value = constructor(leaf, 7)
            elif name == "TextDate":
                value = constructor(leaf, now, long_date=True)
            else:
                value = constructor(leaf)
            rich_values.append(value)
            rendered = export.render_rich_text(value)
            self.assertIsInstance(rendered.plain, str, name)
            self.assertIsInstance(rendered.markdown_v2, str, name)
            if name not in {"TextEmpty", "TextImage"}:
                self.assertTrue(rendered.plain, name)
        self.assertEqual(len(rich_values), 29)

        caption = types.PageCaption(
            types.TextPlain("caption"), types.TextPlain("credit")
        )
        nested = types.PageBlockParagraph(types.TextPlain("nested"))
        page_values = []
        for constructor in get_args(types.TypePageBlock):
            name = constructor.__name__
            value = constructor.__new__(constructor)
            for field_name, parameter in inspect.signature(constructor).parameters.items():
                annotation = str(parameter.annotation)
                if field_name == "text":
                    field_value = leaf
                elif field_name == "author":
                    field_value = leaf if "RichText" in annotation else "Author"
                elif field_name == "caption":
                    field_value = caption
                elif field_name == "cover":
                    field_value = nested
                elif field_name == "blocks":
                    field_value = [nested]
                elif field_name == "items":
                    if name == "PageBlockList":
                        field_value = [types.PageListItemText(leaf)]
                    elif name == "PageBlockOrderedList":
                        field_value = [types.PageListOrderedItemText(leaf)]
                    else:
                        field_value = [nested]
                elif field_name == "rows":
                    field_value = [
                        types.PageTableRow([types.PageTableCell(text=leaf, header=True)])
                    ]
                elif field_name == "articles":
                    field_value = [
                        types.PageRelatedArticle(
                            "https://example.com/article",
                            1,
                            title="Related",
                            description="Description",
                            author="Writer",
                        )
                    ]
                elif field_name == "channel":
                    field_value = types.User(7, first_name="Channel")
                elif field_name == "geo":
                    field_value = types.GeoPoint(2.0, 1.0, 3)
                elif field_name == "html":
                    field_value = "<b>embedded</b><br>&amp; visible"
                elif field_name == "source":
                    field_value = "x+y"
                elif "datetime.datetime" in annotation:
                    field_value = now
                elif "bool" in annotation:
                    field_value = True
                elif "int" in annotation:
                    field_value = 1
                elif "str" in annotation:
                    field_value = "value"
                else:
                    field_value = None
                setattr(value, field_name, field_value)
            page_values.append(value)
            rendered = export.render_page_block(value)
            self.assertIsInstance(rendered.plain, str, name)
            self.assertIsInstance(rendered.markdown_v2, str, name)
            self.assertNotIn("object at", rendered.plain, name)
        self.assertEqual(len(page_values), 39)

        rich = types.RichMessage(page_values, [], [])
        rendered = export.render_rich_message(rich)
        self.assertIn("visible", rendered.plain)
        self.assertIn("embedded\n& visible", rendered.plain)
        self.assertIn("caption\ncredit", rendered.plain)

    def test_markdown_v2_entities_use_utf16_and_never_lose_text(self):
        text = "😀entity"
        constructors = get_args(types.TypeMessageEntity)
        self.assertEqual(len(constructors), 25)
        for constructor in constructors:
            value = constructor.__new__(constructor)
            for field_name, parameter in inspect.signature(constructor).parameters.items():
                annotation = str(parameter.annotation).lower()
                if field_name == "offset":
                    field_value = 2
                elif field_name == "length":
                    field_value = 6
                elif field_name == "url":
                    field_value = "https://example.com/a_(b)"
                elif field_name == "user_id":
                    field_value = 7
                elif field_name == "document_id":
                    field_value = 8
                elif field_name == "language":
                    field_value = "python"
                elif field_name == "old_text":
                    field_value = "old"
                elif "datetime.datetime" in annotation:
                    field_value = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
                elif "bool" in annotation:
                    field_value = True
                else:
                    field_value = None
                setattr(value, field_name, field_value)
            rendered = export.render_text_with_entities(text, [value])
            self.assertEqual(rendered.plain, text, constructor.__name__)
            self.assertIsInstance(rendered.markdown_v2, str, constructor.__name__)
            self.assertIn("entity", rendered.markdown_v2, constructor.__name__)

        astral = export.render_text_with_entities(
            "😀a*b",
            [types.MessageEntityBold(offset=2, length=3)],
        )
        self.assertEqual(astral.plain, "😀a*b")
        self.assertEqual(astral.markdown_v2, "😀*a\\*b*")
        crossing = export.render_text_with_entities(
            "abcdef",
            [
                types.MessageEntityBold(0, 4),
                types.MessageEntityItalic(2, 4),
            ],
        )
        self.assertEqual(crossing.plain, "abcdef")
        self.assertEqual(crossing.markdown_v2, "*abcd*ef")

    def test_message_data_contains_unescaped_markdown_entity_markup(self):
        message = types.Message(
            id=72,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="123 456 678 90",
            entities=[
                types.MessageEntityBold(offset=4, length=3),
                types.MessageEntityUnderline(offset=8, length=3),
                types.MessageEntityItalic(offset=12, length=2),
            ],
        )

        row = self.serialize(message)

        self.assertEqual(row["data"], "123 **456** __678__ _90_")
        self.assertNotIn("\\", row["data"])
        self.assertNotIn("formatted", row)

    def test_message_data_markup_uses_utf16_offsets_and_preserves_nesting(self):
        message = types.Message(
            id=73,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="raw _ * [x] (y)! 😀nested",
            entities=[
                # Telegram offsets count the astral emoji as two UTF-16 units.
                types.MessageEntityBold(offset=19, length=6),
                types.MessageEntityUnderline(offset=19, length=6),
            ],
        )

        row = self.serialize(message)

        self.assertEqual(
            row["data"],
            "raw _ * [x] (y)! 😀**__nested__**",
        )
        self.assertNotIn("\\", row["data"])

    def test_message_data_markup_preserves_source_backslashes_and_atomic_stars(self):
        cases: tuple[tuple[str, list[Any], str], ...] = (
            (
                r"path\file * _ [x]" + "\rnext",
                [],
                r"path\file * _ [x]" + "\rnext",
            ),
            ("a*b", [types.MessageEntityCode(0, 3)], "`a*b`"),
            (
                "x",
                [types.MessageEntityTextUrl(0, 1, "https://example.com/*")],
                "[x](https://example.com/*)",
            ),
        )
        for index, (text, entities, expected) in enumerate(cases, start=1):
            with self.subTest(index=index):
                message = types.Message(
                    id=73 + index,
                    peer_id=types.PeerUser(7),
                    date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
                    message=text,
                    entities=entities,
                )
                self.assertEqual(self.serialize(message)["data"], expected)

    def test_text_sources_dedupe_into_single_readable_data_string(self):
        message = types.Message(
            id=7,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="same",
            rich_message=types.RichMessage(
                [types.PageBlockParagraph(types.TextBold(types.TextPlain("same")))],
                [],
                [],
            ),
        )

        row = self.serialize(message)

        self.assertEqual(row["data"], "**same**")
        self.assertIsInstance(row["data"], str)
        self.assertNotIn("formatted", row)

    def test_history_source_is_emitted_only_when_it_differs_from_source(self):
        message = types.Message(
            id=71,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="history",
        )
        exporter: Any = object.__new__(export.ChatExporter)
        exporter.self_id = 99

        same = exporter.serialize_message(message, [], self.source(7))
        different = exporter.serialize_message(message, [], self.source(8))

        self.assertNotIn("history_source", same)
        self.assertEqual(different["history_source"], 8)
        export.validate_message_contract(same)
        export.validate_message_contract(different)

    def test_text_rendering_preserves_whitespace_repetition_and_boundaries(self):
        concat = export.render_rich_text(
            types.TextConcat(
                [
                    types.TextPlain("a"),
                    types.TextPlain(" "),
                    types.TextPlain("b"),
                ]
            )
        )
        self.assertEqual(concat.plain, "a b")
        self.assertEqual(concat.markdown_v2, "a b")

        italic_underline = export.render_rich_text(
            types.TextItalic(types.TextUnderline(types.TextPlain("x")))
        )
        underline_italic = export.render_rich_text(
            types.TextUnderline(types.TextItalic(types.TextPlain("x")))
        )
        self.assertEqual(italic_underline.markdown_v2, "_\r__x__\r_")
        self.assertEqual(underline_italic.markdown_v2, "__\r_x_\r__")

        entity_nested = export.render_text_with_entities(
            "x",
            [types.MessageEntityItalic(0, 1), types.MessageEntityUnderline(0, 1)],
        )
        self.assertEqual(entity_nested.markdown_v2, "_\r__x__\r_")

        html_text = export.visible_html_text(
            "<head><title>hidden</title></head>"
            "<div>a<div>b</div>c</div>"
            "<script>alert(1)</script><style>.x { color: red }</style>"
            "<pre>d   e\n\n f</pre><p>next</p>"
        )
        self.assertEqual(html_text, "a\nb\nc\nd   e\n\n f\nnext")

        reversed_list = types.PageBlockOrderedList(
            [
                types.PageListOrderedItemText(types.TextPlain("A")),
                types.PageListOrderedItemText(types.TextPlain("B")),
            ],
            start=5,
            reversed=True,
        )
        self.assertEqual(
            export.render_page_block(reversed_list).plain,
            "5. A\n4. B",
        )

    def test_markdown_v2_nesting_stays_valid_without_losing_text(self):
        nested_bold = types.TextBold(
            types.TextConcat(
                [
                    types.TextPlain("a"),
                    types.TextBold(types.TextPlain("b")),
                ]
            )
        )
        self.assertEqual(export.render_rich_text(nested_bold).markdown_v2, "*ab*")

        adjacent_italic = types.TextConcat(
            [
                types.TextItalic(types.TextPlain("a")),
                types.TextItalic(types.TextPlain("b")),
            ]
        )
        self.assertEqual(
            export.render_rich_text(adjacent_italic).markdown_v2,
            "_a_\r_b_",
        )

        mixed_code = types.TextBold(
            types.TextConcat(
                [
                    types.TextPlain("a "),
                    types.TextFixed(types.TextPlain("code")),
                    types.TextPlain(" b"),
                ]
            )
        )
        mixed = export.render_rich_text(mixed_code)
        self.assertEqual(mixed.plain, "a code b")
        self.assertEqual(mixed.markdown_v2, "*a *`code`* b*")

        linked_emoji = types.TextUrl(
            types.TextCustomEmoji(123, "🙂"),
            "https://example.com",
            1,
        )
        self.assertEqual(
            export.render_rich_text(linked_emoji).markdown_v2,
            "![🙂](tg://emoji?id=123)",
        )
        nested_links = types.TextUrl(
            types.TextUrl(types.TextPlain("x"), "https://inner", 1),
            "https://outer",
            2,
        )
        self.assertEqual(
            export.render_rich_text(nested_links).markdown_v2,
            "[x](https://inner)",
        )

        entity_mixed = export.render_text_with_entities(
            "a code b",
            [types.MessageEntityBold(0, 8), types.MessageEntityCode(2, 4)],
        )
        self.assertEqual(entity_mixed.markdown_v2, "*a *`code`* b*")

    def test_repeated_blocks_are_not_mistaken_for_mirrored_sources(self):
        message = types.Message(
            id=70,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="repeat",
            rich_message=types.RichMessage(
                [
                    types.PageBlockParagraph(types.TextPlain("repeat")),
                    types.PageBlockParagraph(types.TextPlain("repeat")),
                ],
                [],
                [],
            ),
        )

        row = self.serialize(message)

        self.assertEqual(row["data"], "repeat\n\nrepeat")

    def test_todo_is_complete_attachment_content(self):
        item = types.TodoItem(
            1,
            types.TextWithEntities(
                "ship", [types.MessageEntityBold(offset=0, length=4)]
            ),
        )
        todo = types.TodoList(
            types.TextWithEntities("release", []),
            [item],
            others_can_append=True,
        )
        completion = types.TodoCompletion(
            1,
            types.PeerUser(42),
            dt.datetime(2025, 1, 2, tzinfo=dt.timezone.utc),
        )
        message = types.Message(
            id=9,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="",
            media=types.MessageMediaToDo(todo, [completion]),
        )

        row = self.serialize(message)

        self.assertEqual(row["id"], 9)
        self.assertNotIn("message", row)
        self.assertNotIn("data", row)
        self.assertNotIn("formatted", row)
        self.assertEqual(row["author"], row["source"])
        todo_attachment = next(
            item for item in row["attachments"] if item["type"] == "todo"
        )
        todo_data = todo_attachment["content"]
        self.assertEqual(todo_data["title"]["text"], "release")
        self.assertEqual(todo_data["items"][0]["title"]["text"], "ship")
        self.assertEqual(todo_data["completions"][0]["item_id"], 1)
        self.assertEqual(todo_data["completions"][0]["completed_by"], 42)
        self.assertEqual(todo_data["completions"][0]["created"], 1735776000)

        exporter: Any = object.__new__(export.ChatExporter)
        exporter.entity = types.User(7)
        exporter.entity_protected = False
        exporter.private_protection_my = False
        exporter.private_protection_peer = False
        exporter.chat_protected = False
        exporter.emoji_documents = {}
        exporter.stats = export.ExportStats()
        exporter.collect_message_effect = lambda _collector, _message: None
        emitted = asyncio.run(
            exporter.attachment_records(None, message, self.source(), None)
        )
        self.assertTrue(any(item["type"] == "todo" for item in emitted))

    def test_service_message_action_is_stored_in_attachments(self):
        message = types.MessageService(
            id=8,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            action=types.MessageActionChatEditTitle("Renamed"),
        )

        row = self.serialize(message)

        self.assertEqual(row["type"], "service")
        self.assertNotIn("data", row)
        action = next(
            item
            for item in row["attachments"]
            if item["type"] == "chat_edit_title"
        )
        self.assertEqual(action["content"]["title"], "Renamed")
        self.assertEqual(row["author"], row["source"])

    def test_rich_message_and_article_blocks_are_preserved(self):
        caption = types.PageCaption(types.TextPlain("caption"), types.TextEmpty())
        article = types.Page(
            "https://example.com/article",
            [
                types.PageBlockTitle(types.TextPlain("Article")),
                types.PageBlockParagraph(
                    types.TextBold(types.TextPlain("Full body"))
                ),
                types.PageBlockPhoto(11, caption),
            ],
            [types.PhotoEmpty(11)],
            [types.DocumentEmpty(22)],
            v2=True,
        )
        webpage = types.WebPage(
            1,
            "https://example.com/article",
            "example.com/article",
            0,
            site_name="Example",
            title="Article",
            description="Summary",
            author="Writer",
            cached_page=article,
        )
        rich = types.RichMessage(
            [
                types.PageBlockHeading1(types.TextPlain("Heading")),
                types.PageBlockEmbed(
                    caption,
                    html="<strong>embedded</strong>",
                ),
            ],
            [types.PhotoEmpty(33)],
            [types.DocumentEmpty(44)],
            rtl=True,
        )
        message = types.Message(
            id=10,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="fallback",
            media=types.MessageMediaWebPage(webpage, safe=True),
            rich_message=rich,
        )

        row = self.serialize(message)

        self.assertEqual(
            row["data"],
            "fallback\n\nHeading\n\ncaption\nembedded\n\nExample\n\nArticle\n\n"
            "Summary\n\nWriter\n\n**Full body**\n\ncaption",
        )
        self.assertEqual(row["data"].count("Article"), 1)
        self.assertNotIn("formatted", row)
        rich_attachment = next(
            item
            for item in row["attachments"]
            if item["type"] == "rich_message"
        )
        self.assertEqual(
            rich_attachment["content"]["blocks"][0]["type"], "heading1"
        )
        self.assertEqual(
            rich_attachment["content"]["blocks"][1]["html"],
            "<strong>embedded</strong>",
        )
        article_data = next(
            item["content"]
            for item in row["attachments"]
            if item["type"] == "article"
        )
        self.assertEqual(article_data["blocks"][1]["type"], "paragraph")
        self.assertNotIn("credit", article_data["blocks"][2]["caption"])
        self.assertNotIn("photos", article_data)
        self.assertNotIn("documents", article_data)
        link_preview = next(
            item
            for item in row["attachments"]
            if item["type"] == "link_preview"
        )
        self.assertEqual(link_preview["content"]["webpage_type"], "web_page")
        self.assertTrue(
            any(
                item.get("id") == 11 and item.get("status") == "unavailable"
                for item in row["attachments"]
            )
        )

    def test_required_false_and_poll_bytes_survive(self):
        action = export.normalized_content(
            types.MessageActionNoForwardsRequest(False, True)
        )
        self.assertIs(action["prev_value"], False)
        self.assertIs(action["new_value"], True)

        answer = types.PollAnswer(
            types.TextWithEntities("A", []),
            b"a",
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        )
        poll = types.Poll(
            1,
            types.TextWithEntities("Choose", []),
            [answer],
            123,
        )
        media = export.normalized_content(
            types.MessageMediaPoll(poll, types.PollResults())
        )
        self.assertEqual(media["answers"][0]["option"]["data"], "YQ==")
        self.assertNotIn("hash", media)
        self.assertNotIn("results", media)
        self.assert_normalized(media)

    def test_dates_cycles_and_opaque_binary_are_safe(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        formatted = export.normalized_content(
            types.MessageEntityFormattedDate(0, 1, now, short_date=True)
        )
        rich_date = export.normalized_content(
            types.TextDate(types.TextPlain("date"), now, long_date=True)
        )
        story = types.StoryItem(
            1,
            now,
            now,
            types.MessageMediaEmpty(),
            edited=True,
            sent_reaction=types.ReactionEmpty(),
        )
        story_data = export.normalized_content(
            types.MessageMediaStory(types.PeerChannel(8), 1, story=story)
        )
        self.assertIs(formatted["short_date"], True)
        self.assertIs(rich_date["long_date"], True)
        self.assertIs(story_data["story"]["is_edited"], True)
        self.assertNotIn("sent_reaction", story_data["story"])
        export.validate_message_contract(
            {
                "id": 1,
                "source": 7,
                "author": 7,
                "created": 1,
                "data": "date",
                "attachments": [
                    {
                        "type": "normalization_test",
                        "content": {
                            "formatted_date": formatted,
                            "rich_date": rich_date,
                            "story": story_data,
                        },
                    }
                ],
            }
        )

        recursive: dict[str, object] = {"_": "Synthetic", "title": "cycle"}
        recursive["child"] = recursive
        cycle = export.normalized_content(recursive)
        self.assertEqual(cycle["child"]["type"], "cycle_reference")

        outcome = message_types.EmojiGameOutcome(b"secret-seed", 1, 2)
        dice = export.normalized_content(
            types.MessageMediaDice(4, "🎲", game_outcome=outcome)
        )
        seed = dice["game_outcome"]["seed"]
        self.assertEqual(seed["type"], "binary")
        self.assertIs(seed["redacted"], True)
        self.assertEqual(seed["size"], 11)
        self.assertEqual(len(seed["hash"]), 64)
        payment = export.normalized_content(
            types.MessageActionPaymentRefunded(
                types.PeerUser(7),
                "USD",
                100,
                types.PaymentCharge("charge", "provider"),
                payload=b"private",
            )
        )
        self.assertTrue(payment["payload"]["redacted"])
        self.assertNotIn("data", payment["payload"])
        callback = export.normalized_content(
            types.KeyboardButtonCallback("Run", b"private-callback")
        )
        self.assertTrue(callback["data"]["redacted"])
        self.assertNotIn("data", callback["data"])
        gift_action = export.normalized_content(
            types.MessageActionStarGift(
                types.StarGift(1, types.DocumentEmpty(1), 10, 5),
                prepaid_upgrade=True,
                prepaid_upgrade_hash="capability-secret",
            )
        )
        prepaid_token = gift_action["prepaid_upgrade_hash"]
        self.assertTrue(prepaid_token["redacted"])
        self.assertNotIn("capability-secret", json.dumps(prepaid_token))
        empty_gift_action = export.normalized_content(
            types.MessageActionStarGift(
                types.StarGift(1, types.DocumentEmpty(1), 10, 5),
                prepaid_upgrade=True,
                prepaid_upgrade_hash="",
            )
        )
        self.assertNotIn("prepaid_upgrade_hash", empty_gift_action)

    def test_monoforum_metadata_never_contains_unsent_drafts(self):
        secret = "UNSENT SECRET DRAFT"
        source = self.source()
        source.topic_peer_id = 7
        source.topic_top_message = 1
        source.topic_entity = types.User(7)
        setattr(
            source,
            "topic_dialog",
            types.MonoForumDialog(
                types.PeerUser(7),
                1,
                0,
                0,
                0,
                0,
                draft=types.DraftMessage(
                    secret,
                    dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
                ),
            ),
        )

        metadata = export.history_source_metadata(source)

        self.assertNotIn("topic_dialog", metadata)
        self.assertNotIn(secret, json.dumps(metadata))

    def test_nested_media_is_exclusive_to_attachment_descriptors(self):
        todo_media = types.MessageMediaToDo(
            types.TodoList(types.TextWithEntities("Tasks", []), [])
        )

        reply = types.MessageReplyHeader(
            reply_to_msg_id=2,
            quote=True,
            reply_media=todo_media,
            poll_option=b"a",
        )
        message = types.Message(
            id=3,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="reply",
            reply_to=reply,
        )
        row = self.serialize(message)
        replied = row["replied"]
        self.assertIs(replied["quoted"], True)
        self.assertNotIn("media", replied)
        self.assertEqual(replied["poll_option"]["data"], "YQ==")
        reply_todo = next(
            item
            for item in row["attachments"]
            if item["type"] == "todo"
        )
        self.assertEqual(reply_todo["content"]["title"]["text"], "Tasks")

        poll = types.Poll(
            1,
            types.TextWithEntities("Question", []),
            [],
            0,
        )
        collector = export.AttachmentCollector(4, False, source_chat_id=7)
        collector.collect_media(
            types.MessageMediaPoll(poll, types.PollResults(), todo_media),
            "message.media",
        )
        attachments = [
            export.public_attachment_record(item) for item in collector.records
        ]
        poll_attachment = next(item for item in attachments if item["type"] == "poll")
        self.assertNotIn("attached_media", poll_attachment.get("content", {}))
        self.assertTrue(any(item["type"] == "todo" for item in attachments))

    def test_attachment_occurrences_deduplicate_without_public_routing_fields(self):
        shared = types.MessageMediaPhoto(photo=types.PhotoEmpty(99))
        answer = types.PollAnswer(
            types.TextWithEntities("A", []),
            b"a",
            media=shared,
        )
        poll = types.Poll(
            1,
            types.TextWithEntities("Question", []),
            [answer],
            0,
        )
        message = types.Message(
            id=44,
            peer_id=types.PeerUser(7),
            date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            message="",
            media=types.MessageMediaPoll(
                poll,
                types.PollResults(),
                attached_media=shared,
            ),
        )
        emitted, _exporter = self.emit_attachments(message)

        unavailable = [item for item in emitted if item["type"] == "image"]
        self.assertEqual(len(unavailable), 1)
        self.assertEqual(unavailable[0]["status"], "unavailable")
        self.assertEqual(unavailable[0]["reason"], "empty_photo")
        self.assertFalse(any(item["type"] == "photo" for item in emitted))

        collector = export.AttachmentCollector(44, False, source_chat_id=7)
        web_document = types.WebDocumentNoProxy(
            "https://example.com/file.jpg",
            10,
            "image/jpeg",
            [],
        )
        collector.add_web_document(web_document, "message.first")
        collector.add_web_document(web_document, "message.second")
        contact = types.MessageMediaContact("+1", "A", "B", "VCARD", 7)
        collector.add_contact(contact, "message.contact.first")
        collector.add_contact(contact, "message.contact.second")
        self.assertEqual(collector.targets[0].cache_key, collector.targets[1].cache_key)
        self.assertEqual(collector.targets[2].cache_key, collector.targets[3].cache_key)

        collector.metadata_record(
            "message_effect",
            "message.effect",
            None,
            id=1,
        )
        effect = export.public_attachment_record(collector.records[-1])
        self.assertEqual(effect["type"], "message_effect")
        self.assertTrue({"role", "roles", "category"}.isdisjoint(effect))

    def test_round_video_uses_one_physical_attachment_record(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        document = types.Document(
            6096011683539460648,
            -3960222961002842050,
            b"reference",
            now,
            "video/mp4",
            123,
            2,
            [
                types.DocumentAttributeVideo(
                    4.5,
                    320,
                    320,
                    round_message=True,
                    video_codec="h264",
                ),
                types.DocumentAttributeFilename("video.mp4"),
            ],
        )
        message = types.Message(
            id=1574,
            peer_id=types.PeerUser(7),
            date=now,
            message="",
            media=types.MessageMediaDocument(
                document=document,
                spoiler=True,
            ),
        )

        emitted, exporter = self.emit_attachments(message)

        self.assertEqual(len(emitted), 1, emitted)
        attachment = emitted[0]
        self.assertEqual(attachment["type"], "round_video")
        self.assertEqual(attachment["id"], 6096011683539460648)
        self.assertEqual(attachment["access_hash"], -3960222961002842050)
        self.assertEqual(attachment["mime"], "video/mp4")
        self.assertEqual(attachment["file_name"], "video.mp4")
        self.assertEqual(attachment["video_codec"], "h264")
        self.assertEqual(attachment["created"], 1735689600)
        self.assertTrue(attachment["content"]["spoiler"])
        self.assertFalse(any(item["type"] == "document" for item in emitted))
        self.assertEqual(exporter.stats.attachments, {"downloaded": 1})
        self.assertEqual(exporter.stats.attachment_categories, {"media": 1})

    def test_photo_and_contact_each_use_one_carrier_record(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        photo = types.Photo(
            101,
            201,
            b"reference",
            now,
            [types.PhotoSize("x", 640, 480, 10)],
            2,
        )
        cases = (
            (
                types.MessageMediaPhoto(photo=photo, spoiler=True),
                "image",
                {"spoiler": True},
            ),
            (
                types.MessageMediaContact(
                    "+123",
                    "First",
                    "Last",
                    "BEGIN:VCARD",
                    42,
                ),
                "contact",
                {"phone_number": "+123", "first_name": "First"},
            ),
        )

        for index, (media, expected_type, expected_content) in enumerate(
            cases,
            start=1,
        ):
            with self.subTest(expected_type=expected_type):
                message = types.Message(
                    id=1600 + index,
                    peer_id=types.PeerUser(7),
                    date=now,
                    message="",
                    media=media,
                )
                emitted, _exporter = self.emit_attachments(message)
                self.assertEqual(len(emitted), 1, emitted)
                attachment = emitted[0]
                self.assertEqual(attachment["type"], expected_type)
                for key, value in expected_content.items():
                    self.assertEqual(attachment["content"][key], value)

    def test_auxiliary_physical_assets_remain_separate_attachments(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        document = types.Document(
            301,
            401,
            b"reference",
            now,
            "video/mp4",
            123,
            2,
            [types.DocumentAttributeVideo(4.5, 320, 320, round_message=True)],
        )
        cover = types.Photo(
            302,
            402,
            b"reference",
            now,
            [types.PhotoSize("x", 640, 480, 10)],
            2,
        )
        message = types.Message(
            id=1700,
            peer_id=types.PeerUser(7),
            date=now,
            message="",
            media=types.MessageMediaDocument(
                document=document,
                video_cover=cover,
                spoiler=True,
            ),
        )

        emitted, exporter = self.emit_attachments(message)

        self.assertEqual([item["type"] for item in emitted], ["round_video", "image"])
        self.assertEqual(len({item["file"] for item in emitted}), 2)
        self.assertTrue(emitted[0]["content"]["spoiler"])
        self.assertNotIn("content", emitted[1])
        self.assertEqual(exporter.stats.attachments, {"downloaded": 2})
        self.assertEqual(
            exporter.stats.attachment_categories,
            {"media": 1, "preview": 1},
        )

    def test_link_preview_retains_each_webpage_state(self):
        web_pages = [
            (types.WebPageEmpty(1), "web_page_empty"),
            (
                types.WebPagePending(
                    1,
                    dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
                ),
                "web_page_pending",
            ),
            (types.WebPageNotModified(cached_page_views=3), "web_page_not_modified"),
        ]
        for webpage, expected_type in web_pages:
            collector = export.AttachmentCollector(1, False, source_chat_id=7)
            collector.collect_media(
                types.MessageMediaWebPage(webpage),
                "message.media",
            )
            descriptor = export.public_attachment_record(collector.records[0])
            self.assertEqual(descriptor["type"], "link_preview")
            self.assertEqual(
                descriptor["content"]["webpage_type"],
                expected_type,
            )

    def test_link_preview_photo_suppresses_every_video_asset(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        photo = types.Photo(
            1801,
            2801,
            b"photo-reference",
            now,
            [
                types.PhotoSize("m", 320, 180, 100),
                types.PhotoSize("x", 1280, 720, 900),
            ],
            2,
            # A webpage preview must not export an animated/live-photo video
            # rendition when a still image is available.
            video_sizes=[types.VideoSize("u", 1280, 720, 1200)],
        )
        video = types.Document(
            1802,
            2802,
            b"video-reference",
            now,
            "video/mp4",
            5000,
            2,
            [types.DocumentAttributeVideo(12.0, 1920, 1080)],
            thumbs=[types.PhotoSize("x", 1280, 720, 800)],
        )
        webpage = types.WebPage(
            1803,
            "https://example.com/video",
            "example.com/video",
            0,
            title="Video preview",
            photo=photo,
            document=video,
        )
        message = types.Message(
            id=1804,
            peer_id=types.PeerUser(7),
            date=now,
            message="https://example.com/video",
            media=types.MessageMediaWebPage(webpage),
        )

        collector = export.AttachmentCollector(1804, False, source_chat_id=7)
        collector.collect_media(message.media, "message.media")

        self.assertEqual(len(collector.targets), 1, collector.targets)
        target = collector.targets[0]
        self.assertEqual(target.metadata["type"], "image")
        self.assertEqual(target.metadata["id"], photo.id)
        self.assertEqual(target.metadata["mime"], "image/jpeg")
        self.assertEqual(target.extension, ".jpg")
        self.assertEqual(target.expected_size, 900)

        emitted, exporter = self.emit_attachments(message)
        downloaded = [item for item in emitted if "file" in item]
        self.assertEqual([item["type"] for item in downloaded], ["image"])
        self.assertEqual(downloaded[0]["id"], photo.id)
        self.assertTrue(downloaded[0]["file"].endswith(".jpg"))
        self.assertFalse(
            any(
                item.get("mime") == "video/mp4"
                or str(item.get("file", "")).endswith(".mp4")
                for item in emitted
            ),
            emitted,
        )
        self.assertEqual(exporter.stats.attachments.get("downloaded"), 1)

    def test_video_only_link_preview_uses_largest_image_thumbnail(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        video = types.Document(
            1811,
            2811,
            b"video-reference",
            now,
            "video/mp4",
            5000,
            2,
            [types.DocumentAttributeVideo(12.0, 1920, 1080)],
            thumbs=[
                types.PhotoSize("m", 320, 180, 100),
                types.PhotoSize("x", 1280, 720, 800),
            ],
        )
        webpage = types.WebPage(
            1812,
            "https://example.com/video-only",
            "example.com/video-only",
            0,
            title="Video-only preview",
            document=video,
        )
        message = types.Message(
            id=1813,
            peer_id=types.PeerUser(7),
            date=now,
            message="https://example.com/video-only",
            media=types.MessageMediaWebPage(webpage),
        )

        collector = export.AttachmentCollector(1813, False, source_chat_id=7)
        collector.collect_media(message.media, "message.media")

        self.assertEqual(len(collector.targets), 1, collector.targets)
        target = collector.targets[0]
        self.assertEqual(target.metadata["type"], "image")
        self.assertEqual(target.metadata["id"], video.id)
        self.assertEqual(target.metadata["mime"], "image/jpeg")
        self.assertEqual(target.extension, ".jpg")
        self.assertEqual(target.expected_size, 800)

        emitted, exporter = self.emit_attachments(message)
        downloaded = [item for item in emitted if "file" in item]
        self.assertEqual([item["type"] for item in downloaded], ["image"])
        self.assertEqual(downloaded[0]["id"], video.id)
        self.assertTrue(downloaded[0]["file"].endswith(".jpg"))
        self.assertFalse(
            any(
                item.get("mime") == "video/mp4"
                or str(item.get("file", "")).endswith(".mp4")
                for item in emitted
            ),
            emitted,
        )
        self.assertEqual(exporter.stats.attachments.get("downloaded"), 1)

        no_thumb_video = types.Document(
            1814,
            2814,
            b"video-reference",
            now,
            "video/mp4",
            5000,
            2,
            [types.DocumentAttributeVideo(12.0, 1920, 1080)],
        )
        no_thumb_webpage = types.WebPage(
            1815,
            "https://example.com/no-thumbnail",
            "example.com/no-thumbnail",
            0,
            document=no_thumb_video,
        )
        no_thumb_collector = export.AttachmentCollector(
            1816,
            False,
            source_chat_id=7,
        )
        no_thumb_collector.collect_media(
            types.MessageMediaWebPage(no_thumb_webpage),
            "message.media",
        )
        self.assertEqual(no_thumb_collector.targets, [])

    def test_recursive_preview_documents_use_thumbnail_policy_but_media_does_not(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        video = types.Document(
            1821,
            2821,
            b"shared-video-reference",
            now,
            "video/mp4",
            5000,
            2,
            [types.DocumentAttributeVideo(12.0, 1920, 1080)],
            thumbs=[
                types.PhotoSize("m", 320, 180, 100),
                types.PhotoSize("x", 1280, 720, 800),
            ],
        )
        cached_page = types.Page(
            "https://example.com/cached-video",
            [],
            [],
            [video],
            v2=True,
        )
        webpage = types.WebPage(
            1822,
            "https://example.com/cached-video",
            "example.com/cached-video",
            0,
            cached_page=cached_page,
        )

        preview_collector = export.AttachmentCollector(
            1823,
            False,
            source_chat_id=7,
        )
        preview_collector.collect_media(
            types.MessageMediaWebPage(webpage),
            "message.media",
        )

        self.assertEqual(len(preview_collector.targets), 1)
        preview = preview_collector.targets[0]
        self.assertEqual(preview.metadata["type"], "image")
        self.assertEqual(preview.metadata["mime"], "image/jpeg")
        self.assertEqual(preview.extension, ".jpg")
        self.assertEqual(preview.expected_size, 800)
        self.assertEqual(preview.cache_key, f"document:{video.id}:thumb:x")
        self.assertEqual(preview.subtype, "image")

        media_collector = export.AttachmentCollector(
            1824,
            False,
            source_chat_id=7,
        )
        media_collector.collect_media(
            types.MessageMediaDocument(document=video),
            "message.media",
        )

        self.assertEqual(len(media_collector.targets), 1)
        media = media_collector.targets[0]
        self.assertEqual(media.metadata["type"], "video")
        self.assertEqual(media.metadata["mime"], "video/mp4")
        self.assertEqual(media.extension, ".mp4")
        self.assertEqual(media.expected_size, 5000)
        self.assertEqual(media.cache_key, f"document:{video.id}")
        self.assertEqual(media.subtype, "video")

    def test_media_references_match_selected_saved_rendition(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)

        def document(document_id, width, height, size):
            return types.Document(
                document_id,
                1,
                b"reference",
                now,
                "video/mp4",
                size,
                2,
                [types.DocumentAttributeVideo(1.0, width, height)],
            )

        low = document(10, 320, 180, 100)
        high = document(11, 1920, 1080, 1000)
        media = types.MessageMediaDocument(document=low, alt_documents=[high])
        normalized = export.normalized_content(media)
        collector = export.AttachmentCollector(1, False, source_chat_id=7)
        collector.collect_media(media, "message.media")
        self.assertEqual(normalized["document"]["id"], 11)
        self.assertEqual(collector.targets[0].metadata["id"], 11)
        self.assertNotIn("alt_documents", normalized)

        web_document = types.WebDocumentNoProxy(
            "https://example.com/signed?token=secret",
            100,
            "image/jpeg",
            [],
        )
        web_reference = export.normalized_content(web_document)
        self.assertNotIn("url", web_reference)
        self.assertNotIn("size", web_reference)

    def test_signed_urls_are_redacted_from_media_diagnostics(self):
        signed_url = "https://user:password@example.com/media?token=super-secret#private"
        request_info: Any = SimpleNamespace(real_url=signed_url)
        error = export.aiohttp.ClientResponseError(
            request_info,
            (),
            status=403,
            message="Forbidden",
        )

        safe_error = export.error_text(error)
        safe_source = export.safe_url_for_log(signed_url)

        self.assertIn("https://example.com/media", safe_error)
        self.assertEqual(safe_source, "https://example.com/media")
        assert safe_source is not None
        for secret in ("user", "password", "token", "super-secret", "private"):
            self.assertNotIn(secret, safe_error)
            self.assertNotIn(secret, safe_source)

    def test_tl_decode_error_text_never_exposes_raw_payload(self):
        error = export.errors.TypeNotFoundError(
            0x3A54685E,
            b"private message body and credentials",
        )

        safe_error = export.error_text(error)

        self.assertIn("constructor 0x3a54685e", safe_error)
        self.assertIn("36 bytes", safe_error)
        self.assertIn("sha256", safe_error)
        self.assertNotIn("private", safe_error)
        self.assertNotIn("credentials", safe_error)

    def test_tl_decode_failure_reconnects_reinitializes_and_retries(self):
        class BaseClient:
            def __init__(self):
                self.disconnects = 0
                self.connects = 0

            async def disconnect(self):
                self.disconnects += 1

            async def connect(self):
                self.connects += 1

        exporter: Any = object.__new__(export.ChatExporter)
        exporter.args = SimpleNamespace(retries=2, jitter=0.0)
        exporter.stats = export.ExportStats()
        exporter.base_client = BaseClient()
        calls = 0

        async def factory():
            nonlocal calls
            calls += 1
            if calls == 1:
                raise export.errors.TypeNotFoundError(
                    0x3A54685E,
                    b"private message body",
                )
            return "current-layer response"

        async def run():
            original_sleep = export.asyncio.sleep

            async def no_sleep(_delay):
                return None

            export.asyncio.sleep = no_sleep
            try:
                return await exporter.rpc(factory, "message history")
            finally:
                export.asyncio.sleep = original_sleep

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = asyncio.run(run())

        self.assertEqual(result, "current-layer response")
        self.assertEqual(calls, 2)
        self.assertEqual(exporter.base_client.disconnects, 1)
        self.assertEqual(exporter.base_client.connects, 1)
        self.assertEqual(exporter.stats.transient_retries, 1)
        self.assertIn("constructor 0x3a54685e", output.getvalue())
        self.assertIn("retrying 1/2", output.getvalue())
        self.assertNotIn("private message body", output.getvalue())

    def test_repeated_tl_decode_failures_are_bounded_and_safe(self):
        class BaseClient:
            def __init__(self):
                self.disconnects = 0
                self.connects = 0

            async def disconnect(self):
                self.disconnects += 1

            async def connect(self):
                self.connects += 1

        exporter: Any = object.__new__(export.ChatExporter)
        exporter.args = SimpleNamespace(retries=1, jitter=0.0)
        exporter.stats = export.ExportStats()
        exporter.base_client = BaseClient()
        calls = 0

        async def factory():
            nonlocal calls
            calls += 1
            raise export.errors.TypeNotFoundError(
                0x3A54685E,
                b"private message body",
            )

        async def run():
            original_sleep = export.asyncio.sleep

            async def no_sleep(_delay):
                return None

            export.asyncio.sleep = no_sleep
            try:
                return await exporter.rpc(factory, "message history")
            finally:
                export.asyncio.sleep = original_sleep

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(RuntimeError, "constructor 0x3a54685e") as raised:
                asyncio.run(run())

        self.assertEqual(calls, 2)
        self.assertEqual(exporter.base_client.disconnects, 1)
        self.assertEqual(exporter.base_client.connects, 1)
        self.assertEqual(exporter.stats.transient_retries, 2)
        self.assertNotIn("private message body", str(raised.exception))
        self.assertNotIn("private message body", output.getvalue())

    def test_marked_peers_fact_check_and_empty_reactions(self):
        now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
        giveaway = export.normalized_content(
            types.MessageMediaGiveaway([8], 1, now)
        )
        results = export.normalized_content(
            types.MessageMediaGiveawayResults(8, 1, 1, 0, [7], now)
        )
        area = export.normalized_content(
            types.MediaAreaChannelPost(types.MediaAreaCoordinates(1, 2, 3, 4, 0), 8, 9)
        )
        allowed_chats = export.normalized_content(
            types.PrivacyValueAllowChatParticipants([6])
        )
        requested_channel = export.normalized_content(
            types.RequestedPeerChannel(8, title="Channel")
        )
        requested_chat = export.normalized_content(
            types.RequestedPeerChat(6, title="Chat")
        )
        self.assertEqual(giveaway["channels"], [-1000000000008])
        self.assertEqual(results["channel_id"], -1000000000008)
        self.assertEqual(area["channel_id"], -1000000000008)
        self.assertEqual(allowed_chats["raw_chat_ids"], [6])
        self.assertEqual(requested_channel["channel_id"], -1000000000008)
        self.assertEqual(requested_chat["chat_id"], -6)
        thread = export.thread_summary(
            SimpleNamespace(replies=types.MessageReplies(3, 987, channel_id=8))
        )
        self.assertEqual(thread["replies"], 3)
        self.assertEqual(thread["channel_id"], -1000000000008)
        self.assertNotIn("replies_pts", thread)

        fact_check = export.normalized_content(
            types.FactCheck(123, text=types.TextWithEntities("checked", []))
        )
        self.assertEqual(fact_check["hash"], 123)

        message = types.Message(
            id=4,
            peer_id=types.PeerUser(7),
            date=now,
            message="",
            reactions=types.MessageReactions(
                [types.ReactionCount(types.ReactionEmpty(), 0)],
                recent_reactions=[
                    types.MessagePeerReaction(
                        types.PeerUser(7), now, types.ReactionEmpty()
                    )
                ],
                top_reactors=[types.MessageReactor(0)],
            ),
        )
        row = self.serialize(message)
        self.assertNotIn("reactions", row)

    def test_writer_rejects_non_resumable_checkpoint(self):
        with self.assertRaisesRegex(ValueError, "history_source"):
            export.validate_message_contract(
                {
                    "id": 1,
                    "source": 7,
                    "author": 7,
                    "history_source": 0,
                    "created": 1,
                }
            )
        base = {
            "id": 1,
            "source": 7,
            "author": 7,
            "created": 1,
        }
        export.validate_message_contract(base)
        with self.assertRaisesRegex(ValueError, "non-zero integer or omitted"):
            export.validate_message_contract({**base, "history_source": None})
        with self.assertRaisesRegex(ValueError, "omitted when it equals source"):
            export.validate_message_contract({**base, "history_source": 7})
        export.validate_message_contract({**base, "history_source": 8})
        with self.assertRaisesRegex(ValueError, "unescaped MarkdownV2 string"):
            export.validate_message_contract({**base, "data": {"text": "legacy"}})
        with self.assertRaisesRegex(ValueError, "top-level formatted is not allowed"):
            export.validate_message_contract(
                {**base, "formatted": {"markdown_v2": "legacy"}}
            )
        export.validate_message_contract(
            {
                **base,
                "attachments": [
                    {
                        "type": "image",
                        "file": "files/media/photo.jpg",
                        "hash": "0" * 64,
                    }
                ],
            }
        )
        for forbidden_field, value in (
            ("role", "message.media"),
            ("roles", ["message.media.photo"]),
            ("category", "media"),
        ):
            with self.subTest(forbidden_field=forbidden_field):
                with self.assertRaisesRegex(ValueError, "unsupported fields"):
                    export.validate_message_contract(
                        {
                            **base,
                            "attachments": [
                                {"type": "image", forbidden_field: value}
                            ],
                        }
                    )
        with self.assertRaisesRegex(ValueError, "current files category"):
            export.validate_message_contract(
                {
                    **base,
                    "attachments": [
                        {
                            "type": "image",
                            "file": "files/not-a-category/photo.jpg",
                            "hash": "0" * 64,
                        }
                    ],
                }
            )
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            export.validate_message_contract(
                {
                    **base,
                    "attachments": [
                        {
                            "type": "image",
                            "file": "files/media/photo.jpg",
                        }
                    ],
                }
            )

    def test_default_pacing_is_zero_and_zero_base_ignores_global_jitter(self):
        parser = export.build_parser()
        args = parser.parse_args(
            ["chat", "--api-id", "1", "--api-hash", "hash"]
        )
        self.assertEqual(
            (
                args.history_delay,
                args.metadata_delay,
                args.media_delay,
                args.chunk_delay,
                args.jitter,
                args.flood_reserve,
            ),
            (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        )

        pacer = export.Pacer(
            history_delay=args.history_delay,
            metadata_delay=args.metadata_delay,
            media_delay=args.media_delay,
            chunk_delay=args.chunk_delay,
            jitter=0.75,
            flood_reserve=args.flood_reserve,
        )
        sleep_calls = []
        original_sleep = export.asyncio.sleep
        original_uniform = export.random.uniform

        async def record_sleep(delay):
            sleep_calls.append(delay)

        def unexpected_uniform(_minimum, _maximum):
            raise AssertionError("successful chunk pacing must not use jitter")

        export.asyncio.sleep = record_sleep
        export.random.uniform = unexpected_uniform
        try:
            async def pace_success_paths():
                await pacer.sleep(0.0)
                await pacer.after_history()
                await pacer.after_metadata()
                await pacer.after_media()
                await pacer.after_chunk()

            asyncio.run(pace_success_paths())
        finally:
            export.asyncio.sleep = original_sleep
            export.random.uniform = original_uniform

        self.assertEqual(sleep_calls, [])

    def test_explicit_chunk_delay_is_exact_without_global_jitter(self):
        pacer = export.Pacer(
            history_delay=0.0,
            metadata_delay=0.0,
            media_delay=0.0,
            chunk_delay=0.25,
            jitter=0.75,
            flood_reserve=0.0,
        )
        sleep_calls = []
        original_sleep = export.asyncio.sleep
        original_uniform = export.random.uniform

        async def record_sleep(delay):
            sleep_calls.append(delay)

        def unexpected_uniform(_minimum, _maximum):
            raise AssertionError("explicit chunk delay must not use jitter")

        export.asyncio.sleep = record_sleep
        export.random.uniform = unexpected_uniform
        try:
            asyncio.run(pacer.after_chunk())
        finally:
            export.asyncio.sleep = original_sleep
            export.random.uniform = original_uniform

        self.assertEqual(sleep_calls, [0.25])

    def test_flood_wait_still_adds_reserve_and_global_jitter(self):
        pacer = export.Pacer(
            history_delay=0.0,
            metadata_delay=0.0,
            media_delay=0.0,
            chunk_delay=0.0,
            jitter=0.5,
            flood_reserve=5.0,
        )
        sleep_calls = []
        uniform_calls = []
        original_sleep = export.asyncio.sleep
        original_uniform = export.random.uniform

        async def record_sleep(delay):
            sleep_calls.append(delay)

        def fixed_uniform(minimum, maximum):
            uniform_calls.append((minimum, maximum))
            return 0.3

        export.asyncio.sleep = record_sleep
        export.random.uniform = fixed_uniform
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                asyncio.run(pacer.flood_wait(9, "test request"))
        finally:
            export.asyncio.sleep = original_sleep
            export.random.uniform = original_uniform

        self.assertEqual(uniform_calls, [(0.0, 0.5)])
        self.assertEqual(sleep_calls, [14.3])
        self.assertIn("sleeping 14.3s", output.getvalue())

    def test_media_flood_wait_is_bounded_logged_and_does_not_block_next_file(self):
        class RecordingPacer:
            def __init__(self):
                self.flood_waits = []
                self.media_delays = 0

            async def flood_wait(self, seconds, label):
                self.flood_waits.append((seconds, label))

            async def after_chunk(self):
                return None

            async def after_media(self):
                self.media_delays += 1

        class DownloadApi:
            def __init__(self):
                self.calls = {"blocked": 0, "good": 0}

            async def download_media(
                self,
                media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                self.calls[media] += 1
                if media == "blocked" and self.calls[media] <= 4:
                    raise export.errors.FloodWaitError(request=None, capture=0)
                Path(file).write_bytes(b"downloaded")
                return file

        def target(media, message_id):
            return export.DownloadTarget(
                obj=media,
                kind="media",
                subtype="file",
                role="message.media.document",
                message_id=message_id,
                cache_key=f"document:{message_id}",
                extension=".bin",
                expected_size=None,
                metadata={"type": "file", "id": message_id},
                source_chat_id=7,
            )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=6,
                jitter=0.0,
            )
            exporter.pacer = RecordingPacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()

            api = DownloadApi()
            unavailable = asyncio.run(
                exporter.download_target(api, target("blocked", 41), 1)
            )
            downloaded = asyncio.run(
                exporter.download_target(api, target("good", 42), 1)
            )

            # Media flood retries are capped independently at three directed
            # waits followed by one final probe. A fourth flood response skips
            # only this unavailable asset, despite the larger generic budget.
            self.assertEqual(api.calls["blocked"], 4)
            self.assertEqual(unavailable["status"], "unavailable")
            self.assertEqual(unavailable["reason"], "flood_wait_limit")
            self.assertEqual(unavailable["error_type"], "FloodWaitError")
            self.assertEqual(unavailable["attempts"], 4)
            public_unavailable = export.public_attachment_record(unavailable)
            self.assertEqual(
                public_unavailable,
                {
                    "type": "file",
                    "id": 41,
                    "status": "unavailable",
                    "reason": "flood_wait_limit",
                },
            )
            export.validate_message_contract(
                {
                    "id": 41,
                    "source": 7,
                    "author": 7,
                    "created": 1,
                    "attachments": [public_unavailable],
                }
            )
            self.assertEqual(exporter.stats.flood_waits, 3)
            self.assertEqual(
                exporter.pacer.flood_waits,
                [
                    (
                        0,
                        "media message.media.document in message 41 "
                        "(media 41, wait 1/3)",
                    ),
                    (
                        0,
                        "media message.media.document in message 41 "
                        "(media 41, wait 2/3)",
                    ),
                    (
                        0,
                        "media message.media.document in message 41 "
                        "(media 41, wait 3/3)",
                    ),
                ],
            )

            self.assertEqual(api.calls["good"], 1)
            self.assertEqual(downloaded["status"], "downloaded")
            self.assertTrue((output / downloaded["file"]).is_file())

            issues = [
                json.loads(line)
                for line in exporter.error_log_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["message_id"], 41)
            self.assertEqual(issues[0]["media_id"], 41)
            self.assertEqual(issues[0]["status"], "unavailable")
            self.assertEqual(issues[0]["reason"], "flood_wait_limit")
            self.assertEqual(issues[0]["error_type"], "FloodWaitError")
            self.assertIn("wait of 0 seconds", issues[0]["error"])
            self.assertEqual(issues[0]["attempts"], 4)
            self.assertEqual(
                [
                    item["telegram_wait_seconds"]
                    for item in issues[0]["flood_wait_history"]
                ],
                [0, 0, 0, 0],
            )

    def test_aligned_document_partial_resumes_with_iter_download(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE
        prefix = b"p" * chunk_size
        suffix = b"finished"

        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class DownloadStream:
            def __init__(self):
                self.chunks = iter((suffix,))
                self.closed = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    return next(self.chunks)
                except StopIteration:
                    raise StopAsyncIteration

            async def close(self):
                self.closed = True

        class BaseClient:
            def __init__(self):
                self.calls = []
                self.stream = DownloadStream()

            def iter_download(self, media, **kwargs):
                self.calls.append((media, kwargs))
                return self.stream

        class UnexpectedDownloadApi:
            async def download_media(self, *_args, **_kwargs):
                raise AssertionError("a resumable partial must use iter_download")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            base_client = BaseClient()
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = base_client
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=0.25,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()

            media = object()
            target = export.DownloadTarget(
                obj=media,
                kind="document",
                subtype="file",
                role="message.media.document",
                message_id=51,
                cache_key="document:51",
                extension=".bin",
                expected_size=len(prefix) + len(suffix),
                metadata={"type": "file", "id": 51},
                source_chat_id=7,
                dc_id=4,
            )
            final_path = (
                exporter.files_dir
                / export.attachment_category(target)
                / exporter.target_filename(target, 1)
            )
            partial_path = final_path.with_suffix(final_path.suffix + ".part")
            partial_path.parent.mkdir(parents=True)
            partial_path.write_bytes(prefix)

            async def run():
                return await asyncio.wait_for(
                    exporter.download_target(UnexpectedDownloadApi(), target, 1),
                    timeout=1.0,
                )

            record = asyncio.run(run())

            self.assertEqual(record["status"], "downloaded")
            self.assertEqual(final_path.read_bytes(), prefix + suffix)
            self.assertFalse(partial_path.exists())
            self.assertTrue(base_client.stream.closed)
            self.assertEqual(len(base_client.calls), 1)
            called_media, kwargs = base_client.calls[0]
            self.assertIs(called_media, media)
            self.assertEqual(kwargs["offset"], len(prefix))
            self.assertEqual(kwargs["request_size"], chunk_size)
            self.assertEqual(kwargs["chunk_size"], chunk_size)
            self.assertEqual(kwargs["file_size"], len(prefix) + len(suffix))
            self.assertEqual(kwargs["dc_id"], 4)

    def test_parallel_document_resume_commits_out_of_order_lanes_in_order(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE
        prefix = b"p" * chunk_size
        first = b"a" * chunk_size
        second = b"b" * chunk_size
        final = b"tail"
        expected_size = len(prefix + first + second + final)
        completion_order = []
        progress = []

        class DownloadStream:
            def __init__(self, lane, values):
                self.lane = lane
                self.values = iter(values)
                self.closed = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    value = next(self.values)
                except StopIteration:
                    raise StopAsyncIteration
                base_client.active += 1
                base_client.max_active = max(
                    base_client.max_active, base_client.active
                )
                try:
                    # Lane 1 must be allowed to finish before lane 0. This
                    # catches implementations which merely alternate two
                    # sequential requests instead of keeping both in flight.
                    if self.lane == 0 and not completion_order:
                        await asyncio.sleep(0.02)
                    completion_order.append(self.lane)
                    return value
                finally:
                    base_client.active -= 1

            async def close(self):
                self.closed = True

        class BaseClient:
            def __init__(self):
                self.calls = []
                self.streams = []
                self.active = 0
                self.max_active = 0

            def iter_download(self, media, **kwargs):
                self.calls.append((media, kwargs))
                lane = len(self.calls) - 1
                values = ((first, final), (second,))[lane]
                stream = DownloadStream(lane, values)
                self.streams.append(stream)
                return stream

        async def progress_callback(downloaded, total):
            progress.append((downloaded, total))

        with tempfile.TemporaryDirectory() as directory:
            partial_path = Path(directory) / "video.mov.part"
            partial_path.write_bytes(prefix)
            base_client = BaseClient()
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.base_client = base_client
            media = object()
            target = export.DownloadTarget(
                obj=media,
                kind="document",
                subtype="video",
                role="message.media.document",
                message_id=57,
                cache_key="document:57",
                extension=".mov",
                expected_size=expected_size,
                metadata={"type": "video", "id": 57},
                source_chat_id=7,
                dc_id=4,
            )

            asyncio.run(
                asyncio.wait_for(
                    exporter.download_document_parallel(
                        target,
                        partial_path,
                        len(prefix),
                        expected_size,
                        progress_callback,
                        workers=2,
                    ),
                    timeout=1.0,
                )
            )

            self.assertEqual(partial_path.read_bytes(), prefix + first + second + final)
            self.assertEqual(completion_order[:2], [1, 0])
            self.assertEqual(base_client.max_active, 2)
            self.assertEqual(len(base_client.calls), 2)
            expected_calls = (
                (len(prefix), 2),
                (len(prefix) + chunk_size, 1),
            )
            for (called_media, kwargs), (offset, limit) in zip(
                base_client.calls, expected_calls
            ):
                self.assertIs(called_media, media)
                self.assertEqual(kwargs["offset"], offset)
                self.assertEqual(kwargs["stride"], 2 * chunk_size)
                self.assertEqual(kwargs["limit"], limit)
                self.assertEqual(kwargs["request_size"], chunk_size)
                self.assertEqual(kwargs["chunk_size"], chunk_size)
                self.assertEqual(kwargs["file_size"], expected_size)
                self.assertEqual(kwargs["dc_id"], 4)
            self.assertTrue(all(stream.closed for stream in base_client.streams))
            self.assertEqual(
                progress,
                [
                    (len(prefix) + len(first), expected_size),
                    (len(prefix) + len(first) + len(second), expected_size),
                    (expected_size, expected_size),
                ],
            )

    def test_parallel_document_does_not_commit_successful_half_round(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE
        prefix = b"p" * chunk_size
        first = b"a" * chunk_size
        expected_size = len(prefix) + 2 * chunk_size
        progress = []

        class ExpectedFailure(RuntimeError):
            pass

        class DownloadStream:
            def __init__(self, lane):
                self.lane = lane
                self.closed = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.lane == 0:
                    return first
                await asyncio.sleep(0.01)
                raise ExpectedFailure("second lane failed")

            async def close(self):
                self.closed = True

        class BaseClient:
            def __init__(self):
                self.streams = []

            def iter_download(self, _media, **_kwargs):
                stream = DownloadStream(len(self.streams))
                self.streams.append(stream)
                return stream

        async def progress_callback(downloaded, total):
            progress.append((downloaded, total))

        with tempfile.TemporaryDirectory() as directory:
            partial_path = Path(directory) / "video.mov.part"
            partial_path.write_bytes(prefix)
            base_client = BaseClient()
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.base_client = base_client
            target = export.DownloadTarget(
                obj=object(),
                kind="document",
                subtype="video",
                role="message.media.document",
                message_id=58,
                cache_key="document:58",
                extension=".mov",
                expected_size=expected_size,
                metadata={"type": "video", "id": 58},
                source_chat_id=7,
            )

            async def run():
                await exporter.download_document_parallel(
                    target,
                    partial_path,
                    len(prefix),
                    expected_size,
                    progress_callback,
                    workers=2,
                )

            with self.assertRaisesRegex(ExpectedFailure, "second lane failed"):
                asyncio.run(asyncio.wait_for(run(), timeout=1.0))

            self.assertEqual(partial_path.read_bytes(), prefix)
            self.assertEqual(progress, [])
            self.assertEqual(len(base_client.streams), 2)
            self.assertTrue(all(stream.closed for stream in base_client.streams))

    def test_parallel_document_cancels_sibling_without_masking_primary_error(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE
        prefix = b"p" * chunk_size
        expected_size = len(prefix) + 2 * chunk_size

        class ExpectedFailure(RuntimeError):
            pass

        class DownloadStream:
            def __init__(self, lane):
                self.lane = lane
                self.cancelled = False
                self.closed = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.lane == 0:
                    await asyncio.sleep(0)
                    raise ExpectedFailure("first lane failed")
                try:
                    await asyncio.get_running_loop().create_future()
                except asyncio.CancelledError:
                    self.cancelled = True
                    raise

            async def close(self):
                self.closed = True
                if self.lane == 1:
                    raise AttributeError("cleanup must not mask download error")

        class BaseClient:
            def __init__(self):
                self.streams = []

            def iter_download(self, _media, **_kwargs):
                stream = DownloadStream(len(self.streams))
                self.streams.append(stream)
                return stream

        async def progress_callback(_downloaded, _total):
            raise AssertionError("failed round must not report progress")

        with tempfile.TemporaryDirectory() as directory:
            partial_path = Path(directory) / "video.mov.part"
            partial_path.write_bytes(prefix)
            base_client = BaseClient()
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.base_client = base_client
            target = export.DownloadTarget(
                obj=object(),
                kind="document",
                subtype="video",
                role="message.media.document",
                message_id=59,
                cache_key="document:59",
                extension=".mov",
                expected_size=expected_size,
                metadata={"type": "video", "id": 59},
                source_chat_id=7,
            )

            async def run():
                await exporter.download_document_parallel(
                    target,
                    partial_path,
                    len(prefix),
                    expected_size,
                    progress_callback,
                    workers=2,
                )

            with self.assertRaisesRegex(ExpectedFailure, "first lane failed"):
                asyncio.run(asyncio.wait_for(run(), timeout=1.0))

            self.assertEqual(partial_path.read_bytes(), prefix)
            self.assertEqual(len(base_client.streams), 2)
            self.assertTrue(base_client.streams[1].cancelled)
            self.assertTrue(all(stream.closed for stream in base_client.streams))

    def test_parallel_document_cdn_redirect_falls_back_immediately(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE
        expected_size = 2 * chunk_size
        parallel_calls = []
        sleep_calls = []

        class _CdnRedirect(Exception):
            pass

        class Pacer:
            def __init__(self):
                self.media_delays = 0

            async def after_chunk(self):
                return None

            async def after_media(self):
                self.media_delays += 1

        class DownloadApi:
            def __init__(self):
                self.calls = 0
                self.partial_existed_at_call = None

            async def download_media(
                self,
                _media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                self.calls += 1
                self.partial_existed_at_call = Path(file).exists()
                Path(file).write_bytes(b"z" * expected_size)
                await progress_callback(expected_size, expected_size)
                return file

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = SimpleNamespace()
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=0.25,
                media_progress_interval=0.0,
                media_download_workers=2,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()
            target = export.DownloadTarget(
                obj=object(),
                kind="document",
                subtype="video",
                role="message.media.document",
                message_id=60,
                cache_key="document:60",
                extension=".mov",
                expected_size=expected_size,
                metadata={"type": "video", "id": 60},
                source_chat_id=7,
                dc_id=4,
            )

            async def redirecting_parallel(
                called_target,
                partial_path,
                resume_offset,
                called_expected_size,
                _progress_callback,
                *,
                workers,
            ):
                parallel_calls.append(
                    (
                        called_target,
                        resume_offset,
                        called_expected_size,
                        workers,
                    )
                )
                Path(partial_path).write_bytes(b"p" * chunk_size)
                raise _CdnRedirect("test CDN redirect")

            async def unexpected_sleep(delay):
                sleep_calls.append(delay)
                raise AssertionError("CDN fallback must not sleep")

            exporter.download_document_parallel = redirecting_parallel
            api = DownloadApi()
            original_min_size = export.PARALLEL_DOCUMENT_MIN_SIZE
            original_sleep = export.asyncio.sleep
            export.PARALLEL_DOCUMENT_MIN_SIZE = 1
            export.asyncio.sleep = unexpected_sleep
            try:
                record = asyncio.run(exporter.download_target(api, target, 1))
            finally:
                export.PARALLEL_DOCUMENT_MIN_SIZE = original_min_size
                export.asyncio.sleep = original_sleep

            self.assertEqual(
                parallel_calls,
                [(target, 0, expected_size, 2)],
            )
            self.assertEqual(api.calls, 1)
            self.assertFalse(api.partial_existed_at_call)
            self.assertEqual(sleep_calls, [])
            self.assertEqual(record["status"], "downloaded")
            self.assertEqual(record["downloaded_size"], expected_size)
            final_path = output / record["file"]
            self.assertEqual(final_path.read_bytes(), b"z" * expected_size)
            self.assertFalse(
                final_path.with_suffix(final_path.suffix + ".part").exists()
            )
            self.assertEqual(exporter.pacer.media_delays, 1)

    def test_expired_document_reference_resumes_bytes_downloaded_before_error(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE
        prefix = b"p" * chunk_size
        suffix = b"after-refresh"

        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class DownloadStream:
            def __init__(self):
                self.chunks = iter((suffix,))
                self.closed = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    return next(self.chunks)
                except StopIteration:
                    raise StopAsyncIteration

            async def close(self):
                self.closed = True

        class BaseClient:
            def __init__(self):
                self.calls = []
                self.stream = DownloadStream()

            def iter_download(self, media, **kwargs):
                self.calls.append((media, kwargs))
                return self.stream

        class DownloadApi:
            def __init__(self):
                self.calls = []

            async def download_media(
                self,
                media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                self.calls.append(media)
                if media.file_reference != b"expired":
                    raise AssertionError(
                        "fresh-reference continuation must use iter_download"
                    )
                Path(file).write_bytes(prefix)
                await progress_callback(len(prefix), len(prefix) + len(suffix))
                raise export.errors.FileReferenceExpiredError(request=None)

        def target(file_reference):
            return export.DownloadTarget(
                obj=SimpleNamespace(file_reference=file_reference),
                kind="document",
                subtype="file",
                role="message.media.document",
                message_id=54,
                cache_key="document:54",
                extension=".bin",
                expected_size=len(prefix) + len(suffix),
                metadata={"type": "file", "id": 54},
                source_chat_id=7,
                dc_id=2,
            )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            base_client = BaseClient()
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = base_client
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=1,
                jitter=0.0,
                media_stall_timeout=0.25,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()

            async def refresh_target(_api, stale_target, diagnostic):
                diagnostic.update(
                    strategy="test",
                    file_reference_before=export.file_reference_fingerprint(
                        stale_target.obj
                    ),
                    steps=[],
                )
                return target(b"fresh")

            exporter.refresh_target = refresh_target
            original_target = target(b"expired")
            final_path = (
                exporter.files_dir
                / export.attachment_category(original_target)
                / exporter.target_filename(original_target, 1)
            )
            partial_path = final_path.with_suffix(final_path.suffix + ".part")
            api = DownloadApi()

            async def run():
                return await asyncio.wait_for(
                    exporter.download_target(api, original_target, 1),
                    timeout=1.0,
                )

            record = asyncio.run(run())

            self.assertEqual(api.calls, [original_target.obj])
            self.assertEqual(len(base_client.calls), 1)
            resumed_media, kwargs = base_client.calls[0]
            self.assertEqual(resumed_media.file_reference, b"fresh")
            self.assertEqual(kwargs["offset"], chunk_size)
            self.assertEqual(kwargs["request_size"], chunk_size)
            self.assertEqual(kwargs["chunk_size"], chunk_size)
            self.assertEqual(kwargs["file_size"], len(prefix) + len(suffix))
            self.assertEqual(kwargs["dc_id"], 2)
            self.assertTrue(base_client.stream.closed)
            self.assertEqual(record["status"], "downloaded")
            self.assertEqual(record["attempts"], 1)
            self.assertEqual(
                record["file_reference_refresh"][0]["result"], "refreshed"
            )
            self.assertEqual(final_path.read_bytes(), prefix + suffix)
            self.assertFalse(partial_path.exists())

    def test_expired_reference_then_stalled_document_keeps_resumable_partial(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE

        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class BaseClient:
            async def disconnect(self):
                return None

            async def connect(self):
                return None

        class DownloadApi:
            def __init__(self):
                self.calls = 0
                self.cancelled = False

            async def download_media(
                self,
                media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                self.calls += 1
                if media.file_reference == b"expired":
                    raise export.errors.FileReferenceExpiredError(request=None)
                Path(file).write_bytes(b"p" * chunk_size)
                await progress_callback(chunk_size, chunk_size * 2)
                try:
                    await asyncio.get_running_loop().create_future()
                except asyncio.CancelledError:
                    self.cancelled = True
                    raise

        def target(file_reference):
            return export.DownloadTarget(
                obj=SimpleNamespace(file_reference=file_reference),
                kind="document",
                subtype="file",
                role="message.media.document",
                message_id=52,
                cache_key="document:52",
                extension=".bin",
                expected_size=chunk_size * 2,
                metadata={"type": "file", "id": 52},
                source_chat_id=7,
            )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = BaseClient()
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=0.02,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()

            async def refresh_target(_api, _target, diagnostic):
                diagnostic.update(
                    strategy="test",
                    file_reference_before=export.file_reference_fingerprint(
                        _target.obj
                    ),
                    steps=[],
                )
                return target(b"fresh")

            exporter.refresh_target = refresh_target
            original_target = target(b"expired")
            final_path = (
                exporter.files_dir
                / export.attachment_category(original_target)
                / exporter.target_filename(original_target, 1)
            )
            partial_path = final_path.with_suffix(final_path.suffix + ".part")
            api = DownloadApi()

            async def run():
                return await asyncio.wait_for(
                    exporter.download_target(api, original_target, 1),
                    timeout=1.0,
                )

            record = asyncio.run(run())

            self.assertEqual(api.calls, 2)
            self.assertTrue(api.cancelled)
            self.assertEqual(record["status"], "failed")
            self.assertEqual(record["reason"], "download_stalled")
            self.assertEqual(record["partial_bytes"], chunk_size)
            self.assertEqual(
                record["partial_file"],
                final_path.relative_to(output).as_posix() + ".part",
            )
            self.assertEqual(partial_path.stat().st_size, chunk_size)
            self.assertFalse(final_path.exists())
            self.assertEqual(
                record["file_reference_refresh"][0]["result"], "refreshed"
            )
            issue = json.loads(
                exporter.error_log_path.read_text(encoding="utf-8").splitlines()[0]
            )
            self.assertEqual(issue["message_id"], 52)
            self.assertEqual(issue["media_id"], 52)
            self.assertEqual(issue["reason"], "download_stalled")
            self.assertEqual(
                issue["file_reference_refresh"][0]["result"], "refreshed"
            )

    def test_stalled_file_reference_refresh_is_bounded_and_keeps_partial(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE

        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class DownloadApi:
            async def download_media(
                self,
                _media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                Path(file).write_bytes(b"p" * chunk_size)
                await progress_callback(chunk_size, chunk_size * 2)
                raise export.errors.FileReferenceExpiredError(request=None)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = SimpleNamespace()
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=0.02,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()
            target = export.DownloadTarget(
                obj=SimpleNamespace(file_reference=b"expired"),
                kind="document",
                subtype="file",
                role="message.media.document",
                message_id=55,
                cache_key="document:55",
                extension=".bin",
                expected_size=chunk_size * 2,
                metadata={"type": "file", "id": 55},
                source_chat_id=7,
            )
            final_path = (
                exporter.files_dir
                / export.attachment_category(target)
                / exporter.target_filename(target, 1)
            )
            partial_path = final_path.with_suffix(final_path.suffix + ".part")
            refresh_cancelled = False

            async def stalled_refresh(_api, _target, diagnostic):
                nonlocal refresh_cancelled
                diagnostic.update(
                    strategy="test",
                    file_reference_before=export.file_reference_fingerprint(
                        _target.obj
                    ),
                    steps=[],
                )
                try:
                    await asyncio.get_running_loop().create_future()
                except asyncio.CancelledError:
                    refresh_cancelled = True
                    raise

            exporter.refresh_target = stalled_refresh

            async def run():
                return await asyncio.wait_for(
                    exporter.download_target(DownloadApi(), target, 1),
                    timeout=1.0,
                )

            record = asyncio.run(run())

            self.assertTrue(refresh_cancelled)
            self.assertEqual(record["status"], "failed")
            self.assertEqual(record["reason"], "file_reference_refresh_failed")
            self.assertEqual(record["partial_bytes"], chunk_size)
            self.assertEqual(partial_path.stat().st_size, chunk_size)
            self.assertFalse(final_path.exists())
            refresh = record["file_reference_refresh"][0]
            self.assertEqual(refresh["result"], "refresh_error")
            self.assertEqual(refresh["error_type"], "TimeoutError")
            issue = json.loads(
                exporter.error_log_path.read_text(encoding="utf-8").splitlines()[0]
            )
            self.assertEqual(issue["message_id"], 55)
            self.assertEqual(issue["media_id"], 55)
            self.assertEqual(issue["reason"], "file_reference_refresh_failed")
            self.assertEqual(
                issue["file_reference_refresh"][0]["error_type"],
                "TimeoutError",
            )

    def test_resumed_stream_close_error_does_not_mask_primary_stall(self):
        chunk_size = export.TELEGRAM_DOWNLOAD_CHUNK_SIZE

        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class StalledStream:
            def __init__(self):
                self.cancelled = False
                self.closed = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    await asyncio.get_running_loop().create_future()
                except asyncio.CancelledError:
                    self.cancelled = True
                    raise

            async def close(self):
                self.closed = True
                raise AttributeError("simulated stream cleanup failure")

        class BaseClient:
            def __init__(self):
                self.stream = StalledStream()

            def iter_download(self, _media, **_kwargs):
                return self.stream

        class UnexpectedDownloadApi:
            async def download_media(self, *_args, **_kwargs):
                raise AssertionError("existing partial must use iter_download")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            base_client = BaseClient()
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = base_client
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=0.02,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()
            target = export.DownloadTarget(
                obj="document",
                kind="document",
                subtype="file",
                role="message.media.document",
                message_id=56,
                cache_key="document:56",
                extension=".bin",
                expected_size=chunk_size * 2,
                metadata={"type": "file", "id": 56},
                source_chat_id=7,
            )
            final_path = (
                exporter.files_dir
                / export.attachment_category(target)
                / exporter.target_filename(target, 1)
            )
            partial_path = final_path.with_suffix(final_path.suffix + ".part")
            partial_path.parent.mkdir(parents=True)
            partial_path.write_bytes(b"p" * chunk_size)

            async def run():
                return await asyncio.wait_for(
                    exporter.download_target(UnexpectedDownloadApi(), target, 1),
                    timeout=1.0,
                )

            record = asyncio.run(run())

            self.assertTrue(base_client.stream.cancelled)
            self.assertTrue(base_client.stream.closed)
            self.assertEqual(record["status"], "failed")
            self.assertEqual(record["reason"], "download_stalled")
            self.assertEqual(record["error_type"], "TimeoutError")
            self.assertNotIn("cleanup failure", record["error"])
            self.assertEqual(record["partial_bytes"], chunk_size)
            self.assertEqual(partial_path.stat().st_size, chunk_size)
            self.assertFalse(final_path.exists())
            issue = json.loads(
                exporter.error_log_path.read_text(encoding="utf-8").splitlines()[0]
            )
            self.assertEqual(issue["message_id"], 56)
            self.assertEqual(issue["reason"], "download_stalled")
            self.assertEqual(issue["error_type"], "TimeoutError")

    def test_media_progress_resets_stall_watchdog(self):
        stall_timeout = 0.15

        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class DownloadApi:
            async def download_media(
                self,
                _media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                with Path(file).open("wb") as output:
                    for downloaded in (1, 2):
                        await asyncio.sleep(0.08)
                        output.write(b"x")
                        await progress_callback(downloaded, 2)
                return file

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.base_client = SimpleNamespace()
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=stall_timeout,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.referenced_files = set()
            target = export.DownloadTarget(
                obj="progressing",
                kind="document",
                subtype="file",
                role="message.media.document",
                message_id=53,
                cache_key="document:53",
                extension=".bin",
                expected_size=2,
                metadata={"type": "file", "id": 53},
                source_chat_id=7,
            )

            async def run():
                loop = asyncio.get_running_loop()
                started = loop.time()
                record = await asyncio.wait_for(
                    exporter.download_target(DownloadApi(), target, 1),
                    timeout=1.0,
                )
                return record, loop.time() - started

            record, elapsed = asyncio.run(run())

            self.assertGreater(elapsed, stall_timeout)
            self.assertEqual(record["status"], "downloaded")
            self.assertEqual((output / record["file"]).read_bytes(), b"xx")

    def test_parser_rejects_negative_media_watchdog_values(self):
        for option in ("--media-stall-timeout", "--media-progress-interval"):
            with self.subTest(option=option):
                parser = export.build_parser()
                args = parser.parse_args(
                    [
                        "chat",
                        "--api-id",
                        "1",
                        "--api-hash",
                        "hash",
                        option,
                        "-0.1",
                    ]
                )
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as raised:
                        export.validate_args(args, parser)
                self.assertEqual(raised.exception.code, 2)
                self.assertIn(option, stderr.getvalue())

    def test_parser_defaults_to_two_media_download_workers_and_rejects_zero(self):
        parser = export.build_parser()
        args = parser.parse_args(
            ["chat", "--api-id", "1", "--api-hash", "hash"]
        )
        self.assertEqual(args.media_download_workers, 2)

        args = parser.parse_args(
            [
                "chat",
                "--api-id",
                "1",
                "--api-hash",
                "hash",
                "--media-download-workers",
                "0",
            ]
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                export.validate_args(args, parser)
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("--media-download-workers", stderr.getvalue())

    def test_empty_placeholders_advance_history_without_becoming_rows(self):
        class Pacer:
            async def after_history(self):
                return None

        source = self.source()
        exporter: Any = object.__new__(export.ChatExporter)
        exporter.pacer = Pacer()
        exporter.stats = export.ExportStats()
        exporter.remember_peers = lambda _response: None

        high_watermark_pages = [
            SimpleNamespace(
                messages=[
                    types.MessageEmpty(id=value, peer_id=types.PeerUser(7))
                    for value in range(200, 100, -1)
                ]
            ),
            SimpleNamespace(
                messages=[
                    types.Message(
                        id=100,
                        peer_id=types.PeerUser(7),
                        date=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
                        message="oldest available",
                    )
                ]
            ),
        ]

        async def high_watermark_page(*_args, **_kwargs):
            return high_watermark_pages.pop(0)

        exporter.history_page = high_watermark_page
        snapshots = asyncio.run(
            exporter.source_range_high_watermarks(None, source, [None])
        )
        self.assertEqual(snapshots, [(None, 100, 1)])

        ascending_pages = [
            SimpleNamespace(
                messages=[
                    types.MessageEmpty(id=value, peer_id=types.PeerUser(7))
                    for value in range(100, 0, -1)
                ]
            ),
            SimpleNamespace(
                messages=[
                    types.Message(
                        id=101,
                        peer_id=types.PeerUser(7),
                        date=dt.datetime(2025, 1, 2, tzinfo=dt.timezone.utc),
                        message="available",
                    )
                ]
            ),
        ]

        async def ascending_page(*_args, **_kwargs):
            return ascending_pages.pop(0)

        async def no_op(*_args, **_kwargs):
            return None

        exporter.history_page = ascending_page
        exporter.hydrate_stories = no_op
        exporter.resolve_custom_emojis = no_op
        exporter.resolve_message_effects = no_op

        async def collect():
            return [
                item
                async for item in exporter.iter_source_messages_ascending(
                    None,
                    source,
                    [(None, 101, 1)],
                    0,
                    2_000_000_000,
                )
            ]

        rows = asyncio.run(collect())
        self.assertEqual([item[0].id for item in rows], [101])
        self.assertEqual(exporter.stats.empty_messages_skipped, 100)

    def test_partial_jsonl_resumes_after_last_verified_message_and_media(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            metadata_path = output / "7.metadata.json"
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            media_path = output / "files" / "media" / "saved.bin"
            media_path.parent.mkdir(parents=True)
            media_path.write_bytes(b"verified media")

            rows = [
                {
                    "id": 1,
                    "source": 7,
                    "author": 7,
                    "created": 10,
                    "data": "first",
                },
                {
                    "id": 2,
                    "source": 7,
                    "author": 7,
                    "created": 20,
                    "data": "second",
                    "attachments": [
                        {
                            "type": "file",
                            "id": 22,
                            "access_hash": 23,
                            "mime": "application/octet-stream",
                            "file": "files/media/saved.bin",
                            "hash": export.file_sha256(media_path),
                        },
                        {
                            "type": "story",
                            "status": "unavailable",
                            "reason": "expired",
                        },
                    ],
                },
            ]
            committed = b"".join(
                json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n"
                for row in rows
            )
            partial_path.write_bytes(committed)

            partial = export.load_partial_export(
                messages_path,
                existing=None,
                expected_chat_id=7,
            )
            self.assertIsNotNone(partial)
            assert partial is not None
            self.assertEqual(partial.message_count, 2)
            self.assertEqual(partial.checkpoints, {(7, 0): 2})
            self.assertEqual(partial.attachment_error_statuses, {"unavailable": 1})
            self.assertEqual(len(partial.media_assets), 1)
            self.assertEqual(len(partial.media_reuse_assets), 1)
            resumed_asset = next(iter(partial.media_assets.values()))
            self.assertEqual(resumed_asset["file"], "files/media/saved.bin")
            self.assertEqual(resumed_asset["hash"], export.file_sha256(media_path))
            with self.assertRaisesRegex(RuntimeError, "current chat/topic scope"):
                export.load_partial_export(
                    messages_path,
                    existing=None,
                    expected_chat_id=7,
                    allowed_checkpoint_keys={(8, 0)},
                )

            header = {
                "schema": export.SCHEMA_NAME,
                "schema_version": export.SCHEMA_VERSION,
                "attachment_hash_algorithm": "sha256",
                "telegram_layer": export.TELEGRAM_LAYER,
                "telethon_version": export.telethon.__version__,
                "exported_at": 100,
                "order": "oldest_to_newest_by_created_at",
                "chat": {
                    "id": 7,
                    "monoforum_scope": None,
                    "history_sources": [],
                },
            }
            writer = export.JsonlExportWriter(
                messages_path,
                metadata_path,
                header,
                overwrite=False,
                partial=partial,
            )
            writer.write_message(
                {
                    "id": 3,
                    "source": 7,
                    "author": 7,
                    "created": 30,
                    "data": "third",
                }
            )
            writer.finish(
                {},
                [],
                partial.media_assets,
                {
                    "messages": 3,
                    "complete": False,
                    "complete_accessible": True,
                    "history_complete": True,
                    "started_at": 100,
                    "finished_at": 101,
                    "duration_seconds": 1.0,
                },
            )

            self.assertTrue(messages_path.read_bytes().startswith(committed))
            resumed_rows = [
                json.loads(line)
                for line in messages_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([row["id"] for row in resumed_rows], [1, 2, 3])
            existing = export.load_existing_export(
                messages_path,
                metadata_path,
                overwrite=False,
                expected_chat_id=7,
            )
            self.assertIsNotNone(existing)
            assert existing is not None
            validation_writer = export.JsonlExportWriter(
                messages_path,
                metadata_path,
                header,
                overwrite=False,
                existing=existing,
            )
            self.assertEqual(len(validation_writer.media_reuse_assets), 1)
            validation_writer.close_incomplete()

    def test_partial_media_signature_reuses_same_category_file_after_tail_rollback(self):
        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class UnexpectedDownloadApi:
            async def download_media(self, *_args, **_kwargs):
                raise AssertionError("validated partial media must be reused")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            relative_file = "files/stickers/7_1_01_900_sticker.webp"
            media_path = output / relative_file
            media_path.parent.mkdir(parents=True)
            payload = b"validated partial sticker"
            media_path.write_bytes(payload)
            valid_row = {
                "id": 1,
                "source": 7,
                "author": 7,
                "created": 10,
                "attachments": [
                    {
                        "type": "sticker",
                        "id": 900,
                        "access_hash": 901,
                        "mime": "image/webp",
                        "file_name": "original-sticker.webp",
                        "file": relative_file,
                        "hash": export.file_sha256(media_path),
                    }
                ],
            }
            failed_row = {
                "id": 2,
                "source": 7,
                "author": 7,
                "created": 20,
                "attachments": [
                    {
                        "type": "file",
                        "status": "failed",
                        "reason": "flood_wait_limit",
                    }
                ],
            }
            valid_line = (
                json.dumps(valid_row, separators=(",", ":")).encode("utf-8")
                + b"\n"
            )
            partial_path.write_bytes(
                valid_line
                + json.dumps(failed_row, separators=(",", ":")).encode("utf-8")
                + b"\n"
            )

            partial = export.load_partial_export(
                messages_path,
                existing=None,
                expected_chat_id=7,
            )

            self.assertIsNotNone(partial)
            assert partial is not None
            self.assertEqual(partial_path.read_bytes(), valid_line)
            self.assertTrue(partial.media_reuse_assets)

            exporter: Any = object.__new__(export.ChatExporter)
            exporter.output_dir = output
            exporter.files_dir = output / "files"
            exporter.error_log_path = output / "media-errors.jsonl"
            exporter.chat_id = 7
            exporter.args = SimpleNamespace(
                max_file_size=0,
                retries=0,
                jitter=0.0,
                media_stall_timeout=0.25,
                media_progress_interval=0.0,
            )
            exporter.pacer = Pacer()
            exporter.stats = export.ExportStats()
            exporter.media_cache = {}
            exporter.media_asset_cache = {}
            exporter.media_reuse_cache = dict(partial.media_reuse_assets)
            exporter.referenced_files = set()
            target = export.DownloadTarget(
                obj=object(),
                kind="document",
                subtype="sticker",
                role="message.media.document",
                message_id=3,
                cache_key="document:900",
                extension=".webp",
                expected_size=len(payload),
                metadata={
                    "type": "sticker",
                    "id": 900,
                    "access_hash": 901,
                    "mime": "image/webp",
                    "file_name": "renamed-sticker.webp",
                },
                original_name="renamed-sticker.webp",
                source_chat_id=7,
            )

            record = asyncio.run(
                exporter.download_target(UnexpectedDownloadApi(), target, 4)
            )

            self.assertEqual(record["status"], "reused")
            self.assertEqual(record["file"], relative_file)
            self.assertEqual(record["hash"], export.file_sha256(media_path))
            self.assertEqual(media_path.read_bytes(), payload)
            self.assertFalse(
                (
                    exporter.files_dir
                    / "stickers"
                    / exporter.target_filename(target, 4)
                ).exists()
            )

    def test_partial_media_signature_rejects_size_category_and_unknown_size_aliases(self):
        class Pacer:
            async def after_chunk(self):
                return None

            async def after_media(self):
                return None

        class DownloadApi:
            def __init__(self, payload):
                self.payload = payload
                self.calls = 0

            async def download_media(
                self,
                _media,
                *,
                file,
                thumb,
                progress_callback,
            ):
                self.calls += 1
                Path(file).write_bytes(self.payload)
                return file

        cases = (
            ("different physical size", "stickers", b"replacement!", 12),
            ("different category", "icons", b"replacement", 11),
            ("unknown target size", "stickers", b"replacement", None),
        )
        for label, target_category, downloaded_payload, expected_size in cases:
            with self.subTest(label), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                messages_path = output / "7.jsonl"
                partial_path = messages_path.with_suffix(
                    messages_path.suffix + ".part"
                )
                relative_file = "files/stickers/7_1_01_900_sticker.webp"
                media_path = output / relative_file
                media_path.parent.mkdir(parents=True)
                cached_payload = b"old sticker"
                media_path.write_bytes(cached_payload)
                valid_row = {
                    "id": 1,
                    "source": 7,
                    "author": 7,
                    "created": 10,
                    "attachments": [
                        {
                            "type": "sticker",
                            "id": 900,
                            "access_hash": 901,
                            "mime": "image/webp",
                            "file": relative_file,
                            "hash": export.file_sha256(media_path),
                        }
                    ],
                }
                failed_row = {
                    "id": 2,
                    "source": 7,
                    "author": 7,
                    "created": 20,
                    "attachments": [
                        {
                            "type": "file",
                            "status": "failed",
                            "reason": "flood_wait_limit",
                        }
                    ],
                }
                partial_path.write_bytes(
                    json.dumps(valid_row, separators=(",", ":")).encode("utf-8")
                    + b"\n"
                    + json.dumps(failed_row, separators=(",", ":")).encode("utf-8")
                    + b"\n"
                )
                partial = export.load_partial_export(
                    messages_path,
                    existing=None,
                    expected_chat_id=7,
                )
                self.assertIsNotNone(partial)
                assert partial is not None

                exporter: Any = object.__new__(export.ChatExporter)
                exporter.output_dir = output
                exporter.files_dir = output / "files"
                exporter.error_log_path = output / "media-errors.jsonl"
                exporter.chat_id = 7
                exporter.args = SimpleNamespace(
                    max_file_size=0,
                    retries=0,
                    jitter=0.0,
                    media_stall_timeout=0.25,
                    media_progress_interval=0.0,
                )
                exporter.pacer = Pacer()
                exporter.stats = export.ExportStats()
                exporter.media_cache = {}
                exporter.media_asset_cache = {}
                exporter.media_reuse_cache = dict(partial.media_reuse_assets)
                exporter.referenced_files = set()
                target = export.DownloadTarget(
                    obj=object(),
                    kind="document",
                    subtype="sticker",
                    role="message.media.document",
                    message_id=3,
                    cache_key="document:900",
                    extension=".webp",
                    expected_size=expected_size,
                    metadata={
                        "type": "sticker",
                        "id": 900,
                        "access_hash": 901,
                        "mime": "image/webp",
                    },
                    original_name="renamed-sticker.webp",
                    source_chat_id=7,
                    category_hint=(
                        target_category if target_category != "stickers" else None
                    ),
                )
                api = DownloadApi(downloaded_payload)

                record = asyncio.run(exporter.download_target(api, target, 4))

                self.assertEqual(api.calls, 1)
                self.assertEqual(record["status"], "downloaded")
                self.assertNotEqual(record["file"], relative_file)
                self.assertEqual(
                    (output / record["file"]).read_bytes(),
                    downloaded_payload,
                )
                self.assertEqual(media_path.read_bytes(), cached_payload)

    def test_partial_jsonl_truncates_only_recoverable_tail_failures(self):
        first = {
            "id": 1,
            "source": 7,
            "author": 7,
            "created": 10,
            "data": "first",
        }
        first_line = (
            json.dumps(first, separators=(",", ":")).encode("utf-8") + b"\n"
        )

        with self.subTest("unterminated JSON write"):
            with tempfile.TemporaryDirectory() as directory:
                messages_path = Path(directory) / "7.jsonl"
                partial_path = messages_path.with_suffix(
                    messages_path.suffix + ".part"
                )
                partial_path.write_bytes(first_line + b'{"id":2,"source":7')

                partial = export.load_partial_export(
                    messages_path,
                    existing=None,
                    expected_chat_id=7,
                )

                self.assertIsNotNone(partial)
                assert partial is not None
                self.assertEqual(partial.message_count, 1)
                self.assertEqual(partial.checkpoints, {(7, 0): 1})
                self.assertEqual(partial_path.read_bytes(), first_line)

        for label, attachment, create_file in (
            (
                "missing final media",
                {
                    "type": "file",
                    "file": "files/media/missing.bin",
                    "hash": "0" * 64,
                },
                False,
            ),
            (
                "hash-mismatched final media",
                {
                    "type": "file",
                    "file": "files/media/bad-hash.bin",
                    "hash": "0" * 64,
                },
                True,
            ),
            (
                "failed final media",
                {
                    "type": "file",
                    "status": "failed",
                    "reason": "flood_wait_limit",
                },
                False,
            ),
        ):
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory)
                    messages_path = output / "7.jsonl"
                    partial_path = messages_path.with_suffix(
                        messages_path.suffix + ".part"
                    )
                    if create_file:
                        media_path = output / "files" / "media" / "bad-hash.bin"
                        media_path.parent.mkdir(parents=True)
                        media_path.write_bytes(b"does not match declared hash")
                    failed_row = {
                        "id": 2,
                        "source": 7,
                        "author": 7,
                        "created": 20,
                        "attachments": [attachment],
                    }
                    partial_path.write_bytes(
                        first_line
                        + json.dumps(
                            failed_row,
                            separators=(",", ":"),
                        ).encode("utf-8")
                        + b"\n"
                    )

                    partial = export.load_partial_export(
                        messages_path,
                        existing=None,
                        expected_chat_id=7,
                    )

                    self.assertIsNotNone(partial)
                    assert partial is not None
                    self.assertEqual(partial.message_count, 1)
                    self.assertEqual(partial.checkpoints, {(7, 0): 1})
                    self.assertEqual(partial_path.read_bytes(), first_line)

    def test_partial_jsonl_recovers_media_gap_but_rejects_structural_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            rows = [
                {
                    "id": 1,
                    "source": 7,
                    "author": 7,
                    "created": 10,
                    "attachments": [
                        {
                            "type": "file",
                            "file": "files/media/missing.bin",
                            "hash": "0" * 64,
                        }
                    ],
                },
                {
                    "id": 2,
                    "source": 7,
                    "author": 7,
                    "created": 20,
                    "data": "later committed row",
                },
            ]
            original = b"".join(
                json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n"
                for row in rows
            )
            partial_path.write_bytes(original)

            partial = export.load_partial_export(
                messages_path,
                existing=None,
                expected_chat_id=7,
            )
            self.assertIsNotNone(partial)
            assert partial is not None
            self.assertEqual(partial.message_count, 0)
            self.assertEqual(partial.checkpoints, {})
            self.assertEqual(partial_path.read_bytes(), b"")

        with tempfile.TemporaryDirectory() as directory:
            messages_path = Path(directory) / "7.jsonl"
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            partial_path.write_bytes(
                b'{"id":1,"source":7,"author":7,"created":10}\n'
                b'{"id":2,"source":7}\n'
            )
            with self.assertRaises(RuntimeError):
                export.load_partial_export(
                    messages_path,
                    existing=None,
                    expected_chat_id=7,
                )

    def test_partial_jsonl_prefix_mismatch_falls_back_to_published_export(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            published_row = {
                "id": 1,
                "source": 7,
                "author": 7,
                "created": 10,
                "data": "published",
            }
            published = (
                json.dumps(published_row, separators=(",", ":")).encode("utf-8")
                + b"\n"
            )
            messages_path.write_bytes(published)
            partial_path.write_bytes(published.replace(b"published", b"different"))
            existing = export.ExistingExportState(
                metadata={},
                message_count=1,
                byte_size=len(published),
                sha256=export.hashlib.sha256(published).hexdigest(),
                checkpoints={(7, 0): 1},
                first_created_epoch=10,
                last_created_epoch=10,
                has_undated_messages=False,
                peers={},
                peer_avatars=[],
                media_assets={},
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                partial = export.load_partial_export(
                    messages_path,
                    existing=existing,
                    expected_chat_id=7,
                )

            self.assertIsNone(partial)
            self.assertRegex(stderr.getvalue().lower(), r"interrupted.*jsonl")
            self.assertIn("published", stderr.getvalue().lower())

    def test_published_failed_attachment_stages_safe_prefix_and_statuses(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            unavailable_row = {
                "id": 1,
                "source": 7,
                "author": 7,
                "created": 10,
                "attachments": [
                    {
                        "type": "story",
                        "status": "unavailable",
                        "reason": "story_expired",
                    }
                ],
            }
            failed_row = {
                "id": 2,
                "source": 7,
                "author": 7,
                "created": 20,
                "attachments": [
                    {
                        "type": "image",
                        "id": 200,
                        "status": "failed",
                        "reason": "flood_wait_limit",
                    }
                ],
            }
            later_row = {
                "id": 3,
                "source": 7,
                "author": 7,
                "created": 30,
                "data": "later",
            }
            lines = [
                json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n"
                for row in (unavailable_row, failed_row, later_row)
            ]
            published = b"".join(lines)
            messages_path.write_bytes(published)
            existing = export.ExistingExportState(
                metadata={
                    "summary": {
                        "complete_accessible": False,
                        "attachments": {"failed": 1, "unavailable": 1},
                    }
                },
                message_count=3,
                byte_size=len(published),
                sha256=export.hashlib.sha256(published).hexdigest(),
                checkpoints={(7, 0): 3},
                first_created_epoch=10,
                last_created_epoch=30,
                has_undated_messages=False,
                peers={},
                peer_avatars=[],
                media_assets={},
            )

            repair = export.scan_published_failure_repair(messages_path, existing)

            self.assertIsNotNone(repair)
            assert repair is not None
            self.assertEqual(repair.first_failed_message_id, 2)
            self.assertEqual(repair.original_message_count, 3)
            self.assertEqual(repair.base.message_count, 1)
            self.assertEqual(repair.base.byte_size, len(lines[0]))
            self.assertEqual(repair.base.checkpoints, {(7, 0): 1})
            export.stage_published_failure_repair(messages_path, repair)
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            self.assertEqual(partial_path.read_bytes(), lines[0])
            self.assertEqual(messages_path.read_bytes(), published)

            partial = export.load_partial_export(
                messages_path,
                repair.base,
                expected_chat_id=7,
                include_published_attachment_errors=True,
            )

            self.assertIsNotNone(partial)
            assert partial is not None
            self.assertEqual(partial.message_count, 1)
            self.assertEqual(partial.checkpoints, {(7, 0): 1})
            self.assertEqual(
                partial.attachment_error_statuses,
                {"unavailable": 1},
            )
            self.assertEqual(messages_path.read_bytes(), published)

    def test_repeated_published_failure_repair_keeps_repaired_partial_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            media_path = output / "files" / "media" / "repaired.jpg"
            media_path.parent.mkdir(parents=True)
            media_path.write_bytes(b"repaired media")
            first_row = {
                "id": 1,
                "source": 7,
                "author": 7,
                "created": 10,
                "data": "safe prefix",
            }
            failed_row = {
                "id": 2,
                "source": 7,
                "author": 7,
                "created": 20,
                "attachments": [
                    {
                        "type": "image",
                        "id": 200,
                        "status": "failed",
                        "reason": "download_failed",
                    }
                ],
            }
            later_row = {
                "id": 3,
                "source": 7,
                "author": 7,
                "created": 30,
                "data": "old published suffix",
            }
            repaired_row = {
                "id": 2,
                "source": 7,
                "author": 7,
                "created": 20,
                "attachments": [
                    {
                        "type": "image",
                        "id": 200,
                        "access_hash": 201,
                        "mime": "image/jpeg",
                        "file": "files/media/repaired.jpg",
                        "hash": export.file_sha256(media_path),
                    }
                ],
            }
            published_lines = [
                json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n"
                for row in (first_row, failed_row, later_row)
            ]
            published = b"".join(published_lines)
            messages_path.write_bytes(published)
            existing = export.ExistingExportState(
                metadata={
                    "summary": {
                        "complete_accessible": False,
                        "attachments": {"failed": 1},
                    }
                },
                message_count=3,
                byte_size=len(published),
                sha256=export.hashlib.sha256(published).hexdigest(),
                checkpoints={(7, 0): 3},
                first_created_epoch=10,
                last_created_epoch=30,
                has_undated_messages=False,
                peers={},
                peer_avatars=[],
                media_assets={},
            )
            repair = export.scan_published_failure_repair(messages_path, existing)
            self.assertIsNotNone(repair)
            assert repair is not None
            export.stage_published_failure_repair(messages_path, repair)
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            repaired_line = (
                json.dumps(repaired_row, separators=(",", ":")).encode("utf-8")
                + b"\n"
            )
            partial_path.write_bytes(published_lines[0] + repaired_line)

            # A second invocation must preserve work newer than the published
            # failed row instead of restaging the old safe prefix over it.
            export.stage_published_failure_repair(messages_path, repair)
            self.assertEqual(
                partial_path.read_bytes(),
                published_lines[0] + repaired_line,
            )
            partial = export.load_partial_export(
                messages_path,
                repair.base,
                expected_chat_id=7,
                include_published_attachment_errors=True,
            )

            self.assertIsNotNone(partial)
            assert partial is not None
            self.assertEqual(partial.message_count, 2)
            self.assertEqual(partial.checkpoints, {(7, 0): 2})
            self.assertEqual(
                partial.referenced_files,
                {"files/media/repaired.jpg"},
            )
            self.assertTrue(partial.media_assets)
            self.assertEqual(messages_path.read_bytes(), published)

    def test_published_failed_avatar_stages_complete_message_base(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            rows = [
                {
                    "id": message_id,
                    "source": 7,
                    "author": 7,
                    "created": message_id * 10,
                }
                for message_id in (1, 2)
            ]
            published = b"".join(
                json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n"
                for row in rows
            )
            messages_path.write_bytes(published)
            existing = export.ExistingExportState(
                metadata={
                    "summary": {
                        "complete_accessible": False,
                        "attachments": {"failed": 1},
                    }
                },
                message_count=2,
                byte_size=len(published),
                sha256=export.hashlib.sha256(published).hexdigest(),
                checkpoints={(7, 0): 2},
                first_created_epoch=10,
                last_created_epoch=20,
                has_undated_messages=False,
                peers={},
                peer_avatars=[
                    {
                        "type": "avatar",
                        "id": 99,
                        "owner_id": 7,
                        "status": "failed",
                        "reason": "download_failed",
                    }
                ],
                media_assets={},
            )

            repair = export.scan_published_failure_repair(messages_path, existing)

            self.assertIsNotNone(repair)
            assert repair is not None
            self.assertIsNone(repair.first_failed_message_id)
            self.assertEqual(repair.failed_avatar_count, 1)
            self.assertEqual(repair.base.message_count, 2)
            export.stage_published_failure_repair(messages_path, repair)
            partial_path = messages_path.with_suffix(messages_path.suffix + ".part")
            self.assertEqual(partial_path.read_bytes(), published)
            self.assertEqual(messages_path.read_bytes(), published)
            partial = export.load_partial_export(
                messages_path,
                repair.base,
                expected_chat_id=7,
                include_published_attachment_errors=True,
            )
            self.assertIsNotNone(partial)
            assert partial is not None
            self.assertEqual(partial.message_count, 2)
            self.assertEqual(partial.checkpoints, {(7, 0): 2})

    def test_writer_and_resume_use_id(self):
        # Preview download selection changed behavior, not the JSON contract;
        # existing schema-14 exports must therefore remain resumable.
        self.assertEqual(export.SCHEMA_VERSION, 14)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            messages_path = output / "7.jsonl"
            metadata_path = output / "7.metadata.json"
            header = {
                "schema": export.SCHEMA_NAME,
                "schema_version": 14,
                "attachment_hash_algorithm": "sha256",
                "telegram_layer": export.TELEGRAM_LAYER,
                "telethon_version": export.telethon.__version__,
                "exported_at": 100,
                "order": "oldest_to_newest_by_created_at",
                "chat": {
                    "id": 7,
                    "monoforum_scope": None,
                    "history_sources": [],
                },
            }
            row = {
                "id": 1,
                "source": 7,
                "author": 7,
                "created": 10,
                "data": "hello",
            }
            summary = {
                "messages": 1,
                "complete": True,
                "complete_accessible": True,
                "history_complete": True,
                "started_at": 100,
                "finished_at": 101,
                "duration_seconds": 1.0,
            }
            writer = export.JsonlExportWriter(
                messages_path,
                metadata_path,
                header,
                overwrite=False,
            )
            writer.write_message(row)
            with self.assertRaisesRegex(RuntimeError, "does not advance"):
                writer.write_message(row)
            writer.write_message(
                {
                    **row,
                    "history_source": 8,
                    "created": 11,
                }
            )
            summary["messages"] = 2
            writer.finish({}, [], {}, summary)

            saved_rows = [
                json.loads(line)
                for line in messages_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([item["id"] for item in saved_rows], [1, 1])
            self.assertNotIn("message", saved_rows[0])
            self.assertNotIn("history_source", saved_rows[0])
            self.assertEqual(saved_rows[1]["history_source"], 8)
            state = export.load_existing_export(
                messages_path,
                metadata_path,
                overwrite=False,
                expected_chat_id=7,
            )
            self.assertIsNotNone(state)
            assert state is not None
            self.assertEqual(state.checkpoints[(7, 0)], 1)
            self.assertEqual(state.checkpoints[(8, 0)], 1)

            legacy_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            legacy_metadata["schema_version"] = export.SCHEMA_VERSION - 1
            metadata_path.write_text(
                json.dumps(legacy_metadata),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "requires version"):
                export.load_existing_export(
                    messages_path,
                    metadata_path,
                    overwrite=False,
                    expected_chat_id=7,
                )


if __name__ == "__main__":
    unittest.main()
