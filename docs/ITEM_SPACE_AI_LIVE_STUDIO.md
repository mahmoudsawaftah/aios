# Item Space AI Live Studio — v0.1 (local-only, preview + monitor)

## Overview
The dedicated Studio opens from a task's **"Live Studio"** link or at:
\`http://127.0.0.1:8765/studio/<task-id>\`.

This is a Replit-inspired local **read-only monitoring and development preview panel**.
The feature does **not** include a terminal, full IDE, code editing, automatic app
bootstrapping, or a cloud-hosted preview.

### Features
- Embedded iframe preview of an **explicitly supplied loopback-only developer port**.
- Same-origin JSON task status and stage monitoring, polling every 3s while the tab is visible.
- Actual event history and the end of stage reports, without initiating any model call.
- Names of tracked, non-sensitive repository files (not their contents).
- Global worker status from local heartbeat, and a link to the real approval panel.
- Browser application preview does not mean the app was deployed.

### Safety and limitations
- Requires a **separately running developer server** for the selected project.
- The preview port must be 1024–65535 and cannot be the Item Space AI console port.
  It is always \`http://127.0.0.1:<port>/\`. No arbitrary URLs, hostname inputs,
  remote deployments, tunnels, or automatic process starts.
- The iframe uses sandbox attributes and an exact frame-src Content Security Policy.
  It can execute code from the *chosen local development server*. Only preview
  trusted projects using local test data, never real production credentials.
- Changing preview port writes only \`.factory-runtime/studio-previews.json\`;
  it does not modify tasks, approvals, the schema, or project source code.
- Never run the general worker as a prerequisite for preview. The worker may
  execute existing pending tasks; use a task-specific execution workflow separately.
- The worker heartbeat is **global**, not a per-task execution signal.
- Source code contents are not exposed. Some file names are intentionally omitted.
- This is a local development feature, not an internet-shareable Replit clone.

### Review/test prior to activation
The UI is developed on its own branch. Do **not** pull this code into the local
working directory while Codex is editing it or a task is in progress.

On a separate checkout, run:

\`\`\`powershell
python -m unittest discover -s tests -p "test_*.py" -v
python -m factory.console --port 8877 --open-browser
\`\`\`

Use a disposable local app server on a different port, select that port in Studio,
and confirm task status updates and iframe rendering. Check the browser console for
CSP and app-server \`X-Frame-Options\` / frame-ancestors restrictions. Note that apps
can prohibit embedding in iframes; use the "open in new tab" link in that case.

### Next iterations (not implemented yet)
1. Secure per-project dev-server lifecycle with explicit start/stop approval,
   resource limits, process groups and command allowlists.
2. Structured logs from app server process, staged diff, lint and test streams.
3. Real file tree/code viewer with path validation, and eventually editor with
   change review, without exposing secrets.
4. Screenshots, responsive device presets, and visual feedback.
5. Agent/meeting visualizations grounded in persisted actual workflow events.

## Launch safely while another task is running (Windows)

Keep the active checkout `C:\Users\ENG_Mahmoud\Documents\aios` unchanged.

Clone `feat/item-space-ai-live-studio` into a **different directory**, then
double-click `LAUNCH_LIVE_STUDIO_READONLY.cmd`. The launcher:

1. Runs the full Python test suite in the separate checkout and stops on failure.
2. Opens `http://127.0.0.1:8877/`, using the original factory's SQLite
   database in read-only mode so you can see **real, current tasks**.
3. Keeps project creation, approval forms, research, marketing and worker
   execution **disabled** in this preview.
4. Allows only preview-port preference, stored in this separate checkout's
   `.preview-runtime/studio-previews.json`.

The preview browser is NOT a production deployment, does not start a dev server,
and does not stop the active worker when closed. Do not clone on top of the
running AIOS checkout. Do not copy source code into the active directory while
the worker is using it.
