from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.resume import Resume
from src.models.candidate import Candidate
from src.schemas.common import ResumeResponse
from src.services.resume_parser import ResumeParser
from src.utils.file_validation import validate_file_upload, sanitize_filename
from typing import List
import shutil
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = "data/raw"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.get("/", summary="List all resumes", response_model=List[ResumeResponse])
def list_resumes(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    List all resumes in the database with pagination and filtering.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Filter by status (parsed, failed, etc.)
    """
    query = db.query(Resume).filter(Resume.deleted_at.is_(None))
    
    if status:
        query = query.filter(Resume.status == status)
    
    resumes = query.offset(skip).limit(limit).all()
    
    # Build enhanced responses
    responses = []
    for resume in resumes:
        response = ResumeResponse.model_validate(resume)
        parsed_data = resume.parsed_data_json or {}
        skills_data = parsed_data.get('skills', {})
        if isinstance(skills_data, dict):
            response.skills_with_proficiency = skills_data.get('enhanced', [])
            response.proficiency_summary = skills_data.get('proficiency_summary', {})
        response.career_timeline = parsed_data.get('career_timeline', {})
        responses.append(response)
    
    return responses


@router.get("/{resume_id}", summary="Get resume by ID", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific resume.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id, 
        Resume.deleted_at.is_(None)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Build enhanced response
    response = ResumeResponse.model_validate(resume)
    parsed_data = resume.parsed_data_json or {}
    skills_data = parsed_data.get('skills', {})
    if isinstance(skills_data, dict):
        response.skills_with_proficiency = skills_data.get('enhanced', [])
        response.proficiency_summary = skills_data.get('proficiency_summary', {})
    response.career_timeline = parsed_data.get('career_timeline', {})
    
    return response


@router.post("/upload", summary="Upload and parse a resume file", response_model=ResumeResponse)
def upload_resume(file: UploadFile = File(..., description="Resume file (PDF, DOC, DOCX, max 10MB)"), db: Session = Depends(get_db)):
    """
    Upload a resume file, extract text and metadata, and create candidate profile.
    
    This endpoint:
    - Validates file type (PDF, DOC, DOCX only)
    - Validates file size (max 10MB)
    - Extracts text, skills, experience, education
    - Creates resume and candidate records
    - Returns parsed resume data with quality score
    
    **Example Request:**
    ```
    curl -X POST "http://localhost:8000/api/v1/resumes/upload" \\
         -F "file=@john_doe_resume.pdf"
    ```
    
    **Response includes:**
    - Personal information (name, email, phone)
    - Skills with proficiency levels
    - Work experience timeline
    - Education details
    - Quality score (0-10)
    """
    logger.info(f"Upload request received: {file.filename}")
    
    # Validate file using comprehensive validation
    try:
        validate_file_upload(file)
    except HTTPException as e:
        logger.warning(f"File validation failed: {e.detail}")
        raise
    
    # Save file to disk with sanitized filename
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    sanitized_name = sanitize_filename(file.filename)
    safe_filename = f"{timestamp}_{sanitized_name}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    logger.info(f"Saving file to: {file_path}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved successfully: {safe_filename}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Parse resume to extract data
    parser = ResumeParser()
    try:
        logger.info(f"Parsing resume: {safe_filename}")
        parsed_data = parser.parse(file_path)
        logger.info(f"Resume parsed successfully: {parsed_data.get('personal_info', {}).get('name', 'Unknown')}")
    except Exception as e:
        # Clean up file if parsing fails
        logger.error(f"Error parsing resume: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up failed upload: {file_path}")
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
    
    # Build enhanced response with proficiency and timeline data
    response = ResumeResponse.model_validate(resume)
    skills_data = parsed_data.get('skills', {})
    if isinstance(skills_data, dict):
        response.skills_with_proficiency = skills_data.get('enhanced', [])
        response.proficiency_summary = skills_data.get('proficiency_summary', {})
    response.career_timeline = parsed_data.get('career_timeline', {})
    
    return response


@router.post("/batch-upload", summary="Upload multiple resume files")
async def batch_upload_resumes(
    files: List[UploadFile] = File(..., description="Multiple resume files (PDF, DOC, DOCX)"),
    db: Session = Depends(get_db)
):
    """
    Upload multiple resume files at once for bulk processing.
    
    This endpoint processes multiple resumes in a single request:
    - Validates each file independently
    - Continues processing even if some files fail
    - Returns detailed success/failure report
    - Ideal for bulk candidate imports
    
    **Example Request:**
    ```
    curl -X POST "http://localhost:8000/api/v1/resumes/batch-upload" \\
         -F "files=@resume1.pdf" \\
         -F "files=@resume2.pdf" \\
         -F "files=@resume3.docx"
    ```
    
    **Response includes:**
    - Total count and success/failure counts
    - List of successfully uploaded resumes with IDs
    - List of failed uploads with error messages
    """
    logger.info(f"Batch upload request: {len(files)} files")
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


@router.put("/{resume_id}", summary="Update resume metadata", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Update resume metadata (status, etc.).
    Does not re-parse the file.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.deleted_at.is_(None)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Update fields
    if status:
        resume.status = status
    
    resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(resume)
    
    # Build enhanced response
    response = ResumeResponse.model_validate(resume)
    parsed_data = resume.parsed_data_json or {}
    skills_data = parsed_data.get('skills', {})
    if isinstance(skills_data, dict):
        response.skills_with_proficiency = skills_data.get('enhanced', [])
        response.proficiency_summary = skills_data.get('proficiency_summary', {})
    response.career_timeline = parsed_data.get('career_timeline', {})
    
    return response


@router.delete("/{resume_id}", summary="Delete resume (soft delete)")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a resume. Sets deleted_at timestamp.
    The resume can still be recovered if needed.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.deleted_at.is_(None)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Soft delete
    resume.deleted_at = datetime.utcnow()
    resume.status = "deleted"
    db.commit()
    
    return {
        "id": resume_id,
        "deleted": True,
        "deleted_at": resume.deleted_at
    }


@router.post("/{resume_id}/reparse", summary="Re-parse an existing resume file", response_model=ResumeResponse)
def reparse_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Re-parse an existing resume file with the latest parser.
    Useful when parser logic is improved.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.deleted_at.is_(None)
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on disk")
    
    # Re-parse
    parser = ResumeParser()
    try:
        parsed_data = parser.parse(resume.file_path)
        resume.parsed_data_json = parsed_data
        resume.status = "parsed"
        resume.updated_at = datetime.utcnow()
        
        # Update candidate record if exists
        candidate = db.query(Candidate).filter(Candidate.resume_id == resume_id).first()
        if candidate:
            candidate.extracted_info_json = parsed_data
            candidate.experience_level = parsed_data.get('experience_level')
            candidate.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(resume)
        
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error re-parsing resume: {str(e)}")
    
    # Build enhanced response
    response = ResumeResponse.model_validate(resume)
    skills_data = parsed_data.get('skills', {})
    if isinstance(skills_data, dict):
        response.skills_with_proficiency = skills_data.get('enhanced', [])
        response.proficiency_summary = skills_data.get('proficiency_summary', {})
    response.career_timeline = parsed_data.get('career_timeline', {})
    
    return response
