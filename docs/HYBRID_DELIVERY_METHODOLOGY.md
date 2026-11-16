# Hybrid Agile + Traditional Delivery

**Traditional (predictive)** is best for fixed contracts, regulatory requirements, architectural invariants and irreversible approvals. **Agile** is best for implementation, feedback and uncertain requirements. **Hybrid** combines an approved baseline with iterative delivery.

| Phase | Predictive control | Agile iteration | Required evidence |
|---|---|---|---|
| Discovery | business case, charter | discovery hypotheses | signed scope / assumptions |
| Requirements | traceability and constraints | backlog, user stories | Given/When/Then acceptance |
| Architecture | ADR baseline, threat model | architecture runway, spike | risks, contracts, ADRs |
| Planning | WBS, milestones, change control | sprint planning and estimation | dependencies and DoD |
| Build | approved change request if baseline changes | small vertical slices | commits/diffs and review |
| Verification | formal test plan / traceability | CI, regression, exploratory tests | actual test logs |
| Release | go/no-go, rollback signoff | review and retrospectives | checklist + owner approval |

**Recommendation:** methodology `hybrid` as default. Lock only expensive-to-reverse decisions (tenant boundaries, payment handling, compliance, data retention). Allow iterative UX and feature scope within an approved MVP. Changes beyond architecture/scope baseline become explicit decision requests.

## Definition of Done for a user story
- Testable requirement with acceptance criteria and observable outcome.
- Security and tenant isolation checked when relevant.
- Code reviewed, automated tests run, failures documented.
- Documentation, migration and rollback instructions updated.
- No secrets or customer data committed; deployment done only after owner signoff.

## Evidence checkpoint (every stage)
Each agent produces a Markdown handoff naming decisions, files changed, tests actually run, blockers and next-stage actions. A stage may be **done with gaps** but must not claim unsupported quality.
