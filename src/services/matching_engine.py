"""
Semantic Matching Engine
Uses sentence transformers to compute similarity between resumes and job descriptions.
"""
from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class MatchingEngine:
    """
    Semantic matching engine for resume-job matching.
    Uses sentence transformers for embedding and cosine similarity for scoring.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the matching engine.
        
        Args:
            model_name: Name of the sentence transformer model
                       Options: 'all-MiniLM-L6-v2' (fast, lightweight)
                               'all-mpnet-base-v2' (better quality, slower)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load the sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"Warning: Could not load model {self.model_name}: {e}")
            self.model = None
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1: First text (e.g., resume)
            text2: Second text (e.g., job description)
            
        Returns:
            Similarity score between 0 and 1
        """
        if not self.model:
            # Fallback to keyword-based matching if model not loaded
            return self._keyword_similarity(text1, text2)
        
        # Encode texts to embeddings
        embeddings = self.model.encode([text1, text2])
        
        # Compute cosine similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return float(similarity)
    
    def match_resume_to_job(
        self, 
        resume_text: str, 
        job_description: str,
        resume_skills: List[str] = None,
        job_requirements: List[str] = None
    ) -> Dict[str, any]:
        """
        Comprehensive matching between a resume and job.
        
        Args:
            resume_text: Full resume text
            job_description: Full job description
            resume_skills: Extracted skills from resume
            job_requirements: Required skills from job
            
        Returns:
            Dictionary with overall score and breakdown
        """
        scores = {}
        
        # 1. Semantic similarity (40% weight)
        semantic_score = self.compute_similarity(resume_text, job_description)
        scores['semantic_similarity'] = semantic_score
        
        # 2. Skill match (40% weight)
        if resume_skills and job_requirements:
            skill_score = self._skill_match_score(resume_skills, job_requirements)
        else:
            skill_score = 0.5  # Default if skills not provided
        scores['skill_match'] = skill_score
        
        # 3. Keyword match (20% weight)
        keyword_score = self._keyword_similarity(resume_text, job_description)
        scores['keyword_match'] = keyword_score
        
        # Compute weighted overall score
        overall_score = (
            semantic_score * 0.4 +
            skill_score * 0.4 +
            keyword_score * 0.2
        )
        
        scores['overall_score'] = overall_score
        scores['percentage'] = round(overall_score * 100, 2)
        
        return scores
    
    def rank_candidates(
        self,
        resumes: List[Dict[str, any]],
        job_description: str,
        job_requirements: List[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, any]]:
        """
        Rank multiple resumes against a job description.
        
        Args:
            resumes: List of resume dictionaries with 'text' and 'skills'
            job_description: Job description text
            job_requirements: Required skills
            top_k: Number of top candidates to return
            
        Returns:
            List of ranked resume dictionaries with scores
        """
        ranked = []
        
        for resume in resumes:
            match_result = self.match_resume_to_job(
                resume_text=resume.get('text', ''),
                job_description=job_description,
                resume_skills=resume.get('skills', []),
                job_requirements=job_requirements
            )
            
            ranked.append({
                **resume,
                **match_result
            })
        
        # Sort by overall score descending
        ranked.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return ranked[:top_k]
    
    def _skill_match_score(
        self, 
        resume_skills: List[str], 
        job_requirements: List[str]
    ) -> float:
        """
        Calculate skill match score.
        
        Returns score based on:
        - Exact matches
        - Partial matches (fuzzy)
        - Required vs optional skills
        """
        if not job_requirements:
            return 1.0
        
        if not resume_skills:
            return 0.0
        
        # Normalize skills (lowercase)
        resume_skills_lower = {s.lower().strip() for s in resume_skills}
        job_requirements_lower = {s.lower().strip() for s in job_requirements}
        
        # Exact matches
        exact_matches = resume_skills_lower & job_requirements_lower
        exact_match_ratio = len(exact_matches) / len(job_requirements_lower)
        
        # Partial matches (check if any job skill is substring of resume skill or vice versa)
        partial_matches = 0
        for job_skill in job_requirements_lower - exact_matches:
            for resume_skill in resume_skills_lower:
                if job_skill in resume_skill or resume_skill in job_skill:
                    partial_matches += 1
                    break
        
        partial_match_ratio = partial_matches / len(job_requirements_lower)
        
        # Weighted score: exact matches worth more
        score = exact_match_ratio * 0.8 + partial_match_ratio * 0.2
        
        return min(score, 1.0)
    
    def _keyword_similarity(self, text1: str, text2: str) -> float:
        """
        Simple keyword-based similarity (fallback when ML model unavailable).
        Uses Jaccard similarity on word sets.
        """
        # Tokenize and normalize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Remove very common words
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may'
        }
        words1 -= stopwords
        words2 -= stopwords
        
        # Jaccard similarity
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def explain_match(
        self,
        resume_text: str,
        job_description: str,
        resume_skills: List[str],
        job_requirements: List[str]
    ) -> Dict[str, any]:
        """
        Provide detailed explanation of match score.
        
        Returns:
            Dictionary with breakdown of scores and matched/missing skills
        """
        match_scores = self.match_resume_to_job(
            resume_text, job_description, resume_skills, job_requirements
        )
        
        # Identify matched and missing skills
        resume_skills_lower = {s.lower() for s in resume_skills}
        job_requirements_lower = {s.lower() for s in job_requirements}
        
        matched_skills = []
        missing_skills = []
        
        for job_skill in job_requirements:
            job_skill_lower = job_skill.lower()
            if job_skill_lower in resume_skills_lower:
                matched_skills.append(job_skill)
            else:
                # Check partial match
                found_partial = False
                for resume_skill in resume_skills_lower:
                    if job_skill_lower in resume_skill or resume_skill in job_skill_lower:
                        matched_skills.append(f"{job_skill} (partial: {resume_skill})")
                        found_partial = True
                        break
                
                if not found_partial:
                    missing_skills.append(job_skill)
        
        return {
            **match_scores,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_percentage': round(
                len(matched_skills) / len(job_requirements) * 100, 2
            ) if job_requirements else 0
        }


class KnockoutFilter:
    """Apply knockout criteria to filter candidates."""
    
    @staticmethod
    def apply_filters(
        candidate_data: Dict[str, any],
        knockout_criteria: List[Dict[str, any]]
    ) -> Tuple[bool, List[str]]:
        """
        Check if candidate passes all knockout criteria.
        
        Args:
            candidate_data: Candidate information (experience, education, skills, etc.)
            knockout_criteria: List of knockout rules
            
        Returns:
            (passes, reasons) - Whether candidate passes and list of failure reasons
        """
        reasons = []
        
        for criterion in knockout_criteria:
            criterion_type = criterion.get('type')
            required_value = criterion.get('value')
            
            if criterion_type == 'min_experience':
                candidate_exp = candidate_data.get('experience_years', 0)
                if candidate_exp < required_value:
                    reasons.append(
                        f"Insufficient experience: {candidate_exp} years (required: {required_value})"
                    )
            
            elif criterion_type == 'required_skill':
                candidate_skills = {s.lower() for s in candidate_data.get('skills', [])}
                required_skill = str(required_value).lower()
                if required_skill not in candidate_skills:
                    reasons.append(f"Missing required skill: {required_value}")
            
            elif criterion_type == 'education_level':
                candidate_education = candidate_data.get('education', '').lower()
                required_degree = str(required_value).lower()
                if required_degree not in candidate_education:
                    reasons.append(f"Education requirement not met: {required_value}")
            
            elif criterion_type == 'location':
                candidate_location = candidate_data.get('location', '').lower()
                required_location = str(required_value).lower()
                if required_location not in candidate_location:
                    reasons.append(f"Location requirement not met: {required_value}")
        
        passes = len(reasons) == 0
        return passes, reasons
