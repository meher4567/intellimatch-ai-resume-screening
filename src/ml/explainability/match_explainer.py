"""
Enhanced Match Explainer with Feature Importance
Provides detailed explanations of why candidates match (or don't match) jobs
Uses feature importance to show which factors contribute most to the score
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Dict, Any, List, Tuple
import numpy as np


class MatchExplainer:
    """
    Explains match scores with feature importance analysis
    Shows which factors contribute most to the final score
    """
    
    def __init__(self):
        """Initialize match explainer"""
        pass
    
    def explain_match(self,
                     match_result: Dict[str, Any],
                     candidate_data: Dict[str, Any],
                     job_data: Dict[str, Any],
                     top_n: int = 5) -> Dict[str, Any]:
        """
        Generate comprehensive explanation with feature importance
        
        Args:
            match_result: Result from MatchScorer.calculate_match()
            candidate_data: Candidate resume data
            job_data: Job requirements data
            top_n: Number of top contributing factors to show
            
        Returns:
            Dict with detailed explanation and feature importance
        """
        final_score = match_result['final_score']
        scores = match_result['scores']
        weights = match_result['weights']
        details = match_result['details']
        
        # Calculate feature contributions (score * weight)
        contributions = self._calculate_contributions(scores, weights)
        
        # Rank features by contribution
        ranked_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:top_n]
        
        # Generate natural language explanation
        explanation = self._generate_explanation(
            final_score,
            ranked_features,
            details,
            candidate_data,
            job_data
        )
        
        # Identify key matches and gaps
        key_matches = self._identify_key_matches(details, candidate_data, job_data)
        key_gaps = self._identify_key_gaps(details, candidate_data, job_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            scores,
            details,
            key_gaps
        )
        
        return {
            'final_score': final_score,
            'score_breakdown': {
                'semantic': scores['semantic'],
                'skills': scores['skills'],
                'experience': scores['experience'],
                'education': scores['education']
            },
            'feature_contributions': {
                name: round(contrib, 2)
                for name, contrib in contributions.items()
            },
            'top_contributing_factors': [
                {
                    'factor': name,
                    'contribution': round(contrib, 2),
                    'percentage': round((contrib / final_score) * 100, 1) if final_score > 0 else 0
                }
                for name, contrib in ranked_features
            ],
            'explanation': explanation,
            'key_matches': key_matches,
            'key_gaps': key_gaps,
            'recommendations': recommendations,
            'overall_assessment': match_result.get('assessment', '')
        }
    
    def _calculate_contributions(self,
                                scores: Dict[str, float],
                                weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate how much each factor contributes to final score"""
        return {
            factor: scores[factor] * weights[factor]
            for factor in scores.keys()
        }
    
    def _generate_explanation(self,
                            final_score: float,
                            ranked_features: List[Tuple[str, float]],
                            details: Dict[str, Any],
                            candidate_data: Dict[str, Any],
                            job_data: Dict[str, Any]) -> str:
        """Generate natural language explanation"""
        
        # Score assessment
        if final_score >= 85:
            assessment = "This is an **excellent match** - the candidate is highly qualified."
        elif final_score >= 75:
            assessment = "This is a **strong match** - the candidate meets most requirements."
        elif final_score >= 65:
            assessment = "This is a **good match** - the candidate is worth considering."
        elif final_score >= 50:
            assessment = "This is a **fair match** - there are some gaps to review."
        else:
            assessment = "This is a **weak match** - the candidate may not meet key requirements."
        
        # Top contributing factor
        if ranked_features:
            top_factor, top_contrib = ranked_features[0]
            top_pct = (top_contrib / final_score) * 100 if final_score > 0 else 0
            
            factor_detail = self._explain_factor(top_factor, details, candidate_data, job_data)
            
            explanation = f"{assessment}\n\n"
            explanation += f"**Primary Strength**: {top_factor.capitalize()} contributed **{top_contrib:.1f} points** "
            explanation += f"({top_pct:.0f}% of total score). {factor_detail}"
            
            # Add secondary factors if significant
            if len(ranked_features) > 1:
                secondary = ranked_features[1]
                sec_factor, sec_contrib = secondary
                if sec_contrib >= 10:  # Only mention if significant
                    sec_detail = self._explain_factor(sec_factor, details, candidate_data, job_data)
                    explanation += f"\n\n**Secondary Strength**: {sec_factor.capitalize()} added **{sec_contrib:.1f} points**. {sec_detail}"
            
            return explanation
        
        return assessment
    
    def _explain_factor(self,
                       factor: str,
                       details: Dict[str, Any],
                       candidate_data: Dict[str, Any],
                       job_data: Dict[str, Any]) -> str:
        """Explain why a specific factor scored well or poorly"""
        
        if factor == 'semantic':
            return "The candidate's resume content strongly aligns with the job description."
        
        elif factor == 'skills':
            skill_details = details.get('skills', {})
            matched_required = skill_details.get('required_matches', [])
            matched_optional = skill_details.get('optional_matches', [])
            
            if matched_required:
                skills_str = ', '.join(matched_required[:3])
                if len(matched_required) > 3:
                    skills_str += f", and {len(matched_required) - 3} more"
                return f"Key skills matched include: {skills_str}."
            else:
                return "Limited skill overlap with job requirements."
        
        elif factor == 'experience':
            exp_details = details.get('experience', {})
            candidate_years = exp_details.get('candidate_years', 0)
            required_years = exp_details.get('required_years', 0)
            level = exp_details.get('candidate_level', 'unknown')
            
            if candidate_years >= required_years:
                return f"The candidate has {candidate_years} years of experience ({level} level), meeting the {required_years}-year requirement."
            else:
                gap = required_years - candidate_years
                return f"The candidate has {candidate_years} years of experience, but {gap} more years are needed."
        
        elif factor == 'education':
            edu_details = details.get('education', {})
            highest_degree = edu_details.get('highest_degree', 'None')
            field_match = edu_details.get('field_match', False)
            
            if field_match:
                return f"The candidate holds a {highest_degree} in a relevant field."
            elif highest_degree != 'None':
                return f"The candidate holds a {highest_degree}, though the field may not be a perfect match."
            else:
                return "The candidate's education could not be verified."
        
        return ""
    
    def _identify_key_matches(self,
                            details: Dict[str, Any],
                            candidate_data: Dict[str, Any],
                            job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the most important matching factors"""
        matches = []
        
        # Skills matches
        skill_details = details.get('skills', {})
        required_matches = skill_details.get('required_matches', [])
        if required_matches:
            matches.append({
                'category': 'Skills',
                'description': f"Matches {len(required_matches)} required skills",
                'details': required_matches[:5],  # Top 5
                'importance': 'high'
            })
        
        optional_matches = skill_details.get('optional_matches', [])
        if optional_matches:
            matches.append({
                'category': 'Skills (Optional)',
                'description': f"Also has {len(optional_matches)} optional skills",
                'details': optional_matches[:3],
                'importance': 'medium'
            })
        
        # Experience match
        exp_details = details.get('experience', {})
        if exp_details.get('level_match', False):
            matches.append({
                'category': 'Experience Level',
                'description': f"Experience level ({exp_details.get('candidate_level', '')}) matches job requirement",
                'details': [f"{exp_details.get('candidate_years', 0)} years experience"],
                'importance': 'high'
            })
        
        # Education match
        edu_details = details.get('education', {})
        if edu_details.get('degree_match', False):
            matches.append({
                'category': 'Education',
                'description': f"Education meets requirements",
                'details': [f"{edu_details.get('highest_degree', '')} degree"],
                'importance': 'medium'
            })
        
        return matches
    
    def _identify_key_gaps(self,
                         details: Dict[str, Any],
                         candidate_data: Dict[str, Any],
                         job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the most important gaps or mismatches"""
        gaps = []
        
        # Missing skills
        skill_details = details.get('skills', {})
        missing_required = skill_details.get('missing_required', [])
        if missing_required:
            gaps.append({
                'category': 'Skills Gap',
                'description': f"Missing {len(missing_required)} required skills",
                'details': missing_required[:5],  # Top 5
                'severity': 'high' if len(missing_required) > 3 else 'medium'
            })
        
        # Experience gap
        exp_details = details.get('experience', {})
        candidate_years = exp_details.get('candidate_years', 0)
        required_years = exp_details.get('required_years', 0)
        if required_years and candidate_years < required_years:
            gap_years = required_years - candidate_years
            gaps.append({
                'category': 'Experience Gap',
                'description': f"Needs {gap_years} more years of experience",
                'details': [f"Has {candidate_years} years, needs {required_years} years"],
                'severity': 'high' if gap_years > 2 else 'medium'
            })
        
        # Education gap
        edu_details = details.get('education', {})
        if not edu_details.get('degree_match', True) and edu_details.get('required_degree'):
            gaps.append({
                'category': 'Education Gap',
                'description': "Does not meet education requirements",
                'details': [f"Required: {edu_details.get('required_degree', '')}"],
                'severity': 'medium'
            })
        
        return gaps
    
    def _generate_recommendations(self,
                                scores: Dict[str, float],
                                details: Dict[str, Any],
                                gaps: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Hiring recommendations
        if scores['skills'] >= 75 and scores['experience'] >= 70:
            recommendations.append("✅ **Strong candidate** - Recommend for interview")
        elif scores['skills'] >= 60:
            recommendations.append("⚠️ **Potential candidate** - Review additional materials")
        else:
            recommendations.append("❌ **May not meet requirements** - Consider other candidates")
        
        # Skill development recommendations for candidate
        if gaps:
            high_severity_gaps = [g for g in gaps if g.get('severity') == 'high']
            if high_severity_gaps:
                gap = high_severity_gaps[0]
                if gap['category'] == 'Skills Gap':
                    missing_skills = gap['details'][:3]
                    recommendations.append(
                        f"📚 **For candidate**: Develop skills in {', '.join(missing_skills)}"
                    )
                elif gap['category'] == 'Experience Gap':
                    recommendations.append(
                        f"📚 **For candidate**: Gain more practical experience"
                    )
        
        # Interview focus recommendations
        skill_details = details.get('skills', {})
        matched_required = skill_details.get('required_matches', [])
        if matched_required:
            top_skills = matched_required[:2]
            recommendations.append(
                f"💡 **Interview focus**: Assess depth in {', '.join(top_skills)}"
            )
        
        return recommendations
    
    def visualize_contributions(self,
                               explanation_result: Dict[str, Any]) -> str:
        """Generate a text-based visualization of feature contributions"""
        
        contributions = explanation_result['top_contributing_factors']
        final_score = explanation_result['final_score']
        
        viz = "\n📊 **Feature Contribution Breakdown**:\n\n"
        viz += "```\n"
        
        max_width = 50
        for item in contributions:
            factor = item['factor'].capitalize()
            contrib = item['contribution']
            pct = item['percentage']
            
            # Create bar
            bar_width = int((contrib / final_score) * max_width) if final_score > 0 else 0
            bar = "█" * bar_width
            
            viz += f"{factor:12s} [{contrib:5.1f}pts] {bar} {pct:.0f}%\n"
        
        viz += "```\n"
        
        return viz


if __name__ == "__main__":
    print("=" * 80)
    print("🔍 Testing Enhanced Match Explainer")
    print("=" * 80)
    
    # Simulate a match result
    match_result = {
        'final_score': 78.5,
        'scores': {
            'semantic': 82.0,
            'skills': 85.0,
            'experience': 70.0,
            'education': 75.0
        },
        'weights': {
            'semantic': 0.30,
            'skills': 0.40,
            'experience': 0.20,
            'education': 0.10
        },
        'details': {
            'skills': {
                'score': 85.0,
                'required_matches': ['Python', 'Django', 'PostgreSQL'],
                'optional_matches': ['AWS', 'Docker'],
                'missing_required': ['Kubernetes'],
                'total_required': 4,
                'total_optional': 3
            },
            'experience': {
                'score': 70.0,
                'candidate_years': 5,
                'required_years': 5,
                'candidate_level': 'senior',
                'required_level': 'senior',
                'level_match': True
            },
            'education': {
                'score': 75.0,
                'highest_degree': 'Bachelor',
                'required_degree': 'Bachelor',
                'field_match': True,
                'degree_match': True
            }
        },
        'assessment': 'Strong match - Recommended'
    }
    
    candidate_data = {
        'name': 'John Doe',
        'skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker'],
        'experience': [{'title': 'Senior Developer', 'duration_months': 60}],
        'education': [{'degree': 'Bachelor', 'field': 'Computer Science'}]
    }
    
    job_data = {
        'title': 'Senior Backend Engineer',
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'Kubernetes'],
        'optional_skills': ['AWS', 'Docker', 'Redis'],
        'experience_years': 5,
        'experience_level': 'senior'
    }
    
    explainer = MatchExplainer()
    explanation = explainer.explain_match(match_result, candidate_data, job_data)
    
    print(f"\n📊 **Final Score**: {explanation['final_score']}/100")
    print(f"📋 **Assessment**: {explanation['overall_assessment']}")
    
    print("\n" + "=" * 80)
    print("🎯 Top Contributing Factors:")
    print("=" * 80)
    for i, factor in enumerate(explanation['top_contributing_factors'], 1):
        print(f"{i}. {factor['factor'].capitalize():12s} - {factor['contribution']:5.1f} points ({factor['percentage']:.0f}%)")
    
    print("\n" + "=" * 80)
    print("💬 Explanation:")
    print("=" * 80)
    print(explanation['explanation'])
    
    if explanation['key_matches']:
        print("\n" + "=" * 80)
        print("✅ Key Matches:")
        print("=" * 80)
        for match in explanation['key_matches']:
            print(f"\n**{match['category']}** ({match['importance']} importance)")
            print(f"   {match['description']}")
            if match['details']:
                print(f"   Details: {', '.join(match['details'])}")
    
    if explanation['key_gaps']:
        print("\n" + "=" * 80)
        print("⚠️  Key Gaps:")
        print("=" * 80)
        for gap in explanation['key_gaps']:
            print(f"\n**{gap['category']}** ({gap['severity']} severity)")
            print(f"   {gap['description']}")
            if gap['details']:
                print(f"   Details: {', '.join(gap['details'])}")
    
    if explanation['recommendations']:
        print("\n" + "=" * 80)
        print("💡 Recommendations:")
        print("=" * 80)
        for rec in explanation['recommendations']:
            print(f"   {rec}")
    
    # Visualization
    print("\n" + "=" * 80)
    viz = explainer.visualize_contributions(explanation)
    print(viz)
    
    print("=" * 80)
    print("✅ Enhanced Match Explainer Test Complete!")
    print("=" * 80)
