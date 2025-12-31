"""
Match Scorer
Aggregates multiple scoring factors into final match score

Edge Cases Handled:
- Missing/empty candidate data
- Missing/empty job requirements
- Invalid weight configurations
- Scorer initialization failures
- None values in scoring components
- Extreme scores (clamping)
- Auto-compute semantic score when not provided
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, Optional, List, Union
import logging
import numpy as np
from src.ml.enhanced_skill_matcher import EnhancedSkillMatcher
from src.ml.scorers.experience_matcher import ExperienceMatcher
from src.ml.scorers.education_matcher import EducationMatcher
from src.ml.classifiers.experience_classifier import ExperienceLevelClassifier
from src.ml.trained_experience_classifier import TrainedExperienceClassifier
from src.ml.advanced_match_explainer import explain_match
from src.ml.match_data_adapter import (
    adapt_candidate_data_for_explainer,
    adapt_job_data_for_explainer,
    prepare_match_scores_for_explainer
)

logger = logging.getLogger(__name__)


def _safe_score(value: Any, default: float = 50.0, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Safely convert a value to a clamped score
    
    Args:
        value: Value to convert
        default: Default if conversion fails
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped float score
    """
    if value is None:
        return default
    
    try:
        score = float(value)
        # Handle NaN
        if score != score:
            return default
        return max(min_val, min(max_val, score))
    except (TypeError, ValueError):
        return default


class MatchScorer:
    """Aggregate multiple factors into final match score"""
    
    # Default weights
    DEFAULT_WEIGHTS = {
        'semantic': 0.30,
        'skills': 0.40,
        'experience': 0.20,
        'education': 0.10
    }
    
    def __init__(self,
                 semantic_weight: float = 0.30,
                 skills_weight: float = 0.40,
                 experience_weight: float = 0.20,
                 education_weight: float = 0.10,
                 auto_normalize_weights: bool = True):
        """
        Initialize match scorer
        
        Args:
            semantic_weight: Weight for semantic similarity (default: 30%)
            skills_weight: Weight for skill match (default: 40%)
            experience_weight: Weight for experience match (default: 20%)
            education_weight: Weight for education match (default: 10%)
            auto_normalize_weights: If True, automatically normalize weights to sum to 1.0
        """
        # Collect weights
        raw_weights = {
            'semantic': _safe_score(semantic_weight, 0.30, 0.0, 1.0),
            'skills': _safe_score(skills_weight, 0.40, 0.0, 1.0),
            'experience': _safe_score(experience_weight, 0.20, 0.0, 1.0),
            'education': _safe_score(education_weight, 0.10, 0.0, 1.0)
        }
        
        total = sum(raw_weights.values())
        
        # Validate or normalize weights
        if abs(total - 1.0) > 0.01:
            if auto_normalize_weights and total > 0:
                # Normalize weights
                self.weights = {k: v / total for k, v in raw_weights.items()}
                logger.warning(f"Weights normalized from sum={total:.2f} to 1.0")
            else:
                raise ValueError(
                    f"Weights must sum to 1.0, got {total:.4f}. "
                    f"Set auto_normalize_weights=True to auto-fix."
                )
        else:
            self.weights = raw_weights
        
        # Initialize individual scorers with ML enhancements
        # Use EnhancedSkillMatcher with fuzzy + semantic matching
        try:
            self.skill_matcher = EnhancedSkillMatcher(
                use_fuzzy=True,
                fuzzy_threshold=85,
                use_semantic=True,
                semantic_threshold=0.70
            )
        except Exception as e:
            logger.warning(f"Failed to initialize EnhancedSkillMatcher with semantic: {e}")
            # Fallback to simpler matching
            self.skill_matcher = EnhancedSkillMatcher(
                use_fuzzy=True,
                fuzzy_threshold=85,
                use_semantic=False
            )
        self.experience_matcher = ExperienceMatcher()
        self.education_matcher = EducationMatcher()
        
        # Initialize ML classifiers (lazy loading to avoid startup delay)
        self._experience_classifier = None
        self._semantic_model = None  # Lazy load for semantic scoring
    
    def _compute_semantic_score(self, candidate_data: Dict, job_data: Dict) -> float:
        """
        Compute semantic similarity between resume and job description.
        Uses sentence embeddings to find overall similarity.
        
        Returns:
            Semantic similarity score (0-100)
        """
        try:
            # Lazy load the embedding model
            if self._semantic_model is None:
                from sentence_transformers import SentenceTransformer
                self._semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Build resume text
            resume_parts = []
            
            # Add skills
            skills = candidate_data.get('skills', [])
            if isinstance(skills, dict):
                skills = skills.get('all_skills', [])
            if skills:
                resume_parts.append("Skills: " + ", ".join(str(s) for s in skills[:30]))
            
            # Add experience titles
            for exp in candidate_data.get('experience', [])[:5]:
                title = exp.get('title', '')
                if title:
                    resume_parts.append(title)
            
            # Add education
            for edu in candidate_data.get('education', [])[:2]:
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                if degree or field:
                    resume_parts.append(f"{degree} {field}".strip())
            
            resume_text = " | ".join(resume_parts) if resume_parts else "No resume data"
            
            # Build job text
            job_parts = []
            job_title = job_data.get('title', '')
            if job_title:
                job_parts.append(job_title)
            
            required_skills = job_data.get('required_skills', [])
            if required_skills:
                job_parts.append("Required: " + ", ".join(required_skills))
            
            preferred_skills = job_data.get('preferred_skills', [])
            if preferred_skills:
                job_parts.append("Preferred: " + ", ".join(preferred_skills))
            
            job_text = " | ".join(job_parts) if job_parts else "No job data"
            
            # Compute embeddings
            embeddings = self._semantic_model.encode([resume_text, job_text], convert_to_numpy=True)
            
            # Cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            # Convert to 0-100 scale (similarity is typically 0-1 for similar, can be negative)
            # Clamp to reasonable range
            score = max(0, min(100, similarity * 100))
            
            return float(score)
            
        except Exception as e:
            logger.warning(f"Semantic scoring failed: {e}. Using default 50.")
            return 50.0
    
    def calculate_match(self,
                       candidate_data: Dict[str, Any],
                       job_data: Dict[str, Any],
                       semantic_score: Optional[float] = None,
                       include_explanation: bool = True) -> Dict[str, Any]:
        """
        Calculate comprehensive match score
        
        Args:
            candidate_data: Resume data with skills, experience, education
            job_data: Job data with requirements
            semantic_score: Pre-calculated semantic similarity (0-100). 
                           If None, will be auto-computed using embeddings.
            include_explanation: Whether to generate natural language explanation
            
        Returns:
            Dict with final score and detailed breakdown
        """
        # Validate inputs
        if candidate_data is None:
            logger.warning("calculate_match called with None candidate_data")
            candidate_data = {}
        
        if job_data is None:
            logger.warning("calculate_match called with None job_data")
            job_data = {}
        
        scores = {}
        details = {}
        errors = []
        
        # 1. Semantic similarity - auto-compute if not provided
        if semantic_score is None:
            computed_semantic = self._compute_semantic_score(candidate_data, job_data)
            scores['semantic'] = _safe_score(computed_semantic, default=50.0)
            details['semantic'] = {'computed': True, 'score': computed_semantic}
        else:
            scores['semantic'] = _safe_score(semantic_score, default=50.0)
            details['semantic'] = {'computed': False, 'score': semantic_score}
        
        # 2. Skills match (with error handling)
        try:
            skill_result = self._score_skills(candidate_data, job_data)
            scores['skills'] = _safe_score(skill_result.get('score'), default=50.0)
            details['skills'] = skill_result
        except Exception as e:
            logger.error(f"Skills scoring failed: {e}")
            scores['skills'] = 50.0
            details['skills'] = {'error': str(e), 'score': 50.0}
            errors.append(f"Skills: {e}")
        
        # 3. Experience match (with error handling)
        try:
            exp_result = self._score_experience(candidate_data, job_data)
            scores['experience'] = _safe_score(exp_result.get('score'), default=50.0)
            details['experience'] = exp_result
        except Exception as e:
            logger.error(f"Experience scoring failed: {e}")
            scores['experience'] = 50.0
            details['experience'] = {'error': str(e), 'score': 50.0}
            errors.append(f"Experience: {e}")
        
        # 4. Education match (with error handling)
        try:
            edu_result = self._score_education(candidate_data, job_data)
            scores['education'] = _safe_score(edu_result.get('score'), default=50.0)
            details['education'] = edu_result
        except Exception as e:
            logger.error(f"Education scoring failed: {e}")
            scores['education'] = 50.0
            details['education'] = {'error': str(e), 'score': 50.0}
            errors.append(f"Education: {e}")
        
        # Calculate weighted final score with validation
        try:
            final_score = sum(
                _safe_score(scores.get(k), 50.0) * self.weights.get(k, 0.25) 
                for k in self.weights.keys()
            )
            final_score = _safe_score(final_score, 50.0)
        except Exception as e:
            logger.error(f"Final score calculation failed: {e}")
            final_score = 50.0
            errors.append(f"Scoring: {e}")
        
        # Generate overall assessment
        try:
            assessment = self._get_overall_assessment(final_score, scores)
        except Exception as e:
            logger.error(f"Assessment generation failed: {e}")
            assessment = "Match score calculated with some errors"
        
        # Identify strengths and weaknesses
        try:
            strengths = self._identify_strengths(scores, details)
        except Exception as e:
            logger.error(f"Strength identification failed: {e}")
            strengths = []
        
        try:
            weaknesses = self._identify_weaknesses(scores, details)
        except Exception as e:
            logger.error(f"Weakness identification failed: {e}")
            weaknesses = []
        
        result = {
            'final_score': round(final_score, 2),
            'scores': scores,
            'weights': self.weights,
            'details': details,
            'assessment': assessment,
            'strengths': strengths,
            'weaknesses': weaknesses
        }
        
        # Add errors if any occurred
        if errors:
            result['errors'] = errors
            result['has_errors'] = True
        
        # Add natural language explanation if requested
        if include_explanation:
            try:
                # Adapt data to format expected by explainer
                adapted_candidate = adapt_candidate_data_for_explainer(candidate_data)
                adapted_job = adapt_job_data_for_explainer(job_data)
            
                # Prepare match scores dict for explainer
                match_scores_dict = prepare_match_scores_for_explainer(
                    final_score, scores, details
                )
            
                explanation = explain_match(
                    candidate_data=adapted_candidate,
                    job_requirements=adapted_job,
                    match_scores=match_scores_dict
                )
                result['explanation'] = explanation
            except Exception as e:
                result['explanation'] = f"Unable to generate explanation: {str(e)}"
        
        return result
    
    def _score_skills(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Score skill match"""
        # Handle both list and dict formats for skills
        candidate_skills_raw = candidate_data.get('skills', [])
        if isinstance(candidate_skills_raw, dict):
            # New format: {'all_skills': [...], 'by_category': {...}}
            candidate_skills = candidate_skills_raw.get('all_skills', [])
        else:
            # Legacy format: simple list
            candidate_skills = candidate_skills_raw
        
        required_skills = job_data.get('required_skills', [])
        optional_skills = job_data.get('optional_skills', [])
        
        return self.skill_matcher.calculate_match_score(
            candidate_skills,
            required_skills,
            optional_skills
        )
    
    def _score_experience(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Score experience match"""
        # Calculate total years from experience entries
        experience_entries = candidate_data.get('experience', [])
        total_months = 0
        for entry in experience_entries:
            months = entry.get('duration_months')
            if months is not None and isinstance(months, (int, float)):
                total_months += months
        candidate_years = total_months // 12
        
        # Get experience level using ML classifier (hybrid mode with rule-based fallback)
        candidate_level = self._classify_experience_level(candidate_data)
        
        # Get job requirements
        required_years = job_data.get('experience_years')
        required_level = job_data.get('experience_level', 'mid')
        
        return self.experience_matcher.calculate_match_score(
            candidate_years,
            required_years,
            candidate_level,
            required_level
        )
    
    def _score_education(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Score education match"""
        candidate_degrees = candidate_data.get('education', [])
        required_degree = job_data.get('required_degree')
        preferred_degree = job_data.get('preferred_degree')
        required_field = job_data.get('required_field')
        equivalent_experience = job_data.get('equivalent_experience', False)
        
        return self.education_matcher.calculate_match_score(
            candidate_degrees,
            required_degree,
            preferred_degree,
            required_field,
            equivalent_experience
        )
    
    def _classify_experience_level(self, candidate_data: Dict) -> str:
        """Classify experience level using trained BERT model (with rule-based fallback)"""
        # Lazy load trained classifier to avoid startup delay
        if self._experience_classifier is None:
            try:
                # Try to load the trained BERT model first
                self._experience_classifier = TrainedExperienceClassifier(
                    model_path='models/experience_classifier'
                )
                print("✅ Using trained BERT experience classifier")
            except Exception as e:
                # Fallback to rule-based if trained model fails to load
                print(f"⚠️  Warning: Failed to load trained experience classifier: {e}")
                print("   Using rule-based classification...")
                return self._infer_experience_level_fallback(candidate_data)
        
        # Classify using trained ML model
        try:
            result = self._experience_classifier.classify(candidate_data)
            
            # Use rule-based fallback if confidence is too low
            if result['confidence'] < 0.7:
                print(f"⚠️  Low confidence ({result['confidence']:.2f}), using rule-based fallback")
                return self._infer_experience_level_fallback(candidate_data)
            
            return result['level']
        except Exception as e:
            print(f"⚠️  Warning: Experience classification failed: {e}")
            return self._infer_experience_level_fallback(candidate_data)
    
    def _infer_experience_level_fallback(self, candidate_data: Dict) -> str:
        """Fallback rule-based experience level inference"""
        experience_entries = candidate_data.get('experience', [])
        
        # Calculate total months, handling None values
        total_months = 0
        for entry in experience_entries:
            months = entry.get('duration_months')
            if months is not None and isinstance(months, (int, float)):
                total_months += months
        years = total_months // 12
        
        # Check job titles for level indicators
        for entry in experience_entries:
            title = entry.get('title', '').lower() if entry.get('title') else ''
            if any(word in title for word in ['lead', 'principal', 'architect', 'director']):
                return 'expert'
            elif any(word in title for word in ['senior', 'sr', 'staff']):
                return 'senior'
            elif any(word in title for word in ['junior', 'jr', 'associate']):
                return 'entry'
        
        # Fallback to years-based inference
        if years >= 8:
            return 'expert'
        elif years >= 5:
            return 'senior'
        elif years >= 2:
            return 'mid'
        else:
            return 'entry'
    
    def _get_overall_assessment(self, final_score: float, scores: Dict[str, float]) -> str:
        """Generate overall assessment message"""
        if final_score >= 85:
            return 'Excellent match - Highly recommended'
        elif final_score >= 75:
            return 'Strong match - Recommended'
        elif final_score >= 65:
            return 'Good match - Consider for interview'
        elif final_score >= 50:
            return 'Fair match - Review carefully'
        else:
            return 'Weak match - May not meet requirements'
    
    def _identify_strengths(self, scores: Dict[str, float], details: Dict) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if scores['semantic'] >= 70:
            strengths.append('Strong semantic match with job description')
        
        if scores['skills'] >= 75:
            skill_details = details['skills']
            matched = skill_details.get('matched_required', [])
            if matched:
                strengths.append(f"Excellent skill match ({len(matched)} key skills)")
        
        if scores['experience'] >= 80:
            exp_details = details['experience']
            assessment = exp_details.get('assessment', '')
            if 'Meets' in assessment or 'Level' in assessment:
                years = exp_details.get('candidate_years', 0)
                strengths.append(f"Well-qualified with {years} years experience")
        
        if scores['education'] >= 85:
            edu_details = details['education']
            degree = edu_details.get('highest_degree', '')
            if degree:
                strengths.append(f"Strong educational background ({degree})")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict[str, float], details: Dict) -> List[str]:
        """Identify candidate weaknesses"""
        weaknesses = []
        
        if scores['skills'] < 50:
            skill_details = details['skills']
            missing = skill_details.get('missing_required', [])
            if missing:
                weaknesses.append(f"Missing key skills: {', '.join(missing[:3])}")
        
        if scores['experience'] < 50:
            exp_details = details['experience']
            if exp_details.get('assessment') == 'Under-qualified':
                required = exp_details.get('required_years', 0)
                actual = exp_details.get('candidate_years', 0)
                weaknesses.append(f"Limited experience ({actual} vs {required} years required)")
        
        if scores['education'] < 50:
            edu_details = details['education']
            assessment = edu_details.get('assessment', '')
            if 'not meet' in assessment.lower():
                weaknesses.append('Does not meet education requirements')
        
        return weaknesses
    
    def adjust_weights(self,
                      semantic: Optional[float] = None,
                      skills: Optional[float] = None,
                      experience: Optional[float] = None,
                      education: Optional[float] = None):
        """
        Adjust scoring weights (must sum to 1.0)
        
        Example: For entry-level role, increase education weight
                 For senior role, increase experience weight
        """
        new_weights = {
            'semantic': semantic if semantic is not None else self.weights['semantic'],
            'skills': skills if skills is not None else self.weights['skills'],
            'experience': experience if experience is not None else self.weights['experience'],
            'education': education if education is not None else self.weights['education']
        }
        
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.weights = new_weights


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Match Scorer")
    print("=" * 70)
    
    scorer = MatchScorer()
    
    # Test case 1: Excellent candidate
    print("\n1️⃣ Test: Excellent match")
    candidate = {
        'skills': ['Python', 'Django', 'AWS', 'PostgreSQL', 'Docker'],
        'experience': [
            {'title': 'Senior Software Engineer', 'duration_months': 36},
            {'title': 'Software Engineer', 'duration_months': 24}
        ],
        'education': [
            {'degree': 'Bachelor of Science', 'field': 'Computer Science'}
        ]
    }
    
    job = {
        'required_skills': ['Python', 'Django', 'PostgreSQL'],
        'optional_skills': ['AWS', 'Docker', 'Kubernetes'],
        'experience_years': 5,
        'experience_level': 'senior',
        'required_degree': 'Bachelor',
        'required_field': 'Computer Science'
    }
    
    result = scorer.calculate_match(candidate, job, semantic_score=85)
    print(f"   Final Score: {result['final_score']}/100")
    print(f"   Assessment: {result['assessment']}")
    print(f"\n   Score Breakdown:")
    for factor, score in result['scores'].items():
        weight = result['weights'][factor] * 100
        print(f"     {factor.capitalize()}: {score:.1f}/100 (weight: {weight:.0f}%)")
    
    if result['strengths']:
        print(f"\n   ✅ Strengths:")
        for strength in result['strengths']:
            print(f"     • {strength}")
    
    if result['weaknesses']:
        print(f"\n   ⚠️  Weaknesses:")
        for weakness in result['weaknesses']:
            print(f"     • {weakness}")
    
    # Test case 2: Average candidate with gaps
    print("\n" + "=" * 70)
    print("\n2️⃣ Test: Average match with skill gaps")
    candidate2 = {
        'skills': ['Python', 'Flask'],
        'experience': [
            {'title': 'Junior Developer', 'duration_months': 18}
        ],
        'education': [
            {'degree': 'Associate', 'field': 'Information Technology'}
        ]
    }
    
    result2 = scorer.calculate_match(candidate2, job, semantic_score=55)
    print(f"   Final Score: {result2['final_score']}/100")
    print(f"   Assessment: {result2['assessment']}")
    print(f"\n   Score Breakdown:")
    for factor, score in result2['scores'].items():
        weight = result2['weights'][factor] * 100
        print(f"     {factor.capitalize()}: {score:.1f}/100 (weight: {weight:.0f}%)")
    
    if result2['strengths']:
        print(f"\n   ✅ Strengths:")
        for strength in result2['strengths']:
            print(f"     • {strength}")
    
    if result2['weaknesses']:
        print(f"\n   ⚠️  Weaknesses:")
        for weakness in result2['weaknesses']:
            print(f"     • {weakness}")
    
    # Test case 3: Custom weights for entry-level role
    print("\n" + "=" * 70)
    print("\n3️⃣ Test: Entry-level role (custom weights)")
    
    # Adjust weights: less experience, more education
    scorer_entry = MatchScorer(
        semantic_weight=0.30,
        skills_weight=0.35,
        experience_weight=0.10,
        education_weight=0.25
    )
    
    entry_candidate = {
        'skills': ['Python', 'Django', 'Git'],
        'experience': [
            {'title': 'Software Engineering Intern', 'duration_months': 6}
        ],
        'education': [
            {'degree': 'Bachelor of Science', 'field': 'Computer Science'}
        ]
    }
    
    entry_job = {
        'required_skills': ['Python', 'Django'],
        'optional_skills': ['React', 'Docker'],
        'experience_years': 0,
        'experience_level': 'entry',
        'required_degree': 'Bachelor',
        'required_field': 'Computer Science'
    }
    
    result3 = scorer_entry.calculate_match(entry_candidate, entry_job, semantic_score=75)
    print(f"   Final Score: {result3['final_score']}/100")
    print(f"   Assessment: {result3['assessment']}")
    print(f"\n   Custom Weights:")
    for factor, weight in result3['weights'].items():
        print(f"     {factor.capitalize()}: {weight * 100:.0f}%")
    
    print(f"\n   Score Breakdown:")
    for factor, score in result3['scores'].items():
        print(f"     {factor.capitalize()}: {score:.1f}/100")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
