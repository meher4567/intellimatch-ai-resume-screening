from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.core.dependencies import get_db
from src.models.match import Match
from src.models.job import Job
from src.models.resume import Resume
from src.schemas.match import MatchCreate, MatchUpdate, MatchResponse
from typing import List
import datetime

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=MatchResponse, summary="Create a match between a resume and a job")
def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == match_data.resume_id, Resume.deleted_at.is_(None)).first()
    job = db.query(Job).filter(Job.id == match_data.job_id, Job.deleted_at.is_(None)).first()
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or Job not found")
    
    # Calculate match score using the matching engine if not provided
    score = match_data.score
    explanation_data = None
    
    if score is None or match_data.include_explanation:
        from src.services.matching_engine import MatchingEngine
        from src.services.skill_extractor import SkillExtractor
        from src.ml.match_scorer import MatchScorer
        
        try:
            matcher = MatchingEngine()
            skill_extractor = SkillExtractor()
            
            # Extract skills from resume and job
            resume_text = resume.raw_text or ""
            job_text = job.description or ""
            
            resume_skills = skill_extractor.extract_skills(resume_text)
            resume_skill_names = [s['name'] for s in resume_skills]
            
            job_skills = skill_extractor.extract_skills(job_text)
            job_skill_names = [s['name'] for s in job_skills]
            
            # Compute match score
            match_result = matcher.match_resume_to_job(
                resume_text=resume_text,
                job_description=job_text,
                resume_skills=resume_skill_names,
                job_requirements=job_skill_names
            )
            
            score = match_result['overall_score'] * 100  # Convert to percentage
            
            # Generate explanation if requested
            if match_data.include_explanation:
                parsed_data = resume.parsed_data_json or {}
                candidate_data = {
                    'name': parsed_data.get('name', 'Unknown'),
                    'skills': resume_skill_names,
                    'experience': parsed_data.get('experience', []),
                    'education': parsed_data.get('education', [])
                }
                job_data = {
                    'title': job.title or 'Unknown',
                    'description': job_text,
                    'required_skills': job_skill_names,
                    'experience_level': job.experience_level or 'Not specified'
                }
                
                # Use MatchScorer to generate explanation
                scorer = MatchScorer()
                explanation_result = scorer.calculate_match(
                    candidate_data,
                    job_data,
                    include_explanation=True
                )
                explanation_data = explanation_result.get('explanation')
                
        except Exception as e:
            print(f"Error computing match score: {e}")
            import traceback
            traceback.print_exc()
            score = 50.0  # Default score if computation fails
    
    match = Match(
        resume_id=match_data.resume_id, 
        job_id=match_data.job_id,
        similarity_score=score,
        created_at=datetime.datetime.utcnow()
    )
    db.add(match)
    try:
        db.commit()
        db.refresh(match)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Match already exists for this resume and job")
    
    # Add explanation to response
    response = MatchResponse.model_validate(match)
    if explanation_data:
        response.explanation = explanation_data
    return response

@router.get("/", response_model=List[MatchResponse], summary="List all matches")
def list_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Match)
    if status:
        query = query.filter(Match.status == status)
    matches = query.offset(skip).limit(limit).all()
    return matches

@router.get("/{match_id}", response_model=MatchResponse, summary="Get match details")
def get_match(
    match_id: int, 
    include_explanation: bool = Query(False, description="Include natural language explanation"),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    response = MatchResponse.model_validate(match)
    
    # Generate explanation if requested
    if include_explanation:
        try:
            from src.services.skill_extractor import SkillExtractor
            from src.ml.match_scorer import MatchScorer
            
            resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
            job = db.query(Job).filter(Job.id == match.job_id).first()
            
            if resume and job:
                skill_extractor = SkillExtractor()
                resume_text = resume.raw_text or ""
                job_text = job.description or ""
                
                resume_skills = skill_extractor.extract_skills(resume_text)
                resume_skill_names = [s['name'] for s in resume_skills]
                
                job_skills = skill_extractor.extract_skills(job_text)
                job_skill_names = [s['name'] for s in job_skills]
                
                parsed_data = resume.parsed_data_json or {}
                candidate_data = {
                    'name': parsed_data.get('name', 'Unknown'),
                    'skills': resume_skill_names,
                    'experience': parsed_data.get('experience', []),
                    'education': parsed_data.get('education', [])
                }
                job_data = {
                    'title': job.title or 'Unknown',
                    'description': job_text,
                    'required_skills': job_skill_names,
                    'experience_level': job.experience_level or 'Not specified'
                }
                
                scorer = MatchScorer()
                explanation_result = scorer.calculate_match(
                    candidate_data,
                    job_data,
                    include_explanation=True
                )
                response.explanation = explanation_result.get('explanation')
        except Exception as e:
            print(f"Error generating explanation: {e}")
            import traceback
            traceback.print_exc()
    
    return response

@router.put("/{match_id}", response_model=MatchResponse, summary="Update a match")
def update_match(match_id: int, update_data: MatchUpdate, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(match, key, value)
    
    match.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(match)
    return match

@router.delete("/{match_id}", summary="Delete a match (soft delete)")
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "deleted"
    match.updated_at = datetime.datetime.utcnow()
    db.commit()
    return {"id": match.id, "deleted": True}

@router.get("/job/{job_id}", response_model=List[MatchResponse], summary="List all matches for a job")
def job_matches(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    matches = db.query(Match).filter(Match.job_id == job_id).offset(skip).limit(limit).all()
    return matches

@router.get("/resume/{resume_id}", response_model=List[MatchResponse], summary="List all matches for a resume")
def resume_matches(
    resume_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    matches = db.query(Match).filter(Match.resume_id == resume_id).offset(skip).limit(limit).all()
    return matches

@router.post(
    "/find",
    summary="Find matching candidates for a job using ML",
    responses={
        200: {
            "description": "List of matching candidates with scores and explanations",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "candidate_id": 7,
                            "candidate_name": "John Doe",
                            "resume_id": 12,
                            "score": 87.5,
                            "skill_match": 92.0,
                            "experience_match": 85.0,
                            "semantic_match": 88.0,
                            "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                            "missing_skills": ["Kubernetes", "AWS"],
                            "quality_score": 89.0,
                            "experience_level": "Senior",
                            "explanation": "Strong match with 4/6 required skills..."
                        }
                    ]
                }
            }
        }
    }
)
def find_matches(
    job_id: int = Query(..., description="ID of the job to find matches for"),
    min_score: float = Query(50.0, ge=0, le=100, description="Minimum match score (0-100) to include in results"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of matches to return"),
    db: Session = Depends(get_db)
):
    """
    Find best matching candidates for a job using ML-powered matching engine.
    
    This endpoint:
    1. Analyzes the job description and requirements
    2. Compares against all active resumes in the database
    3. Computes semantic similarity using embeddings
    4. Calculates skill overlap and experience matching
    5. Returns ranked candidates with detailed explanations
    
    **ML Features:**
    - Semantic text matching using BERT embeddings
    - Skills extraction and comparison
    - Experience level classification
    - Quality score analysis
    - Natural language explanations
    
    **Example Usage:**
    ```
    POST /api/v1/matches/find?job_id=5&min_score=70&limit=10
    ```
    
    Returns top 10 candidates with 70%+ match score for job ID 5.
    """
    from src.services.matching_engine import MatchingEngine
    from src.services.skill_extractor import SkillExtractor
    
    # Get job
    job = db.query(Job).filter(Job.id == job_id, Job.deleted_at.is_(None)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all active resumes
    resumes = db.query(Resume).filter(Resume.deleted_at.is_(None)).all()
    print(f"📋 Found {len(resumes)} resumes in database")
    if not resumes:
        return []
    
    try:
        # First index all resumes into the matching engine
        matcher = MatchingEngine()
        skill_extractor = SkillExtractor()
        
        # Index resumes
        indexed_count = 0
        for resume in resumes:
            parsed_data = resume.parsed_data_json or {}
            
            # Extract name from parsed data
            name = parsed_data.get('name', 'Unknown')
            
            # Extract contact info from parsed data
            contact_info = parsed_data.get('contact_info', {})
            
            # Check if resume has required data
            has_text = bool(parsed_data.get('text', ''))
            has_skills = len(parsed_data.get('skills', [])) > 0
            
            print(f"   Resume {resume.id}: name={name}, text={has_text}, skills={has_skills}")
            
            # Ensure we have basic fields
            resume_data = {
                'resume_id': resume.id,
                'name': name,
                'email': contact_info.get('email', ''),
                'phone': contact_info.get('phone', ''),
                'location': contact_info.get('location', ''),
                'skills': parsed_data.get('skills', []),
                'experience': parsed_data.get('experience', []),
                'education': parsed_data.get('education', []),
                'experience_years': parsed_data.get('total_years_experience', 0),
                'summary': parsed_data.get('summary', ''),
                'raw_text': parsed_data.get('text', '')
            }
            
            if resume_data['raw_text']:  # Only index if we have text
                matcher.index_resume(resume_data, resume_id=str(resume.id))
                indexed_count += 1
        
        print(f"✅ Indexed {indexed_count} resumes successfully")
        
        # Parse job description
        job_text = job.description or ""
        job_parsed = matcher.parse_job(job_text)
        
        # Convert to dict and add job info
        if hasattr(job_parsed, 'to_dict'):
            job_data = job_parsed.to_dict()
        elif hasattr(job_parsed, '__dict__'):
            job_data = job_parsed.__dict__.copy()
        else:
            job_data = dict(job_parsed)
        
        job_data['title'] = job.title
        job_data['job_id'] = job.id
        
        # Find matches using the matching engine
        candidates = matcher.find_matches(
            job_data=job_data,
            top_k=100,
            min_score=min_score / 100.0 if min_score else None
        )
        
        # Format results
        matches = []
        for candidate in candidates[:limit]:
            match_details = candidate.get('match_details', {})
            matches.append({
                'candidate_id': candidate['resume_id'],
                'candidate_name': candidate.get('name', 'Unknown'),
                'score': round(candidate['match_score'] * 100, 2),
                'skill_match': round(match_details.get('skill_score', 0) * 100, 2),
                'experience_match': round(match_details.get('experience_score', 0) * 100, 2),
                'semantic_match': round(match_details.get('semantic_score', 0) * 100, 2),
                'matched_skills': match_details.get('matched_skills', []),
                'missing_skills': match_details.get('missing_skills', []),
                'email': candidate.get('email'),
                'phone': candidate.get('phone'),
                'location': candidate.get('location'),
                'quality_score': round(candidate.get('quality_score', 0) * 100, 2),
                'experience_level': candidate.get('experience_level')
            })
        
        return matches
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error finding matches: {e}")
        raise HTTPException(status_code=500, detail=f"Error computing matches: {str(e)}")
