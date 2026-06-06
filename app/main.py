#!/usr/bin/env python3
"""
BTU HiWi Outreach Agent — Full Pipeline Orchestrator (v2)
Run: python main.py
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def check_prerequisites():
    missing = []
    if not Path("data/transcript.pdf").exists():
        missing.append("data/transcript.pdf  (upload your BTU transcript PDF)")
    if not Path(".env").exists():
        missing.append(".env  (create with ANTHROPIC_API_KEY=...)")
    if not Path("data/cv_profile.json").exists():
        missing.append("data/cv_profile.json  (run step 0 setup)")
    if missing:
        print("Missing prerequisites:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def main():
    check_prerequisites()

    # Step 0: Hunt for open HiWi positions (run first so scorer can use results)
    print_separator("Step 0: HiWi job hunter")
    from agents.job_hunter import run_job_hunter
    positions = await run_job_hunter()
    with open("data/open_positions.json", "w") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)
    log(f"Found {len(positions)} open HiWi positions")

    # Step 1: Parse transcript
    print_separator("Step 1: Parsing transcript")
    from agents.parser import parse_btu_transcript
    courses = parse_btu_transcript("data/transcript.pdf")
    with open("data/courses.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    log(f"Found {len(courses)} courses")

    # Step 2: Scrape transcript professors
    print_separator("Step 2: Finding transcript professors")
    from agents.scraper import run_scraper
    transcript_profs = await run_scraper(courses)
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(transcript_profs, f, ensure_ascii=False, indent=2)
    log(f"Found {len(transcript_profs)} transcript professors")

    # Step 3: Profile + grant detection
    print_separator("Step 3: Profiling + grant detection")
    from agents.profiler import run_profiler
    transcript_profs = await run_profiler(transcript_profs)
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(transcript_profs, f, ensure_ascii=False, indent=2)

    # Step 4: University-wide discovery
    print_separator("Step 4: University-wide discovery")
    from agents.discovery import discover_all_professors
    existing_names = {p["name"] for p in transcript_profs}
    new_profs = await discover_all_professors(existing_names)
    all_professors = transcript_profs + new_profs
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)
    log(f"Total: {len(all_professors)} professors")

    # Profile new professors too
    all_professors = await run_profiler(all_professors)
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)

    # Step 5: Language detection (before scoring and drafting)
    print_separator("Step 5: Language detection")
    from agents.language_agent import run_language_detection
    all_professors = run_language_detection(all_professors)
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)

    # Step 6: 5-signal fit scoring
    print_separator("Step 6: Fit scoring (5 signals)")
    from agents.matcher import compute_fit_score
    with open("data/cv_profile.json") as f:
        cv_profile = json.load(f)
    with open("data/open_positions.json") as f:
        open_positions = json.load(f)

    # Score anyone with a research summary OR an email + a real course connection.
    to_score = [p for p in all_professors
                if (p.get("research_summary") or p.get("email") or p.get("source_courses"))
                and not p.get("relevance_breakdown")]
    for i, prof in enumerate(to_score):
        log(f"  [{i+1}/{len(to_score)}] Scoring {prof['name'][:40]}")
        try:
            compute_fit_score(prof, cv_profile, open_positions)
        except Exception as e:
            prof["relevance_score"] = 0
            with open("data/errors.log", "a") as f_:
                f_.write(f"[main/scorer] {prof['name']}: {e}\n")
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)

    # Step 7: Email drafting (German + English)
    print_separator("Step 7: Drafting emails")
    from agents.drafter import draft_email
    # Draft for anyone we can actually reach (has an email); the course taken is the hook.
    to_draft = [p for p in all_professors
                if p.get("email") and not p.get("email_draft")]
    for i, prof in enumerate(to_draft):
        log(f"  [{i+1}/{len(to_draft)}] {prof['name'][:40]} [{prof.get('email_language','en')}]")
        try:
            prof["email_draft"] = draft_email(prof, cv_profile)
        except Exception as e:
            prof["email_draft"] = ""
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)

    # Step 8: Quality review (with one retry)
    print_separator("Step 8: Quality review")
    from agents.reviewer import run_reviewer
    all_professors = run_reviewer(all_professors, cv_profile)
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)

    # Step 9: Follow-up generation
    print_separator("Step 9: Follow-up generation")
    from agents.followup import run_followup_generator
    all_professors = run_followup_generator(all_professors)
    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(all_professors, f, ensure_ascii=False, indent=2)

    # Step 10: Write output sheet
    print_separator("Step 10: Writing spreadsheet")
    from agents.sheet_writer import write_sheet
    output_path = write_sheet(all_professors)

    # Summary
    print_separator("Pipeline complete")
    high  = sum(1 for p in all_professors if (p.get("relevance_score") or 0) >= 60)
    mid   = sum(1 for p in all_professors if 30 <= (p.get("relevance_score") or 0) < 60)
    de    = sum(1 for p in all_professors if p.get("email_language") == "german" and p.get("email_draft"))
    en    = sum(1 for p in all_professors if p.get("email_language") == "english" and p.get("email_draft"))
    flagged = sum(1 for p in all_professors if p.get("status") == "needs_manual_review")
    jobs  = len(open_positions)

    print(f"""
  Total professors:          {len(all_professors)}
  Open HiWi positions found: {jobs}
  High fit (≥60/100):        {high}
  Medium fit (30–59):        {mid}
  German emails drafted:     {de}
  English emails drafted:    {en}
  Flagged for manual review: {flagged}

  Output: {output_path}

  Action plan:
  1. Filter sheet for open_position score > 0 — reply to those FIRST
  2. Sort remaining by score descending
  3. Manually rewrite emails flagged as "needs_manual_review"
  4. Send in batches of 5–10/day
  5. Follow-up Day 7 and Day 18 drafts are pre-written in the sheet
""")


if __name__ == "__main__":
    asyncio.run(main())
