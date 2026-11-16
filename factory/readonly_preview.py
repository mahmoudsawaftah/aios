"""Read-only side-by-side UI preview against an active AIOS state database.

Use only from a SEPARATE checkout (not the live AIOS working tree).
No task mutations, no worker, no approvals. The sole allowed POST is a preview
port preference stored in the SEPARATE checkout, not the active runtime.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import threading
import webbrowser

from factory import cli, console, live_studio

LIVE_TASK = re.compile(r"^/studio/[0-9a-f]{12}/preview$")


class ReadOnlyHandler(console.ConsoleHandler):
    def do_POST(self):
        from urllib.parse import urlsplit
        path = urlsplit(self.path).path
        if not LIVE_TASK.fullmatch(path):
            self._render("Read-only", "<p>هذا وضع معاينة فقط. إنشاء المهام والموافقات معطلة.</p>",
                         code=403)
            return
        return super().do_POST()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Safe preview of Live Studio using active task state.")
    parser.add_argument("--active-root", required=True,
                        help="Existing active AIOS root whose runtime will be read-only.")
    parser.add_argument("--port", type=int, default=8877)
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args(argv)
    source = Path(args.active_root).expanduser().resolve()
    preview = cli.ROOT.resolve()
    if source == preview:
        parser.error("Read-only preview MUST run from a separate checkout.")
    state = source / ".factory-runtime"
    db = state / "state.sqlite3"
    if not db.is_file():
        parser.error("Active factory state.sqlite3 not found. No dummy state will be created.")
    if not 1024 <= args.port <= 65535 or args.port == 8765:
        parser.error("Use a separate preview port between 1024 and 65535, other than 8765.")

    # Project task data is strictly read-only, backed by SQLite URI mode=ro.
    cli.STATE = state
    cli.DB = db
    cli.managed_connect = cli.managed_readonly_connect
    # Preview port settings are isolated to this checkout, never the active runtime.
    preview_config = preview / ".preview-runtime" / "studio-previews.json"
    live_studio._config_file = lambda: preview_config
    # Reject create, approve, marketing, research, GitHub and all other writes.
    console.ConsoleHandler = ReadOnlyHandler

    try:
        with console.ConsoleServer(("127.0.0.1", args.port), auto_run=False) as server:
            url = "http://127.0.0.1:" + str(server.server_port) + "/"
            print("Read-only Item Space AI Operations Campus: " + url, flush=True)
            print("Worker OFF | Active tasks READ-ONLY | Preview ports stored separately", flush=True)
            if args.open_browser:
                threading.Thread(target=webbrowser.open_new_tab, args=(url,),
                                 daemon=True).start()
            try:
                server.serve_forever(poll_interval=0.4)
            except KeyboardInterrupt:
                pass
    except OSError as exc:
        print("Preview UI port unavailable: " + type(exc).__name__, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
