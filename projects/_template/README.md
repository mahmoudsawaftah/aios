# Project Template

Copy this folder to start a new project:
```powershell
Copy-Item -Recurse "aios/projects/_template" "aios/projects/<new-project-name>"
```

## First Steps (Before Writing Code!)
1. `cd aios/projects/<new-project-name>`
2. `git init`
3. Create a new repository on GitHub (e.g. `gh repo create <new-project-name> --private`)
4. `git remote add origin <remote-url>`
5. Perform your initial commit: `git add . && git commit -m "chore: initial scaffold from aios template"`
6. Push: `git push -u origin main`
7. Add a row to `aios/projects/INDEX.md`.
8. Create a matching vault note in `aios/vault/projects/<new-project-name>.md`.
