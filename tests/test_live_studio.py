"""Live Studio safety regression: no jobs, no source reads, no arbitrary URLs."""
from __future__ import annotations

from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from factory import cli, console, live_studio


TASK_ID = "528e9ed89e19"


def mock_detail(**overrides):
    task = {
        "id": TASK_ID,
        "status": "PENDING",
        "next_stage": "discovery",
        "project": "C:/AIOS_Projects/example",
        "events": [{"ts": "2026-11-16T10:00:00Z", "event": "queued", "info": "Ready"}],
        "outputs": [{"stage": "discovery", "content": "Plan details"}],
        "goal": "Demo",
        "error": "",
        "approvals": [],
    }
    task.update(overrides)
    return task


class LiveStudioTests(unittest.TestCase):
    def test_preview_must_be_explicit_loopback_port_and_not_console(self):
        with tempfile.TemporaryDirectory() as td, ExitStack() as stack:
            stack.enter_context(patch.object(cli, "STATE", Path(td)))
            stack.enter_context(patch.object(live_studio, "idea_detail",
                                             return_value=mock_detail()))
            self.assertIsNone(live_studio.preview_port(TASK_ID))
            self.assertEqual(live_studio.save_preview_port(TASK_ID, "5173",
                                                           console_port=8765), 5173)
            self.assertEqual(live_studio.preview_port(TASK_ID), 5173)
            for bad in ("https://example.com", "127.0.0.1:3000", "-1",
                        "8765", "80", "65536", "3e3", "٣٠٠٠"):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    live_studio.save_preview_port(TASK_ID, bad, console_port=8765)
            self.assertEqual(live_studio.preview_port(TASK_ID), 5173)
            self.assertIsNone(live_studio.save_preview_port(TASK_ID, "",
                                                            console_port=8765))
            self.assertIsNone(live_studio.preview_port(TASK_ID))

    def test_no_preview_for_unregistered_task(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
                cli, "STATE", Path(td)), patch.object(
                live_studio, "idea_detail", side_effect=ValueError("Unknown task")):
            with self.assertRaises(ValueError):
                live_studio.save_preview_port(TASK_ID, "3000", console_port=8765)
            self.assertFalse((Path(td) / "studio-previews.json").exists())

    def test_studio_html_escapes_project_and_never_embeds_user_url(self):
        x = live_studio.studio_html("csrf-token", TASK_ID, port=None)
        self.assertIn('data-live-task="' + TASK_ID + '"', x)
        self.assertNotIn("<iframe", x)
        self.assertIn('name="csrf" value="csrf-token"', x)
        self.assertIn('name="port"', x)
        with patch.object(live_studio, "idea_detail",
                          return_value=mock_detail(project="C:/project/<script>")):
            y = live_studio.studio_html("csrf-token", TASK_ID, port=5173)
            self.assertIn('src="http://127.0.0.1:5173/"', y)
            self.assertNotIn("<script>", y)
            self.assertIn("&lt;script&gt;", y)
            self.assertIn('sandbox="allow-scripts allow-same-origin allow-forms"', y)
            self.assertIn('href="/ideas/' + TASK_ID + '#task-approval"', y)

    def test_snapshot_only_reads_actual_persisted_task(self):
        with patch.object(live_studio, "idea_detail",
                          return_value=mock_detail()), patch.object(
                live_studio, "tracked_paths", return_value=["README.md"]), patch.object(
                live_studio, "worker_state", return_value="IDLE"):
            snap = live_studio.task_snapshot(TASK_ID)
        self.assertEqual(snap["status"], "PENDING")
        self.assertEqual(snap["next_stage"], "discovery")
        self.assertEqual(snap["worker_state"], "IDLE")
        self.assertEqual(snap["files"], ["README.md"])
        self.assertEqual(snap["events"][0]["event"], "queued")
        self.assertEqual(snap["outputs"][0]["stage"], "discovery")
        self.assertNotIn("goal", snap)

    def test_tracked_paths_reject_secret_names_without_reading_contents(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / ".git").mkdir()
            files = [b"README.md", b".env", b"vault/private.pem",
                     b"docs/PLAN.md", b"nested/.env.local", b"sub/../escape.md"]
            class Result:
                returncode = 0
                stdout = b"\x00".join(files) + b"\x00"
            (project / "README.md").write_text("ok")
            (project / "docs").mkdir()
            (project / "docs" / "PLAN.md").write_text("ok")
            with patch.object(live_studio.subprocess, "run", return_value=Result()):
                self.assertEqual(live_studio.tracked_paths(str(project)),
                                 ["README.md", "docs/PLAN.md"])

    def test_dashboard_and_details_have_studio_navigation_without_new_execution_buttons(self):
        r = {
            "id": TASK_ID, "title": "example", "status": "PENDING",
            "stage": "discovery", "goal_preview": "Test",
        }
        page = console.home_html("token", [r])
        self.assertIn('/studio/' + TASK_ID, page)
        detail = console.details_html("token", mock_detail())
        self.assertIn('/studio/' + TASK_ID, detail)
        self.assertNotIn('name="gate" value="build"', detail)

    def test_studio_scripts_avoid_innerhtml_and_support_safe_text_only(self):
        self.assertNotIn("innerHTML", live_studio.STUDIO_JS)
        self.assertIn("textContent", live_studio.STUDIO_JS)
        self.assertIn("setInterval(refresh, 3000)", live_studio.STUDIO_JS)


if __name__ == "__main__":
    unittest.main()
