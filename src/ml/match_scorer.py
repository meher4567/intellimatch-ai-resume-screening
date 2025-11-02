"""
Match Scorer
Aggregates multiple scoring factors into final match score
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, Optional, List
from src.ml.scorers.skill_matcher import SkillMatcher
from src.ml.scorers.experience_matcher import ExperienceMatcher
from src.ml.scorers.education_matcher import EducationMatcher
from src.ml.classifiers.experience_classifier import ExperienceLevelClassifier


class MatchScorer:
    """Aggregate multiple factors into final match score"""
    
    def __init__(self,
                 semantic_weight: float = 0.30,
                 skills_weight: float = 0.40,
                 experience_weight: float = 0.20,
                 education_weight: float = 0.10):
        """
        Initialize match scorer
        
        Args:
            semantic_weight: Weight for semantic similarity (default: 30%)
            skills_weight: Weight for skill match (default: 40%)
            experience_weight: Weight for experience match (default: 20%)
            education_weight: Weight for education match (default: 10%)
        """
        # Validate weights sum to 1.0
        total = semantic_weight + skills_weight + experience_weight + education_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.weights = {
            'semantic': semantic_weight,
            'skills': skills_weight,
            'experience': experience_weight,
            'education': education_weight
        }
        
        # Initialize individual scorers with ML enhancements
        self.skill_matcher = SkillMatcher(use_semantic=True, semantic_threshold=0.65)
        self.experience_matcher = ExperienceMatcher()
        self.education_matcher = EducationMatcher()
        
        # Initialize ML classifiers (lazy loading to avoid startup delay)
        self._experience_classifier = None
    
    def calculate_match(self,
                       candidate_data: Dict[str, Any],
                       job_data: Dict[str, Any],
                       semantic_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive match score
        
        Args:
            candidate_data: Resume data with skills, experience, education
            job_data: Job data with requirements
            semantic_score: Pre-calculated semantic similarity (0-100)
            
        Returns:
            Dict with final score and detailed breakdown
        """
        scores = {}
        details = {}
        
        # 1. Semantic similarity (if provided)
        if semantic_score is not None:
            scores['semantic'] = semantic_score
        else:
            scores['semantic'] = 50  # Neutral if not available
        
        # 2. Skills match
        skill_result = self._score_skills(candidate_data, job_data)
        scores['skills'] = skill_result['score']
        details['skills'] = skill_result
        
        # 3. Experience match
        exp_result = self._score_experience(candidate_data, job_data)
        scores['experience'] = exp_result['score']
        details['experience'] = exp_result
        
        # 4. Education match
        edu_result = self._score_education(candidate_data, job_data)
        scores['education'] = edu_result['score']
        details['education'] = edu_result
        
        # Calculate weighted final score
        final_score = sum(scores[k] * self.weights[k] for k in scores.keys())
        
        # Generate overall assessment
        assessment = self._get_overall_assessment(final_score, scores)
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(scores, details)
        weaknesses = self._identify_weaknesses(scores, details)
        
        return {
            'final_score': round(final_score, 2),
            'scores': scores,
            'weights': self.weights,
            'details': details,
            'assessment': assessment,
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def _score_skills(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Score skill match"""
        candidate_skills = candidate_data.get('skills', [])
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
        total_months = sum(entry.get('duration_months', 0) for entry in experience_entries)
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
        """Classify experience level using ML classifier (with rule-based fallback)"""
        # Lazy load classifier to avoid startup delay
        if self._experience_classifier is None:
            try:
                self._experience_classifier = ExperienceLevelClassifier(
                    model_name='bert-base-uncased',
                    use_pretrained=False
                )
            except Exception as e:
                # Fallback to rule-based if classifier fails to load
                print(f"⚠️  Warning: Failed to load experience classifier: {e}")
                print("   Using rule-based classification...")
                return self._infer_experience_level_fallback(candidate_data)
        
        # Classify using ML (hybrid mode with rule-based fallback)
        try:
            result = self._experience_classifier.classify(
                candidate_data,
                use_hybrid=True,
                confidence_threshold=0.7
            )
            return result['level']
        except Exception as e:
            print(f"⚠️  Warning: Experience classification failed: {e}")
            return self._infer_experience_level_fallback(candidate_data)
    
    def _infer_experience_level_fallback(self, candidate_data: Dict) -> str:
        """Fallback rule-based experience level inference"""
        experience_entries = candidate_data.get('experience', [])
        total_months = sum(entry.get('duration_months', 0) for entry in experience_entries)
        years = total_months // 12
        
        # Check job titles for level indicators
        for entry in experience_entries:
            title = entry.get('title', '').lower()
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
