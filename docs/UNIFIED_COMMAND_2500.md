# Item Space AI v3.3 — Unified Command 2500

## Product intent

One calm operations workspace for a project owner who delegates development to AI
and approves high-impact steps. One screen answers: **what is active, what needs
my approval, what was verified, and what should happen next?**

## Design council — decisions by discipline

| Discipline | Decision |
|---|---|
| Product strategy | Focus one selected mission; show all other missions as a narrow list. |
| UX / information architecture | Replace separate decorative dashboard sections with a command rail, focus card, approvals, preview and compact inspector. |
| Visual design | Year-2500 aesthetic: deep ink surfaces, restrained cyan/mint highlights, deliberate typography, low-glare layers; no forced 3D spectacle. |
| Human factors | Large approval entry point; never approve from the global dashboard without opening evidence. |
| Accessibility | RTL layout, semantic headings, contrast-first status labels, keyboard-native details/summary, reduced-motion stylesheet, narrow-viewport stacking. |
| Frontend engineering | Python stdlib server preserved; no npm, frameworks or new dependencies. The former Pixel Office stays available inside a collapsible panel. |
| App security | Same-origin read-only polling, HTML escaping, CSRF on existing POSTs, local loopback iframe only on opted-in port, CSP enforced per page. |
| Reliability / SRE | No commands or Worker started by UI; original SQLite, task queue, Worktrees, and MCP paths unchanged. |
| QA / Acceptance | Show last persisted verdict or NOT VERIFIED; never infer PASS from an agent result or old DONE status. |

## Workspace hierarchy

1. Minimal header: identity, connection mode and 3 primary shortcuts.
2. Left command rail: focus, missions, approvals, live preview, agents, create.
3. Center: task focus + real state, embedded local preview + approval queue.
4. Inspector: last recorded Worker state, acceptance gate verdict and commit,
   short mission switcher, next step.
5. Below: Pixel Office in a single expandable panel; new mission form in a
   separate expandable panel. The form is not hidden after clicking New Mission.
6. Task details: original gate form at top; stage outputs, tools and audit
   events collapsed into separate native HTML details panels.

## Data trust boundaries

- The dashboard reads tasks from `factory.intake.list_ideas()`.
- `GET /command/state` refreshes the task, approval count/list, stored
  acceptance verdict and last recorded worker state every five seconds.
  The JSON intentionally omits full task goals, local project paths and errors.
- The acceptance summary reads `acceptance_stage_results` through
  `cli.managed_readonly_connect()` when the v3.1 fix has installed that table.
- A missing acceptance table or record means **NOT VERIFIED**, including
  historical DONE tasks. That does not retroactively alter old records.
- Stage and Worker polling are read-only. A last Worker state may be stale:
  it is deliberately labelled as the last recorded state, not live telemetry.
- A screenshot-like Pixel Office avatar is an illustration of a task state;
  it does not assert an independently running AI agent.
- An embedded local site appears only if the user previously configured a
  numeric port under Live Studio. The UI does not start a development server.
- Form `POST /ideas` still enqueues a task, not Codex execution.
- `POST /ideas/<id>/approve` is unchanged and retains owner Build/Release gates.

## Changed files in this draft

- `factory/ui_unified.py`: new visual system, centralized home/task HTML,
  optional real acceptance verdict, safe local preview and polling script.
- `factory/console.py`: lightweight adapter to new views and
  `/command.js`/`/command/state`; no
  changes to approval, worker or existing helper API endpoints.
- `factory/pixel_office.py`: pauses hidden-office rendering and polling.
- `tests/test_unified_command.py`: UX and safety regression test coverage.
- `docs/UNIFIED_COMMAND_2500.md`: design contract and release plan.

## Safe preview without touching live work

**Critical**: the owner's v3.1 False Completion fix is local commit `36ebf99`
and is NOT on this remote branch. Do not switch/reset/merge this remote branch
over the existing `C:\Users\ENG_Mahmoud\Documents\aios` checkout.

Use a separate clone of `feat/item-space-v3-3-unified-command-2500` and the
existing `LAUNCH_LIVE_STUDIO_READONLY.cmd` preview launcher from that directory.
It runs Python regression tests and starts the preview at port 8877 against the
active task DB using a read-only connection; the worker is disabled there and
mutation routes are blocked. If tests fail, the preview launcher stops.

### Windows PowerShell (separate checkout)

```powershell
$preview = Join-Path $env:USERPROFILE 'Documents\ItemSpace-Command2500-Preview'
if (Test-Path $preview) { throw 'Preview exists; inspect it before reuse' }
git clone --single-branch --branch feat/item-space-v3-3-unified-command-2500 https://github.com/mahmoudsawaftah/aios.git $preview
if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
& (Join-Path $preview 'LAUNCH_LIVE_STUDIO_READONLY.cmd') 'C:\Users\ENG_Mahmoud\Documents\aios'
```

Then open `http://127.0.0.1:8877/`.

## Release gates

1. Run full Python tests in separate checkout, including acceptance tests when
   the local v3.1 fix is eventually incorporated by review.
2. Inspect homepage with no tasks, a RUNNING task, a WAITING_APPROVAL task,
   NEEDS_WORK/BLOCKED, and historical DONE without acceptance evidence.
3. Test approval process from detail page, report access, form CSRF and origin
   restrictions on a disposable test task only.
4. Validate local iframe with a disposable dev server, plus browser errors and
   desktop/mobile widths, keyboard access and reduced motion.
5. Port or rebase ONLY the UI files onto a clean local checkout that includes
   the v3.1 acceptance fix; never remove the existing local commit or overwrite
   `.factory-runtime`, tasks or Worktrees.
6. Create a local review commit after passing tests. No push/merge/deploy without
   the owner's separate explicit acceptance of that action.

## Known limits

- This is a source branch, **not yet installed or verified on the owner's PC**.
- GitHub Actions may fail before test steps due to runner availability; do not
  infer pass without actual output.
- It is an improved project control dashboard, not a full Replit IDE, code
  editor, server manager or true live multi-agent session tracker.
- The owner should validate real server/mode behavior and report any visual
  regressions before adoption.
- Polling uses a five-second cadence and does not represent websocket streaming
  or true per-agent live process diagnostics.
