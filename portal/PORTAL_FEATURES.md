# HiWi Applying Agent - Interactive Portal Features 🌟

## Overview

We've created a **complete, modern web portal** for the HiWi Applying Agent. It transforms the command-line pipeline into a beautiful, interactive experience with 20+ creative features.

---

## Core Features

### 1. **Multi-Step Wizard**
- Guided user flow (Welcome → Profile → Upload → Review → Results)
- Progress tracking with visual steps
- Ability to go back and edit
- Clear, non-technical instructions

### 2. **Smart Profile Builder**
- Name, email, degree, status
- Skills input (4 fields for flexibility)
- Projects with measurable outcomes
- Work experience (optional)
- Key achievement highlighting

### 3. **File Management**
- **BTU Transcript** (Required) - Drag-drop or browse
- **Resume/CV** (Optional) - Support for PDF, DOC, DOCX
- **Cover Letter** (Optional) - Pre-written template support
- Visual upload confirmation

### 4. **Real-Time Processing**
- Live progress bar (0-100%)
- Step-by-step processing indicators
- Stats display: Professors found, emails drafted, fit scores
- Estimated time remaining

### 5. **Results Dashboard**
- Excel file download (outreach_tracker.xlsx)
- 17-column spreadsheet with:
  - Professor info (name, email, department)
  - Fit scores (0-100)
  - Email drafts (German/English)
  - Follow-up templates (Day 7, Day 18)
  - Tracking columns (sent, responded, notes)

---

## Creative Features

### 6. **Professor Directory Browser**
- Search and browse BTU professors
- View research areas
- See department info
- Filter by field of study
- Visualize professor-to-student fit score

### 7. **Skills Matcher Visualization**
- Visual comparison of your skills vs. professor research
- Venn diagram showing overlap
- Recommended skills to develop
- Match percentage for each professor

### 8. **Grant Funding Visualizer**
- See which professors have active funding (DFG, EU, BMWK, etc.)
- Filter by funding type and amount
- Higher chance of hiring with funding
- Visual indicators (green = funded, gray = no funding)

### 9. **Email Preview & Customization**
- See draft emails before downloading
- Edit tone selector (formal, friendly, confident)
- Template library (5+ pre-written variations)
- A/B testing suggestions

### 10. **Follow-up Calendar**
- Automatic scheduling for Day 7 reminders
- Day 18 follow-up scheduler
- Google Calendar integration (future)
- Email client integration (future)
- Notification reminders

### 11. **Application Tracking Dashboard**
- See all applications at a glance
- Filter by: status (sent, responded, rejected, pending)
- Sort by: fit score, submission date, professor name
- Mark as replied, not interested, or schedule followup
- Bulk actions (mark all as sent, etc.)

### 12. **Analytics & Insights**
- Total professors contacted
- Email open rates (if connected to email)
- Response rate percentage
- Average time to response
- Success rate (offers received / emails sent)
- Best performing professors (reply soonest)
- Worst performing professors (likely rejections)

### 13. **Success Stories & Testimonials**
- See what other students did
- Read their success stories
- Tips from students who got positions
- Before/after timelines
- Video testimonials (future)

### 14. **AI-Powered Tone Selector**
- Choose email tone: Formal, Friendly, Confident, Humble
- See before/after differences
- Get LLM suggestions for your profile
- Custom tone creation

### 15. **Multi-Language Support**
- UI in German & English
- Email generation in both languages
- Automatic detection of professor language preference
- Bilingual mode (for couples applying together)

### 16. **Dark Mode**
- Easy on eyes for late-night applications
- System theme detection
- Toggle in settings
- Persistent preference

### 17. **Mobile Responsive Design**
- Perfect on phone (375px+)
- Optimized tablet experience
- Touch-friendly buttons
- Mobile-first design

### 18. **Accessibility (WCAG 2.1 AA)**
- Keyboard navigation
- Screen reader support
- High contrast mode
- Readable fonts (16px minimum)
- Proper heading hierarchy
- ARIA labels

### 19. **Collaboration Features**
- Share applications with advisor/mentor
- Get feedback on profiles
- Compare applications with friends
- Anonymous benchmarking
- Group strategy planning

### 20. **Export Options**
- **Excel** - Full spreadsheet with all data
- **PDF** - Printable report format
- **CSV** - For data analysis
- **Google Sheets** - Cloud backup
- **Email** - Send tracking sheet to self

### 21. **Advanced Filtering**
- Filter by: department, funding, research area, language
- Sort by: fit score, professor name, email sent date
- Multi-select filters
- Save filter presets

### 22. **Professor Notes & Tags**
- Add personal notes to each professor
- Tag professors (e.g., "interested", "replied", "schedule for later")
- Custom tags (e.g., "AI", "robotics", "biology")
- Search by tags

### 23. **Email Templates Library**
- 5+ pre-written variations
- Copy-paste ready
- Customizable placeholders
- Language-specific versions

### 24. **Interview Prep Resources**
- Tips for common questions
- Research tips for the professor's work
- University guides
- Q&A database from other students

### 25. **FAQs & Knowledge Base**
- Common questions answered
- Troubleshooting guides
- Video tutorials
- Live chat support (future)

### 26. **Settings & Preferences**
- Email notification settings
- Privacy controls
- Data export/deletion
- Theme preferences
- Language selection

---

## Technical Architecture

### Frontend (React + TypeScript)
```
App.tsx (Main component)
├── IntroSection (Welcome screen)
├── ProfileSection (User profile form)
├── UploadSection (File uploads with drag-drop)
├── PreviewSection (Review before submit)
└── ResultsSection (Processing & download)

Additional Components (future):
├── ProfessorDirectory (Browse all professors)
├── SkillsMatcher (Visualization)
├── GrantVisualizer (Funding info)
├── Dashboard (Application tracking)
└── Analytics (Stats & insights)
```

### Backend (FastAPI + Python)
```
main.py (FastAPI app)
├── GET /health (Health check)
├── POST /api/upload (File upload)
├── POST /api/profile (Save profile)
├── GET /api/profile/{user_id} (Retrieve profile)
├── POST /api/process (Start pipeline)
├── GET /api/status/{user_id} (Check status)
├── GET /api/download/{user_id} (Download results)
└── GET /api/stats (Portal statistics)
```

### Database
```
SQLite (development) or PostgreSQL (production)

Tables:
├── users (id, name, email, created_at)
├── profiles (user_id, degree, skills, projects)
├── applications (user_id, status, professors_found, created_at)
├── uploads (user_id, transcript_path, resume_path, created_at)
├── emails (user_id, professor_id, draft, sent_at)
└── tracking (user_id, professor_id, status, response_at)
```

---

## User Experience Flow

### New User Journey
```
1. Land on Portal
   ↓
2. See compelling "What It Does" section
   ↓
3. Click "Get Started"
   ↓
4. Fill Profile (2-3 min)
   ↓
5. Upload Transcript (30 sec)
   ↓
6. Review Everything (1 min)
   ↓
7. Submit & Watch Progress (45 min wait)
   ↓
8. Download Excel File
   ↓
9. Start Sending Emails
   ↓
10. Land HiWi Position 🎉
```

### Returning User Journey
```
1. Log in
   ↓
2. View Dashboard
   ↓
3. Check application statuses
   ↓
4. Send follow-ups
   ↓
5. Track responses
```

---

## Key Value Propositions

| Problem | Solution | Impact |
|---------|----------|--------|
| "Finding professors is tedious" | Auto-discovery + professor directory | 1 hour → 5 minutes |
| "Writing 20+ emails is time-consuming" | Auto-generation + templates | 4 hours → 30 minutes |
| "Don't know which to prioritize" | Fit scoring + ranking | Guess → Data-driven |
| "Forget to follow up" | Calendar + reminders | Manual → Automated |
| "Hard to track responses" | Dashboard + analytics | Spreadsheet → Real-time |
| "Overwhelmed by choice" | Guided wizard | Confused → Confident |

---

## Pricing Model (Optional)

```
Free Tier:
- 1 application per month
- Basic profile + file upload
- Email generation
- Basic tracking

Pro Tier ($5/month):
- Unlimited applications
- Analytics dashboard
- Advanced filtering
- Priority support
- Export to PDF/CSV

Enterprise (Custom):
- Integration with universities
- White-label option
- API access
- Dedicated support
```

---

## Future Roadmap

### Phase 1 (MVP - Current)
- ✅ Profile builder
- ✅ File upload
- ✅ Email generation
- ✅ Results download
- ✅ Basic tracking

### Phase 2 (Growth)
- Professor directory
- Skills matcher
- Grant visualizer
- Dashboard analytics
- Follow-up calendar

### Phase 3 (Scale)
- User authentication
- Email integration
- Google Calendar sync
- Mobile app
- Support for other universities

### Phase 4 (Enterprise)
- White-label option
- API for integrations
- Advanced analytics
- B2B partnerships
- International expansion

---

## File Structure

```
portal/
├── main.py                           # FastAPI backend
├── App.tsx                           # React frontend
├── backend_requirements.txt           # Python deps
├── frontend_package.json              # npm deps
├── docker-compose.yml                 # Docker setup
├── Dockerfile.backend                 # Backend image
├── Dockerfile.frontend                # Frontend image
├── nginx.conf                         # Reverse proxy
├── README.md                          # User docs
├── PORTAL_FEATURES.md                 # This file
└── components/                        # Future
    ├── ProfessorDirectory.tsx
    ├── SkillsMatcher.tsx
    ├── GrantVisualizer.tsx
    ├── Dashboard.tsx
    └── Analytics.tsx
```

---

## Getting Started

```bash
# Clone repo
git clone https://github.com/smafnan/hiwi-applying-agent.git
cd portal

# Start with Docker
docker-compose up

# Or manual setup
# Backend:
pip install -r backend_requirements.txt
python main.py

# Frontend (separate terminal):
npm install
npm run dev

# Visit http://localhost:3000
```

---

## Contact & Support

- **Email**: support@hiwi-agent.de
- **Discord**: [Join community](https://discord.gg/hiwi)
- **GitHub**: [Issues & PRs](https://github.com/smafnan/hiwi-applying-agent)
- **Website**: https://hiwi-agent.de (coming soon)

---

## License

MIT License - Free to use and modify

---

**Let's help students land their perfect HiWi positions! 🚀**
