"""Least-privilege GitHub review publishing via the official gh CLI.

Default is read-only preflight. Explicit owner opt-in is required for any write.
Creates *private* repositories and pull requests; never merges or deploys.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from factory import cli


def run(args: list[str], *, cwd: Path | None = None, timeout: int = 90) -> str:
    done = subprocess.run(args, cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, errors="replace",
                          timeout=timeout, check=False)
    if done.returncode:
        # stderr and stdout might contain credentials or private content.
        raise RuntimeError("Command failed (" + Path(args[0]).name
                           + ", exit=" + str(done.returncode) + "). Check local command output.")
    return done.stdout.strip()


def suspicious(path: str) -> bool:
    path = path.replace("\\", "/").lower().lstrip("./")
    pieces = path.split("/")
    leaf = pieces[-1]
    if leaf == ".env.example":
        return False
    if leaf == ".env" or leaf.startswith(".env.") or leaf in (
        "id_rsa", "id_ed25519", "credentials.json", "secrets.json",
        "service-account.json", "config.local.json", "state.sqlite3",
    ):
        return True
    if any(p in ("vault", ".factory-runtime", ".aios-update-backups",
                 "recovery", "backups", ".git") for p in pieces):
        return True
    return leaf.endswith((".pem", ".p12", ".pfx", ".key", ".sqlite", ".sqlite3",
                          ".db", ".bak", ".kdbx"))


def names_to_check(repo: Path) -> list[str]:
    tracked = run(["git", "-C", str(repo), "ls-files", "-z"]).split("\0")
    status = run(["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard", "-z"]).split("\0")
    return [n for n in tracked + status if n]


def _worktree(row) -> Path:
    original = Path(row["project"])
    location = original.parent / ".aios-worktrees" / (
        original.name + "-" + row["id"])
    if not location.is_dir() or not cli.is_git_repository(location):
        raise ValueError("No task worktree found. Complete the approved implementation first.")
    if location.resolve() == original.resolve():
        raise ValueError("Refusing to change the original project checkout.")
    return location


def preflight(task_id: str) -> dict:
    if not isinstance(task_id, str) or not re.fullmatch(r"[0-9a-f]{12}", task_id):
        raise ValueError("Invalid task ID.")
    with cli.managed_connect() as db:
        row = cli.task(db, task_id)
        is_complete = row["stage_idx"] >= len(cli.STAGES)
        gates = [r["gate"] for r in db.execute(
            "SELECT gate FROM approvals WHERE task_id=?", (task_id,))]
    project = cli.project_path(row["project"])
    flagged = [n for n in names_to_check(project) if suspicious(n)]
    has_gh = shutil.which("gh") is not None
    worktree = None
    worktree_flagged = []
    try:
        worktree = _worktree(row)
        worktree_flagged = [n for n in names_to_check(worktree) if suspicious(n)]
    except ValueError:
        pass
    remote = run(["git", "-C", str(project), "remote"]).splitlines()
    return {
        "task_id": task_id, "project": str(project),
        "worktree": str(worktree) if worktree else None,
        "pipeline_complete": is_complete,
        "build_approved": "build" in gates,
        "release_approved": "release" in gates,
        "gh_cli_installed": has_gh,
        "has_origin": "origin" in remote,
        "suspicious_files": sorted(set(flagged + worktree_flagged))[:30],
        "ready_for_private_pr": (is_complete and "build" in gates
                                 and worktree is not None and has_gh
                                 and not flagged and not worktree_flagged),
        "warning": (
            "Filename screening is NOT a secret scanner. Review content and test "
            "results before publishing. No GitHub write has occurred."
        ),
    }


def publish_private_pr(task_id: str) -> dict:
    if os.environ.get("AIOS_ALLOW_GITHUB_PR") != "1":
        raise PermissionError("Owner must explicitly set AIOS_ALLOW_GITHUB_PR=1.")
    info = preflight(task_id)
    if not info["ready_for_private_pr"]:
        raise ValueError("Preflight not ready. Inspect blockers and QA evidence.")
    with cli.managed_connect() as db:
        row = cli.task(db, task_id)
        project = Path(row["project"])
    worktree = Path(info["worktree"])
    # Explicit owner action, limited to a separate task worktree and a private PR.
    account = run(["gh", "api", "user", "--jq", ".login"], timeout=25)
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", account):
        raise RuntimeError("GitHub CLI returned an invalid account name.")
    repository_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", project.name)[:80].strip(".-")
    if not repository_name:
        raise ValueError("Invalid repository name.")
    full_name = account + "/" + repository_name
    if info["has_origin"]:
        existing = run(["git", "-C", str(project), "remote", "get-url", "origin"])
        # Refuse unknown hosts or mismatched repositories.
        expected_https = "https://github.com/" + full_name + ".git"
        expected_ssh = "git@github.com:" + full_name + ".git"
        if existing.rstrip("/") not in (expected_https, expected_https[:-4],
                                          expected_ssh, expected_ssh[:-4]):
            raise ValueError("Existing origin does not match the authenticated GitHub owner/repo.")
    else:
        run(["gh", "repo", "create", full_name, "--private", "--source",
             str(project), "--remote", "origin", "--push"], timeout=120)
    if run(["gh", "repo", "view", full_name, "--json", "isPrivate",
            "--jq", ".isPrivate"], timeout=30).strip().lower() != "true":
        raise ValueError("Refusing to publish to a non-private repository.")
    # Pre-commit check is not a substitute for scanning contents.
    run(["git", "-C", str(worktree), "diff", "--check"])
    if any(suspicious(n) for n in names_to_check(worktree)):
        raise ValueError("New suspicious file detected after preflight.")
    run(["git", "-C", str(worktree), "add", "-A"])
    run(["git", "-C", str(worktree), "diff", "--cached", "--check"])
    branch = run(["git", "-C", str(worktree), "branch", "--show-current"])
    if branch != "aios/task-" + task_id:
        raise ValueError("Unexpected task branch; no push.")
    changed = run(["git", "-C", str(worktree), "diff", "--cached", "--name-only", "-z"])
    if any(suspicious(n) for n in changed.split("\0") if n):
        raise ValueError("Staged changes include sensitive-looking files.")
    if changed:
        run(["git", "-C", str(worktree), "commit", "-m",
             "feat: implement AIOS task " + task_id], timeout=60)
    run(["git", "-C", str(worktree), "push", "-u", "origin", branch], timeout=120)
    # Idempotent PR selection if already created.
    check = subprocess.run(["gh", "pr", "view", branch, "--repo", full_name,
                            "--json", "url", "--jq", ".url"],
                           capture_output=True, text=True, timeout=35, check=False)
    if check.returncode == 0 and check.stdout.strip().startswith("https://github.com/"):
        url = check.stdout.strip()
    else:
        url = run(["gh", "pr", "create", "--repo", full_name, "--base", "main",
                   "--head", branch, "--title", "AIOS task " + task_id,
                   "--body", "AIOS-generated implementation for owner review. "
                   "Verify tests, secrets, security and license obligations before merge."],
                  cwd=worktree, timeout=90)
    with cli.managed_connect() as db:
        cli.event(db, task_id, "github_pr_created", url[:300])
    return {"task_id": task_id, "private_repo": full_name, "pull_request": url,
            "merged": False, "deployed": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Item Space AI: private GitHub review publishing")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("task_id")
    p = sub.add_parser("publish-private-pr")
    p.add_argument("task_id")
    args = parser.parse_args(argv)
    try:
        result = preflight(args.task_id) if args.cmd == "preflight" else publish_private_pr(args.task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, PermissionError, OSError) as exc:
        print("ERROR: " + str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
