import asyncio
import json
import re
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from agents import llm as anthropic  # NVIDIA NIM shim
from dotenv import load_dotenv

load_dotenv()

# Verified live (June 2026): BTU student job board — server-rendered, paginated
# (/?p=20#list), postings at /NNNNN-title. Includes HiWi/Werkstudent/Hilfskraft.
BTU_JOBS_URL = "https://jobboerse.b-tu.de/"

HIWI_KEYWORDS = [
    "hiwi", "hilfskraft", "studentische hilfskraft",
    "student assistant", "research assistant", "werkstudent",
    "wissenschaftliche hilfskraft", "studentischer mitarbeiter",
]

EXTRACT_PROMPT = """Extract all student assistant / HiWi job postings from this page text.
Return ONLY a valid JSON array. Each object must have:
- title (string): job title as listed
- professor (string or null): responsible professor if mentioned
- department (string or null)
- deadline (string or null): application deadline in YYYY-MM-DD if found
- url (string or null): direct link to the posting
- raw_snippet (string): first 200 chars of the listing text

Only include positions that match: HiWi, Hilfskraft, Studentische Hilfskraft,
Student Assistant, Research Assistant, Werkstudent.
If no positions found, return empty array [].
No markdown fences, no preamble."""


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[job_hunter] {msg}\n")


def is_hiwi_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in HIWI_KEYWORDS)


def extract_postings_with_llm(page_text: str, source_url: str) -> list[dict]:
    client = anthropic.Anthropic()
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"{EXTRACT_PROMPT}\n\nSource URL: {source_url}\n\nPage text:\n{page_text[:5000]}"
            }]
        )
        text = resp.content[0].text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        postings = json.loads(text)
        # Stamp source URL on each posting
        for p in postings:
            if not p.get("url"):
                p["url"] = source_url
        return postings
    except Exception as e:
        log_error(f"LLM extraction failed for {source_url}: {e}")
        return []


async def scrape_btu_jobs(page) -> list[dict]:
    """Scrape the main BTU jobs / vacancies page."""
    postings = []
    try:
        await page.goto(BTU_JOBS_URL, timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        content = await page.inner_text("body")

        if is_hiwi_relevant(content):
            postings = extract_postings_with_llm(content, BTU_JOBS_URL)
            print(f"    BTU jobs page → {len(postings)} postings")

        # Also follow links that look like sub-pages
        links = await page.query_selector_all("a[href]")
        hiwi_links = []
        for link in links:
            try:
                href = await link.get_attribute("href") or ""
                text = (await link.inner_text()).strip().lower()
                if is_hiwi_relevant(text) or is_hiwi_relevant(href):
                    full_url = href if href.startswith("http") else urljoin(BTU_JOBS_URL, href)
                    hiwi_links.append(full_url)
            except Exception:
                pass

        for url in list(set(hiwi_links))[:10]:  # cap at 10 sub-links
            try:
                await page.goto(url, timeout=10000, wait_until="domcontentloaded")
                await asyncio.sleep(1)
                sub_content = await page.inner_text("body")
                sub_postings = extract_postings_with_llm(sub_content, url)
                postings.extend(sub_postings)
            except Exception as e:
                log_error(f"Sub-link failed {url}: {e}")

    except Exception as e:
        log_error(f"BTU jobs page failed: {e}")

    return postings


INSTITUTE_PAGES = [
    # Verified live (June 2026): central careers landing + chair pages that post HiWi.
    "https://www.b-tu.de/universitaet/karriere/stellenausschreibungen",
    "https://www.b-tu.de/fg-it-sicherheit/team/stellenausschreibungen",
    "https://www.b-tu.de/institut-fuer-informatik",
]


async def scrape_institute_pages(page) -> list[dict]:
    """Scrape known institute/department pages for posted positions."""
    postings = []
    for url in INSTITUTE_PAGES:
        try:
            await page.goto(url, timeout=10000, wait_until="domcontentloaded")
            await asyncio.sleep(1.5)
            content = await page.inner_text("body")
            if is_hiwi_relevant(content):
                new_posts = extract_postings_with_llm(content, url)
                postings.extend(new_posts)
                print(f"    {url} → {len(new_posts)} postings")
        except Exception as e:
            log_error(f"Institute page failed {url}: {e}")

    return postings


async def run_job_hunter() -> list[dict]:
    all_postings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (compatible; research-bot/1.0)"
        )

        print("  Scanning BTU jobs page...")
        btu_posts = await scrape_btu_jobs(page)
        all_postings.extend(btu_posts)

        print("  Scanning institute pages...")
        inst_posts = await scrape_institute_pages(page)
        all_postings.extend(inst_posts)

        await browser.close()

    # Deduplicate by title + professor
    # NOTE: use `(... or "")` not `.get(k, "")` — the LLM emits null values, so the
    # key is present-but-None and the default never kicks in (None.lower() crashes).
    seen = set()
    unique = []
    for p in all_postings:
        key = ((p.get("title") or "").lower(), (p.get("professor") or "").lower())
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


if __name__ == "__main__":
    print("Hunting for HiWi positions...")
    positions = asyncio.run(run_job_hunter())

    Path("data").mkdir(exist_ok=True)
    with open("data/open_positions.json", "w", encoding="utf-8") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Found {len(positions)} open positions")
    for pos in positions:
        print(f"  - {pos.get('title', 'unknown')} | Prof: {pos.get('professor', 'n/a')} | Deadline: {pos.get('deadline', 'n/a')}")
