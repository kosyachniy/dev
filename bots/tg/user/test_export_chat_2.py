import asyncio
import datetime as dt
import inspect
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
