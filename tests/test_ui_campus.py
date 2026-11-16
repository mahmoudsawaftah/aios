"""Read-only UI regression checks for the Operations Campus redesign.

These tests must not create tasks, run Codex, touch SQLite, or approve anything.
"""
from __future__ import annotations

import unittest
from factory import console
from factory.ui_campus import approval_center, approval_panel, stage_track


class OperationsCampusTests(unittest.TestCase):
    def _record(self, **changes):
        record = {
            "id": "528e9ed89e19", "title": "My Project",
            "status": "WAITING_APPROVAL", "stage": "implementation",
            "goal_preview": "Safe example",
        }
        record.update(changes)
        return record

    def _detail(self, **changes):
        detail = {
            "id": "528e9ed89e19", "status": "WAITING_APPROVAL",
            "next_stage": "implementation", "project": "C:/AIOS_Projects/my-project",
            "goal": "A demo", "error": "", "outputs": [],
            "events": [], "approvals": [],
        }
        detail.update(changes)
        return detail

    def test_home_places_approval_center_before_intake_and_preserves_actions(self):
        html = console.home_html("test-csrf", [self._record()])
        self.assertLess(html.index('id="approvals"'), html.index('id="mission-intake"'))
        self.assertIn('id="departments"', html)
        self.assertIn('id="missions"', html)
        self.assertIn('href="/ideas/528e9ed89e19#task-approval"', html)
        self.assertIn('action="/ideas"', html)
        self.assertIn('name="csrf" value="test-csrf"', html)
        self.assertNotIn('action="/ideas/528e9ed89e19/approve"', html)

    def test_home_does_not_invent_pending_approvals(self):
        html = approval_center([self._record(status="PENDING")])
        self.assertIn("لا توجد موافقات", html)
        self.assertNotIn('href="/ideas/', html)

    def test_approval_button_only_renders_for_real_waiting_build_gate(self):
        html = console.details_html("csrftoken", self._detail())
        self.assertIn('id="task-approval"', html)
        self.assertIn('name="csrf" value="csrftoken"', html)
        self.assertIn('name="gate" value="build"', html)
        self.assertIn('action="/ideas/528e9ed89e19/approve"', html)
        self.assertEqual(html.count('action="/ideas/528e9ed89e19/approve"'), 1)
        self.assertIn('href="#reports"', html)
        self.assertLess(html.index('id="task-approval"'), html.index("أدوات المشروع"))

    def test_release_approval_is_explicit_and_not_deployment(self):
        html = approval_panel("token", self._detail(next_stage="release_gate"))
        self.assertIn('name="gate" value="release"', html)
        self.assertIn("لا تنفذ نشر", html)
        self.assertNotIn('name="gate" value="build"', html)

    def test_non_waiting_has_no_approval_form(self):
        html = console.details_html("token", self._detail(status="RUNNING"))
        self.assertIn("لا يوجد قرار مطلوب", html)
        self.assertNotIn('action="/ideas/528e9ed89e19/approve"', html)

    def test_escaped_text_and_matching_stage_labels(self):
        attack = '<img src=x onerror=alert(1)>'
        html = console.home_html("csrf", [self._record(title=attack)])
        self.assertIn("&lt;img", html)
        self.assertNotIn(attack, html)
        detail = console.details_html("csrf", self._detail(project="C:/x/<script>", goal=attack))
        self.assertNotIn(attack, detail)
        self.assertIn("&lt;script&gt;", detail)
        self.assertIn('class="stage-cell current"', stage_track(self._detail()))

    def test_html_page_preserves_security_and_accessibility(self):
        html = console.page("Test", console.home_html("csrf", []), "csrf",
                            auto_run=False).decode("utf-8")
        self.assertIn('aria-labelledby="approval-center-title"', html)
        self.assertIn('aria-label="التنقل الرئيسي"', html)
        self.assertIn("prefers-reduced-motion", html)
        self.assertIn("no GitHub push", html)
        self.assertIn("MISSION CONTROL", html)


if __name__ == "__main__":
    unittest.main()
