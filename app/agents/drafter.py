import json
from agents import llm as anthropic  # NVIDIA NIM shim
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── English email ────────────────────────────────────────────────

EN_SYSTEM = """You write professional academic outreach emails in English for a student
seeking HiWi positions. Emails must feel personal, not mass-produced. Each must open with
a unique line referencing this specific professor's research. Tone: confident, genuine, respectful.
Length: 200–280 words. No bullet points. Write the subject line first as: Subject: [subject]
Then a blank line, then the body."""

EN_PROMPT = """Write a HiWi outreach email to {name} ({dept}).
Their research: {research}
Current projects: {projects}
CV connection: {connection}
{open_position_note}

Applicant: {applicant_name}, {degree} at BTU ({degree_status}). {work_background}
Key achievement: {key_achievement}. Skills: {skills}."""

# ── German email ─────────────────────────────────────────────────

DE_SYSTEM = """Sie schreiben professionelle akademische Bewerbungs-E-Mails auf Deutsch
für einen Studierenden, der eine HiWi-Position sucht.
Ton: höflich, direkt, kompetent. Keine übermäßigen Floskeln.
Deutsche Professoren bevorzugen kurze, strukturierte E-Mails.
Länge: 180–240 Wörter. Keine Aufzählungen.
Erste Zeile: Betreff: [Betreff]
Dann eine Leerzeile, dann der E-Mail-Text."""

DE_PROMPT = """Schreiben Sie eine HiWi-Bewerbungs-E-Mail an {name} ({dept}).
Forschungsgebiet: {research}
Aktuelle Projekte: {projects}
Bezug zum Lebenslauf: {connection}
{open_position_note}

Bewerber: {applicant_name}, {degree} an der BTU ({degree_status}).
{work_background}
Wichtigste Leistung: {key_achievement}
Kompetenzen: {skills}"""

def draft_email(professor: dict, cv_profile: dict) -> str:
    client = anthropic.Anthropic()
    lang = professor.get(“email_language”, “english”)

    dept = professor.get(“department”) or “your department”
    research = professor.get(“research_summary”)
    if not research:
        sc = professor.get(“source_courses”)
        research = (
            f”(No research summary available. The applicant took this professor's course “
            f””{sc[0]}” at BTU — open the email by referencing that course specifically, “
            “not generic praise.)”
        ) if sc else “your research area”
    projects = “; “.join(professor.get(“current_projects”, [])) or “your current projects”
    connection = professor.get(“cv_connection”) or “My background may be useful for your work.”

    # Build applicant info from CV profile
    applicant_name = cv_profile.get(“name”, “Applicant Name”)
    degree = cv_profile.get(“degree”, “M.Sc. [Field]”)
    degree_status = cv_profile.get(“degree_status”, “ongoing”)
    skills = “, “.join(cv_profile.get(“top_skills”, []))
    key_achievement = cv_profile.get(“key_achievement”, “Delivered quality work”)

    # Build work background from experience
    work_exp = cv_profile.get(“work_experience”, [])
    if work_exp:
        work_lines = [f”{exp.get('role')} at {exp.get('company')}” for exp in work_exp]
        work_background = f”Previous experience: {'; '.join(work_lines)}.”
    else:
        work_background = “Student with practical experience in my field.”

    # Add open position note if applicable
    open_position_note = “”
    if professor.get(“relevance_breakdown”, {}).get(“open_position”, 0) > 0:
        if lang == “german”:
            open_position_note = “Hinweis: Es gibt eine offene Stelle in dieser Gruppe — bitte darauf Bezug nehmen.”
        else:
            open_position_note = “Note: There is an open position in this group — reference it naturally.”

    if lang == “german”:
        prompt = DE_PROMPT.format(
            name=professor[“name”],
            dept=dept,
            research=research,
            projects=projects,
            connection=connection,
            open_position_note=open_position_note,
            applicant_name=applicant_name,
            degree=degree,
            degree_status=degree_status,
            work_background=work_background,
            key_achievement=key_achievement,
            skills=skills,
        )
        resp = client.messages.create(
            model=”claude-sonnet-4-6”,
            max_tokens=700,
            system=DE_SYSTEM,
            messages=[{“role”: “user”, “content”: prompt}],
        )
    else:
        prompt = EN_PROMPT.format(
            name=professor[“name”],
            dept=dept,
            research=research,
            projects=projects,
            connection=connection,
            open_position_note=open_position_note,
            applicant_name=applicant_name,
            degree=degree,
            degree_status=degree_status,
            work_background=work_background,
            key_achievement=key_achievement,
            skills=skills,
        )
        resp = client.messages.create(
            model=”claude-sonnet-4-6”,
            max_tokens=700,
            system=EN_SYSTEM,
            messages=[{“role”: “user”, “content”: prompt}],
        )

    return resp.content[0].text.strip()


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[drafter] {msg}\n")


if __name__ == "__main__":
    profs_path = Path("data/professors.json")
    cv_path = Path("data/cv_profile.json")

    with open(profs_path) as f:
        professors = json.load(f)
    with open(cv_path) as f:
        cv_profile = json.load(f)

    to_draft = [
        p for p in professors
        if p.get("email") and p.get("research_summary") and not p.get("email_draft")
    ]
    print(f"Drafting {len(to_draft)} emails...")

    for i, prof in enumerate(to_draft):
        lang = prof.get("email_language", "english")
        print(f"  [{i+1}/{len(to_draft)}] {prof['name'][:45]} [{lang.upper()}]")
        try:
            prof["email_draft"] = draft_email(prof, cv_profile)
            first_line = prof["email_draft"].split("\n")[0]
            print(f"    → {first_line}")
        except Exception as e:
            log_error(f"Draft failed for '{prof['name']}': {e}")
            prof["email_draft"] = ""

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)

    de_count = sum(1 for p in professors if p.get("email_language") == "german" and p.get("email_draft"))
    en_count = sum(1 for p in professors if p.get("email_language") == "english" and p.get("email_draft"))
    print(f"\n✓ Done: {de_count} German, {en_count} English emails drafted")
