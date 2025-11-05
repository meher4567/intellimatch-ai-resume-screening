from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.dependencies import get_db
from src.models.skill import Skill
from src.models.candidate_skill import CandidateSkill
from typing import List, Dict, Any, Optional
import json

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("/", summary="List all skills with usage stats")
def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    List all skills in the database with usage statistics.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Optional search term to filter skills by name
    """
    query = db.query(
        Skill,
        func.count(CandidateSkill.id).label('usage_count')
    ).outerjoin(CandidateSkill).group_by(Skill.id)
    
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))
    
    skills = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "category": skill.category,
            "usage_count": usage_count,
            "created_at": skill.created_at,
            "updated_at": skill.updated_at
        }
        for skill, usage_count in skills
    ]

@router.get("/top", summary="Get top N most used skills")
def get_top_skills(
    n: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get the top N most frequently used skills across all candidates.
    
    - **n**: Number of top skills to return (default: 10)
    """
    top_skills = db.query(
        Skill.name,
        Skill.category,
        func.count(CandidateSkill.id).label('usage_count')
    ).join(CandidateSkill).group_by(Skill.id, Skill.name, Skill.category).order_by(
        func.count(CandidateSkill.id).desc()
    ).limit(n).all()
    
    return [
        {
            "name": name,
            "category": category,
            "count": count
        }
        for name, category, count in top_skills
    ]

@router.get("/categories", summary="Get all skill categories")
def get_skill_categories(db: Session = Depends(get_db)) -> List[str]:
    """
    Get a list of all unique skill categories.
    """
    categories = db.query(Skill.category).distinct().filter(
        Skill.category.isnot(None)
    ).all()
    return [cat[0] for cat in categories if cat[0]]

@router.get("/by-category/{category}", summary="Get skills in a specific category")
def get_skills_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all skills in a specific category.
    
    - **category**: The category name (e.g., "Programming Languages", "Frameworks")
    """
    skills = db.query(Skill).filter(
        Skill.category == category
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "category": skill.category
        }
        for skill in skills
    ]

@router.get("/taxonomy", summary="Get skill taxonomy as hierarchical structure")
def get_skill_taxonomy(db: Session = Depends(get_db)) -> Dict[str, List[str]]:
    """
    Get the complete skill taxonomy organized by category.
    
    Returns a dictionary where keys are categories and values are lists of skill names.
    """
    skills = db.query(Skill).order_by(Skill.category, Skill.name).all()
    
    taxonomy = {}
    for skill in skills:
        category = skill.category or "Uncategorized"
        if category not in taxonomy:
            taxonomy[category] = []
        taxonomy[category].append(skill.name)
    
    return taxonomy

@router.post("/", summary="Add a new skill")
def create_skill(
    name: str,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add a new skill to the database.
    
    - **name**: Skill name (e.g., "Python", "Machine Learning")
    - **category**: Optional category (e.g., "Programming Languages", "Data Science")
    """
    # Check if skill already exists
    existing = db.query(Skill).filter(
        func.lower(Skill.name) == name.lower()
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Skill '{name}' already exists")
    
    skill = Skill(name=name, category=category)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    
    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "created_at": skill.created_at
    }

@router.put("/{skill_id}", summary="Update a skill")
def update_skill(
    skill_id: int,
    name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update an existing skill's name or category.
    
    - **skill_id**: ID of the skill to update
    - **name**: New name (optional)
    - **category**: New category (optional)
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    if name:
        skill.name = name
    if category:
        skill.category = category
    
    db.commit()
    db.refresh(skill)
    
    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "updated_at": skill.updated_at
    }

@router.delete("/{skill_id}", summary="Delete a skill")
def delete_skill(skill_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Delete a skill from the database.
    
    Note: This will also remove all candidate-skill associations.
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill_name = skill.name
    db.delete(skill)
    db.commit()
    
    return {"id": skill_id, "name": skill_name, "deleted": True}
