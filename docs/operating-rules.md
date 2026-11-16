# Operating Rules

Twenty foundational rules that keep Moe's environment clean, safe, and reliable. Every rule includes its **Why**, because a rule without a reason gets abandoned.

---

## Writing Things Down

### 1. Fix the record in the same turn as discovery
- **Rule**: Whenever you discover a correction, new constraint, or broken assumption, update the memory file and documentation in that exact turn.
- **Why**: An update that lives only in a chat response is forgotten the moment the window closes. The next session will start from the stale premise and repeat the mistake.

### 2. Update every surface that carries the claim
- **Rule**: When a fact changes, update the memory file, the `MEMORY.md` index line, the directive, the script comments, and the vault note.
- **Why**: Updating only one surface leaves stale contradictory claims on other surfaces, causing agents to produce conflicting results.

### 3. Mark superseded premises explicitly
- **Rule**: Mark superseded notes explicitly and repoint active links. Request approval before deleting or moving user data.
- **Why**: Leaving discredited notes in place allows future agents to cite them as valid evidence.

### 4. Search for contradictions before you finish
- **Rule**: Before completing a documentation update, check related files to ensure you haven't asserted contradictory requirements.
- **Why**: Internal contradictions in project guidelines confuse both human developers and language models.

### 5. Name what you updated
- **Rule**: At the end of every task that changed files, list the exact files that were modified.
- **Why**: Moe needs to know exactly what was written to his disk so he can maintain trust in the system.

---

## Where Things Go

### 6. Place files in their designated home
- **Rule**: Control reports belong in `output/`, scratch in `raw/`, and product code and client deliverables in their independent external product workspace. External vault and communications data require explicit authorization.
- **Why**: Clear boundaries prevent code repositories from being polluted with temporary scratch files or confidential client messages.

### 7. Never leave loose files in root directories
- **Rule**: Keep root folders clean. Never drop scripts, markdown dumps, or screenshots directly into `aios/` or `moevault/`.
- **Why**: Cluttered root directories make it impossible to tell what is active infrastructure versus throwaway scrap.

### 8. Never produce a deliverable directly from a scratch directory
- **Rule**: Move working data into a permanent project path before generating the final deliverable.
- **Why**: If you generate an output from a scratch folder that gets deleted, the deliverable cannot be audited, reproduced, or regenerated later.

### 9. One idea per file
- **Rule**: One fact per memory note, one procedure per directive, one project per vault note.
- **Why**: Files covering multiple distinct topics are hard to index, link, and update cleanly.

---

## Working Safely

### 10. Confirm before anything irreversible
- **Rule**: Never delete files, force-push git branches, drop database tables, or overwrite configurations without explicit human confirmation.
- **Why**: Safety beats speed every single time.

### 11. Change one thing at a time when risky
- **Rule**: When migrating infrastructure or updating build tools, test incremental changes alongside the working baseline before cutting over completely.
- **Why**: Bundling five risky changes together makes troubleshooting impossible when something breaks.

### 12. Verify against live state, not stale documentation
- **Rule**: Always run a check command (e.g. `git status`, `node -v`, API queries) to verify current reality instead of trusting old notes.
- **Why**: Code and cloud environments change independently of documentation.

### 13. Use the access you have
- **Rule**: If a CLI or API tool exists, query the system directly instead of asking Moe to manually look things up in a browser.
- **Why**: The agent's role is to reduce Moe's cognitive load, not assign him manual research tasks.

### 14. Scripts must be paste-safe
- **Rule**: Never write commands with arbitrary line breaks that fail when pasted into PowerShell. Save complex workflows as files in `execution/` and execute the file.
- **Why**: Broken interactive commands can partially execute and leave the terminal in a broken state.

### 15. Verify before claiming done
- **Rule**: Execute the test or validation command, read the actual terminal output, and confirm success before declaring a task finished.
- **Why**: Assuming code works without running it leads to embarrassing regressions.

---

## Keeping It Tidy Over Time

### 16. Check `execution/` before writing a new script
- **Rule**: Always search existing folders in `execution/` before creating a new helper.
- **Why**: Reusing existing tools prevents duplicate scripts from drifting apart.

### 17. No new files unasked
- **Rule**: Extend an existing document when appropriate rather than creating duplicate parallel notes.
- **Why**: Proliferation of redundant files degrades search precision.

### 18. Archive, don't delete
- **Rule**: When a client contract or university project finishes, move its vault note to `archive/` with a note on the outcome. Keep the repo intact.
- **Why**: Past work and lessons learned are valuable references for future freelance gigs.

### 19. Every project has a remote
- **Rule**: Each external project needs an owner-approved remote and recovery plan. A Git remote does not protect uncommitted files, runtime state, credentials or databases. Do not publish automatically.
- **Why**: Work that exists only on local disk is one hardware failure or corrupted sector away from being lost forever.

### 20. Review changes before publication
- **Rule**: End modifying sessions with verified diffs and evidence. Commit, push and publication require explicit owner authorization; never run the legacy sync helper automatically.
- **Why**: Review preserves repository boundaries and approval gates.
