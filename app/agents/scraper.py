import asyncio
import json
import re
from pathlib import Path
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from agents import llm as anthropic  # NVIDIA NIM shim
from dotenv import load_dotenv

load_dotenv()

# Verified live (June 2026): central module catalogue (Modulübersicht table:
# Modulnummer | Bezeichnung, with module detail pages listing Lehrverantwortliche).
BTU_MODULE_SEARCH = "https://www.b-tu.de/modul"
BTU_BASE = "https://www.b-tu.de"


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[scraper] {msg}\n")


def extract_professor_from_html(html: str, course_name: str) -> str | None:
    """Use Claude to find professor name in HTML content."""
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": (
                f"Find the responsible professor (Lehrverantwortliche/r) for the course "
                f"'{course_name}' in this HTML/text. "
                "Return ONLY the professor's full name (e.g. 'Prof. Dr. Max Mustermann') "
                "or the single word NULL if not found. No other text.\n\n"
                f"Content (first 3000 chars):\n{html[:3000]}"
            )
        }]
    )
    result = resp.content[0].text.strip()
    if result.upper() == "NULL" or len(result) < 5:
        return None
    return result


def _normalize_prof_name(raw: str) -> str:
    """'Prof. Dr. rer. nat. habil. Hofstedt, Petra' -> 'Prof. Dr. rer. nat. habil. Petra Hofstedt'."""
    raw = raw.strip()
    # Split leading academic titles from the actual name
    m = re.match(r"^((?:Prof\.?|Dr\.?|rer\.?|nat\.?|habil\.?|-Ing\.?|h\.?c\.?|PD|apl\.?|\s)+)\s*(.*)$", raw)
    titles, rest = (m.group(1).strip(), m.group(2).strip()) if m else ("", raw)
    if "," in rest:                       # "Lastname, Firstname" -> "Firstname Lastname"
        last, first = [x.strip() for x in rest.split(",", 1)]
        rest = f"{first} {last}".strip()
    return f"{titles} {rest}".strip()


async def load_module_catalogue(page) -> list[dict]:
    """Load the full BTU module list once: [{num, name}] from /modul (≈4700 modules)."""
    await page.goto(BTU_MODULE_SEARCH, timeout=25000, wait_until="domcontentloaded")
    await asyncio.sleep(2)
    rows = await page.eval_on_selector_all(
        'a[href^="/modul/"]',
        "els => els.map(e => { const tr = e.closest('tr');"
        " return {num: e.getAttribute('href').split('/').pop(),"
        " row: (tr ? tr.innerText : '').replace(/\\s+/g,' ').trim()}; })"
    )
    cat = []
    for r in rows:
        row = r["row"]
        # row looks like "14034 Languages of Artificial Intelligence"
        name = re.sub(r"^\d+\s+", "", row).strip()
        if name:
            cat.append({"num": r["num"], "name": name})
    return cat


def _match_module(course_name: str, catalogue: list[dict]) -> str | None:
    """Return the module number whose catalogue name best matches the course."""
    cl = course_name.lower().strip()
    # exact-ish containment first
    for m in catalogue:
        if cl[:35] and cl[:35] in m["name"].lower():
            return m["num"]
    # fall back to token overlap for slightly different wording
    ctoks = {t for t in re.findall(r"[a-z]+", cl) if len(t) > 3}
    best, best_score = None, 0
    for m in catalogue:
        mtoks = {t for t in re.findall(r"[a-z]+", m["name"].lower()) if len(t) > 3}
        score = len(ctoks & mtoks)
        if score > best_score and score >= max(2, len(ctoks) // 2):
            best, best_score = m["num"], score
    return best


async def find_professor_for_course(page, course: dict, catalogue: list[dict]) -> str | None:
    name = course["module_name"]
    num = _match_module(name, catalogue)
    if not num:
        return None
    try:
        await page.goto(f"{BTU_BASE}/modul/{num}", timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(1)
        body = await page.inner_text("body")

        # BTU module detail pages expose "Responsible Staff Member:" / "Verantwortliche/r"
        m = re.search(
            r"(?:Responsible Staff Member|Modulverantwortlich\w*|Verantwortlich\w*)\s*:?\s*\n?\s*"
            r"((?:Prof\.?|PD|Dr\.?|apl\.?)[^\n]{3,70})",
            body, re.I
        )
        if m:
            return _normalize_prof_name(m.group(1))

        # Fallback: first Prof. occurrence on the focused detail page
        m2 = re.search(r"(Prof\.[^\n]{3,70})", body)
        if m2:
            return _normalize_prof_name(m2.group(1))

        # Last resort: LLM extraction on the detail page
        result = extract_professor_from_html(body, name)
        if result:
            return _normalize_prof_name(result)
    except Exception as e:
        log_error(f"Module detail failed for '{name}' (/modul/{num}): {e}")
    return None


async def run_scraper(courses: list) -> list[dict]:
    professors_by_name: dict[str, dict] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (compatible; research-bot/1.0)"
        )

        print("  Loading BTU module catalogue (/modul)...")
        catalogue = await load_module_catalogue(page)
        print(f"  Catalogue loaded: {len(catalogue)} modules")

        for i, course in enumerate(courses):
            print(f"  [{i + 1}/{len(courses)}] {course['module_name'][:60]}")
            try:
                prof_name = await find_professor_for_course(page, course, catalogue)
                if prof_name:
                    if prof_name not in professors_by_name:
                        professors_by_name[prof_name] = {
                            "name": prof_name,
                            "email": None,
                            "department": None,
                            "research_summary": None,
                            "current_projects": [],
                            "profile_url": None,
                            "source_courses": [],
                            "relevance_score": None,
                            "cv_connection": None,
                            "email_draft": None,
                            "status": "draft",
                        }
                    professors_by_name[prof_name]["source_courses"].append(
                        course["module_name"]
                    )
                    print(f"    → {prof_name}")
                else:
                    print("    → not found")
            except Exception as e:
                log_error(f"Unexpected error for '{course['module_name']}': {e}")

            await asyncio.sleep(1.5)

        await browser.close()

    return list(professors_by_name.values())


if __name__ == "__main__":
    if not Path("data/courses.json").exists():
        print("ERROR: Run parser.py first.")
        raise SystemExit(1)

    with open("data/courses.json") as f:
        courses = json.load(f)

    print(f"Searching for professors across {len(courses)} courses...")
    professors = asyncio.run(run_scraper(courses))

    with open("data/professors.json", "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Found {len(professors)} unique professors from your transcript")
