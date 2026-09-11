import base64
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

import export_chat as export


def message(message_id, body="", *, incoming=False, date="2 янв 2020 в 3:04:05", edited=None):
    author = '<a href="https://vk.ru/id123">Test User</a>' if incoming else "Вы"
    edit = f"<span class='message-edited' title='{edited}'> (ред.)</span>" if edited else ""
    return (f'<div class="item"><div class="item__main"><div class="message" data-id="{message_id}">'
            f'<div class="message__header">{author}, {date}{edit}</div>'
            f'<div>{body}</div></div></div></div>')


def attachment(description, url=None):
    link = f'<a class="attachment__link" href="{url}">{url}</a>' if url else ""
    return (f'<div class="attachment"><div class="attachment__description">'
            f'{description}</div>{link}</div>')


class ExportChatTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve() / "123"
        self.folder.mkdir()

    def page(self, messages, *, name="messages0.html", encoding="cp1251", owner=456):
        meta = ""
        if owner is not None:
            data = base64.b64encode(json.dumps({"user_id": owner}).encode()).decode().rstrip("=")
            meta = f'<meta name="jd" content="{data}">'
        html = (f'<!DOCTYPE html><html><head><meta charset="{encoding}">{meta}</head>'
                '<body><div class="pagination">ignore this</div>'
                f'{messages}</body></html>')
        path = self.folder / name
        path.write_bytes(html.encode(encoding))
        return path

    def rows(self, **kwargs):
        result = export.export_chat(self.folder, **kwargs)
        self.assertEqual(result["output"], self.folder.with_suffix(".jsonl"))
        return result, [json.loads(line) for line in result["output"].read_text(encoding="utf-8").splitlines()]

    def test_core_schema_encoding_entities_newlines_and_edits(self):
        self.page(message(1, "  Привет &amp; &lt;мир&gt;<br>ещё!<div class='kludges'></div>  ",
                          edited="2 янв 2020 в 3:05:06"))
        _, rows = self.rows()
        self.assertEqual(rows, [{
            "data": "  Привет & <мир>\nещё!  ", "source": 123, "author": 456,
            "id": 1, "created": 1577923445, "type": "message",
            "edited": 1577923506, "flags": {"out": True},
        }])

    def test_all_pages_sort_by_time_then_id_and_skip_identical_duplicates(self):
        older = message(100, "old", incoming=True, date="1 янв 2020 в 3:04:05")
        newer = message(1, "new", incoming=True)
        self.page(newer)
        self.page(message(2, "same date"), name="messages50.html", encoding="utf-8")
        self.page(older + newer, name="messages100.html")
        result, rows = self.rows()
        self.assertEqual([row["id"] for row in rows], [100, 1, 2])
        self.assertEqual(result["pages"], 3)
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(rows[0]["author"], 123)
        self.assertNotIn("flags", rows[0])
        before = result["output"].read_bytes()
        self.rows()
        self.assertEqual(result["output"].read_bytes(), before)

    def test_attachments_preserve_urls_missing_details_and_forward_count(self):
        body = "<div class='kludges'>" + "".join([
            attachment("Фотография", "https://example.com/a.jpg?one=1&amp;two=2"),
            attachment("Файл", "https://example.com/a.ogg"),
            attachment("Стикер"),
            attachment("2 прикреплённых сообщения"),
            attachment("Новый тип"),
            attachment("Звонок"),
        ]) + "</div>"
        self.page(message(1, body))
        result, rows = self.rows()
        self.assertNotIn("data", rows[0])
        self.assertEqual(result["attachments"], 6)
        image, file, sticker, forwarded, unknown, call = rows[0]["attachments"]
        self.assertEqual(image, {"type": "image", "mime": "image/jpeg", "content": {
            "description": "Фотография", "url": "https://example.com/a.jpg?one=1&two=2",
        }})
        self.assertEqual(file["type"], "file")  # An .ogg alone does not prove it is a voice message.
        self.assertEqual(sticker["status"], "unavailable")
        self.assertEqual(forwarded["content"]["count"], 2)
        self.assertEqual(forwarded["type"], "forwarded_messages")
        self.assertEqual(unknown["content"]["description"], "Новый тип")
        self.assertEqual(call["type"], "phone_call")
        self.assertNotIn("file", image)

    def test_utf8_formatting_and_empty_messages(self):
        self.page(message(1, '<b>Hi</b> <a href="https://example.com">link</a> 😀')
                  + message(2, incoming=True), encoding="utf-8")
        _, rows = self.rows()
        self.assertEqual(rows[0]["data"], "*Hi* [link](https://example.com) 😀")
        self.assertNotIn("data", rows[1])
        self.assertNotIn("attachments", rows[1])

    def test_timezone_override_and_historical_moscow_offset(self):
        self.page(message(1, date="1 июл 2013 в 4:00:00"))
        _, moscow = self.rows()
        _, utc = self.rows(timezone="UTC")
        expected = int(dt.datetime(2013, 7, 1, tzinfo=dt.timezone.utc).timestamp())
        self.assertEqual(moscow[0]["created"], expected)
        self.assertEqual(utc[0]["created"] - moscow[0]["created"], 4 * 3600)
        self.assertEqual(export.timestamp("1 мая 2020 в 0:00", ZoneInfo("UTC")), 1588291200)

    def test_missing_owner_requires_override_for_outgoing_messages(self):
        self.page(message(1), owner=None)
        with self.assertRaisesRegex(ValueError, "--self-id"):
            self.rows()
        _, rows = self.rows(self_id=789, source_id=987)
        self.assertEqual(rows[0]["author"], 789)
        self.assertEqual(rows[0]["source"], 987)

    def test_bad_page_preserves_previous_output_and_reports_filename_and_id(self):
        path = self.page(message(1))
        result, _ = self.rows()
        before = result["output"].read_bytes()
        self.page(message(2, date="not a date"), name="messages50.html")
        with self.assertRaisesRegex(ValueError, "messages50.html: message 2:"):
            self.rows()
        self.assertEqual(result["output"].read_bytes(), before)
        self.assertTrue(path.exists())
        self.assertEqual(list(self.folder.parent.glob("*.tmp")), [])

    def test_conflicting_duplicates_and_mixed_owners_are_errors(self):
        self.page(message(1, "first"))
        self.page(message(1, "changed"), name="messages50.html")
        with self.assertRaisesRegex(ValueError, "conflicting message 1"):
            self.rows()
        self.page(message(2), name="messages50.html", owner=999)
        with self.assertRaisesRegex(ValueError, "conflicting archive owners"):
            self.rows()

    def test_unknown_author_is_not_silently_assigned_to_conversation_partner(self):
        path = self.page(message(1, incoming=True))
        path.write_bytes(path.read_bytes().replace(b"/id123", b"/screen_name"))
        with self.assertRaisesRegex(ValueError, "cannot identify message author"):
            self.rows()

    def test_truncated_and_unrecognized_pages_are_errors(self):
        path = self.page(message(1))
        path.write_bytes(path.read_bytes().removesuffix(b"</body></html>"))
        with self.assertRaisesRegex(ValueError, "incomplete HTML"):
            self.rows()
        self.page("")
        with self.assertRaisesRegex(ValueError, "page contains no messages"):
            self.rows()

    def test_input_errors_and_output_guards(self):
        with self.assertRaisesRegex(ValueError, "no messages"):
            self.rows()
        page = self.page(message(1))
        with self.assertRaisesRegex(ValueError, "output must have"):
            export.export_chat(self.folder, page)
        output = self.folder.with_suffix(".jsonl")
        output.symlink_to(page)
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            self.rows()


if __name__ == "__main__":
    unittest.main()
