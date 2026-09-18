# Directive: Weekly Review SOP

- **Schedule**: Every Friday afternoon (~10 minutes)
- **Goal**: Prevent drift, ensure all project work is committed and pushed, verify secret boundaries, and graduate lessons into the vault.

---

## Execution Sequence

### Step 1: Run System Health Check
```powershell
powershell -File execution/check/Check-AiosHealth.ps1
```
- Verify:
  - No projects with uncommitted changes or missing remotes.
  - All memory notes in `vault/memory/` resolve.
  - No loose files in root folders.

### Step 2: Review Upcoming Reminders
- Open `aios/reminders/`.
- Inspect any reminders due in the coming 7 days (domain renewals, client milestone check-ins, certificate updates).
- Move completed reminders to status `CLOSED` or delete them.

### Step 3: Check Project Git Status
- Ensure every project in `projects/` has pushed its active branches to its remote.
- Ensure no `.env` files are untracked or unignored.

### Step 4: Graduate One Lesson to the Vault
- Look back at the week's coding sessions.
- Pick one tricky bug, configuration nuance, or client insight learned this week.
- Create a durable note in `moevault/knowledge/` or update an existing note in `moevault/projects/`.

### Step 5: Sync & Push `aios`
```powershell
powershell -File execution/util/Sync-Aios.ps1 -Message "chore: weekly review $(Get-Date -Format 'yyyy-MM-dd')"
```
