import json
import re
from agents import llm as anthropic  # NVIDIA NIM shim
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert at evaluating research-skill alignment
for academic job applications. You are specific, concrete, and never generic."""

MATCH_PROMPT = """Given this professor's profile and the applicant's CV,
return ONLY valid JSON with these keys:

- ai_overlap_score: int 0–25
  (How directly does the applicant's skills/experience align with professor's research?
   25 = direct match in methods, tools, or domain; 0 = no overlap)
- cv_connection: string
  2–3 sentences max. Name SPECIFIC skills/projects from the CV that map to
  SPECIFIC aspects of the professor's research. No vague generic claims.

No markdown fences, no preamble.

Professor: {name}
Research: {research}
Projects: {projects}

Applicant skills: {skills}
Applicant projects: {cv_projects}"""


def compute_fit_score(professor: dict, cv_profile: dict,
                      open_positions: list) -> dict:
    """
    5-signal weighted fit score (100 points max):
      1. Took their course      → 25 pts (binary: yes/no)
      2. AI research overlap    → 25 pts (LLM-scored 0–25)
      3. Active grant funding   → 20 pts (has grant_indicators)
      4. Open HiWi posting      → 20 pts (in open_positions)
      5. Recent publications    → 10 pts (has current_projects)
    """
    client = anthropic.Anthropic()

    # Signal 1: course taken
    took_course = 25 if professor.get("source_courses") else 0

    # Signal 3: active grant
    has_grant = 20 if professor.get("grant_indicators") else 0

    # Signal 4: open position
    prof_name_lower = professor.get("name", "").lower()
    has_open_position = 20 if any(
        prof_name_lower in (pos.get("professor") or "").lower()
        for pos in open_positions
    ) else 0

    # Signal 5: recent publications / projects
    has_publications = 10 if professor.get("current_projects") else 0

    # Signal 2: AI overlap (LLM-scored)
    ai_overlap = 0
    cv_connection = ""
    research = professor.get("research_summary") or ""

    if research:
        try:
            prompt = MATCH_PROMPT.format(
                name=professor["name"],
                research=research,
                projects="; ".join(professor.get("current_projects", [])) or "none listed",
                skills=", ".join(cv_profile["top_skills"]),
                cv_projects="; ".join(cv_profile["strongest_projects"]),
            )
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            data = json.loads(text)
            ai_overlap = min(25, max(0, int(data.get("ai_overlap_score", 0))))
            cv_connection = data.get("cv_connection", "")
        except Exception as e:
            with open("data/errors.log", "a") as f:
                f.write(f"[matcher] LLM call failed for {professor['name']}: {e}\n")

    # If we have no scraped research but the applicant took the professor's course,
    # ground the connection in that real fact rather than leaving it blank.
    if not cv_connection and professor.get(“source_courses”):
        course = professor[“source_courses”][0]
        cv_connection = (
            f”I completed your course “{course}” as part of my studies at BTU, “
            “and I would like to support your group as a HiWi. My practical background in my field “
            “could be useful for research tooling, data pipelines, or project support in your group.”
        )

    total = took_course + ai_overlap + has_grant + has_open_position + has_publications

    professor["relevance_score"] = total
    professor["relevance_breakdown"] = {
        "course_taken": took_course,
        "ai_overlap": ai_overlap,
        "active_grant": has_grant,
        "open_position": has_open_position,
        "has_publications": has_publications,
    }
    professor["cv_connection"] = cv_connection
    return professor


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[matcher] {msg}\n")


if __name__ == "__main__":
    profs_path = Path("data/professors.json")
    cv_path = Path("data/cv_profile.json")
    positions_path = Path("data/open_positions.json")

    with open(profs_path) as f:
        professors = json.load(f)
    with open(cv_path) as f:
        cv_profile = json.load(f)

    open_positions = []
    if positions_path.exists():
        with open(positions_path) as f:
            open_positions = json.load(f)

    to_match = [
        p for p in professors
        if p.get("research_summary") and not p.get("relevance_breakdown")
    ]
    print(f"Scoring {len(to_match)} professors (5-signal formula)...")

    for i, prof in enumerate(to_match):
        print(f"  [{i+1}/{len(to_match)}] {prof['name'][:50]}")
        try:
            compute_fit_score(prof, cv_profile, open_positions)
            bd = prof.get("relevance_breakdown", {})
            print(
                f"    → total: {prof['relevance_score']}/100 "
                f"(course:{bd.get('course_taken',0)} "
                f"AI:{bd.get('ai_overlap',0)} "
                f"grant:{bd.get('active_grant',0)} "
                f"posting:{bd.get('open_position',0)} "
                f"pubs:{bd.get('has_publications',0)})"
            )
        except Exception as e:
            log_error(f"Scoring failed for '{prof['name']}': {e}")
            prof["relevance_score"] = 0
            prof["cv_connection"] = ""

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)

    high = sum(1 for p in professors if (p.get("relevance_score") or 0) >= 60)
    mid  = sum(1 for p in professors if 30 <= (p.get("relevance_score") or 0) < 60)
    print(f"\n✓ Scoring complete: {high} high (≥60), {mid} medium (30–59)")
