# AIOS Software Factory v2 — Architecture and Operating Contract

## Goal
Build a **supervised, restartable AI software delivery system** on a Windows/WSL2 developer workstation. The owner defines the goals, reviews sensitive decisions and approves production releases. The agents perform repeatable, auditable work in **separate product repositories**.

## Boundaries
- **Control repository:** AIOS holds roles, policies, state machine, process documents and checks; it does NOT hold products or secrets.
- **Product repositories:** one Git repo per product, separate working trees and branches. Post-planning stages run in a task-isolated Git worktree on `aios/task-ID` branch; the project must have a clean committed baseline before coding. Never keep client code in `aios/projects`.
- **Run state:** `.factory-runtime/state.sqlite3` (WAL), per-task events and output artifacts, intentionally Git-ignored. Local state must be backed up separately; GitHub alone is NOT a task-state backup.
- **Model runtime:** Codex CLI in sandbox; no privileged shell bypass, no automated pushes, merges or deployments. Real commands require a working `codex login` and an available model.
- **Human gates:** `build` gate after planning; `release` signoff after release planning. Approvals are recorded and do not trigger deployment.

## Stages
1. `discovery` — problem, stakeholders, evidence and scope.
2. `requirements` — user stories, specification and acceptance criteria.
3. `architecture` — threat model, ADRs, interface contracts, nonfunctional constraints.
4. `backlog` — prioritized slices, milestones, Definition of Done.
5. `implementation` — owner-approved coding work in a sandbox.
6. `qa` — automated checks and failure analysis.
7. `security` — independent read-only risk review.
8. `release_plan` — staging/release/rollback evidence and go/no-go package.

## Execution semantics (current MVP)
- Python stdlib + SQLite durability: task state stored at each stage boundary.
- Two attempts per stage by default; failures pause instead of retrying forever.
- OS lock prevents two runners controlling the same task on **one host**. No distributed scheduler or parallel worker pool is implemented yet.
- A `run-pending` command can be scheduled by the owner for unattended restart; no scheduler is installed automatically. On process restart, an interrupted `RUNNING` stage is re-executed **from the beginning**, not exactly resumed at the last model token. This means repeated side effects may occur within the project. The implementation role prohibits destructive operations, and incremental commits/clean worktrees are recommended for production use.
- An `--ask-for-approval never` noninteractive invocation does NOT mean arbitrary access: it runs with `read-only` or `workspace-write` sandbox. A prompt cannot enforce complete security; use an isolated Windows account/container for untrusted repositories.
- Build and release gates prevent advancement without explicit owner input. This is **not** full autonomous development or production readiness.

## Operating model
- Owner: funding, external systems, architecture baseline, production permissions.
- Product: discovery, backlog, user acceptance.
- Engineering: design, implementation, tests, security, release readiness.
- Orchestrator: durable routing, retries, audit trail and signoff enforcement.

## Next engineering milestones
- Deterministic test harness and stricter worktree diff policy.
- Staged branch/PR creation with CODEOWNERS, required checks and review gates.
- Optional Windows Task Scheduler registration, durable heartbeat and execution watchdog for auto-resume after reboot.
- Human-readable dashboard for backlog, budget, model usage, issues and evidence.
- Containerized workers, per-tool permissions, secret manager, egress policy.
- Iterative sprint loops with backlog refinement and repeated QA/security cycles (current MVP executes one pass only).

## Important limitations
This update is a **working prototype**, not a full multi-agent platform. Different named role prompts are run sequentially via a single Codex CLI worker. It does not implement true concurrent isolated agents, autonomous GitHub publishing, external service actions, application deployment, monitoring or cost enforcement.
