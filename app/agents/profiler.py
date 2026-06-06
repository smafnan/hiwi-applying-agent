import asyncio
import json
import re
from pathlib import Path
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from agents import llm as anthropic  # NVIDIA NIM shim
from dotenv import load_dotenv

load_dotenv()

BTU_STAFF_BASE = "https://www.b-tu.de/universitaet/beschaeftigte"
# BTU Solr site search — reliably surfaces a professor's chair/team page.
BTU_STAFF_BASE_SEARCH = "https://www.b-tu.de/suche"


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[profiler] {msg}\n")


def _clean_email(raw):
    """De-obfuscate BTU emails: 'petra.hofstedt(at)b-tu.de' -> 'petra.hofstedt@b-tu.de'."""
    if not raw:
        return None
    e = raw.strip()
    e = re.sub(r"\s*[\(\[]\s*at\s*[\)\]]\s*", "@", e, flags=re.I)
    e = re.sub(r"\s+at\s+", "@", e, flags=re.I)
    e = re.sub(r"\s*[\(\[]\s*dot\s*[\)\]]\s*", ".", e, flags=re.I)
    e = e.replace(" ", "")
    return e if re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", e) else None


def _email_from_text(text: str):
    """Regex fallback: pull a b-tu.de email out of page text, handling (at)/[at] forms."""
    m = re.search(r"[A-Za-z0-9._%+-]+\s*(?:@|\(at\)|\[at\])\s*[A-Za-z0-9.-]*b-tu\.de", text, re.I)
    return _clean_email(m.group(0)) if m else None


# v2 upgrade: detect DFG / EU Horizon / BMWK / industrial funding per professor.
PROFILE_PROMPT = """Extract profile information for professor '{name}' from this BTU staff page text.
Return ONLY valid JSON with exactly these keys:
- email (string or null)
- department (string or null)
- research_summary (2–3 sentence description of their main research area, or null)
- current_projects (list of project title strings, empty list if none)
- grant_indicators (list of objects — find any active funding mentions):
    Each object: {{"funder": string, "project": string, "year_range": string or null}}
    Look for: DFG, EU, Horizon Europe, Horizon 2020, BMWK, BMBF, ERC,
    industrial partner, funded by, research consortium, project grant.
    Empty list if nothing found.

No markdown fences, no preamble."""


def extract_profile_data(html_text: str, professor_name: str) -> dict:
    """Use Claude Haiku to extract structured profile including grant signals."""
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": PROFILE_PROMPT.format(name=professor_name) +
                       f"\n\nPage text (first 4000 chars):\n{html_text[:4000]}"
        }]
    )
    text = resp.content[0].text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except Exception:
        data = {}

    return {
        "email": data.get("email"),
        "department": data.get("department"),
        "research_summary": data.get("research_summary"),
        "current_projects": data.get("current_projects", []),
        "grant_indicators": data.get("grant_indicators", []),
    }


async def fetch_professor_profile(browser, professor: dict) -> dict:
    name = professor["name"]
    page = await browser.new_page(
        user_agent="Mozilla/5.0 (compatible; research-bot/1.0)"
    )

    try:
        # Strip academic titles down to a plain "First Last". Drop title tokens and
        # stray punctuation, then keep only capitalised name tokens (incl. hyphenated),
        # so "Prof. Dr. rer. nat. habil. Petra Hofstedt" -> "Petra Hofstedt".
        cleaned = re.sub(r"\b(Prof|PD|apl|Dr|rer|nat|habil|Ing|hc|h|c)\b\.?", " ",
                         name.replace(",", " "))
        cleaned = re.sub(r"[.·]", " ", cleaned)
        tokens = [t for t in cleaned.split() if re.match(r"^[A-ZÄÖÜ][\wäöüß-]+$", t)]
        search_name = " ".join(tokens) if tokens else name
        last_name = tokens[-1] if tokens else name.split()[-1]

        # BTU's Solr site search reliably surfaces a professor's chair team page.
        search_url = f"{BTU_STAFF_BASE_SEARCH}?tx_solr%5Bq%5D={quote_plus(search_name)}"
        await page.goto(search_url, timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(1.5)

        # Rank result links and pick the professor's OWN profile page, not a generic
        # institute/list page. A URL ending in the name slug (…/petra-hofstedt) wins.
        anchors = await page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => ({t:(e.innerText||'').trim(), h:e.getAttribute('href')||''}))"
        )
        first = search_name.split()[0].lower() if search_name else ""
        last = last_name.lower()

        def score_anchor(href: str, text: str) -> int:
            hl = href.lower()
            if last not in (hl + " " + text.lower()):
                return -1
            slug = hl.rstrip("/").split("/")[-1]
            s = 0
            if last in slug and first and first in slug:
                s += 6                       # …/petra-hofstedt  → personal profile
            elif last in slug:
                s += 3
            if "/team/" in hl:
                s += 2
            if re.search(r"professor|professorin|mitarbeiter", hl):
                s += 2
            if "/fg-" in hl or "/lehrstuhl" in hl:
                s += 1
            if re.search(r"publikation|news|suche|forschung", hl):
                s -= 3                       # not a profile page
            return s

        best, best_s = None, 0
        for a in anchors:
            sc = score_anchor(a["h"], a["t"])
            if sc > best_s:
                best, best_s = a["h"], sc
        if best:
            profile_url = best if best.startswith("http") else f"https://www.b-tu.de{best}"
        else:
            profile_url = None

        if profile_url:
            await page.goto(profile_url, timeout=15000, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            professor["profile_url"] = page.url

        content = await page.inner_text("body")
        profile_data = extract_profile_data(content, name)

        professor["email"] = _clean_email(profile_data.get("email")) or _email_from_text(content)
        professor["department"] = profile_data.get("department")
        professor["research_summary"] = profile_data.get("research_summary")
        professor["current_projects"] = profile_data.get("current_projects", [])
        professor["grant_indicators"] = profile_data.get("grant_indicators", [])  # v2

    except Exception as e:
        log_error(f"Profile fetch failed for '{name}': {e}")
    finally:
        await page.close()

    return professor


async def run_profiler(professors: list) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for i, prof in enumerate(professors):
            if prof.get("email"):
                print(f"  [{i + 1}/{len(professors)}] {prof['name'][:50]} — already profiled, skipping")
                continue

            print(f"  [{i + 1}/{len(professors)}] {prof['name'][:50]}")
            await fetch_professor_profile(browser, prof)
            email_display = prof.get("email") or "no email"
            dept_display = prof.get("department") or "no dept"
            print(f"    → email: {email_display} | dept: {dept_display}")
            await asyncio.sleep(1.5)

        await browser.close()

    return professors


if __name__ == "__main__":
    profs_path = Path("data/professors.json")
    if not profs_path.exists():
        print("ERROR: Run scraper.py first.")
        raise SystemExit(1)

    with open(profs_path) as f:
        professors = json.load(f)

    print(f"Profiling {len(professors)} professors...")
    professors = asyncio.run(run_profiler(professors))

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)

    with_email = sum(1 for p in professors if p.get("email"))
    with_research = sum(1 for p in professors if p.get("research_summary"))
    print(f"\n✓ Profiled: {with_email}/{len(professors)} have emails, "
          f"{with_research}/{len(professors)} have research summaries")
