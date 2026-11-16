"""Local, no-model verification for the first AIOS v3 idea console milestone."""
from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from factory import cli
from factory import intake
from factory import console


class IdeaConsoleTests(unittest.TestCase):
    def test_slug_is_safe_and_never_empty(self):
        self.assertEqual(intake.slugify("New Salon CRM!"), "new-salon-crm")
        self.assertEqual(intake.slugify("../../"), "project")
        self.assertTrue(intake.slugify("مشروع جديد"))

    def test_render_escapes_untrusted_ideas(self):
        html = console.home_html("csrf", [{
            "id": "a1b2c3d4e5f6", "title": "<script>alert(1)</script>",
            "status": "PENDING", "stage": "discovery",
            "goal_preview": "<b>unsafe</b>",
        }])
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;b&gt;", html)
        detail = console.details_html("csrf", {
            "id": "a1b2c3d4e5f6", "status": "PENDING",
            "next_stage": "discovery", "project": r"C:\temp\<unsafe>",
            "goal": "<img src=x onerror=alert(1)>", "error": "",
            "outputs": [{"stage": "discovery", "content": "<script>bad</script>"}],
            "events": [], "approvals": [],
        })
        self.assertNotIn("<img src=", detail)
        self.assertNotIn("<script>", detail)
        self.assertIn("&lt;img", detail)

    def test_rejects_invalid_input_without_writing(self):
        with self.assertRaises(ValueError):
            intake.create_idea("")
        with self.assertRaises(ValueError):
            intake.create_idea("a" * 4001)
        with self.assertRaises(ValueError):
            intake.create_idea("good", methodology="invalid")
        with self.assertRaises(ValueError):
            intake.create_idea("good", title="x" * 101)

    def test_create_separate_repository_and_durable_task(self):
        with tempfile.TemporaryDirectory() as td, ExitStack() as stack:
            root = Path(td)
            stack.enter_context(patch.dict("os.environ", {"AIOS_PROJECTS_ROOT": str(root / "products")}))
            stack.enter_context(patch.object(cli, "STATE", root / "runtime"))
            stack.enter_context(patch.object(cli, "DB", root / "runtime" / "state.sqlite3"))
            stack.enter_context(patch.object(intake, "owner_identity",
                                           return_value=("Test Owner", "test@example.invalid")))
            output = intake.create_idea(
                "Create a bilingual booking app", title="Salon Booking", methodology="hybrid")
            project = Path(output["project"])
            self.assertTrue(project.is_dir())
            self.assertTrue((project / ".git").exists())
            self.assertNotIn("bilingual booking", (project / "README.md").read_text(encoding="utf-8"))
            self.assertEqual(output["status"], "PENDING")
            detail = intake.idea_detail(output["id"])
            self.assertEqual(detail["goal"], "Create a bilingual booking app")
            self.assertEqual(detail["next_stage"], "discovery")
            self.assertEqual(len(intake.list_ideas()), 1)

    def test_local_binding_and_safe_defaults(self):
        self.assertEqual(console.HOST, "127.0.0.1")
        self.assertEqual(console.main.__defaults__, (None,))
        self.assertIn("no GitHub push", console.page("test", "ok", "csrf", auto_run=False).decode())


if __name__ == "__main__":
    unittest.main()
