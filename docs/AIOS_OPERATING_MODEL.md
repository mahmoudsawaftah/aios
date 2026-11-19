# AIOS operating model for Item Space

## When to use the full flow
Use the complete flow for a new product slice, broad refactor, multi-file change, or work affecting architecture, data, tenancy, security, or release behavior. Small contained fixes may use the matching skill and direct implementation.

## Major delivery stages
1. **Discovery:** establish the current Git root, baseline, user problem, and existing evidence.
2. **Requirements:** describe actors, workflow, constraints, and testable acceptance criteria.
3. **Architecture:** assess trust boundaries, tenant isolation, data model/API impact, failure modes, and rollback for consequential choices.
4. **Backlog:** order small vertical slices and identify dependencies.
5. **Implementation:** the task request authorizes in-scope edits after material product/architecture choices are clear.
6. **QA:** inspect the code and run checks defined by the repository.
7. **Security review:** independently inspect relevant boundaries; security review is read-only unless fixes are separately requested.
8. **Release planning:** document target, evidence, risks, backup, and rollback. A release plan is not a deployment.

## Evidence rules
- A stage output is a handoff, not proof that its requirements passed.
- Acceptance criteria must map to actual code paths and meaningful tests.
- Report real check commands, exit status, and failures. A test file existing does not prove a runner executed it.
- Distinguish facts from assumptions; ask the user to decide unresolved product choices.
- Record relevant decisions and status in the existing `PLANS.md`; do not create competing plans.

## Human decisions
Routine in-scope code work may proceed from the task request. Ask the user to choose when a business outcome, MVP boundary, irreversible architecture choice, regulated-data policy, or production target is unresolved. Commit, push, merge, deploy, billing, and permission changes always need separate explicit authorization.

## Roles versus agents
The role guides in `agents/roles/` are sequential review perspectives for the primary Codex agent. They are not separate processes and do not prove parallel review occurred. Subagents may be used only when the Codex runtime actually exposes them; use them for independent work and verify their findings.
