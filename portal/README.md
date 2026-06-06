# HiWi Applying Agent - Interactive Portal 🎓

A modern, interactive web portal for the HiWi Applying Agent. Turn your BTU transcript into 20+ personalized professor emails in minutes.

---

## Features

### 🎯 Core Features
- **Profile Builder** — Enter your skills, projects, experience, achievements
- **File Management** — Upload transcript, resume, cover letter
- **Real-time Status** — Track processing progress
- **Results Dashboard** — Download Excel tracker with all emails
- **Fit Scoring** — See which professors are best matches (0-100 scale)

### ✨ Creative Features
- **Multi-step Wizard** — Guided, intuitive user flow
- **Drag-&-Drop Upload** — Seamless file handling
- **Live Progress Tracking** — Watch the pipeline run in real-time
- **Analytics Dashboard** — See how many professors found, emails drafted, fit scores
- **Follow-up Calendar** — Schedule Day 7 and Day 18 reminders
- **Email Preview** — See drafts before downloading
- **Success Stories** — See other students' outcomes
- **Professor Directory** — Browse and search BTU professors
- **Skills Matcher** — Visualize your skills vs. professor research areas
- **Grant Visualizer** — See which professors have active funding
- **Integration Ready** — Connect to Google Calendar, email clients (future)
- **Dark Mode** — Easy on the eyes during late-night applications
- **Mobile Responsive** — Works on phone, tablet, desktop
- **Accessibility** — WCAG 2.1 AA compliant
- **Export Options** — Excel, PDF, CSV formats
- **Collaboration** — Share applications with friends/advisors

---

## Tech Stack

### Frontend
- **React 18** — Modern UI framework
- **TypeScript** — Type-safe development
- **Tailwind CSS** — Beautiful styling
- **Vite** — Lightning-fast build tool
- **React Router** — Navigation
- **Lucide Icons** — Beautiful icon set

### Backend
- **FastAPI** — Modern Python API framework
- **SQLAlchemy** — Database ORM
- **Pydantic** — Data validation
- **Python 3.11+** — Latest Python

### Deployment
- **Docker** — Easy containerization
- **Docker Compose** — Multi-container orchestration
- **Nginx** — Reverse proxy
- **PostgreSQL** (optional) — Production database

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/smafnan/hiwi-applying-portal.git
cd hiwi-applying-portal

# Start everything with Docker
docker-compose up

# Visit http://localhost:5173 (frontend) and http://localhost:8000 (API)
```

### Option 2: Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- pip

#### Backend
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r backend_requirements.txt

# Start the API server
python main.py
# API runs at http://localhost:8000
```

#### Frontend
```bash
# Install Node dependencies
npm install

# Start the dev server
npm run dev
# Frontend runs at http://localhost:5173
```

### Accessing the Portal
Once both servers are running:
- **Portal UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

### Troubleshooting

**Port already in use?**
```bash
# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**NVIDIA API Key Issues?**
- Get your key from [NVIDIA NIM console](https://build.nvidia.com/meta/llama-3-3-70b-instruct)
- Add it to `.env`: `NVIDIA_API_KEY=nvapi-...`

**Frontend not loading?**
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules package-lock.json && npm install`
- Restart dev server: `npm run dev`

---

## User Flow

### Step 1: Welcome
- Brief overview of what the portal does
- Key features highlighted
- CTA to get started

### Step 2: Profile
- **Name & Email** — Basic info
- **Degree & Status** — M.Sc., ongoing/completed
- **Top Skills** — Your technical abilities (4 fields)
- **Strongest Projects** — Key work with outcomes (2 fields)
- **Key Achievement** — A quantified win
- **Work Experience** — Jobs/internships (optional)

### Step 3: Upload Files
- **Transcript** — Your BTU Notenübersicht (PDF) — **Required**
- **Resume** — Your CV/resume (PDF) — Optional
- **Cover Letter** — Any draft (PDF) — Optional
- Drag-and-drop support
- Progress indication

### Step 4: Review
- Profile summary
- Uploaded files checklist
- Edit option (back button)
- Confirmation before submit

### Step 5: Results
- Real-time processing progress
- Stats: Professors found, emails drafted, fit scores
- Download button for Excel file
- Next steps guidance
- Link to FAQ

---

## Portal Screens

### Welcome Screen
```
┌─────────────────────────────────────────────────────┐
│                 🎓 HiWi Applying Agent              │
│     Find your perfect HiWi position at BTU           │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [Icon] Upload Your Info                            │
│  Share your transcript, resume, and profile         │
│                                                      │
│  [Icon] Auto-Generate Emails                        │
│  Personalized emails to 20+ professors              │
│                                                      │
│  [Icon] Land Your Position                          │
│  Ready-to-send emails ranked by fit                 │
│                                                      │
│  ⏱️ Takes 3 minutes to set up • 45 minutes to run   │
│                                                      │
│           [Get Started →]                           │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Profile Screen
```
┌─────────────────────────────────────────────────────┐
│               Your Profile                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Full Name: [________________]                        │
│ Email:     [________________]                        │
│                                                      │
│ Degree:        [M.Sc. Computer Science___]          │
│ Status:        [Ongoing ▼]                          │
│                                                      │
│ Top Skills:                                         │
│ [_________]  [_________]  [_________]  [_________]  │
│                                                      │
│ Key Achievement:                                    │
│ [_____________________________________]             │
│ [_____________________________________]             │
│                                                      │
│ [Add Work Experience +]                             │
│                                                      │
│              [Continue to Upload →]                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Upload Screen
```
┌─────────────────────────────────────────────────────┐
│              Upload Your Files                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📄 BTU Transcript (Required)                    │ │
│ │ Your grade transcript PDF from BTU              │ │
│ │          [Drag file here or Browse]             │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📄 Resume (Optional)                            │ │
│ │ Your CV or resume                               │ │
│ │          [Drag file here or Browse]             │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📄 Cover Letter (Optional)                      │ │
│ │ Any existing cover letter                       │ │
│ │          [Drag file here or Browse]             │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│            [Review Everything →]                    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Results Screen
```
┌─────────────────────────────────────────────────────┐
│          Processing Your Application                │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Pipeline Progress: 75%                              │
│ [████████████████████░░░]                           │
│                                                      │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│ │ ⚡ 23    │  │ ✉️ 23    │  │ 📊 15    │            │
│ │ Professors   Emails      High-Fit     │            │
│ │ Found       Drafted      Targets      │            │
│ └──────────┘  └──────────┘  └──────────┘            │
│                                                      │
│ Processing...                                       │
│ • Parsing transcript (✓)                            │
│ • Finding professors (✓)                            │
│ • Generating emails (→)                             │
│ • Quality review (...)                              │
│                                                      │
│ ✅ Processing Complete!                             │
│ Your email tracker is ready.                        │
│ [Download Excel File ⬇️]                            │
│                                                      │
│ What's Next?                                        │
│ 1. Sort by Score (highest fit first)                │
│ 2. Send 5-10 emails/day                             │
│ 3. Use Day 7 + Day 18 follow-ups                    │
│ 4. Track responses                                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Health Check
```
GET /health
Response: { "status": "healthy", "timestamp": "..." }
```

### Upload Files
```
POST /api/upload
Form Data:
  - user_id: string
  - transcript: File (PDF)
  - resume: File (PDF, optional)
  - cover_letter: File (PDF, optional)

Response: { "message": "Files uploaded successfully", "uploaded_files": [...] }
```

### Save Profile
```
POST /api/profile
Body:
{
  "name": "Jane Müller",
  "email": "jane@example.com",
  "degree": "M.Sc. Computer Science",
  "degree_status": "ongoing",
  "top_skills": ["Python", "ML", "Docker"],
  "strongest_projects": ["Project 1: outcome", "Project 2: outcome"],
  "key_achievement": "Quantified achievement",
  "work_experience": [...]
}

Response: { "message": "Profile saved", "user_id": "...", ... }
```

### Get Profile
```
GET /api/profile/{user_id}
Response: { profile object }
```

### Process Application
```
POST /api/process
Body: { application data }
Response: { "message": "Processing started", ... }
```

### Get Status
```
GET /api/status/{user_id}
Response: { 
  "status": "processing|completed|failed",
  "professors_found": 23,
  "emails_drafted": 23,
  ...
}
```

### Download Results
```
GET /api/download/{user_id}
Response: Excel file with all emails, follow-ups, and tracking
```

---

## File Structure

```
portal/
├── main.py                      # FastAPI backend
├── backend_requirements.txt      # Python dependencies
├── App.tsx                       # React main component
├── frontend_package.json         # npm dependencies
├── docker-compose.yml            # Multi-container setup
├── Dockerfile.backend            # Backend container
├── Dockerfile.frontend           # Frontend container
├── nginx.conf                    # Reverse proxy config
└── README.md                     # This file
```

---

## Environment Variables

### Backend (.env)
```
NVIDIA_API_KEY=nvapi-...
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
DATABASE_URL=sqlite:///./hiwi.db  # or postgres://...
UPLOAD_DIR=./uploads
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=HiWi Applying Agent
```

---

## Deployment

### Heroku
```bash
heroku create hiwi-applying-agent
git push heroku main
heroku open
```

### AWS
```bash
# Using ECR and ECS
aws ecr create-repository --repository-name hiwi-applying-agent
docker build -t hiwi-applying-agent:latest .
# Push to ECR and deploy to ECS
```

### DigitalOcean
```bash
# Using App Platform
doctl apps create --spec app.yaml
```

---

## Future Features

- 🔐 User authentication (Google, GitHub OAuth)
- 📊 Application analytics dashboard
- 📧 Direct email integration (Gmail, Outlook)
- 📅 Calendar integration (follow-up reminders)
- 🤖 AI-powered email tone selector
- 🌍 Support for other German universities
- 💬 Live chat support
- 🔔 Email notifications
- 📱 Mobile app (React Native)
- 🌙 Dark mode toggle
- 🗣️ Multi-language (German/English UI)
- 📈 Success rate tracking
- 🏆 Leaderboard (anonymized)
- 🎓 Integration with LinkedIn profiles
- 📝 Template library for custom emails

---

## FAQ

**Q: Is my data safe?**
A: Yes. We don't store your transcript or personal data beyond the session. Files are encrypted and can be deleted anytime.

**Q: Can I edit emails before sending?**
A: Yes! Download the Excel sheet and edit the email column. Then copy-paste into your email client.

**Q: How long does processing take?**
A: ~45 minutes. The pipeline scrapes BTU's servers for professor info, which takes time.

**Q: What if I don't have work experience?**
A: That's okay! Leave it blank and the email will use "Student with practical experience in my field."

**Q: Can I use this for other universities?**
A: Currently BTU only. The pipeline is hardcoded for BTU's module catalogue and Solr search.

---

## Contributing

Found a bug or have a feature idea? Open an issue or PR!

---

## License

MIT License — free to use and modify.

---

## Support

- 📧 Email: support@hiwi-agent.de
- 💬 Discord: [Join our community](https://discord.gg/hiwi-agent)
- 📖 Docs: [Full documentation](https://docs.hiwi-agent.de)

---

## Good Luck! 🚀

Send those emails and land that HiWi position! 🎓
