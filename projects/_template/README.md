# Project Template

Copy this folder to start a new project:
```powershell
Copy-Item -Recurse "projects/_template" "C:\Dev\projects\sample-service"
```

## First Steps (Before Writing Code!)
1. Select an owner-approved external location; the command above is an example only.
2. Configure explicit policy paths in AGENTS.md; do not assume relative AIOS/vault paths.
3. Define project-local requirements, architecture, backlog and verification commands.
4. Review Git baseline, secret exclusions and recovery arrangements before implementation.
5. Add a registry entry only when the owner selects this project.
6. Follow the hybrid SDLC with build/release approvals. Repository initialization, commits, remote creation, vault edits and publication require separate authorization.
