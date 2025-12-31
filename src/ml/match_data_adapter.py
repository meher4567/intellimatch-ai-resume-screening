"""
Data Adapter for Match Explainer
Transforms resume parser output format to match explainer input format
"""

from typing import Dict, List, Any


def adapt_candidate_data_for_explainer(candidate_data: Dict) -> Dict:
    """
    Transform candidate data from resume parser format to match explainer format.
    
    Args:
        candidate_data: Output from ResumeParser or similar format with nested structures
        
    Returns:
        Dict in format expected by advanced_match_explainer
    """
    adapted = candidate_data.copy()
    
    # Ensure skills is a dict with all_skills list
    if 'skills' in adapted:
        skills = adapted['skills']
        if isinstance(skills, list):
            # Legacy format: simple list
            adapted['skills'] = {
                'all_skills': skills,
                'by_category': {}
            }
        elif isinstance(skills, dict) and 'all_skills' not in skills:
            # Missing all_skills, try to build from other fields
            all_skills = []
            if 'technical' in skills:
                all_skills.extend(skills['technical'])
            if 'soft' in skills:
                all_skills.extend(skills['soft'])
            if 'tools' in skills:
                all_skills.extend(skills['tools'])
            adapted['skills']['all_skills'] = all_skills
    
    # Calculate total_experience_years if not present
    if 'total_experience_years' not in adapted and 'experience' in adapted:
        experience_list = adapted['experience']
        if isinstance(experience_list, list):
            total_months = sum(
                exp.get('duration_months', 0) for exp in experience_list
            )
            adapted['total_experience_years'] = round(total_months / 12, 1)
        else:
            adapted['total_experience_years'] = 0
    
    # Add experience_level if not present
    if 'experience_level' not in adapted and 'total_experience_years' in adapted:
        years = adapted['total_experience_years']
        if years >= 10:
            adapted['experience_level'] = 'senior'
        elif years >= 5:
            adapted['experience_level'] = 'mid'
        elif years >= 2:
            adapted['experience_level'] = 'junior'
        else:
            adapted['experience_level'] = 'entry'
    
    # Extract education level if not present
    if 'education_level' not in adapted and 'education' in adapted:
        education_list = adapted['education']
        if isinstance(education_list, list) and education_list:
            # Get highest degree
            degree_hierarchy = {
                'phd': 4, 'doctorate': 4, 'ph.d': 4,
                'master': 3, 'msc': 3, 'ms': 3, 'mba': 3, 'm.s': 3,
                'bachelor': 2, 'bsc': 2, 'bs': 2, 'ba': 2, 'b.s': 2,
                'associate': 1, 'diploma': 1
            }
            highest_level = 0
            highest_degree = "Bachelor's"
            
            for edu in education_list:
                # Handle both dict and string formats
                if isinstance(edu, dict):
                    degree = edu.get('degree', '').lower()
                elif isinstance(edu, str):
                    degree = edu.lower()
                else:
                    continue
                    
                for key, level in degree_hierarchy.items():
                    if key in degree:
                        if level > highest_level:
                            highest_level = level
                            if isinstance(edu, dict):
                                highest_degree = edu.get('degree', "Bachelor's")
                            else:
                                highest_degree = edu
                        break
            
            adapted['education_level'] = highest_degree
    
    # Add name if not present
    if 'name' not in adapted:
        adapted['name'] = 'The candidate'
    
    return adapted


def adapt_job_data_for_explainer(job_data: Dict) -> Dict:
    """
    Ensure job data has all required fields for match explainer.
    
    Args:
        job_data: Job description data
        
    Returns:
        Dict in format expected by advanced_match_explainer
    """
    adapted = job_data.copy()
    
    # Ensure required_skills is a list
    if 'required_skills' not in adapted:
        adapted['required_skills'] = []
    
    # Ensure optional_skills is a list
    if 'optional_skills' not in adapted:
        adapted['optional_skills'] = []
    
    # Ensure title is present
    if 'title' not in adapted:
        adapted['title'] = 'this position'
    
    # Add experience requirements if not present
    if 'experience_years' not in adapted:
        adapted['experience_years'] = 3  # Default to mid-level
    
    if 'experience_level' not in adapted:
        adapted['experience_level'] = 'mid'
    
    # Add education requirements if not present
    if 'education_level' not in adapted:
        adapted['education_level'] = "Bachelor's"
    
    return adapted


def prepare_match_scores_for_explainer(
    final_score: float,
    component_scores: Dict[str, float],
    details: Dict[str, Any]
) -> Dict:
    """
    Prepare match scores in format expected by explainer.
    
    Args:
        final_score: Overall match score (0-100)
        component_scores: Dict with skills, experience, education, semantic scores
        details: Detailed breakdown from each matcher
        
    Returns:
        Dict in format expected by advanced_match_explainer
    """
    return {
        'overall': final_score,
        'skill_match': component_scores.get('skills', 0),
        'experience_match': component_scores.get('experience', 0),
        'education_match': component_scores.get('education', 0),
        'semantic_similarity': component_scores.get('semantic', 0),
        'details': details
    }
