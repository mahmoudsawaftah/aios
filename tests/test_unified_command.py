"""Unified Command 2500 regression coverage: clarity, security, truthfulness."""
from __future__ import annotations

from contextlib import contextmanager
import io
import json
import sqlite3
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

from factory import console, ui_unified


TEST_ID = "528e9ed89e19"


def mission(status="PENDING", **extra):
    r = {"id": TEST_ID, "title": "Project <unsafe>", "status": status,
         "stage": "discovery", "goal_preview": "<b>test</b>",
         "updated_at": "2026-11-17T10:00:00Z", "error": ""}
    r.update(extra)
    return r


def detail(status="PENDING", **extra):
    r = {"id": TEST_ID, "status": status, "next_stage": "discovery",
         "project": "C:/AIOS_Projects/<unsafe>", "goal": "<script>alert(1)</script>",
         "error": "", "outputs": [], "events": [], "approvals": []}
    r.update(extra)
    return r


class Command2500Tests(unittest.TestCase):
    def render(self, records=None):
        if records is None:
            records = [mission()]
        with patch.object(ui_unified, "preview_port", return_value=None), patch.object(
                ui_unified, "worker_state", return_value="IDLE"), patch.object(
                ui_unified, "_verification", return_value={
                    "verdict": "NOT VERIFIED", "stage": "—", "sha": ""}):
            return ui_unified.home_html("secret_csrf", records)

    def test_single_clean_layout_has_all_critical_destinations(self):
        html, port = self.render([mission()])
        self.assertIsNone(port)
        for marker in ('id="workspace"', 'id="focus"', 'id="live"',
                       'id="approvals"', 'id="agents"', 'id="mission-intake"',
                       'id="missions"', 'id="departments"'):
            self.assertIn(marker, html)
        self.assertLess(html.index('id="approvals"'), html.index('id="mission-intake"'))
        self.assertEqual(html.count('id="approvals"'), 1)
        self.assertIn('href="/studio/' + TEST_ID + '"', html)
        self.assertIn('href="/office"', html)
        self.assertIn('name="csrf" value="secret_csrf"', html)
        self.assertIn('name="idea"', html)
        self.assertIn('name="methodology"', html)
        self.assertIn('action="/ideas"', html)
        self.assertNotIn('action="/ideas/' + TEST_ID + '/approve"', html)

    def test_only_explicitly_configured_preview_port_embeds_app(self):
        with patch.object(ui_unified, "preview_port", return_value=5173), patch.object(
                ui_unified, "worker_state", return_value="IDLE"), patch.object(
                ui_unified, "_verification", return_value={
                    "verdict": "NOT VERIFIED", "stage": "—", "sha": ""}):
            html, port = ui_unified.home_html("token", [mission()])
        self.assertEqual(port, 5173)
        self.assertIn('src="http://127.0.0.1:5173/"', html)
        self.assertIn('sandbox="allow-scripts allow-same-origin allow-forms"', html)
        self.assertNotIn('http://example.com', html)

    def test_missing_preview_is_explicit_and_never_autostarts_dev_server(self):
        html, port = self.render()
        self.assertIsNone(port)
        self.assertIn("المعاينة غير متصلة", html)
        self.assertNotIn("<iframe", html)
        self.assertIn("لن يتم تشغيل أي أمر تلقائياً", html)

    def test_approval_queue_links_to_real_gate_not_quick_approve(self):
        html, _ = self.render([mission("WAITING_APPROVAL", stage="implementation")])
        self.assertIn('href="/ideas/' + TEST_ID + '#task-approval"', html)
        self.assertIn('data-state="WAITING_APPROVAL"', html)
        self.assertNotIn('name="gate"', html)
        self.assertNotIn('/approve"', html)
        self.assertNotIn("لا توجد موافقات", html)

    def test_failure_state_is_visible_and_not_marked_as_success(self):
        html, _ = self.render([mission("NEEDS_WORK", stage="implementation")])
        self.assertIn('data-state="NEEDS_WORK"', html)
        self.assertIn("المهمة تحتاج معالجة", html)
        self.assertIn("NOT VERIFIED", html)
        self.assertNotIn('class="ok"', html)

    def test_selection_prefers_running_but_honors_explicit_focus(self):
        a = mission(status="PENDING")
        a["id"] = "111111111111"; a["title"] = "Queued"
        b = mission(status="RUNNING")
        b["id"] = "222222222222"; b["title"] = "Active"
        chosen = ui_unified._pick_task([a, b], None)
        self.assertEqual(chosen["id"], b["id"])
        self.assertEqual(ui_unified._pick_task([a, b], "111111111111")["id"], a["id"])
        self.assertEqual(ui_unified._pick_task([a, b], "../../")["id"], b["id"])

    def test_escapes_all_untrusted_fields_and_refuses_fake_script_tags(self):
        html, _ = self.render([mission(title="<script>danger</script>",
                                       goal_preview="<img src=x onerror=alert(1)>")])
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>danger</script>", html)
        self.assertNotIn("<img src=", html)
        details = console.details_html("token", detail())
        self.assertIn("&lt;script&gt;", details)
        self.assertNotIn("<script>alert", details)
        self.assertIn("&lt;unsafe&gt;", details)

    def test_detail_preserves_genuine_build_and_release_approval_contracts(self):
        build = console.details_html("token", detail(
            status="WAITING_APPROVAL", next_stage="implementation"))
        self.assertIn('action="/ideas/' + TEST_ID + '/approve"', build)
        self.assertIn('name="gate" value="build"', build)
        self.assertEqual(build.count('action="/ideas/' + TEST_ID + '/approve"'), 1)
        self.assertLess(build.index('id="task-approval"'), build.index('id="reports"'))
        self.assertIn('id="project-tools"', build)
        self.assertIn('id="audit-events"', build)
        released = console.details_html("token", detail(
            status="WAITING_APPROVAL", next_stage="release_gate"))
        self.assertIn('name="gate" value="release"', released)
        self.assertNotIn('name="gate" value="build"', released)
        blocked = console.details_html("token", detail(status="BLOCKED"))
        self.assertNotIn('action="/ideas/' + TEST_ID + '/approve"', blocked)

    def test_real_acceptance_evidence_query_and_missing_gate_fail_closed(self):
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        @contextmanager
        def readonly():
            yield db
        try:
            with patch.object(ui_unified.cli, "managed_readonly_connect", readonly):
                self.assertEqual(ui_unified._verification(TEST_ID)["verdict"], "NOT VERIFIED")
                db.execute("CREATE TABLE acceptance_stage_results "
                           "(task_id TEXT, stage TEXT, verdict TEXT, commit_sha TEXT, updated_at TEXT)")
                db.execute("INSERT INTO acceptance_stage_results VALUES "
                           "(?,?,?,?,?)", (TEST_ID, "qa", "NEEDS_WORK", "f"*40, "2026-11-17"))
                evidence = ui_unified._verification(TEST_ID)
                self.assertEqual(evidence["verdict"], "NEEDS_WORK")
                self.assertEqual(evidence["stage"], "qa")
                self.assertEqual(evidence["sha"], "f"*12)
        finally:
            db.close()

    def test_home_without_tasks_still_has_intake_and_no_approval(self):
        html, port = self.render([])
        self.assertIsNone(port)
        self.assertIn("لا توجد مهام بعد", html)
        self.assertIn('id="mission-intake"', html)
        self.assertIn("لا توجد موافقات", html)

    def test_historical_done_without_final_acceptance_is_not_green(self):
        html, _ = self.render([mission("DONE")])
        self.assertIn('data-state="LEGACY_DONE"', html)
        self.assertIn("DONE · غير متحقق", html)
        self.assertIn("NOT VERIFIED", html)

    def test_final_acceptance_is_needed_for_verified_done_badge(self):
        with patch.object(ui_unified, "preview_port", return_value=None), patch.object(
                ui_unified, "worker_state", return_value="IDLE"), patch.object(
                ui_unified, "_verification", return_value={
                    "verdict": "ACCEPTED", "stage": "final", "sha": "f"*12}):
            html, _ = ui_unified.home_html("token", [mission("DONE")])
        self.assertIn('data-state="DONE"', html)
        self.assertNotIn("DONE · غير متحقق", html)
        self.assertIn('data-accepted="true"', html)

    def test_empty_first_run_can_expand_new_mission_via_click(self):
        js = ui_unified.COMMAND_JS
        self.assertLess(js.index("document.querySelectorAll('a[href="),
                        js.index("if (!root) return;"))
        self.assertIn("target.open = true", js)

    def test_collapsed_office_pauses_unnecessary_animation_and_polling(self):
        from factory import pixel_office
        self.assertIn("canvas.closest('details')", pixel_office.OFFICE_JS)
        self.assertIn("!isVisible()", pixel_office.OFFICE_JS)
        self.assertIn("if(isVisible()){draw();}", pixel_office.OFFICE_JS)

    def test_command_js_uses_safe_text_without_inserting_html(self):
        self.assertNotIn("innerHTML", ui_unified.COMMAND_JS)
        self.assertIn("textContent", ui_unified.COMMAND_JS)
        self.assertIn("setInterval(update, 5000)", ui_unified.COMMAND_JS)
        self.assertIn("prefers-reduced-motion", ui_unified.COMMAND_CSS)
        self.assertIn("@media(max-width:720px)", ui_unified.COMMAND_CSS)

    def test_real_http_route_has_scoped_csp_without_exposing_task_state_for_writes(self):
        with patch.object(console, "list_ideas", return_value=[mission()]), patch.object(
                ui_unified, "preview_port", return_value=3000), patch.object(
                ui_unified, "worker_state", return_value="IDLE"), patch.object(
                ui_unified, "_verification", return_value={
                    "verdict": "NOT VERIFIED", "stage": "—", "sha": ""}):
            with console.ConsoleServer(("127.0.0.1", 0), auto_run=False) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                url = "http://127.0.0.1:" + str(server.server_port)
                try:
                    with urlopen(url + "/?task=" + TEST_ID, timeout=3) as r:
                        html = r.read().decode("utf-8")
                        csp = r.headers["Content-Security-Policy"]
                    self.assertIn("UNIFIED COMMAND", html)
                    self.assertIn("script-src 'self'", csp)
                    self.assertIn("connect-src 'self'", csp)
                    self.assertIn("frame-src http://127.0.0.1:3000", csp)
                    with urlopen(url + "/command.js", timeout=3) as r:
                        self.assertIn("textContent", r.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
