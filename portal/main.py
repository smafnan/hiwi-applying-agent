"""
HiWi Applying Agent - Interactive Portal Backend
FastAPI application for managing HiWi applications
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from pathlib import Path
import json
import uuid
from datetime import datetime
import asyncio
import subprocess

app = FastAPI(
    title="HiWi Applying Agent Portal",
    description="Interactive portal for finding and applying to HiWi positions at BTU",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# ============ Data Models ============

class UserProfile(BaseModel):
    name: str
    degree: str
    degree_status: str
    email: EmailStr
    top_skills: List[str]
    strongest_projects: List[str]
    key_achievement: str
    work_experience: List[dict]

class ApplicationRequest(BaseModel):
    user_id: str
    profile: UserProfile
    transcript_uploaded: bool
    resume_uploaded: bool
    cover_letter_uploaded: bool

class ApplicationStatus(BaseModel):
    user_id: str
    status: str  # "uploaded", "processing", "completed", "failed"
    professors_found: int = 0
    emails_drafted: int = 0
    error_message: Optional[str] = None
    output_file: Optional[str] = None
    created_at: str
    updated_at: str

# ============ Routes ============

@app.get("/")
async def root():
    return {
        "message": "HiWi Applying Agent Portal API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/api/upload",
            "profile": "/api/profile",
            "process": "/api/process",
            "status": "/api/status/{user_id}",
            "download": "/api/download/{user_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============ File Upload ============

@app.post("/api/upload")
async def upload_files(
    user_id: str = Form(...),
    transcript: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    cover_letter: Optional[UploadFile] = File(None)
):
    """Upload files (transcript, resume, cover letter)"""

    user_dir = UPLOADS_DIR / user_id
    user_dir.mkdir(exist_ok=True)

    uploaded = {}

    # Save transcript
    if transcript:
        transcript_path = user_dir / "transcript.pdf"
        contents = await transcript.read()
        with open(transcript_path, "wb") as f:
            f.write(contents)
        uploaded["transcript"] = str(transcript_path)

    # Save resume
    if resume:
        resume_path = user_dir / "resume.pdf"
        contents = await resume.read()
        with open(resume_path, "wb") as f:
            f.write(contents)
        uploaded["resume"] = str(resume_path)

    # Save cover letter
    if cover_letter:
        cover_letter_path = user_dir / "cover_letter.pdf"
        contents = await cover_letter.read()
        with open(cover_letter_path, "wb") as f:
            f.write(contents)
        uploaded["cover_letter"] = str(cover_letter_path)

    return {
        "message": "Files uploaded successfully",
        "user_id": user_id,
        "uploaded_files": list(uploaded.keys()),
        "timestamp": datetime.now().isoformat()
    }

# ============ Profile Management ============

@app.post("/api/profile")
async def save_profile(user_id: str, profile: UserProfile):
    """Save user profile"""

    user_dir = UPLOADS_DIR / user_id
    user_dir.mkdir(exist_ok=True)

    profile_path = user_dir / "profile.json"

    with open(profile_path, "w") as f:
        json.dump(profile.dict(), f, indent=2)

    return {
        "message": "Profile saved successfully",
        "user_id": user_id,
        "profile_path": str(profile_path),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    """Retrieve user profile"""

    profile_path = UPLOADS_DIR / user_id / "profile.json"

    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Profile not found")

    with open(profile_path, "r") as f:
        profile = json.load(f)

    return profile

# ============ Processing ============

@app.post("/api/process")
async def process_application(application: ApplicationRequest):
    """Trigger the HiWi agent pipeline"""

    user_dir = UPLOADS_DIR / application.user_id

    if not user_dir.exists():
        raise HTTPException(status_code=404, detail="User directory not found")

    # Create status file
    status_path = user_dir / "status.json"
    status = {
        "user_id": application.user_id,
        "status": "processing",
        "professors_found": 0,
        "emails_drafted": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    with open(status_path, "w") as f:
        json.dump(status, f, indent=2)

    # Here you would trigger the main.py from the hiwi-applying-agent
    # For now, we'll just return a success message

    return {
        "message": "Processing started",
        "user_id": application.user_id,
        "timestamp": datetime.now().isoformat(),
        "check_status_at": f"/api/status/{application.user_id}"
    }

@app.get("/api/status/{user_id}")
async def get_application_status(user_id: str):
    """Get application processing status"""

    status_path = UPLOADS_DIR / user_id / "status.json"

    if not status_path.exists():
        return {
            "user_id": user_id,
            "status": "not_started",
            "message": "No application found"
        }

    with open(status_path, "r") as f:
        status = json.load(f)

    return status

# ============ Output Download ============

@app.get("/api/download/{user_id}")
async def download_results(user_id: str):
    """Download the generated Excel file"""

    output_path = UPLOADS_DIR / user_id / "output" / "outreach_tracker.xlsx"

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Results not ready yet")

    return {
        "message": "Download results",
        "file_path": str(output_path),
        "user_id": user_id
    }

# ============ Analytics ============

@app.get("/api/stats")
async def get_stats():
    """Get portal statistics"""

    user_count = len(list(UPLOADS_DIR.iterdir())) if UPLOADS_DIR.exists() else 0

    return {
        "total_users": user_count,
        "timestamp": datetime.now().isoformat()
    }

# ============ Error Handling ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
