# HiWi Applying Agent 🎓

**Automated outreach to find HiWi (student assistant) positions at BTU Cottbus-Senftenberg**

An end-to-end pipeline that turns your BTU transcript into personalized emails to professors — helping you land that HiWi position faster.

---

## What It Does (In 30 Seconds)

```
Your Transcript PDF
    ↓
Extract your courses
    ↓
Find professors who taught those courses
    ↓
Scrape their emails, research, projects
    ↓
Score how well they match your skills
    ↓
Generate personalized emails in German/English
    ↓
Excel sheet with all emails ready to send
```

**Result:** A spreadsheet with 10–20+ personalized emails, ranked by fit, with follow-ups pre-written.

---

## The Problem This Solves

❌ **Without this:** Manually googling professors, finding emails, writing generic emails one-by-one (3–4 hours)

✅ **With this:** Automated pipeline produces personalized emails ranked by fit (45 minutes)

---

## Quick Start (3 minutes)

### 1. Clone & Install

```bash
git clone https://github.com/smafnan/hiwi-applying-agent.git
cd hiwi-applying-agent
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Set Up API Key

Create `.env` file:

```bash
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

Get a NVIDIA NIM key for free at [nvidia.com/nim](https://www.nvidia.com/en-us/ai-on-nvidia/)

*(Or use Anthropic API — see Advanced Setup below)*

### 3. Add Your Profile

Copy the template:
```bash
cp data/cv_profile_template.json data/cv_profile.json
```

Edit `data/cv_profile.json` with your details:
```json
{
  "name": "Jane Müller",
  "degree": "M.Sc. Computer Science",
  "degree_status": "ongoing",
  "top_skills": [
    "Python",
    "Machine Learning",
    "Docker",
    "React"
  ],
  "strongest_projects": [
    "Built ML recommendation engine: 40% improvement in accuracy",
    "Developed real-time data pipeline for 10M+ records"
  ],
  "key_achievement": "Production ML system reducing inference time by 50%",
  "work_experience": [
    {
      "role": "ML Engineer",
      "company": "Tech Company",
      "duration": "Jan 2023 – Aug 2023"
    }
  ]
}
```

### 4. Add Your Transcript

Save your BTU Notenübersicht (grade transcript) PDF as:
```
data/transcript.pdf
```

### 5. Run It

```bash
python main.py
```

Wait 30–45 minutes. Grab coffee. ☕

### 6. Open Results

```
output/outreach_tracker.xlsx
```

Excel sheet with:
- All professors ranked by fit score (0–100)
- Personalized email drafts
- Day 7 + Day 18 follow-ups
- Contact info and links

---

## How It Works: The 10-Step Pipeline

### **Step 1: Parse Your Transcript**
- Reads your BTU Notenübersicht PDF
- Extracts course names using pdfplumber
- Handles German characters and grade formats

### **Step 2: Map Courses → Professors**
- Searches BTU's module catalogue (4,710 modules at `https://www.b-tu.de/modul`)
- Finds the professor responsible for each course
- Uses module detail pages to extract "Responsible Staff Member"

### **Step 3: Profile Professors**
- Uses BTU's Solr search to find professor profile pages
- Extracts: email address, department, research area, projects
- De-obfuscates email addresses (BTU uses `(at)` format)
- Detects active grant funding (DFG, EU Horizon, etc.)

### **Step 4: Discover More Professors**
- Scans BTU department pages for additional professors
- Profiles them the same way
- Removes duplicates

### **Step 5: Detect Language Preference**
- Determines if each professor prefers German or English
- Uses LLM to infer from their research area and name

### **Step 6: Score Fit (5 Signals)**
Weighted score (0–100 points):
- **Course taken** (25 pts): Did you take this professor's class?
- **Skill overlap** (25 pts): LLM-scored match between your skills and their research
- **Active grants** (20 pts): Do they have funding to hire?
- **Open position** (20 pts): Is there a job posting from them?
- **Publications** (10 pts): Do they have active projects?

**Result:** Professors ranked by how good a fit they are

### **Step 7: Draft Personalized Emails**
- Generates emails in German or English based on Step 5
- Opens with specific reference to their research or your shared course
- Includes your skills, achievement, and experience
- Length: 200–300 words (professional but personal)

Example opening:
```
Dear Prof. Schmidt,

I am Jane Müller, currently pursuing my M.Sc. in Computer Science at BTU.
Your research in machine learning optimization directly aligns with my work
on recommendation systems and real-time data pipelines. My experience with
Python and distributed systems could be valuable for your group's work.
```

### **Step 8: Quality Review**
- Checks each email for:
  - Not generic ("I'm interested in AI" ❌ vs "Your work in X matches my Y" ✅)
  - Professional tone and length
  - Proper structure and grammar
- Regenerates if any check fails

### **Step 9: Generate Follow-Ups**
- Creates Day 7 follow-up (friendly reminder)
- Creates Day 18 follow-up (more direct call to action)
- Same language and personalized tone as initial email

### **Step 10: Export to Excel**
- Creates `output/outreach_tracker.xlsx` with 17 columns:
  - Professor name, email, department, research area
  - Fit score + signal breakdown
  - Initial email draft
  - Day 7 + Day 18 follow-ups
  - Tracking columns (sent, responded, notes)

---

## Using the Output

### **Column-by-Column Guide**

| Column | What It Is | How to Use |
|--------|-----------|-----------|
| **Score** | Fit score 0–100 | Sort descending; start with high scores |
| **Breakdown** | Individual signals | Shows what contributes to the score |
| **Email draft** | Ready-to-send email | Copy & paste into Gmail |
| **Day 7 follow-up** | First reminder | Send automatically on Day 7 |
| **Day 18 follow-up** | Second follow-up | Send on Day 18 if no response |
| **Notes** | Tracking column | Add "sent", "replied", "not interested" |

### **Recommended Workflow**

1. **Sort by Score** (descending) → Start with highest-fit professors
2. **Filter for open positions** → Priority targets with active job postings
3. **Send in batches** → 5–10 emails/day (avoid spam filters)
4. **Wait 48 hours** between batches
5. **Use follow-ups** → Auto-send Day 7 emails to non-responders
6. **Track in Notes** → Log responses for follow-up
7. **Day 18 final push** → Last chance follow-up

---

## Customization

### **Change Email Tone**

Edit `agents/drafter.py`:
```python
EN_SYSTEM = """You write emails in [your tone here]..."""
DE_SYSTEM = """Sie schreiben E-Mails in [your tone]..."""
```

### **Adjust Fit Scoring**

Edit `agents/matcher.py` to change the 5-signal weights:
```python
took_course = 25        # Course = 25 pts
skill_overlap = 0 to 25 # Skill match = up to 25 pts
has_grant = 20          # Funding = 20 pts
has_open_position = 20  # Job posting = 20 pts
has_publications = 10   # Projects = 10 pts
```

### **Use Anthropic Instead of NVIDIA**

1. Get Anthropic API key
2. Edit `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Edit `agents/llm.py` to use Anthropic client directly

---

## Understanding the Code Structure

```
hiwi-applying-agent/
├── main.py                          # 10-step orchestrator
├── agents/
│   ├── llm.py                       # LLM API shim (NVIDIA/Anthropic)
│   ├── parser.py                    # PDF transcript parsing
│   ├── scraper.py                   # Course → professor mapping
│   ├── profiler.py                  # Email + research scraping
│   ├── discovery.py                 # Find more professors
│   ├── language_agent.py            # Detect German/English
│   ├── matcher.py                   # 5-signal scoring
│   ├── drafter.py                   # Email generation
│   ├── reviewer.py                  # Quality control
│   ├── followup.py                  # Follow-up templates
│   └── sheet_writer.py              # Excel export
├── data/
│   ├── transcript.pdf               # Your BTU grade transcript (you add)
│   ├── cv_profile.json              # Your profile (you create from template)
│   ├── cv_profile_template.json     # Template to copy
│   ├── courses.json                 # Extracted from transcript
│   ├── professors.json              # All professors with data
│   └── open_positions.json          # HiWi job postings
└── output/
    └── outreach_tracker.xlsx        # Final deliverable (you use this)
```

---

## Troubleshooting

### **"API key not valid"**
- Check `.env` file exists and has correct format
- Ensure no extra spaces: `NVIDIA_API_KEY=nvapi-xxx` (not `nvapi-xxx `)
- Get a new key if expired

### **"transcript.pdf not found"**
- Make sure file is saved as `data/transcript.pdf` (exact path)
- File must be a valid PDF of your BTU Notenübersicht

### **"Solr search returns wrong professor"**
- BTU's search sometimes isn't perfect
- Manually look up the professor's email and add to `data/professors.json`
- Re-run from Step 6 onwards

### **"Emails are too generic"**
- Your CV profile is too vague
- Add more **specific skills** and **measurable achievements**
- Include **2–3 strongest projects** with outcomes

### **"Pipeline is slow (45 min runtime)"**
- This is normal! Playwright waits for pages to load
- Most time is spent on BTU's Solr search (network waits)
- Can't be optimized without caching (future enhancement)

### **"Some professors missing research summaries"**
- BTU's profile pages sometimes lack research text
- Fallback: email opens with reference to your shared course instead
- This is actually **more personal** and **more effective**

---

## Technical Details

### **Why NVIDIA NIM?**
- Free tier available (vs. Anthropic's paid API)
- `meta/llama-3.3-70b-instruct` is powerful enough for this task
- Drop-in shim (`agents/llm.py`) makes it easy to switch

### **Why Playwright?**
- BTU's module catalogue and Solr search require JavaScript rendering
- Playwright handles it cleanly
- Headless Chromium is reliable and fast

### **Why pdfplumber?**
- Fast table extraction from PDFs
- Handles German characters without issues
- Fallback to LLM if table parsing fails

### **Why 45 minutes?**
- ~100+ professors × ~20 sec per Solr search = 30 min
- Email generation: ~1 min for 14 professors
- Quality review: ~5 min
- Network waits dominate

---

## What's NOT Included

❌ **Sending emails automatically** — This is intentional. You control what gets sent.

❌ **Storing passwords/tokens** — `.env` is in `.gitignore` for security.

❌ **Personal context** — The tool is generic by design. Add your own profile.

---

## FAQ

**Q: Can I run this outside BTU?**
A: No, it's specific to BTU's infrastructure (module catalogue, Solr search). It won't work for other universities.

**Q: What if I don't have work experience?**
A: Leave `work_experience` as an empty list `[]`. The email will use "Student with practical experience in my field."

**Q: How many emails will I get?**
A: Typically 15–30, depending on how many unique professors taught your courses + discovery results.

**Q: Can I edit the emails before sending?**
A: Yes! The Excel sheet has the full email text. Edit in Excel before copying to your email client.

**Q: What if a professor replies?**
A: Great! Note it in the "Notes" column. Don't send Day 7/18 follow-ups if they already replied.

**Q: How long before I hear back?**
A: HiWi hiring is slow. Usually 1–3 weeks. Some professors don't reply (normal in academia).

**Q: What's a good fit score?**
- **70+** = Excellent fit, send ASAP
- **50–69** = Good fit, include in batch sends
- **30–49** = Worth trying, lower priority
- **<30** = Long shot, send only if highly interested

---

## Contributing

Found a bug? Idea for improvement? Submit an issue or PR on GitHub!

**Common improvements:**
- Add caching to speed up repeated runs
- Support for other German universities
- Better BTU email scraping (currently uses Solr search + regex)
- Automatic email sending (with confirmation)

---

## License

MIT License — use freely, modify, share.

---

## Support & Questions

1. **Check the FAQ above** — answers most common questions
2. **Read the comments in `agents/`** — they explain the logic
3. **Review sample output** — `output/outreach_tracker.xlsx` shows what you'll get
4. **Open a GitHub issue** — describe the problem, include your OS and Python version

---

## Good Luck! 🎓

You've got this. Send those emails. Good HiWi positions are out there.

When you get that position, come back and let us know — would love to hear success stories! 🚀
