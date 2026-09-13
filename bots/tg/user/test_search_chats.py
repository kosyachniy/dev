"""Offline checks for bounded requests, private peers, and flood handling."""

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telethon import errors, functions, types

from search_chats import format_chats, rpc_error_text, search_chats


class SearchChatsTests(unittest.IsolatedAsyncioTestCase):
    def found(self):
        return types.contacts.Found(
            my_results=[types.PeerChat(7), types.PeerChannel(7), types.PeerUser(7)],
            results=[types.PeerChannel(99)],
            chats=[
                types.Chat(
                    7, "Old private group", types.ChatPhotoEmpty(), 2, None, 1,
                    migrated_to=types.InputChannel(70, 123),
                ),
                types.Channel(
                    7, "Old supergroup", types.ChatPhotoEmpty(), None,
                    megagroup=True, access_hash=123,
                ),
                types.Channel(
                    99, "Unrelated public result", types.ChatPhotoEmpty(), None,
                    username="public_result", access_hash=456,
                ),
            ],
            users=[types.User(7, first_name="Old bot", bot=True, access_hash=789)],
        )

    async def test_private_peers_with_colliding_raw_ids_need_only_two_requests(self):
        found = self.found()
        details = SimpleNamespace(dialogs=[
            SimpleNamespace(peer=types.PeerUser(7), top_message=30),
            SimpleNamespace(peer=types.PeerChannel(7), top_message=20),
            SimpleNamespace(peer=types.PeerChat(7), top_message=10),
        ])
        client = AsyncMock(side_effect=[found, details])

        rows = await search_chats(client, "  Old  ")

        self.assertEqual([row["marked_id"] for row in rows], [-7, -1000000000007, 7])
        self.assertEqual([row["last_message"] for row in rows], [10, 20, 30])
        self.assertEqual([row["entity"] for row in rows], ["chat", "channel", "bot"])
        self.assertTrue(all(row["login"] is None for row in rows))
        self.assertEqual(rows[0]["migrated_to"], 70)
        self.assertIn("70(-1000000000070)", format_chats(rows))
        self.assertEqual(client.await_count, 2)
        self.assertEqual(len(client.mock_calls), 2)  # No dialog/entity fetch helpers.
        search = client.await_args_list[0].args[0]
        metadata = client.await_args_list[1].args[0]
        self.assertIsInstance(search, functions.contacts.SearchRequest)
        self.assertEqual(search.q, "Old")
        self.assertIsInstance(metadata, functions.messages.GetPeerDialogsRequest)
        self.assertEqual(len(metadata.peers), 3)
        self.assertIsInstance(metadata.peers[0].peer, types.InputPeerChat)
        self.assertEqual(metadata.peers[1].peer.access_hash, 123)
        self.assertTrue(bytes(search))
        self.assertTrue(bytes(metadata))

    async def test_limit_and_duplicates_do_not_expand_metadata_request(self):
        found = self.found()
        found.my_results.insert(0, types.PeerChat(7))
        client = AsyncMock(side_effect=[found, SimpleNamespace(dialogs=[])])
        rows = await search_chats(client, "Old", limit=2)
        self.assertEqual([row["entity"] for row in rows], ["chat", "channel"])
        self.assertEqual(len(client.await_args_list[1].args[0].peers), 2)
        self.assertTrue(all(row["last_message"] is None for row in rows))

    async def test_no_metadata_option_and_empty_results_use_one_request(self):
        for found, kwargs, count in (
            (self.found(), {"last_message": False}, 3),
            (types.contacts.Found([], [], [], []), {}, 0),
        ):
            with self.subTest(kwargs=kwargs, count=count):
                client = AsyncMock(return_value=found)
                rows = await search_chats(client, "Old", **kwargs)
                self.assertEqual(len(rows), count)
                client.assert_awaited_once()

    async def test_search_flood_is_reported_without_retry(self):
        flood = errors.FloodWaitError(request=None, capture=123)
        client = AsyncMock(side_effect=flood)
        with self.assertRaises(errors.FloodWaitError):
            await search_chats(client, "Old")
        client.assert_awaited_once()
        self.assertIn("123 seconds", rpc_error_text(flood))

    async def test_metadata_failure_preserves_matches_without_retry(self):
        for failure in (
            errors.FloodWaitError(request=None, capture=123),
            errors.ChannelPrivateError(request=None),
        ):
            with self.subTest(failure=type(failure).__name__):
                client = AsyncMock(side_effect=[self.found(), failure])
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    rows = await search_chats(client, "Old")
                self.assertEqual(len(rows), 3)
                self.assertTrue(all(row["last_message"] is None for row in rows))
                self.assertEqual(client.await_count, 2)
                self.assertIn("Latest message IDs unavailable", stderr.getvalue())

    async def test_missing_access_hash_never_triggers_dialog_scan(self):
        found = self.found()
        found.my_results = [types.PeerChannel(7)]
        found.chats[1].access_hash = None
        client = AsyncMock(return_value=found)
        with contextlib.redirect_stderr(io.StringIO()):
            rows = await search_chats(client, "Old")
        self.assertEqual(rows[0]["id"], 7)
        self.assertIsNone(rows[0]["last_message"])
        self.assertEqual(len(client.mock_calls), 1)

    async def test_invalid_arguments_make_no_requests(self):
        client = AsyncMock()
        for query, limit in (("  ", 50), ("Old", 0), ("Old", 101)):
            with self.subTest(query=query, limit=limit):
                with self.assertRaises(ValueError):
                    await search_chats(client, query, limit)
        client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
