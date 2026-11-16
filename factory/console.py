"""Loopback-only AIOS v3 idea console (Python standard library).

Launch using: python -m factory.console
Optional, explicitly enabled worker: python -m factory.console --auto-run
Never expose this HTTP server directly to the public Internet.
"""
from __future__ import annotations

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import parse_qs, urlsplit
from factory import cli
from factory.intake import create_idea, idea_detail, list_ideas

HOST = "127.0.0.1"
MAX_BODY = 8192
POLL_INTERVAL = 8
STYLE = """body{font-family:system-ui,'Segoe UI',sans-serif;background:#0b1020;color:#ebefff;margin:0}
main{max-width:950px;margin:32px auto;padding:0 18px;line-height:1.6}
h1{font-size:1.65rem}a{color:#9bcbff}button{cursor:pointer;background:#5298ef;border:0;border-radius:9px;padding:11px 18px;color:#07172b;font-weight:700}
input,textarea,select{box-sizing:border-box;width:100%;background:#19223b;color:#fff;border:1px solid #455475;border-radius:8px;padding:12px;font:inherit}
textarea{min-height:140px;resize:vertical}label{display:block;margin:14px 0 7px}
section,.task{background:#151d32;border:1px solid #35425d;padding:18px;margin:16px 0;border-radius:13px}
small,.muted{color:#a8b5ce}code,pre{white-space:pre-wrap;overflow-wrap:anywhere}
pre{background:#091023;padding:13px;border-radius:8px;max-height:500px;overflow:auto}
.task a{font-weight:bold}.row{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.flag{display:inline-block;background:#283951;border-radius:7px;padding:2px 8px;font-size:.8rem}
.warn{color:#ffd089}.err{color:#ffa9a9}.ok{color:#9de2ba}
@media(max-width:600px){main{margin:15px auto}section{padding:13px}}
"""


def page(title: str, content: str, csrf: str, *, auto_run: bool, message: str = "") -> bytes:
    status = '<p class="muted">Auto-run: ' + ('ON (until approval gate)' if auto_run else 'OFF (safe preview)') + '</p>'
    banner = '<p class="warn">' + escape(message) + '</p>' if message else ''
    return (
        '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<title>' + escape(title) + '</title><style>' + STYLE + '</style></head><body><main>'
        '<div class="row"><a href="/">الرئيسية</a><strong>AIOS v3 — Idea Console</strong></div>'
        + status + banner + content + '<footer><small>'
        'Local-only prototype • no GitHub push, deployment, or production payments.'
        '</small></footer></main></body></html>'
    ).encode("utf-8")


def form_token(csrf: str) -> str:
    return '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'


def home_html(csrf: str, records: list[dict]) -> str:
    result = '<h1>أعطني الفكرة — AIOS ينظّم المشروع</h1><section><form method="post" action="/ideas">'
    result += form_token(csrf)
    result += '<label>الفكرة المطلوبة</label><textarea name="idea" maxlength="4000" required placeholder="صف المنتج أو الخدمة والمتطلبات..."></textarea>'
    result += '<label>اسم المشروع (اختياري)</label><input name="title" maxlength="100" placeholder="اسم قصير">'
    result += '<label>منهجية التسليم</label><select name="methodology">'
    result += '<option value="hybrid">Hybrid</option><option value="agile">Agile</option><option value="traditional">Traditional</option>'
    result += '</select><p><button type="submit">إنشاء مشروع محلي وتسجيل المهمة</button></p>'
    result += '</form><p class="muted">الإنشاء لا يرسل الفكرة للخارج. عند تشغيل Auto-run قد تُرسل إلى مزود AI عبر Codex.</p></section>'
    result += '<h2>المشاريع والمهام</h2>'
    if not records:
        return result + '<p>لا توجد مهام بعد.</p>'
    for r in records:
        result += '<div class="task"><a href="/ideas/' + escape(r["id"]) + '">' + escape(r["title"]) + '</a>'
        result += '<p><span class="flag">' + escape(r["status"]) + '</span> · ' + escape(r["stage"]) + '</p>'
        result += '<p>' + escape(r["goal_preview"]) + '</p></div>'
    return result


def details_html(csrf: str, r: dict) -> str:
    result = '<h1>تفاصيل المشروع</h1><section>'
    result += '<div class="row"><strong>' + escape(r["id"]) + '</strong><span class="flag">' + escape(r["status"]) + '</span></div>'
    result += '<p><b>Next:</b> ' + escape(r["next_stage"]) + '</p>'
    result += '<p><b>Local repo:</b> <code>' + escape(r["project"]) + '</code></p>'
    result += '<h3>الفكرة</h3><pre>' + escape(r["goal"]) + '</pre>'
    if r["error"]:
        result += '<p class="err">' + escape(r["error"]) + '</p>'
    result += '</section>'
    if r["status"] == "WAITING_APPROVAL" and r["next_stage"] == "implementation":
        result += '<section><h3>مراجعة مرحلة البناء</h3>'
        result += '<p class="warn">الضغط يسجل اعتماد البناء، ويتيح للوكيل تعديل الكود في Worktree معزول. راجع التقارير أولاً.</p>'
        result += '<form method="post" action="/ideas/' + escape(r["id"]) + '/approve">'
        result += form_token(csrf) + '<input type="hidden" name="gate" value="build">'
        result += '<button>أوافق على بدء البرمجة</button></form></section>'
    if r["status"] == "WAITING_APPROVAL" and r["next_stage"] == "release_gate":
        result += '<section><h3>توقيع اعتماد المراجعة</h3><p class="warn">هذا اعتماد إداري فقط، وليس نشراً إنتاجياً.</p>'
        result += '<form method="post" action="/ideas/' + escape(r["id"]) + '/approve">'
        result += form_token(csrf) + '<input type="hidden" name="gate" value="release">'
        result += '<button>أوافق على توقيع المراجعة</button></form></section>'
    for output in r["outputs"]:
        result += '<section><h3>' + escape(output["stage"]) + '</h3><pre>' + escape(output["content"]) + '</pre></section>'
    result += '<section><h3>سجل الأحداث</h3><pre>'
    for e in r["events"]:
        result += escape(e["ts"] + "  " + e["event"] + "  " + e["info"][:180]) + '\n'
    return result + '</pre></section>'


class ConsoleServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, *, auto_run: bool = False):
        super().__init__(address, ConsoleHandler)
        self.csrf = secrets.token_urlsafe(36)
        self.auto_run = auto_run
        self.worker_stop = threading.Event()
        self.worker_thread = None
        if auto_run:
            self.worker_thread = threading.Thread(target=self.worker_loop, daemon=True)
            self.worker_thread.start()

    def worker_loop(self):
        # One worker. The v2 engine provides per-task file locking and approval gates.
        while not self.worker_stop.is_set():
            try:
                with cli.connect() as db:
                    args = argparse.Namespace(limit=1, timeout=1800, max_attempts=2)
                    cli.run_pending(db, args)
            except Exception as exc:
                # Never print credentials or raw AI logs.
                print("AIOS worker needs review: " + type(exc).__name__, flush=True)
            self.worker_stop.wait(POLL_INTERVAL)

    def server_close(self):
        self.worker_stop.set()
        super().server_close()


class ConsoleHandler(BaseHTTPRequestHandler):
    server: ConsoleServer

    def _send(self, code: int, contents: bytes, extra_headers=None):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(contents)))
        self.end_headers()
        self.wfile.write(contents)

    def _safe_host(self) -> bool:
        authority = self.headers.get("Host", "")
        return authority in ("127.0.0.1:" + str(self.server.server_port),)

    def _render(self, title, inner, *, code=200, message=""):
        self._send(code, page(title, inner, self.server.csrf, auto_run=self.server.auto_run, message=message))

    def do_GET(self):
        if not self._safe_host():
            self._render("Denied", "<p>Invalid local host.</p>", code=403)
            return
        path = urlsplit(self.path).path
        try:
            if path == "/":
                self._render("AIOS Ideas", home_html(self.server.csrf, list_ideas()))
                return
            if path.startswith("/ideas/") and path.count("/") == 2:
                self._render("AIOS Task", details_html(self.server.csrf, idea_detail(path.split("/")[-1])))
                return
        except (ValueError, OSError) as exc:
            self._render("Not found", '<p>' + escape(str(exc)) + '</p>', code=404)
            return
        self._render("Not found", "<p>Unknown route.</p>", code=404)

    def do_POST(self):
        if not self._safe_host():
            self._render("Denied", "<p>Invalid local host.</p>", code=403)
            return
        origin = self.headers.get("Origin")
        if origin and origin != "http://127.0.0.1:" + str(self.server.server_port):
            self._render("Denied", "<p>Cross-origin requests are disabled.</p>", code=403)
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/x-www-form-urlencoded":
            self._render("Error", "<p>Unsupported form encoding.</p>", code=415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._render("Error", "<p>Invalid request size.</p>", code=413)
            return
        try:
            fields = parse_qs(self.rfile.read(length).decode("utf-8", "strict"), keep_blank_values=True,
                              max_num_fields=12, errors="strict")
            if len(fields.get("csrf", [])) != 1 or not secrets.compare_digest(fields["csrf"][0], self.server.csrf):
                self._render("Denied", "<p>Invalid form token.</p>", code=403)
                return
            path = urlsplit(self.path).path
            if path == "/ideas":
                r = create_idea(
                    fields.get("idea", [""])[0],
                    fields.get("title", [""])[0],
                    fields.get("methodology", ["hybrid"])[0],
                )
                self._send(303, b"", {"Location": "/ideas/" + r["id"]})
                return
            if path.startswith("/ideas/") and path.endswith("/approve"):
                tid = path.removeprefix("/ideas/").removesuffix("/approve").strip("/")
                gate = fields.get("gate", [""])[0]
                if gate not in ("build", "release"):
                    raise ValueError("Unknown approval gate.")
                # Reuse the v2 approval gate validation with a short-lived DB transaction.
                with cli.connect() as db:
                    cli.approve(db, argparse.Namespace(id=tid, gate=gate))
                self._send(303, b"", {"Location": "/ideas/" + tid})
                return
            self._render("Not found", "<p>Unknown route.</p>", code=404)
        except (ValueError, OSError, RuntimeError, UnicodeError) as exc:
            self._render("Request error", '<p class="err">' + escape(str(exc)) + '</p>', code=400)

    def log_message(self, format, *args):
        # Avoid logging full query strings or user task details.
        pass


def main(argv=None):
    p = argparse.ArgumentParser(description="AIOS v3 local idea console")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--auto-run", action="store_true",
                   help="Explicitly start one Codex worker; may consume plan usage.")
    args = p.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        p.error("Port must be between 1024 and 65535")
    with ConsoleServer((HOST, args.port), auto_run=args.auto_run) as server:
        print("AIOS idea console: http://127.0.0.1:" + str(args.port), flush=True)
        print("Local only. " + ("Auto-run ON" if args.auto_run else "Auto-run OFF"), flush=True)
        try:
            server.serve_forever(poll_interval=0.4)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
