"""
Phase 3: Enhanced Match Explainer with Recommendations
Provides detailed, actionable explanations and interview guidance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedMatchExplainer:
    """Generate comprehensive, actionable match explanations"""
    
    def __init__(self):
        logger.info("EnhancedMatchExplainer initialized")
    
    def explain_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive match explanation
        
        Args:
            match_data: Complete match data including scores, details, candidate info
            
        Returns:
            Dict with summary, strengths, concerns, recommendations, and interview focus
        """
        final_score = match_data.get('final_score', 0)
        scores = match_data.get('scores', {})
        details = match_data.get('details', {})
        
        # Generate overall summary
        summary = self._generate_summary(final_score, scores)
        
        # Identify key strengths
        strengths = self._identify_strengths(scores, details)
        
        # Identify concerns/gaps
        concerns = self._identify_concerns(scores, details)
        
        # Generate actionable recommendations
        recommendations = self._generate_recommendations(final_score, scores, details, concerns)
        
        # Suggest interview focus areas
        interview_focus = self._generate_interview_focus(scores, details, concerns)
        
        # Confidence score
        confidence = self._calculate_confidence(scores, details)
        
        return {
            'summary': summary,
            'strengths': strengths,
            'concerns': concerns,
            'recommendations': recommendations,
            'interview_focus': interview_focus,
            'confidence': confidence,
            'hiring_recommendation': self._get_hiring_recommendation(final_score, confidence)
        }
    
    def _generate_summary(self, final_score: float, scores: Dict[str, float]) -> str:
        """Generate one-sentence summary"""
        # Get rating
        if final_score >= 85:
            rating = "excellent"
            fit = "strong"
        elif final_score >= 70:
            rating = "good"
            fit = "solid"
        elif final_score >= 55:
            rating = "moderate"
            fit = "reasonable"
        else:
            rating = "weak"
            fit = "limited"
        
        # Find strongest area
        strongest_area = max(scores.items(), key=lambda x: x[1])[0] if scores else "overall"
        
        return f"This is a {rating} match ({final_score:.1f}%) with {fit} alignment, particularly strong in {strongest_area}."
    
    def _identify_strengths(self, scores: Dict[str, float], details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify and explain key strengths"""
        strengths = []
        
        # Skill strengths
        skill_details = details.get('skills', {})
        skill_score = skill_details.get('score') or 0  # Handle None
        if skill_score >= 70:
            matched_count = skill_details.get('total_matched') or 0
            required_count = skill_details.get('total_required') or 0
            strengths.append({
                'area': 'Technical Skills',
                'score': skill_score,
                'description': f"Strong skill alignment with {matched_count}/{required_count} required skills matched",
                'details': skill_details.get('required_matches', [])[:5]  # Top 5
            })
        
        # Experience strengths
        exp_details = details.get('experience', {})
        exp_score = exp_details.get('score') or 0  # Handle None
        if exp_score >= 70:
            years = exp_details.get('candidate_years') or 0
            required = exp_details.get('required_years') or 0
            if years >= required:
                strengths.append({
                    'area': 'Experience Level',
                    'score': exp_score,
                    'description': f"Exceeds experience requirements with {years} years (needs {required}+)",
                    'details': []
                })
        
        # Semantic strengths
        semantic_score = scores.get('semantic') or 0  # Handle None
        if semantic_score >= 75:
            strengths.append({
                'area': 'Overall Fit',
                'score': semantic_score,
                'description': "Strong semantic alignment between resume and job requirements",
                'details': []
            })
        
        # Education strengths
        edu_details = details.get('education', {})
        edu_score = edu_details.get('score') or 0  # Handle None
        if edu_score >= 70:
            degree_level = edu_details.get('highest_degree', 'Bachelor')
            strengths.append({
                'area': 'Education',
                'score': edu_score,
                'description': f"Meets education requirements with {degree_level} level degree",
                'details': []
            })
        
        return strengths
    
    def _identify_concerns(self, scores: Dict[str, float], details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential concerns or gaps"""
        concerns = []
        
        # Skill gaps
        skill_details = details.get('skills', {})
        missing_skills = skill_details.get('missing_required', [])
        if missing_skills:
            skill_score = skill_details.get('score') or 0  # Handle None
            concerns.append({
                'area': 'Skill Gaps',
                'severity': 'high' if len(missing_skills) > 3 else 'medium',
                'description': f"Missing {len(missing_skills)} required skills",
                'details': missing_skills[:5],  # Top 5 missing
                'impact': f"May require training or learning curve ({skill_score:.0f}% skill coverage)"
            })
        
        # Experience gaps
        exp_details = details.get('experience', {})
        candidate_years = exp_details.get('candidate_years') or 0  # Handle None
        required_years = exp_details.get('required_years') or 0  # Handle None
        if required_years > 0 and candidate_years < required_years * 0.7:  # Less than 70% of required
            gap = required_years - candidate_years
            concerns.append({
                'area': 'Experience Level',
                'severity': 'high' if gap > 3 else 'medium',
                'description': f"Below experience requirements by {gap} years",
                'details': [f"Has {candidate_years} years, needs {required_years}+"],
                'impact': "May need additional mentoring or longer ramp-up time"
            })
        
        # Education concerns
        edu_details = details.get('education', {})
        edu_score = edu_details.get('score') or 0  # Handle None
        if edu_score < 50:
            concerns.append({
                'area': 'Education',
                'severity': 'low',
                'description': "Education level below preferred requirements",
                'details': [f"Has {edu_details.get('highest_degree', 'N/A')}, prefers {edu_details.get('preferred_degree', 'Bachelor')}"],
                'impact': "May be offset by strong practical experience"
            })
        
        return concerns
    
    def _generate_recommendations(self, 
                                 final_score: float,
                                 scores: Dict[str, float], 
                                 details: Dict[str, Any],
                                 concerns: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if final_score >= 85:
            recommendations.append("🎯 **Strong candidate - proceed to interview**")
            recommendations.append("Focus interview on culture fit and team dynamics")
            recommendations.append("Consider for senior role if performance exceeds expectations")
        elif final_score >= 70:
            recommendations.append("✅ **Good candidate - recommended for interview**")
            recommendations.append("Assess depth of experience in key technical areas")
            if concerns:
                recommendations.append(f"Probe into {concerns[0]['area'].lower()} during interview")
        elif final_score >= 55:
            recommendations.append("⚠️ **Moderate match - interview with caution**")
            recommendations.append("Extensive technical assessment recommended")
            recommendations.append("Consider for junior role or with training plan")
        else:
            recommendations.append("❌ **Weak match - not recommended**")
            recommendations.append("Significant gaps in required qualifications")
            recommendations.append("Only consider if candidate shows exceptional potential")
        
        # Specific skill recommendations
        skill_details = details.get('skills', {})
        missing_critical = skill_details.get('missing_required', [])
        if missing_critical and len(missing_critical) <= 3:
            recommendations.append(f"💡 Candidate could strengthen profile by learning: {', '.join(missing_critical[:3])}")
        
        # Experience recommendations
        exp_details = details.get('experience', {})
        candidate_years = exp_details.get('candidate_years') or 0  # Handle None
        required_years = exp_details.get('required_years') or 0  # Handle None
        if required_years > 0 and candidate_years < required_years:
            recommendations.append("Consider offering mentorship program to bridge experience gap")
        
        return recommendations
    
    def _generate_interview_focus(self, 
                                  scores: Dict[str, float],
                                  details: Dict[str, Any],
                                  concerns: List[Dict]) -> List[Dict[str, Any]]:
        """Suggest specific areas to probe in interview"""
        focus_areas = []
        
        # Technical deep dive
        skill_details = details.get('skills', {})
        matched_skills = skill_details.get('required_matches', [])
        if matched_skills:
            focus_areas.append({
                'category': 'Technical Skills',
                'priority': 'high',
                'topics': matched_skills[:3],
                'questions': [
                    f"Describe a complex project where you used {matched_skills[0] if matched_skills else 'key skills'}",
                    "Walk me through your approach to problem-solving",
                    "What are the latest developments in your technical stack?"
                ]
            })
        
        # Experience depth
        exp_details = details.get('experience', {})
        exp_score = exp_details.get('score') or 0  # Handle None
        if exp_score >= 60:
            focus_areas.append({
                'category': 'Experience & Impact',
                'priority': 'high',
                'topics': ['Leadership', 'Project ownership', 'Team collaboration'],
                'questions': [
                    "Tell me about the most challenging project you've led",
                    "How do you handle conflicting priorities?",
                    "Describe a time you mentored junior team members"
                ]
            })
        
        # Address concerns
        if concerns:
            top_concern = concerns[0]
            focus_areas.append({
                'category': f"Addressing {top_concern['area']}",
                'priority': 'high',
                'topics': top_concern['details'][:2],
                'questions': [
                    f"How do you plan to bridge the gap in {top_concern['area'].lower()}?",
                    "Describe your learning approach for new technologies",
                    "What resources do you use to stay current?"
                ]
            })
        
        # Cultural fit
        focus_areas.append({
            'category': 'Cultural Fit',
            'priority': 'medium',
            'topics': ['Work style', 'Communication', 'Values'],
            'questions': [
                "Describe your ideal work environment",
                "How do you handle feedback and criticism?",
                "What motivates you in your work?"
            ]
        })
        
        return focus_areas
    
    def _calculate_confidence(self, scores: Dict[str, float], details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence in the match assessment"""
        # Factors that increase confidence
        confidence_score = 50  # Base
        
        # High scores increase confidence
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        if avg_score >= 80:
            confidence_score += 30
        elif avg_score >= 60:
            confidence_score += 20
        elif avg_score >= 40:
            confidence_score += 10
        
        # Consistency across dimensions increases confidence
        if scores:
            score_variance = max(scores.values()) - min(scores.values())
            if score_variance < 20:  # Consistent
                confidence_score += 15
            elif score_variance < 40:
                confidence_score += 10
        
        # Data completeness increases confidence
        skill_details = details.get('skills', {})
        if skill_details.get('total_matched', 0) >= 5:
            confidence_score += 10
        
        confidence_score = min(confidence_score, 95)  # Cap at 95%
        
        # Determine level
        if confidence_score >= 80:
            level = "high"
            description = "Strong confidence in assessment - comprehensive data available"
        elif confidence_score >= 60:
            level = "medium"
            description = "Moderate confidence - some gaps in data but overall solid"
        else:
            level = "low"
            description = "Limited confidence - insufficient data for robust assessment"
        
        return {
            'score': confidence_score,
            'level': level,
            'description': description
        }
    
    def _get_hiring_recommendation(self, final_score: float, confidence: Dict[str, Any]) -> str:
        """Generate final hiring recommendation"""
        conf_level = confidence['level']
        
        if final_score >= 85 and conf_level in ['high', 'medium']:
            return "STRONG YES - Highly recommended for hire"
        elif final_score >= 70 and conf_level == 'high':
            return "YES - Recommended for hire with standard interview"
        elif final_score >= 70 and conf_level == 'medium':
            return "YES - Recommended with additional technical assessment"
        elif final_score >= 55:
            return "MAYBE - Consider for entry-level or with training plan"
        else:
            return "NO - Not recommended based on current qualifications"


def test_enhanced_explainer():
    """Test enhanced match explainer"""
    print("\\n" + "="*70)
    print("TESTING ENHANCED MATCH EXPLAINER")
    print("="*70)
    
    explainer = EnhancedMatchExplainer()
    
    # Test case: Good candidate with minor gaps
    match_data = {
        'final_score': 76.5,
        'scores': {
            'semantic': 78,
            'skills': 82,
            'experience': 70,
            'education': 75
        },
        'details': {
            'skills': {
                'score': 82,
                'required_matches': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS'],
                'missing_required': ['Kubernetes', 'Docker'],
                'total_matched': 5,
                'total_required': 7
            },
            'experience': {
                'score': 70,
                'candidate_years': 4,
                'required_years': 5
            },
            'education': {
                'score': 75,
                'highest_degree': 'Bachelor',
                'preferred_degree': 'Bachelor'
            }
        }
    }
    
    explanation = explainer.explain_match(match_data)
    
    print(f"\\n📊 Summary: {explanation['summary']}")
    print(f"\\n✨ Strengths ({len(explanation['strengths'])}):")
    for strength in explanation['strengths']:
        print(f"  • {strength['area']}: {strength['description']}")
    
    print(f"\\n⚠️ Concerns ({len(explanation['concerns'])}):")
    for concern in explanation['concerns']:
        print(f"  • {concern['area']} ({concern['severity']}): {concern['description']}")
    
    print(f"\\n💡 Recommendations:")
    for rec in explanation['recommendations']:
        print(f"  {rec}")
    
    print(f"\\n🎯 Interview Focus Areas:")
    for focus in explanation['interview_focus']:
        print(f"  • {focus['category']} (Priority: {focus['priority']})")
        print(f"    Sample question: {focus['questions'][0]}")
    
    print(f"\\n🎲 Confidence: {explanation['confidence']['level'].upper()} ({explanation['confidence']['score']}%)")
    print(f"   {explanation['confidence']['description']}")
    
    print(f"\\n✅ Hiring Recommendation: {explanation['hiring_recommendation']}")
    
    print("\\n" + "="*70)


if __name__ == "__main__":
    test_enhanced_explainer()
