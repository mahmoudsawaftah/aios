---
name: aios-verify
description: Use before saying a code task is complete or before commit/PR. Discover and run the project's real lint, typecheck, tests, and build checks. Do not assume commands from another project.
---
1. Read the target project's AGENTS.md, package scripts or equivalent, and CI configuration.
2. Select checks relevant to the change. Use exact commands defined by that project; do not copy generic commands blindly.
3. Run checks in a useful order and capture actual exit status and output. Stop to diagnose failures.
4. Report each check as passed, failed, or not run, with the reason. Never claim a check passed without its result.
5. If a check is unavailable or unsafe, say so and identify the unverified area.
