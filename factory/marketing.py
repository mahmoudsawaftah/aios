"""Draft-only launch planning (no network or social publishing)."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re

from factory import cli

TOPICS = (
    ("تعريف الفكرة", "Reel", "Instagram"),
    ("المشكلة التي يحلها المنتج", "Carousel", "Instagram"),
    ("من يناسبه المنتج؟", "Text", "LinkedIn"),
    ("كيف نحدد نطاق النسخة الأولى", "Video", "TikTok"),
    ("نظرة على تجربة المستخدم", "Image", "Instagram"),
    ("الأسئلة الشائعة", "Carousel", "Instagram"),
    ("القيمة العملية للعميل", "Thread", "X"),
    ("كيف نحمي بيانات العملاء", "Text", "LinkedIn"),
    ("خلف الكواليس: التطوير", "Reel", "Instagram"),
    ("كيفية طلب تجربة", "Image", "Instagram"),
    ("التخصيص حسب القطاع", "Carousel", "Instagram"),
    ("خطوات البداية", "Video", "TikTok"),
    ("الميزات قيد التطوير", "Text", "LinkedIn"),
    ("دعوة لمتابعة التطورات", "Reel", "Instagram"),
)


def generate_marketing_plan(task_id: str) -> dict:
    if not isinstance(task_id, str) or not re.fullmatch(r"[0-9a-f]{12}", task_id):
        raise ValueError("Invalid task ID.")
    with cli.managed_connect() as db:
        row = cli.task(db, task_id)
        goal = row["goal"]
        project = Path(row["project"]).name
        cli.event(db, task_id, "marketing_draft_requested", "Offline calendar; no publication.")
    dest = cli.STATE / "marketing" / task_id
    dest.mkdir(parents=True, exist_ok=True)
    csv_path = dest / "content_calendar.csv"
    md_path = dest / "launch_brief.md"
    rows = []
    for idx, (topic, asset, platform) in enumerate(TOPICS, start=1):
        caption = (
            f"نطوّر {project} لمعالجة احتياج حقيقي. "
            f"موضوع اليوم: {topic}. "
            "تابع تقدم العمل، وشاركنا احتياجك لنأخذه في الاعتبار. "
            "#تطوير_برمجيات #حلول_رقمية"
        )
        rows.append({
            "day": idx * 2 - 1, "platform": platform, "type": asset,
            "topic_ar": topic, "caption_draft_ar": caption,
            "asset_status": "NOT_GENERATED",
            "publication_status": "DRAFT_REVIEW_REQUIRED",
        })
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    brief = (
        f"# Marketing draft — {project}\n\n"
        f"Task ID: {task_id}\n\n## Product brief (unverified)\n\n{goal[:2500]}\n\n"
        "## Brand and product due diligence\n\n"
        "- Verify product name, trademarks, customer segment and positioning.\n"
        "- Confirm product functionality via QA before making performance claims.\n"
        "- Review visuals, typography, translations and accessibility.\n"
        "- Check asset copyright, brand permissions and platform requirements.\n"
        "- Confirm pricing, terms, refund/cancellation policies and privacy.\n\n"
        "## Production checklist\n\n"
        "- Create original logo, design tokens, screenshots and video assets.\n"
        "- Draft landing page and onboarding content.\n"
        "- Produce and manually review 14 scheduled post drafts in content_calendar.csv.\n"
        "- Connect authorized brand-owned platform accounts only.\n"
        "- Obtain approval for each campaign before scheduling or publishing.\n"
        "- Measure clicks, signups, conversions and customer feedback.\n\n"
        "## Status\n\n**DRAFT ONLY**. No graphic, video, social post or paid campaign "
        "was rendered or published. No artificial engagement, reviews or spam.\n"
    )
    md_path.write_text(brief, encoding="utf-8")
    return {
        "task_id": task_id, "status": "DRAFT_REVIEW_REQUIRED", "posts": len(rows),
        "calendar_file": str(csv_path), "brief_file": str(md_path),
        "message": "Generated offline drafts. No social accounts connected or posts published.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate offline social marketing drafts")
    parser.add_argument("task_id")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(generate_marketing_plan(args.task_id), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        print("ERROR: " + str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
