"""Read-only Live Studio for local Item Space AI projects.

Does not run developer commands, expose source file contents, or modify task state.
A preview is only an iframe for an explicitly configured local development port.
The project's dev server must be started separately by the owner/agent.
"""
from __future__ import annotations

from html import escape
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from factory import cli
from factory.intake import idea_detail
from factory.github_ops import suspicious

TASK_ID = re.compile(r"^[0-9a-f]{12}$")
MAX_CONFIG_BYTES = 65536

STUDIO_CSS = r"""
.studio-header{padding:29px 0 20px}
.studio-header h1{font-size:clamp(28px,3vw,42px);margin:8px 0}
.studio-header p{font-size:13px;color:var(--soft);margin:0}
.studio-top{display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap}
.studio-status{padding:8px 13px;border-radius:12px;background:#1d3449;border:1px solid #3b6984;font-weight:750;font-size:12px}
.studio-columns{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(290px,.75fr);gap:15px}
.studio-card{min-width:0;padding:21px;background:#101e31;border:1px solid rgba(132,176,208,.24);border-radius:18px;margin-bottom:15px}
.studio-card h2{margin:0 0 13px;font-size:16px}
.studio-card p{font-size:12px;color:#a9bad0}
.studio-viewport{background:#07121f;min-height:460px;border:1px solid #355575;border-radius:14px;overflow:hidden}
.studio-frame{width:100%;height:580px;border:none;background:#fff;display:block}
.studio-placeholder{display:grid;min-height:460px;place-content:center;text-align:center;padding:32px;color:#afc3da}
.studio-placeholder strong{font-size:22px;color:#eaf6ff}
.studio-port-form{display:flex;gap:10px;align-items:end;flex-wrap:wrap;margin:15px 0 0}
.studio-port-form label{margin:0;font-size:12px;flex:1;min-width:180px}
.studio-port-form input{width:100%;min-height:44px}
.studio-port-form button{padding:11px 18px;background:#82deda;border:0;border-radius:10px;color:#0b202b;font-weight:900;cursor:pointer;font-family:inherit}
.studio-kpis{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:0 0 15px}
.studio-kpi{padding:13px;border:1px solid #2a475b;border-radius:12px;background:#14273b}
.studio-kpi span{display:block;font-size:10px;color:#97b5c9}
.studio-kpi strong{display:block;font-size:15px;margin-top:5px;overflow-wrap:anywhere}
.studio-feed{display:grid;gap:7px;max-height:340px;overflow:auto;list-style:none;margin:0;padding:0}
.studio-feed li{padding:10px;border:1px solid #294156;border-radius:9px;color:#c1d2e5;font-size:11px;overflow-wrap:anywhere}
.studio-files{margin:0;white-space:pre-wrap;font-size:11px;max-height:290px;overflow:auto;background:#0a1727;padding:13px;border-radius:10px;border:1px solid #26435b;color:#b9d4e2}
.studio-note{font-size:11px;color:#a6bacf;margin:10px 0}
.studio-live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#89dfc8;margin-inline-end:6px}
.studio-browser-actions{display:flex;align-items:center;justify-content:space-between;gap:9px;margin-bottom:10px;flex-wrap:wrap}
.studio-open{font-size:11px;color:#a4e4eb}
.studio-layout-footer{font-size:11px;color:#a4bbd1}
@media(max-width:1000px){.studio-columns{grid-template-columns:1fr}.studio-frame{height:500px}}
@media(max-width:600px){.studio-card{padding:14px}.studio-frame{height:420px}.studio-kpis{grid-template-columns:1fr 1fr}}
"""

STUDIO_JS = r"""'use strict';
(() => {
  const root = document.querySelector('[data-live-task]');
  if (!root) return;
  const taskId = root.getAttribute('data-live-task');
  if (!/^[0-9a-f]{12}$/.test(taskId)) return;
  const select = (id) => document.getElementById(id);
  let inflight = false;
  const refresh = async () => {
    if (inflight || document.hidden) return;
    inflight = true;
    try {
      const response = await fetch('/studio/' + taskId + '/state', {cache: 'no-store'});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      if (data.id !== taskId) throw new Error('Task mismatch');
      select('studio-state').textContent = data.status;
      select('studio-stage').textContent = data.next_stage;
      select('studio-worker').textContent = data.worker_state;
      select('studio-updated').textContent = data.last_event || '—';
      const events = select('studio-events');
      events.replaceChildren();
      (data.events || []).forEach((event) => {
        const li = document.createElement('li');
        li.textContent = (event.ts || '') + ' · ' + (event.event || '') + ' · ' + (event.info || '');
        events.appendChild(li);
      });
      const outputs = select('studio-outputs');
      outputs.replaceChildren();
      (data.outputs || []).forEach((entry) => {
        const li = document.createElement('li');
        li.textContent = entry.stage + ': ' + entry.summary;
        outputs.appendChild(li);
      });
      select('studio-files').textContent = (data.files || []).join('\n') || 'No tracked files yet';
      select('studio-connection').textContent = 'متصل · تحديث تلقائي';
    } catch (_error) {
      select('studio-connection').textContent = 'الاتصال متوقف · إعادة محاولة';
    } finally {
      inflight = false;
    }
  };
  refresh();
  setInterval(refresh, 3000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
})();
"""


def _require_task(task_id: str) -> None:
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        raise ValueError("Invalid task ID.")


def _config_file() -> Path:
    return cli.STATE / "studio-previews.json"


def _read_config() -> dict:
    location = _config_file()
    if not location.is_file():
        return {}
    if location.stat().st_size > MAX_CONFIG_BYTES:
        raise ValueError("Preview configuration is too large.")
    contents = json.loads(location.read_text(encoding="utf-8"))
    return contents if isinstance(contents, dict) else {}


def preview_port(task_id: str) -> int | None:
    _require_task(task_id)
    value = _read_config().get(task_id)
    return value if type(value) is int and 1024 <= value <= 65535 else None


def save_preview_port(task_id: str, raw_port: str, *, console_port: int) -> int | None:
    """Only store a loopback port after validating the task; never start a process."""
    _require_task(task_id)
    idea_detail(task_id)
    if not isinstance(raw_port, str) or len(raw_port) > 5:
        raise ValueError("Provide a valid local port.")
    if raw_port.strip() == "":
        port = None
    elif not raw_port.isascii() or not raw_port.isdecimal():
        raise ValueError("Port must contain digits only.")
    else:
        port = int(raw_port)
        if not 1024 <= port <= 65535 or port == console_port:
            raise ValueError("Select a development port between 1024 and 65535, excluding the console port.")
    config = _read_config()
    if port is None:
        config.pop(task_id, None)
    else:
        config[task_id] = port
    target = _config_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replace; no task database mutations.
    handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".tmp",
                                         dir=target.parent, delete=False)
    try:
        with handle as f:
            json.dump(config, f, ensure_ascii=False)
        os.replace(handle.name, target)
    finally:
        if os.path.exists(handle.name):
            os.unlink(handle.name)
    return port


def tracked_paths(project_path: str, limit: int = 120) -> list[str]:
    """List safe tracked filenames only, never contents; skip symlinks and ignored dirs."""
    project = Path(project_path)
    if not project.is_dir() or not (project / ".git").exists():
        return []
    try:
        output = subprocess.run(
            ["git", "-C", str(project), "ls-files", "-z"],
            capture_output=True, timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if output.returncode != 0 or len(output.stdout) > 2_000_000:
        return []
    paths = []
    for raw in output.stdout.split(b"\x00"):
        if not raw:
            continue
        name = raw.decode("utf-8", errors="replace").replace("\\", "/")
        if name.startswith("/") or suspicious(name):
            continue
        if any(piece in (".git", "node_modules", ".venv", ".factory-runtime", "vault")
               for piece in name.split("/")):
            continue
        local = project / name
        if local.is_symlink() or not local.is_file():
            continue
        paths.append(name)
        if len(paths) >= limit:
            break
    return paths


def worker_state() -> str:
    path = cli.STATE / "worker-status.json"
    try:
        if not path.is_file() or path.stat().st_size > 32_768:
            return "NOT REPORTED"
        status = json.loads(path.read_text(encoding="utf-8"))
        state = status.get("state", "UNKNOWN")
        return str(state)[:40] if isinstance(status, dict) else "UNKNOWN"
    except (OSError, ValueError, TypeError, AttributeError):
        return "UNKNOWN"


def task_snapshot(task_id: str) -> dict:
    """Read-only snapshot for same-origin polling. No calls to Codex or workers."""
    _require_task(task_id)
    item = idea_detail(task_id)
    events = item.get("events", [])[:12]
    outputs = item.get("outputs", [])[-8:]
    return {
        "id": item["id"],
        "status": item["status"],
        "next_stage": item["next_stage"],
        "worker_state": worker_state(),
        "last_event": events[0]["ts"] if events else "",
        "events": [{"ts": e["ts"], "event": e["event"], "info": e["info"][:160]}
                   for e in events],
        "outputs": [{"stage": o["stage"], "summary": o["content"][-600:].strip()}
                    for o in outputs],
        "files": tracked_paths(item["project"]),
    }


def studio_html(csrf: str, task_id: str, *, port: int | None) -> str:
    _require_task(task_id)
    task = idea_detail(task_id)
    name = Path(task["project"].replace("\\", "/")).name
    port_display = "" if port is None else str(port)
    url = "" if port is None else f"http://127.0.0.1:{port}/"
    if port is None:
        viewport = ('<div class="studio-placeholder"><strong>معاينة المشروع</strong>'
                    '<p>حدد منفذ سيرفر التطوير المحلي لعرض الموقع هنا. '
                    'هذا لا يشغّل المشروع تلقائياً.</p></div>')
    else:
        viewport = ('<iframe class="studio-frame" title="Local project preview" loading="lazy" '
                    'referrerpolicy="no-referrer" sandbox="allow-scripts allow-same-origin allow-forms" '
                    'src="' + escape(url, quote=True) + '"></iframe>')
    return (
        '<div data-live-task="' + escape(task_id, quote=True) + '">'
        '<section class="studio-header"><div class="studio-top"><div>'
        '<p class="eyebrow">ITEM SPACE AI / LIVE STUDIO</p>'
        '<h1>شاهد مشروعك <em>وهو يتطوّر.</em></h1>'
        '<p>' + escape(name) + ' · ' + escape(task_id) + '</p></div>'
        '<span class="studio-status"><span class="studio-live-dot"></span>'
        '<span id="studio-connection">تجهيز الاتصال...</span></span></div></section>'
        '<section class="studio-kpis" aria-label="Live project status">'
        '<div class="studio-kpi"><span>حالة المهمة</span><strong id="studio-state">'
        + escape(task["status"]) + '</strong></div>'
        '<div class="studio-kpi"><span>المرحلة الحالية</span><strong id="studio-stage">'
        + escape(task["next_stage"]) + '</strong></div></section>'
        '<div class="studio-columns"><div>'
        '<section class="studio-card"><div class="studio-browser-actions">'
        '<h2>◈ Live Preview · متصفح المشروع</h2>'
        + ('<a class="studio-open" href="' + escape(url, quote=True)
           + '" target="_blank" rel="noopener noreferrer">فتح المعاينة بنافذة جديدة ↗</a>'
           if url else '') + '</div>'
        '<div class="studio-viewport">' + viewport + '</div>'
        '<form class="studio-port-form" method="post" action="/studio/'
        + escape(task_id, quote=True) + '/preview">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        '<label for="studio-preview-port">منفذ سيرفر التطوير المحلي'
        '<input id="studio-preview-port" name="port" type="number" min="1024" max="65535" '
        'value="' + escape(port_display, quote=True)
        + '" placeholder="مثال: 3000 أو 5173"></label>'
        '<button type="submit">ربط المعاينة</button></form>'
        '<p class="studio-note">المعاينة محلية 127.0.0.1 فقط. '
        'يجب تشغيل سيرفر المشروع بنفسك أو عبر وكيل التطوير، ولا يتم تشغيل أي أوامر من هنا. '
        'افرغ رقم المنفذ للحذف.</p></section>'
        '<section class="studio-card"><h2>◉ النشاط والمخرجات الحقيقية</h2>'
        '<ul class="studio-feed" id="studio-events"></ul>'
        '<h2 style="margin-top:20px">تقارير المراحل</h2>'
        '<ul class="studio-feed" id="studio-outputs"></ul></section></div>'
        '<aside><section class="studio-card"><h2>◈ مراقبة العامل</h2>'
        '<p>Worker: <strong id="studio-worker">—</strong></p>'
        '<p>آخر حدث: <strong id="studio-updated">—</strong></p>'
        '<p class="studio-note">الحالة تُقرأ من ملفات مراقبة النظام، '
        'ولا تعني أن كل قسم مرسوم لديه وكيل يعمل حالياً.</p></section>'
        '<section class="studio-card"><h2>⌘ ملفات المشروع المتتبعة في Git</h2>'
        '<pre class="studio-files" id="studio-files">جاري القراءة...</pre>'
        '<p class="studio-note">أسماء الملفات فقط. لا تُعرض محتويات ملفات المشروع أو المفاتيح السرية.</p>'
        '</section><section class="studio-card"><h2>قرارات المالك</h2>'
        '<p>الموافقات تبقى في مركز القرارات الرئيسي.</p>'
        '<a class="review-link" href="/ideas/' + escape(task_id, quote=True)
        + '#task-approval">فتح الموافقات والتقارير</a></section></aside></div>'
        '<p class="studio-layout-footer">تحديث تلقائي كل 3 ثوانٍ عند فتح التبويب. '
        'المعاينة ليست نشر إنتاج ولا تمنح صلاحية كتابة في المشروع.</p>'
        '<script src="/studio.js" defer></script></div>'
    )
