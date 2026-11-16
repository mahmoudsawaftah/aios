"""No-network regression tests for Item Space AI MCP, research, marketing and safety."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from factory import cli, github_ops, marketing, mcp_bridge, oss_research, supervisor


class AutonomyTests(unittest.TestCase):
    def test_mcp_initialize_and_tools_are_protocol_shaped(self):
        x = mcp_bridge.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                               "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(x["id"], 1)
        self.assertIn("tools", x["result"]["capabilities"])
        z = mcp_bridge.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {t["name"] for t in z["result"]["tools"]}
        self.assertTrue({"submit_idea", "submit_existing_project", "get_task",
                         "search_open_source", "generate_marketing_plan",
                         "github_preflight"}.issubset(names))
        self.assertIsNone(mcp_bridge.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_mcp_tool_dispatch_does_not_execute_a_worker(self):
        with patch.object(mcp_bridge, "create_idea",
                          return_value={"id": "abc123", "status": "PENDING"}) as create:
            x = mcp_bridge.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                   "params": {"name": "submit_idea",
                                              "arguments": {"idea": "salon CRM"}}})
            create.assert_called_once_with("salon CRM", "", "hybrid")
            self.assertIn("PENDING", x["result"]["content"][0]["text"])

    def test_mcp_cannot_bypass_gates_or_call_unknown_tool(self):
        x = mcp_bridge.handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                               "params": {"name": "approve_release", "arguments": {}}})
        self.assertTrue(x["result"]["isError"])
        self.assertNotIn("approve_release", {t["name"] for t in mcp_bridge.TOOLS})

    def test_license_classification_is_conservative(self):
        self.assertEqual(oss_research.license_class("MIT"),
                         "PERMISSIVE_CHECK_NOTICE_AND_DEPENDENCIES")
        self.assertEqual(oss_research.license_class("AGPL-3.0"),
                         "COPYLEFT_HUMAN_LEGAL_REVIEW")
        self.assertEqual(oss_research.license_class("NOASSERTION"),
                         "UNKNOWN_OR_CUSTOM_LEGAL_REVIEW")

    def test_open_source_search_saves_grounded_evidence_without_cloning(self):
        result = {"items": [{
            "full_name": "example/salon-app",
            "html_url": "https://github.com/example/salon-app",
            "description": "Booking",
            "language": "Python", "stargazers_count": 48,
            "pushed_at": datetime.now(timezone.utc).isoformat(),
            "archived": False,
            "license": {"spdx_id": "MIT"},
        }]}
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, count):
                return json.dumps(result).encode("utf-8")
        with tempfile.TemporaryDirectory() as td:
            with patch.object(cli, "STATE", Path(td)), patch.object(
                    oss_research, "urlopen", return_value=FakeResponse()):
                report = oss_research.search_open_source("booking salon", 5)
                self.assertEqual(len(report["results"]), 1)
                self.assertTrue(Path(report["saved_to"]).exists())
                self.assertEqual(report["results"][0]["license_spdx"], "MIT")

    def test_marketing_drafts_persist_in_separate_runtime_directory(self):
        with tempfile.TemporaryDirectory() as td, ExitStack() as stack:
            root = Path(td)
            stack.enter_context(patch.object(cli, "STATE", root / "runtime"))
            stack.enter_context(patch.object(cli, "DB", root / "runtime" / "state.sqlite3"))
            with cli.managed_connect() as db:
                ts = cli.utcnow()
                db.execute(
                    "INSERT INTO tasks(id,project,goal,methodology,status,created_at,updated_at)"
                    " VALUES(?,?,?,?,?,?,?)",
                    ("aabbccddeeff", str(root / "salon"), "Booking for salons",
                     "hybrid", "PENDING", ts, ts))
            output = marketing.generate_marketing_plan("aabbccddeeff")
            self.assertEqual(output["status"], "DRAFT_REVIEW_REQUIRED")
            self.assertEqual(output["posts"], 14)
            self.assertTrue(Path(output["calendar_file"]).exists())
            self.assertTrue(Path(output["brief_file"]).exists())

    def test_github_publishing_is_disabled_by_default(self):
        with patch.dict("os.environ", {"AIOS_ALLOW_GITHUB_PR": "0"}):
            with self.assertRaises(PermissionError):
                github_ops.publish_private_pr("aabbccddeeff")
        self.assertTrue(github_ops.suspicious(".env"))
        self.assertTrue(github_ops.suspicious("vault/client-keys.json"))
        self.assertFalse(github_ops.suspicious(".env.example"))

    def test_worker_heartbeat_is_local_and_atomic(self):
        with tempfile.TemporaryDirectory() as td, patch.object(cli, "STATE", Path(td)):
            supervisor.heartbeat(state="IDLE", note="test")
            status = json.loads((Path(td) / "worker-status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["state"], "IDLE")


if __name__ == "__main__":
    unittest.main()
