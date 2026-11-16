"""No-model tests for item space AI branding and one-click browser startup."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from factory import branding, console


class ItemSpaceBrandingTests(unittest.TestCase):
    def test_generated_windows_icon_is_valid_ico_with_png_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "item-space-ai.ico"
            branding.create_icon(dest)
            raw = dest.read_bytes()
            self.assertGreater(len(raw), 2000)
            self.assertEqual(struct.unpack_from("<HHH", raw, 0), (0, 1, 2))
            for i in range(2):
                size, offset = struct.unpack_from("<II", raw, 6 + i * 16 + 8)
                self.assertEqual(raw[offset:offset + 8], b"\x89PNG\r\n\x1a\n")
                self.assertLess(offset + size, len(raw) + 1)

    def test_branded_page_preserves_html_escaping(self):
        page = console.page("<unsafe>", "content", "token", auto_run=False).decode()
        self.assertIn("item space AI", page)
        self.assertIn("MISSION CONTROL", page)
        self.assertIn("&lt;unsafe&gt;", page)
        self.assertNotIn("<unsafe>", page)
        self.assertIn("no GitHub push", page)

    def test_existing_local_server_is_detected_by_header(self):
        class Response:
            headers = {"X-Item-Space-AI": "local-console"}
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False

        with patch.object(console, "urlopen", return_value=Response()) as mock:
            self.assertTrue(console.console_already_running(8765))
            self.assertIn("127.0.0.1:8765", mock.call_args[0][0])

    def test_browser_open_is_opt_in(self):
        with patch.object(console, "ConsoleServer") as server_cls:
            instance = server_cls.return_value.__enter__.return_value
            with patch.object(console, "console_already_running", return_value=True):
                with patch.object(console.webbrowser, "open_new_tab") as browser:
                    self.assertEqual(console.main(["--open-browser"]), 0)
                    browser.assert_called_once_with("http://127.0.0.1:8765/")
                    server_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
