import json
from agents import llm as anthropic  # NVIDIA NIM shim
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FOLLOWUP_PROMPT_EN = """Write a brief, polite follow-up email for this professor.
This is {followup_number} (day {day}).
The initial email was about HiWi/student assistant opportunities.
Tone: professional, not pushy. Length: 80–120 words. No repetition of the original email.
Reference one specific thing from their research to show genuine continued interest.

Professor: {name}
Research: {research}
Original email subject: {original_subject}

Start with: Subject: Re: [original subject]
Then the body."""

FOLLOWUP_PROMPT_DE = """Schreiben Sie eine kurze, höfliche Folge-E-Mail für diesen Professor.
Dies ist {followup_number} (Tag {day}).
Die ursprüngliche E-Mail handelte von HiWi/Studentische-Hilfskraft-Möglichkeiten.
Ton: professionell, nicht aufdringlich. Länge: 80–110 Wörter.

Professor: {name}
Forschungsgebiet: {research}
Ursprünglicher Betreff: {original_subject}

Beginnen Sie mit: Betreff: Re: [ursprünglicher Betreff]
Dann der Text."""


def generate_followup(professor: dict, day: int, followup_number: str) -> str:
    client = anthropic.Anthropic()
    lang = professor.get("email_language", "english")
    research = professor.get("research_summary") or "your research"
    name = professor["name"]

    # Extract subject from original draft
    draft = professor.get("email_draft", "")
    original_subject = "HiWi opportunity enquiry"
    for line in draft.split("\n")[:3]:
        if line.lower().startswith("subject:") or line.lower().startswith("betreff:"):
            original_subject = line.split(":", 1)[1].strip()
            break

    if lang == "german":
        prompt = FOLLOWUP_PROMPT_DE.format(
            name=name, research=research[:400],
            original_subject=original_subject,
            followup_number=followup_number, day=day
        )
    else:
        prompt = FOLLOWUP_PROMPT_EN.format(
            name=name, research=research[:400],
            original_subject=original_subject,
            followup_number=followup_number, day=day
        )

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def run_followup_generator(professors: list) -> list:
    """Generate follow-up drafts for all professors who have an email draft."""
    to_process = [
        p for p in professors
        if p.get("email_draft") and not p.get("followup_day7")
    ]
    print(f"Generating follow-up pairs for {len(to_process)} professors...")

    for i, prof in enumerate(to_process):
        try:
            prof["followup_day7"] = generate_followup(prof, day=7, followup_number="first follow-up")
            prof["followup_day18"] = generate_followup(prof, day=18, followup_number="final follow-up")
            if (i + 1) % 10 == 0:
                print(f"  {i+1}/{len(to_process)} done...")
        except Exception as e:
            with open("data/errors.log", "a") as f:
                f.write(f"[followup] {prof['name']}: {e}\n")
            prof["followup_day7"] = ""
            prof["followup_day18"] = ""

    print(f"\n✓ Follow-up generation complete")
    return professors


if __name__ == "__main__":
    profs_path = Path("data/professors.json")

    with open(profs_path) as f:
        professors = json.load(f)

    professors = run_followup_generator(professors)

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)
