"""Unified Command 2500: one ergonomic, grounded AIOS workspace.

Presentation only. Reads task state and Acceptance Gate verdicts through
read-only SQLite. Never runs an agent, mutates a task, approves a gate or starts
a developer server. All user-controlled text is HTML-escaped.
"""
from __future__ import annotations

from html import escape
import re
import sqlite3

from factory import cli
from factory.live_studio import preview_port, worker_state
from factory.pixel_office import office_html
from factory.ui_campus import approval_panel, stage_track, task_hero

TASK_ID = re.compile(r"^[0-9a-f]{12}$")

COMMAND_CSS = r"""
/* Unified Command 2500 — functional space-station UI, not ornament overload */
:root{--bg:#080d18;--panel:#101b2b;--edge:#284055;--cyan:#95f3e4;--violet:#a8bcff;--light:#eaf5fb;--soft:#8ea8ba;--gold:#f5c586;--green:#8ddab9}
html{scroll-padding-top:90px}
body{background:radial-gradient(ellipse at 67% -9%,rgba(48,114,143,.19),transparent 43%),linear-gradient(180deg,#080e19,#090e17 70%);font-family:Segoe UI,Arial,sans-serif;color:#eaf4f9}
body:before{display:none}body:after{display:none}
.shell{max-width:1690px;padding:0 28px 35px}
.topbar{height:72px;min-height:72px;background:rgba(8,16,29,.91);position:sticky;top:0;z-index:30;border-bottom:1px solid #294055;backdrop-filter:blur(14px)}
.brand .mark{width:39px;height:39px}
.brand-text strong{font-size:16px;letter-spacing:.4px}
.brand-text small{letter-spacing:1.6px;color:#6f96ac}
.topnav{display:flex;gap:6px}
.topnav a{padding:8px 14px;color:#acc4d4;border:1px solid transparent;border-radius:9px}
.topnav .nav-approval{color:#e6d8bc;background:transparent;border-color:transparent}
.topnav .nav-approval:hover{background:#263b46}
.pill{padding:5px 11px;border-color:#315267;font-size:10px}
.panel{background:#101b2b;border-color:#274159;box-shadow:none}
.action{box-shadow:none}
.command-intro{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:26px 2px 22px;border-bottom:1px solid #21374b}
.command-headline .eyebrow{font-size:9px;color:#89d9d2;letter-spacing:1.9px;margin:0 0 5px}
.command-headline h1{font-size:clamp(25px,3vw,37px);line-height:1.25;margin:0;letter-spacing:-.7px;font-weight:780}
.command-headline h1 em{background:none;color:#9de6df}
.command-headline p{color:#92b0c1;font-size:12px;line-height:1.8;margin:8px 0 0}
.command-new-btn{white-space:nowrap;text-align:center;border:1px solid #60bfb8;background:#143b42;color:#c2fff2;padding:11px 16px;border-radius:10px;font-size:12px;font-weight:800}
.command-new-btn:hover{background:#21545a;color:white}
.command-grid{display:grid;grid-template-columns:170px minmax(0,1fr) 258px;gap:17px;padding-top:21px;align-items:start}
.command-rail{position:sticky;top:92px;border:1px solid #263f51;border-radius:14px;padding:10px;background:#101b2b;display:grid;gap:3px}
.command-rail .rail-caption{font-size:9px;color:#678da0;letter-spacing:2px;padding:8px 12px 12px;text-transform:uppercase}
.command-rail a{display:flex;align-items:center;gap:9px;border-radius:9px;padding:11px 12px;color:#adcad8;font-size:12px}
.command-rail a:hover,.command-rail a.rail-active{background:#1b3645;color:#b9f3e9}
.command-rail a .rail-icon{font-size:15px;opacity:.9;width:19px;text-align:center}
.command-rail .rail-divider{height:1px;background:#294054;margin:9px 10px}
.command-main{min-width:0}
.command-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin-bottom:13px}
.command-metric{border:1px solid #29435a;background:#111f30;border-radius:12px;padding:12px 17px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.command-metric span{font-size:11px;color:#8eaabd;line-height:1.5}
.command-metric strong{font-size:23px;color:#f0f8fb;font-weight:740;line-height:1}
.command-metric.priority{border-color:#856947;background:#241f23}
.command-metric.priority strong{color:#ffd5a2}
.command-card{scroll-margin-top:94px;border:1px solid #2b455b;border-radius:15px;background:linear-gradient(160deg,#112035,#0d1929);padding:19px;margin-bottom:13px;min-width:0}
.command-card h2{margin:0;font-size:15px;font-weight:780;color:#e6f4f8}
.command-card h3{font-size:13px;margin:0}
.command-card-header{display:flex;justify-content:space-between;align-items:center;gap:11px;margin:0 0 14px}
.command-card-header small{color:#7ea9b7;font-size:10px}
.command-card-sub{color:#8faac0;font-size:11px}
.command-subline{margin:9px 0 0;color:#adc3d1;font-size:11px;overflow-wrap:anywhere}
.command-badge{font-size:10px;border:1px solid #426579;color:#abdbdb;border-radius:7px;padding:5px 8px;white-space:nowrap}
.command-badge[data-state="WAITING_APPROVAL"]{border-color:#a27b4d;color:#f2d1a3}
.command-badge[data-state="NEEDS_WORK"],.command-badge[data-state="BLOCKED"],.command-badge[data-state="FAILED"]{border-color:#92565c;color:#f2b5b5}
.command-badge[data-state="RUNNING"]{border-color:#3d8c80;color:#a1efd2}
.command-badge[data-state="DONE"]{border-color:#487965;color:#a1dfb6}
.command-badge[data-state="LEGACY_DONE"]{border-color:#a27b4d;color:#f2d1a3}
.command-focus-heading{display:flex;align-items:center;justify-content:space-between;gap:12px}
.command-focus-heading a{color:#e5f6fa;max-width:85%;font-size:19px;font-weight:760;overflow-wrap:anywhere}
.command-focus-heading a:hover{color:#9df4e9}
.command-focus-meta{margin-top:11px;display:flex;flex-wrap:wrap;gap:9px}
.command-chip{padding:5px 9px;border:1px solid #345168;background:#17283c;border-radius:8px;color:#aac2d2;font-size:10px}
.command-chip strong{color:#d9edf4}
.command-focus-note{margin-top:12px;color:#9bb6c6;font-size:12px;line-height:1.8;max-width:700px}
.command-focus-links{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.command-link{color:#b8f0e8;display:inline-flex;align-items:center;justify-content:center;padding:8px 12px;border:1px solid #3c6979;border-radius:9px;font-size:11px;font-weight:740;background:#16313e}
.command-link.secondary{background:transparent;border-color:#36536a;color:#c3d5e3}
.command-link:hover{background:#234b57;color:#fff}
.command-working-grid{display:grid;grid-template-columns:minmax(0,1.27fr) minmax(235px,.73fr);gap:13px}
.command-preview-screen{border:1px solid #38536a;border-radius:12px;overflow:hidden;background:#091829;min-height:295px}
.command-preview-placeholder{min-height:295px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;text-align:center;padding:27px;background:radial-gradient(circle at 50% 24%,#1b394c,#0d1b2d 62%)}
.command-preview-placeholder .preview-icon{font-size:37px;color:#8cdbd3}
.command-preview-placeholder strong{font-size:14px}
.command-preview-placeholder p{font-size:11px;color:#92afc0;line-height:1.9;max-width:290px;margin:0}
.command-preview-screen iframe{width:100%;height:340px;background:white;border:0;display:block}
.command-preview-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:space-between;margin-top:11px}
.command-preview-actions small{font-size:10px;color:#89a7b9}
.command-approval-stack{display:grid;gap:8px}
.command-approval-item{border:1px solid #796043;background:#26212a;border-radius:10px;padding:11px}
.command-approval-item strong{display:block;font-size:12px;overflow-wrap:anywhere}
.command-approval-item p{font-size:10px;color:#c7b9b0;margin:7px 0}
.command-approval-item a{font-size:11px;color:#ffdab0;font-weight:790}
.command-approval-empty{font-size:12px;color:#9fc5ba;display:flex;align-items:center;gap:8px;line-height:1.7}
.command-approval-help{font-size:10px;color:#96acba;line-height:1.8;margin-top:10px}
.command-issue{margin-top:12px;padding:11px;border:1px solid #845866;border-radius:9px;color:#e8bcc2;background:#301f2e;font-size:12px}
.command-inspector{position:sticky;top:92px;display:grid;gap:12px}
.command-inspector .command-card{margin:0}
.command-inspector h2{font-size:13px}
.command-inspector p{font-size:11px;color:#92b0c2;line-height:1.8}
.command-health{display:grid;gap:9px}
.command-health-line{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#9ab0c5;font-size:11px}
.command-health-line strong{color:#d3e9ef;max-width:140px;text-align:left;overflow-wrap:anywhere}
.command-health-line strong.warn{color:#ffcb93}
.command-health-line strong.ok{color:#94e4c4}
.command-mission-list{display:grid;gap:5px}
.command-mission-list a{display:block;padding:10px;border-radius:9px;border:1px solid transparent;color:#bfd4df;font-size:11px;overflow-wrap:anywhere}
.command-mission-list a:hover,.command-mission-list a.selected{background:#1c3445;border-color:#3a6270;color:#f4fbff}
.command-mission-list small{display:block;color:#819daf;margin-top:4px}
.command-detail-toggle{border:1px solid #34546a;border-radius:13px;background:#101e30;margin-bottom:12px;overflow:hidden;scroll-margin-top:95px}
.command-detail-toggle summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:15px;padding:15px 20px;color:#dceaf1;font-weight:760;font-size:13px}
.command-detail-toggle summary::-webkit-details-marker{display:none}
.command-detail-toggle summary:after{content:"+";font-size:18px;color:#95d8d3}
.command-detail-toggle[open] summary:after{content:"−"}
.command-detail-toggle[open] summary{border-bottom:1px solid #2b495e}
.command-detail-content{padding:16px 19px}
.command-detail-content h2{font-size:14px;margin:0 0 12px}
.command-detail-content .office-intro{display:none}
.command-detail-content .office-layout{grid-template-columns:minmax(0,1.5fr) minmax(200px,.7fr)}
.command-detail-content .office-panel{padding:12px}
.command-detail-content .office-task-list{max-height:310px}
.command-detail-content .office-scene{background:#0b1726}
.command-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.command-form-grid label{margin:0}
.command-form-grid input,.command-form-grid select{margin-top:7px}
.command-form-textarea{margin:12px 0}
.command-form-textarea label{margin:0 0 7px}
.command-form-textarea textarea{min-height:117px}
.command-submit{margin:6px 0 0;max-width:270px}
.command-footer-note{font-size:10px;color:#87a0b3;line-height:1.8;margin-top:9px}
.command-audit{border-top:1px solid #294155;margin-top:13px;padding-top:12px;font-size:11px;color:#90b0c4}
.command-detail-page{max-width:1060px;margin:0 auto}
.command-detail-page .task-headline{margin:12px 0 15px}
.command-detail-page .stage-section{border-color:#294b62;background:#101e30}
.command-detail-page .approval-detail{margin:16px 0}
.command-detail-page .detail-block{background:#111f31}
.command-detail-page .command-detail-toggle pre{max-height:370px}
.command-detail-page .command-detail-toggle .action{max-width:400px}
.command-detail-page .command-detail-toggle .panel{border:none;box-shadow:none;background:transparent;padding:8px}
.command-detail-page .command-detail-toggle .panel h3{font-size:14px}
.command-detail-page .command-detail-toggle .panel-head{margin-bottom:8px}
.command-detail-page .command-detail-toggle .hint{margin-top:4px}
.command-detail-page .command-detail-toggle form{margin-bottom:11px}
.command-quick-status{display:flex;gap:9px;align-items:center;flex-wrap:wrap}
.command-connect{color:#98b3c2;font-size:10px}
.command-separator{width:1px;height:14px;background:#355267}
.command-screenreader{position:absolute;clip-path:inset(50%);width:1px;height:1px;overflow:hidden}
@media(min-width:1500px){.command-grid{grid-template-columns:190px minmax(0,1fr) 282px;gap:20px}.command-working-grid{grid-template-columns:minmax(0,1.3fr) minmax(280px,.7fr)}}
@media(max-width:1200px){.command-grid{grid-template-columns:142px minmax(0,1fr)}.command-inspector{grid-column:2;position:static;grid-template-columns:1fr 1fr}.command-working-grid{grid-template-columns:1fr 1fr}}
@media(max-width:930px){.command-grid{grid-template-columns:1fr}.command-rail{position:static;display:flex;overflow-x:auto;white-space:nowrap;gap:4px}.command-rail .rail-caption,.command-rail .rail-divider{display:none}.command-rail a{flex:none;padding:8px 10px}.command-inspector{grid-column:1}.command-intro{padding-top:18px}.command-detail-content .office-layout{grid-template-columns:1fr}.command-rail{scrollbar-width:thin}}
@media(max-width:720px){.shell{padding-inline:13px}.topbar{height:68px;min-height:68px}.topright .pill:not(.online){display:none}.command-working-grid{grid-template-columns:1fr}.command-metrics{gap:7px}.command-metric{padding:11px}.command-metric span{font-size:10px}.command-metric strong{font-size:20px}.command-inspector{grid-template-columns:1fr}.command-card{padding:15px}.command-intro{align-items:start;flex-direction:column}.command-form-grid{grid-template-columns:1fr}.command-headline h1{font-size:26px}.command-preview-screen iframe{height:260px}.command-quick-status{display:none}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

COMMAND_JS = r"""'use strict';
(() => {
  document.querySelectorAll('a[href="#mission-intake"],a[href="#agents"]').forEach((a) => {
    a.addEventListener('click', () => {
      const target = document.getElementById(a.getAttribute('href').slice(1));
      if (target && target.tagName === 'DETAILS') target.open = true;
    });
  });
  if (location.hash === '#agents' || location.hash === '#mission-intake') {
    const target = document.getElementById(location.hash.slice(1));
    if (target && target.tagName === 'DETAILS') target.open = true;
  }
  const root = document.querySelector('[data-command-task]');
  if (!root) return;
  const accepted = root.getAttribute('data-accepted') === 'true';
  const taskId = root.getAttribute('data-command-task');
  if (!/^[0-9a-f]{12}$/.test(taskId)) return;
  let inflight = false;
  const update = async () => {
    if (inflight || document.hidden) return;
    inflight = true;
    try {
      const r = await fetch('/studio/' + taskId + '/state', {cache:'no-store'});
      if (!r.ok) throw Error('No live state');
      const d = await r.json();
      if (d.id !== taskId) throw Error('Mismatched task');
      const status = document.getElementById('command-task-state');
      const stage = document.getElementById('command-task-stage');
      const connection = document.getElementById('command-connection');
      if (status) {
        const state = String(d.status || 'UNKNOWN');
        status.textContent = state === 'DONE' && !accepted ? 'DONE · غير متحقق' : state;
        status.dataset.state = state === 'DONE' && !accepted ? 'LEGACY_DONE' : state;
      }
      if (stage) stage.textContent = String(d.next_stage || '—');
      if (connection) connection.textContent = 'متصل · حالة فعلية';
    } catch (_) {
      const connection = document.getElementById('command-connection');
      if (connection) connection.textContent = 'آخر حالة محفوظة · الاتصال متوقف';
    } finally { inflight = false; }
  };
  update();
  setInterval(update, 5000);
  document.addEventListener('visibilitychange', () => {if (!document.hidden) update();});
})();
"""


def _pick_task(records: list[dict], requested: str | None) -> dict | None:
    if requested and TASK_ID.fullmatch(requested):
        for r in records:
            if r["id"] == requested:
                return r
    for status in ("RUNNING", "NEEDS_WORK", "BLOCKED", "WAITING_APPROVAL",
                   "INTERRUPTED", "PENDING"):
        for r in records:
            if r["status"] == status:
                return r
    return records[0] if records else None


def _verification(task_id: str) -> dict:
    """Never manufacture a PASS if the v3.1 Acceptance Gate isn't available."""
    if not TASK_ID.fullmatch(task_id):
        return {"verdict": "UNKNOWN", "stage": "—", "sha": ""}
    try:
        with cli.managed_readonly_connect() as db:
            last = db.execute(
                "SELECT stage, verdict, commit_sha FROM acceptance_stage_results "
                "WHERE task_id=? ORDER BY updated_at DESC LIMIT 1", (task_id,)
            ).fetchone()
            if last is None:
                return {"verdict": "NOT VERIFIED", "stage": "—", "sha": ""}
            return {"verdict": str(last["verdict"])[:40],
                    "stage": str(last["stage"])[:40],
                    "sha": str(last["commit_sha"])[:12]}
    except (sqlite3.Error, ValueError, OSError):
        return {"verdict": "NOT VERIFIED", "stage": "—", "sha": ""}


def home_html(csrf: str, records: list[dict], *, focus: str | None = None) -> tuple[str, int | None]:
    """Return HTML and explicitly configured iframe port for a restricted CSP."""
    active = _pick_task(records, focus)
    waiting = [r for r in records if r["status"] == "WAITING_APPROVAL"]
    running = sum(r["status"] == "RUNNING" for r in records)
    failures = sum(r["status"] in ("NEEDS_WORK", "BLOCKED", "FAILED") for r in records)
    port = None
    if active:
        try:
            port = preview_port(active["id"])
        except (OSError, ValueError, TypeError):
            port = None
    verification = _verification(active["id"]) if active else {"verdict": "—", "stage": "—", "sha": ""}
    accepted_final = bool(active and active["status"] == "DONE" and
                          verification["verdict"] == "ACCEPTED" and
                          verification["stage"] == "final")
    worker = worker_state()
    result = (
        '<section class="command-intro" id="workspace"><div class="command-headline">'
        '<p class="eyebrow">ITEM SPACE AI / UNIFIED COMMAND / YEAR 2500</p>'
        '<h1>كل شغلك. <em>مركز قيادة واحد.</em></h1>'
        '<p>المهام، قراراتك، المعاينة الحية، والوكلاء — بدون صفحات متكررة أو معلومات شكلية.</p>'
        '</div><a class="command-new-btn" href="#mission-intake">＋ مهمة جديدة</a></section>'
        '<div class="command-grid"><nav class="command-rail" aria-label="أقسام مركز القيادة">'
        '<span class="rail-caption">NAVIGATION</span>'
        '<a class="rail-active" href="#workspace"><span class="rail-icon">◈</span> القيادة</a>'
        '<a href="#missions"><span class="rail-icon">▤</span> المهام</a>'
        '<a href="#approvals"><span class="rail-icon">◇</span> الموافقات</a>'
        '<a href="#live"><span class="rail-icon">▣</span> المعاينة</a>'
        '<a href="#agents"><span class="rail-icon">⌘</span> الوكلاء</a>'
        '<span class="rail-divider"></span>'
        '<a href="#mission-intake"><span class="rail-icon">＋</span> إنشاء مشروع</a>'
        '</nav><div class="command-main">'
        '<section class="command-metrics" aria-label="ملخص المهام">'
        '<div class="command-metric"><span>إجمالي المهام</span><strong>'
        + str(len(records)) + '</strong></div>'
        '<div class="command-metric"><span>تنفيذ جارٍ</span><strong>'
        + str(running) + '</strong></div>'
        '<div class="command-metric priority"><span>تحتاج قرارك</span><strong>'
        + str(len(waiting)) + '</strong></div></section>'
        '<section class="command-card" id="focus" aria-labelledby="focus-title">'
        '<div class="command-card-header"><h2 id="focus-title">المهمة الحالية</h2>'
        '<span class="command-connect" id="command-connection">حالة محفوظة</span></div>'
    )
    if active:
        tid = escape(active["id"], quote=True)
        result += (
            '<div data-command-task="' + tid + '" data-accepted="'
            + ('true' if accepted_final else 'false') + '">'
            '<div class="command-focus-heading"><a href="/ideas/' + tid +">'
            + escape(active["title"]) + '</a>'
            '<span id="command-task-state" class="command-badge" data-state="'
            + ('LEGACY_DONE' if active["status"] == "DONE" and not accepted_final
               else escape(active["status"], quote=True))
            + '">' + ('DONE · غير متحقق' if active["status"] == "DONE" and not accepted_final
                     else escape(active["status"])) + '</span></div>'
            '<div class="command-focus-meta">'
            '<span class="command-chip">المرحلة: <strong id="command-task-stage">'
            + escape(active["stage"]) + '</strong></span>'
            '<span class="command-chip">ID: ' + tid + '</span>'
            '<span class="command-chip">التحقق: <strong>'
            + escape(verification["verdict"]) + '</strong></span></div>'
            '<p class="command-focus-note">' + escape(active["goal_preview"]) + '</p>'
            '<div class="command-focus-links">'
            '<a class="command-link" href="/ideas/' + tid + '">مراجعة المهمة والتقارير</a>'
            '<a class="command-link secondary" href="/studio/' + tid + '">Live Studio</a>'
            '</div></div>'
        )
        if active["status"] in ("BLOCKED", "NEEDS_WORK", "FAILED"):
            result += ('<div class="command-issue" role="status">'
                       'المهمة تحتاج معالجة. راجع تقرير القبول قبل محاولة المتابعة.</div>')
    else:
        result += (
            '<div class="command-preview-placeholder">'
            '<strong>لا توجد مهام بعد</strong>'
            '<p>ابدأ مشروعاً جديداً وسيظهر هنا مع حالته الفعلية.</p>'
            '<a class="command-link" href="#mission-intake">إنشاء أول مهمة</a></div>'
        )
    result += '</section><div class="command-working-grid">'
    result += (
        '<section class="command-card" id="live">'
        '<div class="command-card-header"><h2>المعاينة الحية</h2>'
        '<small>LOCAL DEVELOPMENT ONLY</small></div>'
        '<div class="command-preview-screen">'
    )
    if active and port is not None:
        url = "http://127.0.0.1:" + str(port) + "/"
        result += (
            '<iframe title="معاينة المشروع المحلية" src="' + escape(url, quote=True)
            + '" loading="lazy" referrerpolicy="no-referrer" '
            'sandbox="allow-scripts allow-same-origin allow-forms"></iframe>'
        )
    else:
        result += (
            '<div class="command-preview-placeholder">'
            '<span class="preview-icon" aria-hidden="true">▣</span>'
            '<strong>المعاينة غير متصلة</strong>'
            '<p>شغّل سيرفر تطوير المشروع وحدد منفذه من Live Studio. '
            'لن يتم تشغيل أي أمر تلقائياً.</p></div>'
        )
    result += '</div><div class="command-preview-actions">'
    if active:
        result += '<a class="command-link secondary" href="/studio/' + escape(active["id"],quote=True) + '">إعداد المعاينة</a>'
    else:
        result += '<a class="command-link secondary" href="#mission-intake">ابدأ مشروعك</a>'
    result += '<small>لا يوجد نشر تلقائي أو تشغيل خفي للسيرفر</small></div></section>'
    result += (
        '<section class="command-card" id="approvals" aria-labelledby="approval-center-title">'
        '<div class="command-card-header"><h2 id="approval-center-title">◈ مركز القرارات</h2>'
        '<span class="command-badge" data-state="WAITING_APPROVAL">'
        + str(len(waiting)) + ' معلّقة</span></div>'
        '<div class="command-approval-stack">'
    )
    if not waiting:
        result += (
            '<div class="command-approval-empty">✓ لا توجد موافقات معلّقة الآن.</div>'
        )
    else:
        for r in waiting:
            tid = escape(r["id"], quote=True)
            result += (
                '<article class="command-approval-item"><strong>' + escape(r["title"])
                + '</strong><p>' + escape(r["stage"])
                + ' · مراجعة إلزامية قبل المتابعة</p>'
                '<a href="/ideas/' + tid + '#task-approval">افتح القرار والتقارير ←</a></article>'
            )
    result += (
        '</div><p class="command-approval-help">لا تُنفّذ الموافقة من هذه القائمة. '
        'افحص التقارير أولاً، ثم اعتمد من صفحة المهمة.</p></section></div>'
    )
    # Keep the original Pixel Office scene, but reveal it on demand to reduce clutter.
    result += (
        '<details class="command-detail-toggle" id="agents">'
        '<summary>⌘ مكتب الـAgents — عرض مصغّر قابل للتوسيع</summary>'
        '<div class="command-detail-content"><section id="departments" aria-label="الأقسام">'
        + office_html() + '</section></div></details>'
    )
    result += (
        '<details class="command-detail-toggle" id="mission-intake">'
        '<summary>＋ إنشاء مهمة أو مشروع جديد</summary>'
        '<div class="command-detail-content"><form method="post" action="/ideas">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<div class="command-form-grid"><label for="title">اسم المشروع'
        '<input id="title" name="title" maxlength="100" placeholder="مثال: Nova Systems">'
        '</label><label for="methodology">منهجية العمل'
        '<select id="methodology" name="methodology">'
        '<option value="hybrid">Hybrid</option><option value="agile">Agile</option>'
        '<option value="traditional">Traditional</option></select></label></div>'
        '<div class="command-form-textarea"><label for="idea">وصف المهمة</label>'
        '<textarea id="idea" name="idea" required maxlength="4000" '
        'placeholder="صف الهدف والحدود، وضع المواصفات التفصيلية داخل مستودع المشروع...">'
        '</textarea></div>'
        '<button type="submit" class="action command-submit">إنشاء المشروع والمهمة</button>'
        '<p class="command-footer-note">إنشاء المهمة لا يشغّل Codex بحد ذاته. '
        'Acceptance Contract مطلوب قبل البناء وفق محرك v3.1.</p></form></div></details>'
        '</div><aside class="command-inspector">'
        '<section class="command-card"><div class="command-card-header"><h2>صحة التنفيذ</h2>'
        '<small>REAL EVIDENCE</small></div>'
        '<div class="command-health">'
        '<div class="command-health-line"><span>آخر Worker state</span><strong>'
        + escape(worker[:40]) + '</strong></div>'
        '<div class="command-health-line"><span>آخر نتيجة قبول</span><strong'
        + (' class="ok"' if verification["verdict"] == "ACCEPTED" else ' class="warn"')
        + '>' + escape(verification["verdict"]) + '</strong></div>'
        '<div class="command-health-line"><span>مرحلة التحقق</span><strong>'
        + escape(verification["stage"]) + '</strong></div>'
        '<div class="command-health-line"><span>Commit متحقق</span><strong>'
        + escape(verification["sha"] or "—") + '</strong></div>'
        '<div class="command-health-line"><span>تحتاج إصلاح</span><strong>'
        + str(failures) + '</strong></div></div>'
        '<p class="command-footer-note">غياب دليل تحقق يُعرض NOT VERIFIED، '
        'ولا يُعتبر اختباراً ناجحاً. Worker state هي آخر حالة مُسجلة فقط.</p>'
        '</section>'
        '<section class="command-card" id="missions">'
        '<div class="command-card-header"><h2>المشاريع والمهام</h2>'
        '<small>' + str(len(records)) + ' TASKS</small></div>'
        '<div class="command-mission-list">'
    )
    if not records:
        result += '<p class="command-card-sub">لا توجد مشاريع مسجلة.</p>'
    for r in records:
        tid = escape(r["id"],quote=True)
        selected = ' selected' if active and active["id"] == r["id"] else ''
        result += (
            '<a class="' + selected.strip() + '" href="/?task=' + tid + '#focus">'
            + escape(r["title"]) + '<small>' + escape(r["status"]) + ' · '
            + escape(r["stage"]) + '</small></a>'
        )
    result += (
        '</div></section>'
        '<section class="command-card"><h2>الإجراء التالي</h2>'
        '<p>راجع الموافقات والقبول أولاً. لا تدمج أو تنشر من لوحة المراقبة.</p>'
        '<a class="command-link secondary" href="/office">فتح المكتب بكامل الشاشة</a>'
        '</section></aside></div>'
        '<script src="/command.js" defer></script>'
    )
    return result, port


def detail_html(csrf: str, r: dict) -> str:
    """Keep current approval routes intact, group verbose tools, outputs, audit."""
    tid = escape(r["id"], quote=True)
    status = escape(r["status"], quote=True)
    result = (
        '<div class="command-detail-page">'
        '<div class="command-intro"><div class="command-headline">'
        '<p class="eyebrow">UNIFIED COMMAND / MISSION DETAIL</p>'
        '<h1>قرارات المهمة <em>ومخرجاتها</em></h1>'
        '<p>مراجعة التقارير أولاً، ثم اعتماد الخطوة المطلوبة.</p>'
        '</div><a class="command-new-btn" href="/">مركز القيادة</a></div>'
        + task_hero(r) + stage_track(r) + approval_panel(csrf, r)
        + '<div class="command-focus-links"><a class="command-link" href="/studio/' + tid
        + '">فتح Live Studio</a>'
        '<a class="command-link secondary" href="/#approvals">مركز الموافقات</a></div>'
        '<section class="command-card" style="margin-top:15px">'
        '<div class="command-card-header"><h2>ملخص المهمة</h2>'
        '<span class="command-badge" data-state="' + status + '">' + status + '</span></div>'
        '<p class="command-subline">المرحلة التالية: <strong>' + escape(r["next_stage"]) + '</strong></p>'
        '<p class="command-subline">المستودع المحلي: <code>' + escape(r["project"]) + '</code></p>'
        '<details class="command-detail-toggle" style="margin-top:12px">'
        '<summary>وصف المهمة الكامل</summary><div class="command-detail-content">'
        '<pre>' + escape(r["goal"]) + '</pre></div></details>'
    )
    if r["error"]:
        result += '<div class="command-issue" role="status">' + escape(r["error"]) + '</div>'
    result += '</section>'
    result += (
        '<h2 id="reports" style="font-size:16px;margin:25px 0 10px">التقارير والتحقق</h2>'
    )
    if not r["outputs"]:
        result += (
            '<section class="command-card"><p class="command-card-sub">'
            'لم تُسجّل تقارير مراحل بعد. غياب التقرير ليس نجاحاً.</p></section>'
        )
    for item in r["outputs"]:
        result += (
            '<details class="command-detail-toggle"><summary>مرحلة: '
            + escape(item["stage"]) + '</summary>'
            '<div class="command-detail-content"><pre>'
            + escape(item["content"]) + '</pre></div></details>'
        )
    result += (
        '<details class="command-detail-toggle" id="project-tools">'
        '<summary>أدوات إضافية — بحث وتسويق وفحص GitHub</summary>'
        '<div class="command-detail-content">'
        '<section class="panel"><div class="panel-head"><h3>أدوات المشروع</h3>'
        '<span class="tag">OPTIONAL</span></div>'
        '<p class="hint">أدوات مساعدة؛ لا تنشر ولا تعتمد النتائج تلقائياً.</p>'
        '<form method="post" action="/ideas/' + tid + '/research">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<label for="research-query">بحث GitHub Open Source</label>'
        '<input id="research-query" name="query" maxlength="150" '
        'placeholder="e.g. booking open source">'
        '<button class="action" type="submit">بحث الرخص والمشاريع</button></form>'
        '<form method="post" action="/ideas/' + tid + '/marketing">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<button class="action" type="submit">تجهيز مسودة تسويق</button></form>'
        '<form method="post" action="/ideas/' + tid + '/github-preflight">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<button class="action" type="submit">فحص جاهزية GitHub PR</button></form>'
        '</section></div></details>'
        '<details class="command-detail-toggle" id="audit-events">'
        '<summary>سجل الأحداث (Audit Log)</summary>'
        '<div class="command-detail-content"><pre>'
    )
    for item in r["events"]:
        result += escape(item["ts"] + "  " + item["event"] + "  "
                         + item["info"][:180]) + "\n"
    return result + '</pre></div></details></div>'
