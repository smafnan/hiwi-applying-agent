import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

# LIMITATION (verified June 2026): BTU has NO single university-wide searchable staff
# directory — personnel are federated across per-chair pages (/fg-<name>/team/...,
# /<chair>/team/professors). This URL is a section landing page, so this step yields
# few/no professors on its own; the reliable professor source is the module catalogue
# (scraper.py -> /modul) and per-chair team pages. Treat discovery as best-effort.
BTU_PEOPLE_URL = "https://www.b-tu.de/beschaeftigte"


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[discovery] {msg}\n")


def build_empty_professor(name: str, profile_url: str = None) -> dict:
    return {
        "name": name,
        "email": None,
        "department": None,
        "research_summary": None,
        "current_projects": [],
        "profile_url": profile_url,
        "source_courses": [],
        "relevance_score": None,
        "cv_connection": None,
        "email_draft": None,
        "status": "draft",
    }


async def discover_all_professors(existing_names: set) -> list[dict]:
    new_professors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (compatible; research-bot/1.0)"
        )

        try:
            await page.goto(BTU_PEOPLE_URL, timeout=15000, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # Filter for professors only if a filter exists
            for selector in ['select[name*="group"]', 'select[name*="type"]',
                              'button[data-filter*="prof"]']:
                try:
                    el = page.locator(selector).first
                    if await el.is_visible():
                        await el.click()
                        await asyncio.sleep(1)
                        break
                except Exception:
                    pass

            # Scroll to load all results (lazy loading)
            prev_count = 0
            for _ in range(20):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
                links = await page.query_selector_all("a[href*='beschaeftigte']")
                if len(links) == prev_count:
                    break
                prev_count = len(links)

            # Extract professor names and profile URLs from all person links
            links = await page.query_selector_all("a[href*='beschaeftigte']")
            seen_urls = set()

            for link in links:
                try:
                    href = await link.get_attribute("href")
                    text = (await link.inner_text()).strip()

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    # Only accept links that look like person profiles (not list pages)
                    if href.count("/") < 4:
                        continue

                    # Try to extract a name from link text
                    name_match = re.search(
                        r"((?:Prof\.?\s+)?(?:Dr\.?\s+)?[A-ZÄÖÜ][a-zäöüß]+"
                        r"(?:[\s-][A-ZÄÖÜ][a-zäöüß]+)+)",
                        text
                    )
                    if name_match:
                        name = name_match.group(1).strip()
                        if name not in existing_names and "Prof" in name:
                            profile_url = href if href.startswith("http") \
                                else f"https://www.b-tu.de{href}"
                            new_professors.append(build_empty_professor(name, profile_url))
                            existing_names.add(name)

                except Exception:
                    pass

        except Exception as e:
            log_error(f"Directory scrape failed: {e}")
        finally:
            await browser.close()

    return new_professors


if __name__ == "__main__":
    profs_path = Path("data/professors.json")
    if profs_path.exists():
        with open(profs_path) as f:
            professors = json.load(f)
    else:
        professors = []

    existing_names = {p["name"] for p in professors}
    print(f"Already have {len(existing_names)} professors. Discovering all BTU faculty...")

    new_profs = asyncio.run(discover_all_professors(existing_names))
    print(f"Found {len(new_profs)} additional professors.")

    professors.extend(new_profs)

    with open(profs_path, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Total professors: {len(professors)}")
    print("Now run profiler.py again to fetch profiles for the new professors.")
