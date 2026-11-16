# The DOE Method: Document, Orchestrate, Execute

DOE is the core operating philosophy of `aios`. It separates work into three distinct layers to make AI agents reliable and repeatable.

---

## 1. Why DOE Exists: The Compound Error Problem

When an agent improvises every technical command from scratch, errors compound rapidly.
- If an agent has a **90% success rate** on a single isolated step, a **5-step workflow** succeeds only **59% of the time** ($0.9^5 \approx 0.59$).
- In a 10-step deployment or migration, success drops to **35%**.

The solution is simple:
1. **Push fragile, deterministic commands into tested scripts** (`execution/`).
2. **Push repeatable procedures and judgment into standard operating documents** (`directives/`).
3. **Let the agent do only routing and decision-making** (Orchestration).

```
   [ DIRECTIVE ]  (directives/)
         |
         | (Agent reads SOP, checks inputs, makes decisions)
         v
   [ ORCHESTRATOR ] (AI Agent)
         |
         | (Calls deterministic scripts with arguments)
         v
   [ EXECUTION ]  (execution/)
         |
         | (Produces structured outputs or reports failures)
         v
   [ DELIVERABLE / REPORT ] (output/)
```

---

## 2. The Three Layers

### 1. Document (`directives/`)
A Markdown SOP specifying:
- **Goal**: What outcome are we trying to achieve?
- **Inputs**: What arguments, files, or environment variables are required?
- **Execution Chain**: Which scripts in `execution/` to run, in what exact order?
- **Outputs**: Where the resulting deliverables or logs are placed.
- **Gotchas & Edge Cases**: Common failure modes discovered during previous attempts.

### 2. Orchestrate (The Agent)
The agent:
- Reads the directive.
- Validates the environment and inputs.
- Executes the scripts in order, checking return codes.
- Diagnoses errors and asks clarifying questions when reality diverges from the document.
- Never improvises complex multi-step pipelines by hand when a script exists.

### 3. Execute (`execution/`)
Deterministic scripts following standard naming conventions:
- **`recon/Recon-*.ps1`**: Read-only discovery. Gathers data, inspects status, changes nothing.
- **`check/Check-*.ps1`**: Read-only health checks. Safe to run anytime.
- **`maint/Maint-*.ps1`**: Modifies state (fixes configs, deploys, runs migrations). Always confirms before irreversible actions.
- **`util/`**: Reusable helpers, data parsers, and tool wrappers.

---

## 3. The Self-Annealing Loop

A system that does not learn from failures decays. Whenever an agent encounters an error or discovers a new constraint:

```
[ Error or New Finding ]
        │
        ▼
1. Fix the immediate problem
        │
        ▼
2. Write or update an execution script in `execution/`
        │
        ▼
3. Update the SOP in `directives/` with the new edge case
        │
        ▼
4. Record durable constraints in authorized docs; external memory requires approval
        │
        ▼
5. Verify and review standards; commit/push only with explicit owner authorization
```

> **The knowledge base is the deliverable.** A bug fix or lesson that exists only in a chat transcript did not happen. If you don't update the directives and vault memory, the next agent session will make the exact same mistake.

---

## 4. Worked Example: Generic Service Verification

Here is how an independent service verification task matures through the DOE lifecycle. Commands and dependencies come from that service, not factory defaults.

### Pass 1: Manual Improvisation (Fragile)
The agent runs one check, misses an integration test, guesses an API command and leaves readiness unverified.

### Pass 2: Scripted Execution (`execution/check/`)
We encapsulate the exact, deterministic verification commands into a single script:
`<external-product-root>/scripts/verify-readiness.ps1`.
Now, the agent runs one tested script that executes the complete verification sequence and outputs a clear PASS/FAIL summary.

### Pass 3: Full DOE System
1. **Directive**: The product's readiness SOP defines safe test inputs, preflight checks, unit/integration commands and failure handling. Configuration remains product-local.
2. **Architecture**: Record trusted server decisions, access boundaries and rollback constraints in the product's approved documentation.
3. **Evidence**: Store actual QA/security outcomes and unresolved risks; optional external notes require authorization.
4. **Result**: Any authorized role can repeat checks. Build/release approvals remain mandatory and release signoff never deploys.
