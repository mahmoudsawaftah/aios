"""Pixel Office must be read-only, local, and represent actual persisted task state."""
from __future__ import annotations

import json
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from factory import console, pixel_office


class PixelOfficeTests(unittest.TestCase):
    def _records(self):
        return [
            {"id": "3fda1e657895", "title": "Item Space <test>", "status": "NEEDS_WORK",
             "stage": "implementation", "updated_at": "2026-11-17T10:00:00+00:00",
             "goal_preview": "private details", "error": "sensitive path"},
            {"id": "528e9ed89e19", "title": "Demo", "status": "WAITING_APPROVAL",
             "stage": "implementation", "updated_at": "2026-11-17T11:00:00+00:00",
             "goal_preview": "another private detail", "error": ""},
        ]

    def test_status_is_persisted_data_not_fabricated_agent_sessions(self):
        with patch.object(pixel_office, "list_ideas", return_value=self._records()) as listed, \
             patch.object(pixel_office, "worker_state", return_value="IDLE"):
            d = pixel_office.office_snapshot()
        listed.assert_called_once_with(limit=50)
        self.assertEqual(d["tasks"][0]["status"], "NEEDS_WORK")
        self.assertEqual(d["tasks"][1]["status"], "WAITING_APPROVAL")
        self.assertEqual(d["worker"], "IDLE")
        self.assertNotIn("goal_preview", json.dumps(d))
        self.assertNotIn("private details", json.dumps(d))
        self.assertNotIn("sensitive path", json.dumps(d))

    def test_canvas_ui_is_local_and_has_a_readonly_notice(self):
        html = pixel_office.office_html()
        self.assertIn('id="office-canvas"', html)
        self.assertIn('id="office-task-list"', html)
        self.assertIn('href="/#approvals"', html)
        self.assertIn("تمثّل مهمة", html)
        self.assertIn('src="/office.js"', html)
        self.assertNotIn("<form", html)
        self.assertNotIn('action="/ideas/', html)

    def test_client_uses_safe_dom_text_and_only_local_task_links(self):
        js = pixel_office.OFFICE_JS
        self.assertIn("textContent", js)
        self.assertIn("fetch('/office/state'", js)
        self.assertIn("document.createElement('a')", js)
        self.assertIn("status==='RUNNING'", js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("https://", js)
        self.assertNotIn("new Function(", js)
        self.assertIn("prefers-reduced-motion", js)
        self.assertIn("WAITING_APPROVAL", js)
        self.assertIn("NEEDS_WORK", js)

    def test_real_routes_require_loopback_and_never_approve(self):
        with patch.object(console, "office_snapshot", return_value={
            "tasks": [{"id": "3fda1e657895", "title": "Test",
                       "status": "BLOCKED", "stage": "qa", "updated_at": "now"}],
            "worker": "IDLE",
        }):
            with console.ConsoleServer(("127.0.0.1", 0), auto_run=False) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base = "http://127.0.0.1:" + str(server.server_port)
                try:
                    with urlopen(base + "/office", timeout=3) as r:
                        html = r.read().decode("utf-8")
                        csp = r.headers["Content-Security-Policy"]
                    self.assertIn("PIXEL OFFICE", html)
                    self.assertIn("script-src 'self'", csp)
                    self.assertIn("connect-src 'self'", csp)
                    with urlopen(base + "/office/state", timeout=3) as r:
                        result = json.loads(r.read().decode("utf-8"))
                        self.assertIn("application/json", r.headers["Content-Type"])
                    self.assertEqual(result["tasks"][0]["status"], "BLOCKED")
                    with urlopen(base + "/office.js", timeout=3) as r:
                        self.assertIn("office-canvas", r.read().decode("utf-8"))
                    # There is no write path for the office visualization.
                    post = Request(base + "/office/state",
                                   data=b"csrf=invalid",
                                   headers={"Content-Type": "application/x-www-form-urlencoded"},
                                   method="POST")
                    with self.assertRaises(HTTPError) as denied:
                        urlopen(post, timeout=3)
                    self.assertEqual(denied.exception.code, 403)
                finally:
                    server.shutdown()
                    thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
