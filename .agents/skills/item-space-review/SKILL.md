---
name: item-space-review
description: Use for an independent diff review or before commit/PR. Find correctness, security, and regression issues; do not fix unless asked.
---
1. Inspect the full diff and relevant surrounding code.
2. Prioritize actionable bugs, authorization or tenant-isolation risks, data loss, and missing tests.
3. Report findings with file and line, severity, and trigger scenario.
4. Mention relevant checks not run and any uncertainty.
5. Do not edit files unless the user requested fixes.
