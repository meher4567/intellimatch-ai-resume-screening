from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.resume import Resume
from src.models.candidate import Candidate
from src.schemas.common import ResumeResponse
from src.services.resume_parser import ResumeParser, get_file_metadata
import shutil
import os
from datetime import datetime

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
        parsed_data = parser.parse_file(file_path)
    except Exception as e:
        # Clean up file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Error parsing resume: {str(e)}")
    
    # Create or update Candidate record
    candidate = None
    if parsed_data.get('email'):
        # Check if candidate exists by email
        candidate = db.query(Candidate).filter(Candidate.email == parsed_data['email']).first()
    
    if not candidate:
        # Create new candidate
        candidate = Candidate(
            name=parsed_data.get('name') or 'Unknown',
            email=parsed_data.get('email'),
            phone=parsed_data.get('phone'),
            skills=', '.join(parsed_data.get('skills', [])),
            experience_years=parsed_data.get('experience_years'),
            education=', '.join(parsed_data.get('education', [])),
            created_at=datetime.utcnow()
        )
        db.add(candidate)
        db.flush()  # Get candidate ID
    
    # Create Resume record
    resume = Resume(
        candidate_id=candidate.id,
        file_path=file_path,
        file_type=file.content_type or f"application/{file_ext.lstrip('.')}",
        source="upload",
        raw_text=parsed_data.get('raw_text'),
        parsed_data=parsed_data,  # Store full parsed data as JSON
        upload_date=datetime.utcnow(),
        status="parsed"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume
