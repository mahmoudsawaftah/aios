"""Single-host long-running worker using Factory v2's durable SQLite queue.

Designed for explicit local startup. Safe crash retry is bounded, not exactly-once.
No worker is launched merely by importing this module or registering MCP tools.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import threading

from factory import cli


def heartbeat(*, state: str, note: str) -> None:
    cli.STATE.mkdir(parents=True, exist_ok=True)
    marker = cli.STATE / "worker-status.json"
    tmp = cli.STATE / ("worker-status-" + str(os.getpid()) + ".tmp")
    tmp.write_text(json.dumps({
        "pid": os.getpid(), "last_seen": cli.utcnow(),
        "state": state, "note": note[:180],
        "state_store_id": cli.state_store_id(),
    }), encoding="utf-8")
    os.replace(tmp, marker)


def tick(*, limit: int = 3, timeout: int = 1800, max_attempts: int = 2) -> None:
    with cli.managed_connect() as db:
        cli.run_pending(db, argparse.Namespace(limit=limit, timeout=timeout,
                                                max_attempts=max_attempts))


def serve(*, poll: int = 20, limit: int = 3, timeout: int = 1800,
          max_attempts: int = 2, once: bool = False) -> None:
    if poll < 5 or limit < 1 or limit > 10 or timeout < 30 or max_attempts < 1:
        raise ValueError("Invalid worker limits.")
    stop = threading.Event()

    def request_stop(*_):
        stop.set()

    # SIGINT exists on Windows; SIGTERM behavior may be limited for console apps.
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, request_stop)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, request_stop)

    with cli.single_runner("item-space-supervisor"):
        while not stop.is_set():
            heartbeat(state="RUNNING", note="Checking durable queue")
            try:
                tick(limit=limit, timeout=timeout, max_attempts=max_attempts)
                heartbeat(state="IDLE", note="Finished bounded queue pass")
            except (RuntimeError, ValueError, OSError) as exc:
                # Do not print user prompts or raw provider logs.
                heartbeat(state="ERROR", note=type(exc).__name__)
            if once:
                break
            stop.wait(poll)
    heartbeat(state="STOPPED", note="Normal worker shutdown")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Item Space AI durable local queue worker")
    p.add_argument("--once", action="store_true")
    p.add_argument("--poll", type=int, default=20)
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--max-attempts", type=int, default=2)
    args = p.parse_args(argv)
    try:
        serve(once=args.once, poll=args.poll, limit=args.limit,
              timeout=args.timeout, max_attempts=args.max_attempts)
    except (ValueError, OSError, BlockingIOError) as exc:
        print("ERROR: " + type(exc).__name__ + " — " + str(exc)[:200])
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
