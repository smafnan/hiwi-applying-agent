import pdfplumber
import json
import re
from agents import llm as anthropic  # NVIDIA NIM shim
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def log_error(msg: str):
    with open("data/errors.log", "a") as f:
        f.write(f"[parser] {msg}\n")


def extract_via_llm(raw_text: str) -> list[dict]:
    """Fallback: use Claude Haiku to parse raw text when table extraction fails."""
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": (
                "Extract all university modules from this BTU transcript text. "
                "Return ONLY a valid JSON array — no preamble, no markdown fences. "
                "Each object must have exactly these keys: "
                "module_code (string or null), module_name (string), "
                "grade (float, convert German comma to dot e.g. 1,7 → 1.7), "
                "ects (int or null). "
                "Skip rows that have no numeric grade (1.0–5.0 range). "
                "Deduplicate by module_name.\n\n"
                f"Transcript text:\n{raw_text[:5000]}"
            )
        }]
    )
    text = resp.content[0].text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def parse_btu_transcript(pdf_path: str) -> list[dict]:
    courses = []
    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            full_text += page_text + "\n"

            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    row = [str(c).strip() if c else "" for c in row]

                    # German grade: 1,0 to 5,0
                    grade_pat = r"^[1-5],[0-9]$"
                    grade_cells = [c for c in row if re.match(grade_pat, c)]
                    if not grade_cells:
                        continue

                    grade = float(grade_cells[0].replace(",", "."))

                    # Module name: longest non-numeric cell
                    text_cells = [
                        c for c in row
                        if len(c) > 4 and not re.match(r"^[\d,.\s/-]+$", c)
                    ]
                    if not text_cells:
                        continue
                    module_name = max(text_cells, key=len)

                    # ECTS: small integer 1–30
                    ects_cells = [
                        c for c in row
                        if re.match(r"^\d{1,2}$", c) and 1 <= int(c) <= 30
                    ]
                    ects = int(ects_cells[0]) if ects_cells else None

                    # Module code: 4–8 digit string or alphanumeric like CS_123
                    code_cells = [
                        c for c in row
                        if re.match(r"^\d{4,8}$|^[A-Z]{1,5}[_-]?\d{3,}$", c)
                    ]
                    module_code = code_cells[0] if code_cells else None

                    courses.append({
                        "module_code": module_code,
                        "module_name": module_name,
                        "grade": grade,
                        "ects": ects,
                        "professor": None,
                        "professor_email": None,
                    })

    # Deduplicate by lowercased module name
    seen = set()
    unique = []
    for c in courses:
        key = c["module_name"].lower().strip()
        if key not in seen and len(key) > 3:
            seen.add(key)
            unique.append(c)

    # Fallback to LLM if table parsing found nothing
    if not unique and full_text.strip():
        print("  Table parsing found no courses — falling back to LLM extraction...")
        try:
            unique = extract_via_llm(full_text)
        except Exception as e:
            log_error(f"LLM fallback failed: {e}")

    return unique


if __name__ == "__main__":
    pdf_path = "data/transcript.pdf"
    if not Path(pdf_path).exists():
        print(f"ERROR: {pdf_path} not found. Upload your transcript and retry.")
        raise SystemExit(1)

    print(f"Parsing {pdf_path}...")
    courses = parse_btu_transcript(pdf_path)

    Path("data").mkdir(exist_ok=True)
    with open("data/courses.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Found {len(courses)} courses:")
    for c in courses:
        grade_str = f"  (grade: {c['grade']}, ECTS: {c['ects']})" if c.get('grade') else ""
        print(f"  - {c['module_name']}{grade_str}")
