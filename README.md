# HiWi Applying Agent 🎓

Automatically generate personalized outreach emails to BTU professors for HiWi positions. This project combines an intelligent agent pipeline with an interactive web portal.

- **Agent** — Analyzes your transcript, finds matching professors, scores fit, and drafts emails
- **Portal** — Beautiful web interface to upload files, track progress, and download results

---

## Project Structure

```
hiwi-applying-agent/
├── app/                   # Agent pipeline (Python)
│   ├── agents/           # LLM agents for profiling, scraping, matching, drafting
│   ├── data/             # Sample transcript and data
│   ├── main.py           # Orchestrator (10-step pipeline)
│   ├── requirements.txt   # Python dependencies
│   └── README.md          # Detailed agent documentation
│
├── portal/               # Web interface (React + FastAPI)
│   ├── App.tsx           # React frontend
│   ├── main.py           # FastAPI backend
│   ├── main.tsx          # React entry point
│   ├── index.html        # HTML entry
│   ├── package.json      # Node dependencies
│   ├── vite.config.ts    # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   ├── backend_requirements.txt  # Python deps
│   ├── docker-compose.yml         # Multi-container setup
│   └── README.md          # Portal documentation
│
├── docker-compose.yml    # Full stack orchestration
└── README.md             # This file
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/smafnan/hiwi-applying-agent.git
cd hiwi-applying-agent

# Full stack: Agent API + Web Portal
docker-compose up

# Access:
# - Portal UI: http://localhost:5173
# - API Docs: http://localhost:8000/docs
```

### Option 2: Agent Only

```bash
cd app
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
export NVIDIA_API_KEY=nvapi-...

python main.py
```

### Option 3: Portal Only

```bash
cd portal

# Backend
python -m venv venv
source venv/bin/activate
pip install -r backend_requirements.txt
python main.py &

# Frontend
npm install
npm run dev

# Access: http://localhost:5173
```

---

## Features

### Agent Pipeline
- 🔍 **BTU Web Scraping** — Module catalogue, professor emails, active projects
- 📊 **5-Signal Fit Scoring** — Course overlap, AI research alignment, active grants, open positions, publications
- 📧 **Email Generation** — Personalized outreach in German/English
- 🎯 **Multi-language Support** — Automatic language detection from transcript
- 🚀 **NVIDIA NIM Integration** — Using Llama 3.3 70B for high-quality emails

### Portal
- 👤 **Profile Builder** — Skills, projects, experience, achievements
- 📁 **File Upload** — Transcript, resume, cover letter (drag-and-drop)
- ⚡ **Real-time Progress** — Watch the pipeline run live
- 📈 **Analytics** — Professors found, fit scores, email drafts
- 📥 **Download Results** — Excel file with all emails and metadata
- 🎨 **Modern UI** — React 18 + TypeScript + Tailwind CSS
- 📱 **Responsive Design** — Desktop, tablet, mobile

---

## Tech Stack

### Agent
- **Python 3.11+**
- **FastAPI** — REST API
- **Playwright** — Web scraping
- **NVIDIA NIM** — LLM inference
- **SQLAlchemy** — Database ORM
- **pdfplumber** — PDF parsing

### Portal
- **React 18** + **TypeScript**
- **Vite** — Build tool
- **Tailwind CSS** — Styling
- **Lucide Icons** — Icon library
- **React Router** — Navigation
- **Axios** — HTTP client

### DevOps
- **Docker** — Containerization
- **Docker Compose** — Orchestration
- **Nginx** — Reverse proxy

---

## Documentation

- **[Agent README](./app/README.md)** — Detailed agent pipeline, architecture, scraping logic, 5-signal scoring
- **[Portal README](./portal/README.md)** — Web interface, user flow, API endpoints, deployment

---

## Environment Variables

### Agent (.env in `app/`)
```
NVIDIA_API_KEY=nvapi-...
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
DATABASE_URL=sqlite:///./hiwi.db
```

### Portal Backend (.env in `portal/`)
```
NVIDIA_API_KEY=nvapi-...
DATABASE_URL=sqlite:///./hiwi.db
UPLOAD_DIR=./uploads
```

### Portal Frontend (.env in `portal/`)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=HiWi Applying Agent
```

---

## Workflow

1. **User fills profile** — Skills, projects, achievement
2. **Uploads files** — Transcript (required), resume & cover letter (optional)
3. **Portal starts pipeline** — Calls `/api/process` endpoint
4. **Agent processes data** — 10 steps:
   - Parse transcript courses
   - Search for matching BTU professors
   - Scrape professor profiles
   - Extract contact emails
   - Score fit (5-signal model)
   - Analyze CV against research areas
   - Draft personalized emails
   - Generate follow-up tasks
   - Compile results
   - Return Excel file
5. **User downloads results** — Excel with emails, fit scores, professor info

---

## Deployment

### Heroku
```bash
git push heroku main
heroku open
```

### AWS/GCP/Azure
See individual component READMEs for container-based deployment.

---

## Contributing

Contributions welcome! Areas for improvement:
- [ ] User authentication (Google/GitHub OAuth)
- [ ] Email client integration
- [ ] Professor database (more than just BTU)
- [ ] Follow-up automation
- [ ] Analytics dashboard
- [ ] Multi-university support

---

## License

MIT — Use freely for educational and commercial purposes.

---

## Questions?

- 📖 Read the [Agent README](./app/README.md) for pipeline details
- 🎨 Read the [Portal README](./portal/README.md) for UI/UX info
- 📧 Contact: smafnan5@gmail.com
