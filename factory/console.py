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
STYLE = """
:root{color-scheme:dark;--bg:#060817;--panel:rgba(17,25,53,.77);--edge:rgba(117,155,240,.24);--cyan:#6beaff;--violet:#a493ff;--light:#eff5ff;--soft:#98a8cd;--green:#67efc4;--gold:#ffd48a}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{min-height:100vh;margin:0;color:var(--light);font-family:'Segoe UI',Tahoma,Arial,sans-serif;line-height:1.65;background:radial-gradient(ellipse at 83% 3%,rgba(53,69,172,.28),transparent 33%),radial-gradient(ellipse at 11% 53%,rgba(19,114,157,.19),transparent 37%),radial-gradient(ellipse at 77% 85%,rgba(119,49,175,.12),transparent 38%),var(--bg);overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.37;background-image:radial-gradient(#e6fbff 1px,transparent 1.6px),radial-gradient(#6da1ff 1px,transparent 1.6px);background-size:91px 101px,163px 149px;background-position:17px 24px,69px 81px;mask-image:linear-gradient(90deg,black,transparent 78%)}
body:after{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 97%,rgba(64,115,194,.055) 100%);background-size:100% 5px;opacity:.42}
a{color:#89eaff;text-decoration:none}a:hover{color:#fff}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:2px solid var(--cyan);outline-offset:3px}
.shell{max-width:1280px;margin:auto;padding:0 26px 44px;position:relative;isolation:isolate}
.topbar{min-height:91px;display:flex;gap:18px;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(122,151,215,.17)}
.brand{display:flex;align-items:center;gap:11px;color:var(--light);direction:ltr}.brand:hover{color:var(--light)}
.mark{width:49px;height:49px;flex:none;filter:drop-shadow(0 0 13px rgba(93,192,251,.48))}
.brand-text{line-height:1.2;display:flex;flex-direction:column;align-items:flex-start}
.brand-text strong{font-size:18px;letter-spacing:2.4px;font-weight:800}.brand-text small{font-size:9px;letter-spacing:3px;color:var(--soft);text-transform:uppercase}
.topright{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.pill{border:1px solid rgba(129,159,237,.29);padding:6px 12px;border-radius:999px;font-size:11px;color:#b8cbf2;background:rgba(47,62,119,.21);letter-spacing:1px}
.online{display:inline-flex;align-items:center;gap:8px}.online:before{content:"";width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green)}
.mode-on{color:var(--green)}.mode-off{color:var(--gold)}
.hero{position:relative;padding:60px 0 35px;display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:20px;align-items:center}
.eyebrow{color:var(--cyan);letter-spacing:3px;font-size:11px;font-weight:700;text-transform:uppercase;direction:ltr;text-align:right;margin:0 0 13px}
h1{font-size:clamp(28px,4vw,53px);letter-spacing:-1.3px;line-height:1.18;margin:0 0 15px;font-weight:850}
h1 em{font-style:normal;background:linear-gradient(90deg,#e2daff,#65dfff);-webkit-background-clip:text;background-clip:text;color:transparent}
.lead{font-size:15px;color:var(--soft);margin:0;max-width:680px;line-height:2}
.orbit{height:255px;display:grid;place-items:center;position:relative}
.orbit:before{content:"";position:absolute;width:224px;height:224px;border:1px solid rgba(99,194,254,.27);border-radius:50%;box-shadow:0 0 50px rgba(56,131,245,.07),inset 0 0 20px rgba(90,186,245,.04)}
.orbit:after{content:"";position:absolute;width:274px;height:100px;border:1px solid rgba(149,120,255,.43);border-radius:50%;transform:rotate(-26deg);box-shadow:0 0 26px rgba(111,107,243,.08)}
.planet{width:145px;height:145px;border-radius:50%;background:radial-gradient(circle at 30% 23%,#a4d8ff 0%,#768cf5 16%,#4b63b4 43%,#172961 73%,#0b1737 100%);box-shadow:inset -18px -20px 31px rgba(4,8,29,.68),0 0 55px rgba(90,123,234,.37);position:relative}
.planet:after{content:"";position:absolute;inset:-16px;border-radius:50%;border:1px dashed rgba(109,184,242,.16)}
.starpoint{position:absolute;top:23px;right:31px;color:#bcf5ff;font-size:27px;filter:drop-shadow(0 0 9px #80caff);animation:twinkle 4s infinite alternate}
@keyframes twinkle{to{opacity:.28;transform:scale(.78)}}@media(prefers-reduced-motion:reduce){.starpoint{animation:none}}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin:9px 0 26px}
.stat{background:linear-gradient(145deg,rgba(36,48,92,.54),rgba(13,23,49,.75));border:1px solid var(--edge);border-radius:15px;padding:17px 20px;min-height:90px;box-shadow:0 12px 35px rgba(0,0,0,.1)}
.stat .num{font-size:29px;font-weight:800;line-height:1.15;color:#dff8ff;direction:ltr;text-align:right}
.stat .desc{color:var(--soft);font-size:11px;letter-spacing:.5px;margin-top:6px}
.grid{display:grid;grid-template-columns:minmax(0,1.17fr) minmax(305px,.83fr);gap:20px;align-items:start}
.panel{border:1px solid var(--edge);background:linear-gradient(145deg,rgba(21,34,71,.89),rgba(10,17,36,.94));border-radius:19px;padding:26px;box-shadow:0 14px 40px rgba(0,0,0,.23),inset 0 1px 0 rgba(187,217,255,.055);backdrop-filter:blur(14px);min-width:0}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:19px}
.panel h2,.panel h3{margin:0;line-height:1.4;font-size:18px}.panel-head small,.muted{color:var(--soft)}
.tag{display:inline-block;border:1px solid rgba(107,234,255,.25);color:var(--cyan);background:rgba(51,149,185,.1);border-radius:7px;padding:3px 9px;font-size:10px;font-weight:800;letter-spacing:1px;direction:ltr}
label{display:block;color:#c1cee9;font-size:13px;font-weight:700;margin:17px 0 8px}
input,textarea,select{width:100%;font-family:inherit;font-size:14px;line-height:1.7;border:1px solid #3c5078;border-radius:11px;color:var(--light);background:rgba(7,14,34,.8);padding:13px 15px}
textarea{min-height:174px;resize:vertical}
input::placeholder,textarea::placeholder{color:#7e90b6}select{cursor:pointer}
.action{display:inline-flex;justify-content:center;align-items:center;gap:12px;width:100%;cursor:pointer;background:linear-gradient(100deg,#66e0f4,#8a9bff);color:#08112b;font-size:14px;font-weight:850;border:0;border-radius:10px;padding:15px 18px;margin-top:20px;box-shadow:0 9px 28px rgba(75,145,224,.22);transition:filter .2s,transform .2s}
.action:hover{filter:brightness(1.12);transform:translateY(-1px)}.action:focus-visible{outline:3px solid white}
.hint{font-size:11px;line-height:1.8;color:var(--soft);margin-top:13px}
.tasks{display:grid;gap:12px}
.task{border:1px solid rgba(131,159,215,.2);background:rgba(10,20,47,.75);padding:15px 17px;border-radius:13px;transition:border-color .2s,background .2s}
.task:hover{border-color:rgba(109,226,255,.45);background:rgba(24,43,86,.74)}
.task-title{font-size:14px;font-weight:800;overflow-wrap:anywhere}.task-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:9px 0;color:var(--soft);font-size:11px}
.flag{display:inline-flex;align-items:center;gap:6px;color:#b4d5ff;border:1px solid rgba(140,174,245,.29);background:rgba(43,64,109,.34);border-radius:999px;padding:3px 9px;font-size:10px;direction:ltr}
.flag.WAITING_APPROVAL{color:var(--gold);border-color:rgba(255,204,122,.35)}.flag.DONE{color:var(--green);border-color:rgba(102,239,196,.35)}.flag.FAILED,.flag.INTERRUPTED{color:#ffa0ba;border-color:rgba(255,118,157,.4)}
.task p{font-size:12px;color:#9cadd2;margin:5px 0 0;overflow-wrap:anywhere}
.empty{padding:30px 15px;text-align:center;border:1px dashed rgba(114,151,222,.37);border-radius:13px;color:var(--soft);font-size:14px}
.empty .symbol{display:block;font-size:31px;color:var(--cyan);margin-bottom:8px}
section.detail-block{margin:16px 0}.detail-block h3{color:#d6e7ff;font-size:15px;margin-bottom:12px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;background:rgba(4,10,26,.74);border:1px solid rgba(117,151,210,.15);padding:15px;border-radius:10px;font-size:12px;color:#b8cceb;max-height:500px;overflow:auto;direction:auto;text-align:start}
code{overflow-wrap:anywhere;font-size:12px;color:#9cdaf3;direction:ltr}
.back{display:inline-block;margin:16px 0;color:var(--cyan);font-size:13px}
.warn{color:var(--gold)}.err{color:#ff9cae}.ok{color:var(--green)}
footer{padding:32px 4px 10px;color:#7285ac;font-size:11px;display:flex;justify-content:space-between;gap:16px;border-top:1px solid rgba(139,170,241,.1);margin-top:35px}
@media(max-width:900px){.hero{grid-template-columns:1fr}.orbit{display:none}.grid{grid-template-columns:1fr}}
@media(max-width:600px){.shell{padding:0 14px 28px}.topbar{min-height:76px}.brand-text strong{font-size:14px}.brand-text small{font-size:8px}.mark{width:42px;height:42px}.topright .pill:not(.online){display:none}.hero{padding:39px 0 26px}.stats{gap:8px}.stat{padding:13px}.stat .num{font-size:23px}.stat .desc{font-size:10px}.panel{padding:18px}.grid{gap:13px}footer{flex-direction:column}}
"""



def page(title: str, content: str, csrf: str, *, auto_run: bool, message: str = "") -> bytes:
    state = ('LIVE AGENT MODE' if auto_run else 'SAFE PREVIEW')
    label = 'mode-on' if auto_run else 'mode-off'
    banner = '<div class="panel warn">' + escape(message) + '</div>' if message else ''
    return (
        '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<meta name="theme-color" content="#060817">'
        '<title>' + escape(title) + ' | item space AI</title><style>' + STYLE
        + '</style></head><body><main class="shell">'
        '<header class="topbar"><a class="brand" href="/" aria-label="item space AI homepage">'
        '<svg class="mark" viewBox="0 0 64 64" role="img" aria-label="Item Space AI logo"><defs><radialGradient id="orb" cx="28%" cy="25%"><stop stop-color="#dbf7ff"/><stop offset=".35" stop-color="#83b8ff"/><stop offset="1" stop-color="#6040b7"/></radialGradient></defs><circle cx="32" cy="32" r="17" fill="url(#orb)"/><ellipse cx="32" cy="33" rx="29" ry="11" fill="none" stroke="#72efff" stroke-width="3" transform="rotate(-26 32 33)"/><circle cx="54" cy="11" r="3" fill="#fff"/><circle cx="8" cy="18" r="2" fill="#b0a8ff"/></svg>'
        '<span class="brand-text"><strong>item space AI</strong><small>MISSION CONTROL · AIOS V3</small></span></a>'
        '<div class="topright"><span class="pill online">LOCAL NODE</span>'
        '<span class="pill ' + label + '">' + state + '</span></div></header>'
        + banner + content
        + '<footer><span>ITEM SPACE AI / MISSION CONTROL</span>'
        '<span>Local-only prototype · no GitHub push, deployment, or production payments.</span>'
        '</footer></main></body></html>'
    ).encode("utf-8")


def form_token(csrf: str) -> str:
    return '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'


def home_html(csrf: str, records: list[dict]) -> str:
    active = sum(r["status"] in ("PENDING", "RUNNING", "INTERRUPTED") for r in records)
    waiting = sum(r["status"] == "WAITING_APPROVAL" for r in records)
    result = (
        '<section class="hero"><div>'
        '<p class="eyebrow">ITEM SPACE AI / COMMAND CENTER / 001</p>'
        '<h1>فكرتك هي البداية.<br><em>ونحن نبني المستقبل.</em></h1>'
        '<p class="lead">حوّل أفكارك إلى مشاريع تقنية منظمة. أدخل المهمة، تابع مراحلها '
        'واحتفظ بقراراتك وتقارير التنفيذ في مركز تحكم واحد.</p>'
        '</div><div class="orbit" aria-hidden="true">'
        '<div class="planet"></div><span class="starpoint">✦</span></div></section>'
        '<div class="stats">'
        '<div class="stat"><div class="num">' + str(len(records)) + '</div>'
        '<div class="desc">TOTAL MISSIONS</div></div>'
        '<div class="stat"><div class="num">' + str(active) + '</div>'
        '<div class="desc">ACTIVE / QUEUED</div></div>'
        '<div class="stat"><div class="num">' + str(waiting) + '</div>'
        '<div class="desc">AWAITING APPROVAL</div></div></div>'
        '<div class="grid"><section class="panel">'
        '<div class="panel-head"><h2>✦ إطلاق مهمة جديدة</h2><span class="tag">NEW MISSION</span></div>'
        '<form method="post" action="/ideas">'
        + form_token(csrf)
        + '<label for="idea">ما هي فكرتك؟</label>'
        '<textarea id="idea" name="idea" maxlength="4000" required '
        'placeholder="مثال: أريد نظام حجوزات للصالونات بالعربية والإنجليزية، '
        'مع إدارة العملاء والاشتراكات الشهرية..."></textarea>'
        '<label for="title">اسم المشروع <span class="muted">(اختياري)</span></label>'
        '<input id="title" name="title" maxlength="100" placeholder="مثال: Nova Booking">'
        '<label for="methodology">طريقة التنفيذ</label>'
        '<select id="methodology" name="methodology">'
        '<option value="hybrid">Hybrid — هجين</option>'
        '<option value="agile">Agile — مرن</option>'
        '<option value="traditional">Traditional — تقليدي</option>'
        '</select>'
        '<button class="action" type="submit">◈ &nbsp; إنشاء مشروع ومهمة</button>'
        '<p class="hint">وضع المعاينة لا يشغّل الذكاء الاصطناعي ولا ينشر أي شيء. '
        'عند تفعيل العامل الآلي قد يتم إرسال المهمة إلى Codex ضمن حدود الاشتراك.</p>'
        '</form></section>'
        '<section class="panel">'
        '<div class="panel-head"><h2>◉ سجل المهام</h2><span class="tag">MISSION LOG</span></div>'
        '<div class="tasks">'
    )
    if not records:
        result += (
            '<div class="empty"><span class="symbol">✧</span>'
            'لا توجد مهام حتى الآن.<br>أطلق أول مهمة من النموذج المجاور.</div>'
        )
    else:
        for r in records:
            status = escape(r["status"], quote=True)
            result += (
                '<article class="task">'
                '<a class="task-title" href="/ideas/' + escape(r["id"], quote=True)
                + '">' + escape(r["title"]) + '</a>'
                '<div class="task-meta"><span class="flag ' + status + '">'
                + escape(r["status"]) + '</span><span>' + escape(r["stage"])
                + '</span></div>'
                '<p>' + escape(r["goal_preview"]) + '</p></article>'
            )
    return result + '</div></section></div>'


def details_html(csrf: str, r: dict) -> str:
    status = escape(r["status"], quote=True)
    result = (
        '<section class="hero"><div><p class="eyebrow">ITEM SPACE AI / MISSION DETAILS</p>'
        '<h1>تفاصيل <em>المهمة</em></h1>'
        '<p class="lead">راجع تقدم المشروع، نتائج المراحل والموافقات المطلوبة.</p>'
        '</div><div class="orbit" aria-hidden="true"><div class="planet"></div>'
        '<span class="starpoint">✦</span></div></section>'
        '<a class="back" href="/">↩ العودة إلى مركز التحكم</a>'
        '<section class="panel detail-block">'
        '<div class="panel-head"><h2>◈ سجل المهمة ' + escape(r["id"])
        + '</h2><span class="flag ' + status + '">' + escape(r["status"]) + '</span></div>'
        '<p class="muted">المرحلة التالية: <strong>' + escape(r["next_stage"]) + '</strong></p>'
        '<p class="muted">المستودع المحلي: <code>' + escape(r["project"]) + '</code></p>'
        '<h3>الفكرة الأصلية</h3><pre>' + escape(r["goal"]) + '</pre>'
    )
    if r["error"]:
        result += '<p class="err">' + escape(r["error"]) + '</p>'
    result += '</section>'
    if r["status"] == "WAITING_APPROVAL" and r["next_stage"] == "implementation":
        result += (
            '<section class="panel detail-block"><h3>⚠ موافقة مرحلة البناء</h3>'
            '<p class="warn">راجع تقارير التخطيط قبل الموافقة. بعدها يمكن للوكيل '
            'تعديل الكود داخل Worktree معزول.</p>'
            '<form method="post" action="/ideas/' + escape(r["id"], quote=True)
            + '/approve">' + form_token(csrf)
            + '<input type="hidden" name="gate" value="build">'
            '<button class="action" type="submit">اعتماد بدء البرمجة</button></form></section>'
        )
    if r["status"] == "WAITING_APPROVAL" and r["next_stage"] == "release_gate":
        result += (
            '<section class="panel detail-block"><h3>⚠ اعتماد المراجعة النهائية</h3>'
            '<p class="warn">توقيع إداري فقط، وليس نشراً للإنتاج.</p>'
            '<form method="post" action="/ideas/' + escape(r["id"], quote=True)
            + '/approve">' + form_token(csrf)
            + '<input type="hidden" name="gate" value="release">'
            '<button class="action" type="submit">اعتماد المراجعة</button></form></section>'
        )
    for output in r["outputs"]:
        result += (
            '<section class="panel detail-block"><div class="panel-head"><h3>'
            + escape(output["stage"]) + '</h3><span class="tag">STAGE OUTPUT</span></div>'
            '<pre>' + escape(output["content"]) + '</pre></section>'
        )
    result += '<section class="panel detail-block"><h3>◉ سجل الأحداث</h3><pre>'
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
                with cli.managed_connect() as db:
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
                with cli.managed_connect() as db:
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
