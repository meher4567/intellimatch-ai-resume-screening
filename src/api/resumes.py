from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.resume import Resume
from src.models.candidate import Candidate
from src.schemas.common import ResumeResponse
from src.services.resume_parser import ResumeParser
from typing import List
import shutil
import os
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = "data/raw"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload", summary="Upload and parse a resume file", response_model=ResumeResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a resume file, extract text and metadata, and create candidate profile.
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Save file to disk
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Parse resume to extract data
    parser = ResumeParser()
    try:
        parsed_data = parser.parse(file_path)
    except Exception as e:
        # Clean up file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Error parsing resume: {str(e)}")
    
    # Create Resume record first
    resume = Resume(
        file_path=file_path,
        file_type=file.content_type or f"application/{file_ext.lstrip('.')}",
        parsed_data_json=parsed_data,  # Store full parsed data as JSON
        source="upload",
        upload_date=datetime.utcnow(),
        status="parsed"
    )
    db.add(resume)
    db.flush()  # Get resume ID
    
    # Create Candidate record
    candidate = Candidate(
        resume_id=resume.id,
        extracted_info_json=parsed_data,
        quality_score=None,  # Calculate later
        experience_level=parsed_data.get('experience_level'),
        created_at=datetime.utcnow()
    )
    db.add(candidate)
    db.commit()
    db.refresh(resume)
    
    return resume


@router.post("/batch-upload", summary="Upload multiple resume files")
async def batch_upload_resumes(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    Upload multiple resume files at once.
    Returns summary of successful and failed uploads.
    """
    results = {
        "successful": [],
        "failed": [],
        "total": len(files),
        "success_count": 0,
        "failed_count": 0
    }
    
    for file in files:
        try:
            # Validate file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                results["failed"].append({
                    "filename": file.filename,
                    "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                })
                results["failed_count"] += 1
                continue
            
            # Validate file size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                results["failed"].append({
                    "filename": file.filename,
                    "error": f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                })
                results["failed_count"] += 1
                continue
            
            # Save file
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse resume
            parser = ResumeParser()
            parsed_data = parser.parse(file_path)
            
            # Create resume record first
            resume = Resume(
                file_path=file_path,
                file_type=file.content_type or f"application/{file_ext.lstrip('.')}",
                parsed_data_json=parsed_data,
                source="batch_upload",
                upload_date=datetime.utcnow(),
                status="parsed"
            )
            db.add(resume)
            db.flush()
            
            # Create candidate record
            candidate = Candidate(
                resume_id=resume.id,
                extracted_info_json=parsed_data,
                quality_score=None,
                experience_level=parsed_data.get('experience_level'),
                created_at=datetime.utcnow()
            )
            db.add(candidate)
            db.commit()
            db.refresh(resume)
            
            results["successful"].append({
                "filename": file.filename,
                "candidate_id": candidate.id,
                "resume_id": resume.id,
                "name": parsed_data.get('name')
            })
            results["success_count"] += 1
            
        except Exception as e:
            results["failed"].append({
                "filename": file.filename,
                "error": str(e)
            })
            results["failed_count"] += 1
            # Clean up file if it was saved
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
    
    return results
