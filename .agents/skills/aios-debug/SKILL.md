---
name: aios-debug
description: Use when investigating a bug, regression, error, or failing test. Find the root cause and reproduce it before changing code. Do not use for feature planning or routine code review.
---
1. Capture the exact symptom and expected behavior; inspect logs, failing output, and relevant code.
2. Reproduce the issue with the narrowest safe command or test. Do not modify data or production services.
3. Trace the failure to its cause and distinguish evidence from hypotheses.
4. Make the smallest in-scope fix and add a regression test when appropriate.
5. Run relevant project checks through `$aios-verify`; report what was and was not verified.
