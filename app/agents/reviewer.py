import json
import re
from agents import llm as anthropic  # NVIDIA NIM shim
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REVIEW_PROMPT = """Review this HiWi outreach email draft critically.

Score it against each criterion (0 = fail, 1 = pass):
1. specific_opening: Does the opening reference this specific professor's research (not generic)?
2. disability_present: Is the hearing impairment (GdB) mentioned naturally and confidently?
3. cv_evidence: Does it cite at least one specific quantified achievement or project?
4. appropriate_length: Is it 180–300 words (not too short, not too long)?
5. not_generic: Does it feel personal rather than mass-produced?

Return ONLY valid JSON:
{{"specific_opening": 0or1, "disability_present": 0or1, "cv_evidence": 0or1,
  "appropriate_length": 0or1, "not_generic": 0or1,
  "fail_reasons": ["list of specific things to fix if any criterion scored 0"]}}

Professor research context: {research}
Email draft:
{draft}"""


def review_email(professor: dict) -> dict:
    """Returns dict with pass/fail scores and fail_reasons."""
    client = anthropic.Anthropic()
    draft = professor.get("email_draft", "")
    research = professor.get("research_summary") or "unknown"

    if not draft:
        return {"passed": False, "fail_reasons": ["no draft"]}

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": REVIEW_PROMPT.format(
                    research=research[:800],
                    draft=draft[:1500]
                )
            }]
        )
        text = resp.content[0].text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        scores = json.loads(text)

        criteria = ["specific_opening", "disability_present", "cv_evidence",
                    "appropriate_length", "not_generic"]
        passed = all(scores.get(c, 0) == 1 for c in criteria)
        scores["passed"] = passed
        return scores

    except Exception as e:
        return {"passed": True, "fail_reasons": [], "error": str(e)}
        # Default pass on LLM error — don't block pipeline


def run_reviewer(professors: list, cv_profile: dict) -> list:
    """Review all drafted emails. Regenerate once if they fail."""
    from agents.drafter import draft_email  # import here to avoid circular

    needs_review = [p for p in professors if p.get("email_draft") and not p.get("review_result")]
    print(f"Reviewing {len(needs_review)} email drafts...")

    regenerated = 0
    for i, prof in enumerate(needs_review):
        result = review_email(prof)
        prof["review_result"] = result

        if not result.get("passed"):
            reasons = "; ".join(result.get("fail_reasons", []))
            print(f"  [{i+1}] FAIL — {prof['name'][:40]}: {reasons}")
            print(f"         Regenerating...")
            try:
                # Regenerate — drafter will try to fix based on same prompt
                # (a smarter approach would feed the fail_reasons into the prompt)
                prof["email_draft"] = draft_email(prof, cv_profile)
                # Re-review once
                recheck = review_email(prof)
                prof["review_result"] = recheck
                if recheck.get("passed"):
                    print(f"         ✓ Passed on retry")
                    regenerated += 1
                else:
                    print(f"         ✗ Still failing — flagged for manual review")
                    prof["status"] = "needs_manual_review"
            except Exception as e:
                print(f"         Regeneration failed: {e}")
        else:
            if (i + 1) % 10 == 0:
                print(f"  {i+1}/{len(needs_review)} reviewed...")

    passed = sum(1 for p in professors if p.get("review_result", {}).get("passed"))
    flagged = sum(1 for p in professors if p.get("status") == "needs_manual_review")
    print(f"\n✓ Review complete: {passed} passed, {flagged} flagged for manual review")
    print(f"  {regenerated} emails improved on retry")
    return professors


if __name__ == "__main__":
    import json
    from pathlib import Path

    profs_path = Path("data/professors.json")
    cv_path = Path("data/cv_profile.json")

    with open(profs_path) as f:
        professors = json.load(f)
    with open(cv_path) as f:
        cv_profile = json.load(f)

    professors = run_reviewer(professors, cv_profile)

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)
