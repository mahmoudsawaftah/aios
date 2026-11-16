# Directive: Weekly Review SOP

- **Schedule**: Every Friday afternoon (~10 minutes)
- **Goal**: Prevent drift, review authorized projects and recovery plans, verify boundaries, and document lessons without automatic publication.

---

## Execution Sequence

### Step 1: Run System Health Check
```powershell
powershell -File execution/check/Check-AiosHealth.ps1
```
- Verify:
  - Control metadata and template are present; no nested products are inspected.
  - Optional memory availability is reported without reconstructing personal notes.
  - Review root metadata separately for accidental scratch files.

### Step 2: Review Upcoming Reminders
- Open `aios/reminders/`.
- Inspect any reminders due in the coming 7 days (domain renewals, client milestone check-ins, certificate updates).
- Mark completed reminders `CLOSED`; do not delete user records without approval.

### Step 3: Check Project Git Status
- Inspect only owner-selected external projects; do not discover or operate on retired nested repositories. Review uncommitted work and recovery gaps without pushing.
- Ensure no `.env` files are untracked or unignored.

### Step 4: Graduate One Lesson to the Vault
- Look back at the week's coding sessions.
- Pick one tricky bug, configuration nuance, or client insight learned this week.
- Create a durable note in `moevault/knowledge/` or update an existing note in `moevault/projects/`.

### Step 5: Verify and Review AIOS
Run the checks in README.md, inspect the diff and summarize unresolved risks.
Never automatically run the legacy sync helper, commit or push. Request separate
owner authorization for publication or external vault writes.
