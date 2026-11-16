"""Stable absolute-file entry point for Codex MCP, regardless of IDE workspace."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.mcp_bridge import serve  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(serve())
