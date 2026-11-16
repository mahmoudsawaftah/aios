"""Verify preview does not expose mutating routes or start workers."""
from __future__ import annotations
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from factory import readonly_preview, console, cli


class ReadOnlyPreviewTests(unittest.TestCase):
    def test_all_mutating_task_routes_are_rejected(self):
        for path in ("/ideas", "/ideas/528e9ed89e19/approve",
                     "/ideas/528e9ed89e19/research",
                     "/ideas/528e9ed89e19/marketing",
                     "/ideas/528e9ed89e19/github-preflight"):
            with self.subTest(path=path):
                handler = object.__new__(readonly_preview.ReadOnlyHandler)
                handler.path = path
                handler._render = Mock()
                handler.do_POST()
                self.assertEqual(handler._render.call_args.kwargs["code"], 403)

    def test_only_preview_preference_route_is_permitted(self):
        self.assertTrue(readonly_preview.LIVE_TASK.fullmatch(
            "/studio/528e9ed89e19/preview"))
        for path in ("/studio/../../preview",
                     "/studio/something/preview", "/studio/528e9ed89e19/state",
                     "/studio/528e9ed89e19/preview/"):
            self.assertIsNone(readonly_preview.LIVE_TASK.fullmatch(path))
        with patch.object(console.ConsoleHandler, "do_POST") as parent_post:
            handler = object.__new__(readonly_preview.ReadOnlyHandler)
            handler.path = "/studio/528e9ed89e19/preview"
            handler.do_POST()
            parent_post.assert_called_once()

    def test_missing_state_fails_before_server_binds(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(
                console, "ConsoleServer") as server:
            with self.assertRaises(SystemExit) as caught:
                readonly_preview.main(["--active-root", temp])
            self.assertEqual(caught.exception.code, 2)
            server.assert_not_called()


if __name__ == "__main__":
    unittest.main()
