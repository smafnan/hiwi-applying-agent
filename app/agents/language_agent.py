import json
import re
from agents import llm as anthropic  # NVIDIA NIM shim
from dotenv import load_dotenv

load_dotenv()

DETECT_PROMPT = """Determine the best language to email this BTU professor in.

Signals for GERMAN: German-only name/bio, German department name, German publication titles,
German website language, no listed international collaborations.

Signals for ENGLISH: International name or background, English-language publications or bio,
international project names (Horizon, EU), explicit international collaborations.

Professor name: {name}
Department: {dept}
Research summary: {research}
Current projects: {projects}

Reply with ONLY one word: GERMAN or ENGLISH"""


def detect_language(professor: dict) -> str:
    """Return 'german' or 'english' for this professor."""
    client = anthropic.Anthropic()
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": DETECT_PROMPT.format(
                    name=professor.get("name", ""),
                    dept=professor.get("department") or "unknown",
                    research=professor.get("research_summary") or "unknown",
                    projects="; ".join(professor.get("current_projects", [])) or "none",
                )
            }]
        )
        result = resp.content[0].text.strip().upper()
        return "german" if "GERMAN" in result else "english"
    except Exception:
        return "english"  # safe default


def run_language_detection(professors: list) -> list:
    to_detect = [p for p in professors if not p.get("email_language")]
    print(f"Detecting language for {len(to_detect)} professors...")

    for i, prof in enumerate(to_detect):
        lang = detect_language(prof)
        prof["email_language"] = lang
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(to_detect)} done...")

    german_count = sum(1 for p in professors if p.get("email_language") == "german")
    english_count = sum(1 for p in professors if p.get("email_language") == "english")
    print(f"  → German: {german_count}, English: {english_count}")
    return professors


if __name__ == "__main__":
    from pathlib import Path

    profs_path = Path("data/professors.json")
    with open(profs_path) as f:
        professors = json.load(f)

    professors = run_language_detection(professors)

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)
