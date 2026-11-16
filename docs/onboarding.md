# Getting started with AIOS Software Factory v2

AIOS coordinates work; your products stay in their own repositories outside AIOS.
Each product chooses its own tools and configuration. The registry contains only
projects explicitly selected by the owner.

1. Read `AGENTS.md`, the architecture contract, hybrid delivery method and security
   policy linked from the main README.
2. Verify the control repository using the README's unit tests, legacy audit and
   diff check. These do not call models or publish anything.
3. Choose an existing independent product repository outside AIOS. Review its
   status, committed baseline and recovery plan before authorizing work.
4. If starting a product, optionally copy `projects/_template/` into an approved
   external location. Configure explicit policy paths; do not assume AIOS is a
   parent directory. Repository creation, remote setup and publication are separate
   owner decisions.
5. Follow `README_FACTORY.md` to create and run an authorized task. Review the
   discovery, requirements, architecture and backlog artifacts before approving
   build. Review QA, security and rollback evidence before release signoff.
6. Keep runtime state and recovery data backed up separately. Interrupted stages
   restart from the beginning; inspect possible partial effects before retrying.

Optional memory is reached through the configured vault index. If missing, report
it and continue with repository guidance. Do not recreate or modify external
personal data without authorization.

The health script checks control metadata and reports optional memory availability.
It does not inspect external or nested products. Use the README checks for full
factory migration verification. The legacy sync entry point now shows a read-only
review; it never stages, commits or pushes.
