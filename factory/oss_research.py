"""Evidence-first open-source discovery: fixed GitHub API host, no cloning/execution."""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid

from factory import cli

API_ROOT = "https://api.github.com/search/repositories"
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD"}
COPYLEFT = {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-2.0"}


def license_class(spdx: str) -> str:
    if spdx in PERMISSIVE:
        return "PERMISSIVE_CHECK_NOTICE_AND_DEPENDENCIES"
    if spdx in COPYLEFT:
        return "COPYLEFT_HUMAN_LEGAL_REVIEW"
    return "UNKNOWN_OR_CUSTOM_LEGAL_REVIEW"


def _score(entry: dict) -> int:
    # Triaging heuristic, NOT a security audit or legal opinion.
    score = 10
    if not entry.get("archived") and not entry.get("disabled"):
        score += 18
    stars = max(0, int(entry.get("stargazers_count") or 0))
    score += min(18, int(stars ** 0.42))
    pushed = entry.get("pushed_at") or ""
    try:
        dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
        months = (datetime.now(timezone.utc) - dt).days / 30
        score += 20 if months <= 6 else 12 if months <= 18 else 2
    except ValueError:
        pass
    lic = (entry.get("license") or {}).get("spdx_id") or "NOASSERTION"
    if lic in PERMISSIVE:
        score += 23
    elif lic in COPYLEFT:
        score += 8
    return min(100, score)


def search_open_source(query: str, limit: int = 6) -> dict:
    if not isinstance(query, str) or not 2 <= len(query.strip()) <= 150:
        raise ValueError("Search query must be between 2 and 150 characters.")
    if not isinstance(limit, int) or not 1 <= limit <= 10:
        raise ValueError("Limit must be 1–10.")
    params = urlencode({"q": query.strip(), "sort": "stars", "order": "desc", "per_page": limit})
    req = Request(
        API_ROOT + "?" + params,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "ItemSpaceAI-Research/3.1",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    try:
        with urlopen(req, timeout=15) as response:
            body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise ValueError("GitHub response exceeded the safe size limit.")
            data = json.loads(body.decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (403, 429):
            raise RuntimeError("GitHub search rate limit reached. Retry later; no paid API required.") from None
        raise RuntimeError("GitHub search unavailable (HTTP " + str(exc.code) + ").") from None
    except (URLError, TimeoutError, OSError, UnicodeError) as exc:
        raise RuntimeError("GitHub public search unavailable: " + type(exc).__name__) from None

    results = []
    for entry in data.get("items", [])[:limit]:
        lic = (entry.get("license") or {}).get("spdx_id") or "NOASSERTION"
        url = entry.get("html_url") or ""
        if not url.startswith("https://github.com/"):
            continue
        results.append({
            "name": str(entry.get("full_name") or "")[:150],
            "url": url, "description": str(entry.get("description") or "")[:300],
            "language": entry.get("language") or "unknown",
            "stars": int(entry.get("stargazers_count") or 0),
            "pushed_at": entry.get("pushed_at") or "",
            "archived": bool(entry.get("archived")),
            "license_spdx": lic, "license_review": license_class(lic),
            "triage_score": _score(entry),
        })
    results.sort(key=lambda r: (r["triage_score"], r["stars"]), reverse=True)
    report = {
        "query": query.strip(), "searched_at": cli.utcnow(),
        "source": "GitHub public repository search API",
        "license_notice": (
            "Metadata is not a legal audit. Inspect LICENSE, dependencies, trademarks, "
            "security, support and AGPL/GPL obligations before commercial customization."
        ),
        "results": results,
    }
    output_dir = cli.STATE / "research"
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / ("oss-" + uuid.uuid4().hex[:12] + ".json")
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["saved_to"] = str(dest)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Item Space AI: open-source discovery")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(search_open_source(args.query, args.limit), ensure_ascii=False, indent=2))
    except (RuntimeError, ValueError) as exc:
        print("ERROR: " + str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
