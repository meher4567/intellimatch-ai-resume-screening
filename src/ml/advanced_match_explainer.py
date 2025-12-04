"""
Advanced Match Explainer with Natural Language Generation

Per ref.md recommendations - provides comprehensive match explanations with
executive summaries, strength/gap analysis, recommendations, and risk assessment.
"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class EnhancedMatchExplainer:
    """
    Generate detailed, natural language explanations for match scores.
    Includes strengths, gaps, and actionable recommendations.
    Quick Win implementation from ref.md Phase 1B enhancements.
    """
    
    def __init__(self):
        self.explanation_templates = self._load_templates()
    
    def generate_comprehensive_explanation(
        self, 
        candidate_data: Dict, 
        job_requirements: Dict, 
        match_scores: Dict
    ) -> Dict:
        """
        Generate comprehensive match explanation with multiple sections.
        
        Returns:
            Dict with:
                - summary: Executive summary (2-3 sentences)
                - match_category: excellent/strong/good/potential/weak
                - strengths: List of top strengths with evidence
                - gaps: List of gaps with severity
                - recommendations: For both candidate and employer
                - overall_assessment: Hiring recommendation
        """
        explanation = {
            'overall_match_score': match_scores.get('overall', 0),
            'match_category': self._categorize_match(match_scores.get('overall', 0)),
            'summary': '',
            'strengths': [],
            'gaps': [],
            'recommendations': {
                'for_employer': [],
                'for_candidate': []
            },
            'overall_assessment': ''
        }
        
        # Generate executive summary
        explanation['summary'] = self._generate_summary(
            candidate_data, job_requirements, match_scores
        )
        
        # Identify strengths
        explanation['strengths'] = self._identify_strengths(
            candidate_data, job_requirements, match_scores
        )
        
        # Identify gaps
        explanation['gaps'] = self._identify_gaps(
            candidate_data, job_requirements, match_scores
        )
        
        # Generate recommendations
        explanation['recommendations'] = self._generate_recommendations(
            candidate_data, job_requirements, explanation['gaps']
        )
        
        # Overall assessment
        explanation['overall_assessment'] = self._generate_assessment(
            explanation['match_category'], 
            len(explanation['strengths']), 
            len(explanation['gaps'])
        )
        
        return explanation
    
    def _categorize_match(self, score: float) -> str:
        """Categorize match quality based on score."""
        if score >= 85:
            return 'excellent_match'
        elif score >= 70:
            return 'strong_match'
        elif score >= 50:
            return 'good_match'
        elif score >= 30:
            return 'potential_match'
        else:
            return 'weak_match'
    
    def _generate_summary(self, candidate: Dict, job: Dict, scores: Dict) -> str:
        """Generate executive summary with natural language."""
        match_category = self._categorize_match(scores.get('overall', 0))
        
        templates = {
            'excellent_match': (
                "{name} is an excellent match for the {job_title} position with {overall_score}% compatibility. "
                "They demonstrate {experience_years} years of relevant experience and possess {skill_match_count} of {required_skills_count} required skills. "
                "This candidate shows exceptional alignment with your requirements and could make immediate contributions."
            ),
            'strong_match': (
                "{name} is a strong candidate for the {job_title} role with {overall_score}% match score. "
                "With {experience_years} years in similar roles and proficiency in {top_matching_skills}, "
                "they meet most critical requirements and show potential for success."
            ),
            'good_match': (
                "{name} shows good potential for the {job_title} position with {overall_score}% compatibility. "
                "While they have {experience_years} years of experience and match {skill_percentage}% of required skills, "
                "some upskilling in {gap_areas} would maximize their effectiveness."
            ),
            'potential_match': (
                "{name} could be considered for the {job_title} role with {overall_score}% match. "
                "They bring {experience_years} years of experience and transferable skills in {transferable_skills}. "
                "Investment in training for {key_gaps} would be needed for optimal performance."
            ),
            'weak_match': (
                "{name} has limited alignment with the {job_title} position at {overall_score}% match. "
                "With {experience_years} years of experience, they would require significant development in {major_gaps} "
                "to meet the role requirements effectively."
            )
        }
        
        template = templates.get(match_category, templates['potential_match'])
        
        # Calculate template variables
        required_skills = job.get('required_skills', [])
        candidate_skills = set(
            s.lower() for s in candidate.get('skills', {}).get('all_skills', [])
        )
        matching_skills = [s for s in required_skills if s.lower() in candidate_skills]
        gap_skills = [s for s in required_skills if s.lower() not in candidate_skills]
        
        # Get top matching skills (first 3)
        top_matching = ', '.join(matching_skills[:3]) if matching_skills else 'relevant skills'
        
        # Get experience years
        exp_years = candidate.get('total_experience_years', 0)
        
        summary = template.format(
            name=candidate.get('name', 'The candidate'),
            job_title=job.get('title', 'this position'),
            overall_score=round(scores.get('overall', 0)),
            experience_years=exp_years,
            skill_match_count=len(matching_skills),
            required_skills_count=len(required_skills),
            skill_percentage=round(len(matching_skills) / max(len(required_skills), 1) * 100),
            top_matching_skills=top_matching,
            transferable_skills=', '.join(matching_skills[:2]) if matching_skills else 'various skills',
            gap_areas=', '.join(gap_skills[:2]) if gap_skills else 'some technical areas',
            key_gaps=', '.join(gap_skills[:3]) if gap_skills else 'key skill areas',
            major_gaps=', '.join(gap_skills[:3]) if gap_skills else 'core competencies'
        )
        
        return summary
    
    def _identify_strengths(self, candidate: Dict, job: Dict, scores: Dict) -> List[Dict]:
        """Identify and rank candidate strengths with evidence."""
        strengths = []
        
        # 1. Skill matches
        required_skills = set(s.lower() for s in job.get('required_skills', []))
        candidate_skills_data = candidate.get('skills', {})
        
        # Check for proficiency data
        if candidate_skills_data.get('skills_with_proficiency'):
            for skill_info in candidate_skills_data['skills_with_proficiency']:
                skill = skill_info.get('skill', '')
                proficiency = skill_info.get('proficiency', 'intermediate')
                years = skill_info.get('years', 0)
                
                if skill.lower() in required_skills and proficiency in ['expert', 'proficient']:
                    strengths.append({
                        'type': 'skill_expertise',
                        'description': f"{proficiency.capitalize()}-level proficiency in {skill}",
                        'evidence': f"{years:.1f} years of experience" if years > 0 else "Strong proficiency demonstrated",
                        'impact': 'high',
                        'score_contribution': 15
                    })
        
        # 2. Experience alignment
        candidate_exp = candidate.get('total_experience_years', 0)
        required_exp = job.get('min_experience_years', 0)
        if candidate_exp >= required_exp:
            strengths.append({
                'type': 'experience',
                'description': f"Strong experience with {candidate_exp} years in relevant roles",
                'evidence': f"Exceeds minimum requirement of {required_exp} years",
                'impact': 'high',
                'score_contribution': 20
            })
        
        # 3. Education match
        if candidate.get('education'):
            for edu in candidate['education']:
                required_degree = job.get('required_degree', '')
                if required_degree and edu.get('degree'):
                    if self._degree_meets_requirement(edu['degree'], required_degree):
                        strengths.append({
                            'type': 'education',
                            'description': f"{edu['degree']} from {edu.get('institution', 'recognized institution')}",
                            'evidence': "Meets educational requirements",
                            'impact': 'medium',
                            'score_contribution': 10
                        })
                        break
        
        # 4. Career progression
        progression = candidate.get('career_progression', {})
        if progression.get('progression_type') == 'upward':
            strengths.append({
                'type': 'career_progression',
                'description': "Consistent upward career progression",
                'evidence': f"{progression.get('promotions', 0)} promotions demonstrated",
                'impact': 'medium',
                'score_contribution': 10
            })
        
        # 5. No job hopping
        job_hopping_score = candidate.get('job_hopping_score', 0.5)
        if job_hopping_score < 0.5:
            avg_tenure = candidate.get('avg_tenure_months', 0)
            strengths.append({
                'type': 'stability',
                'description': "Strong employment stability",
                'evidence': f"Average tenure of {avg_tenure:.0f} months per role",
                'impact': 'medium',
                'score_contribution': 10
            })
        
        # Sort by impact and score contribution
        strengths.sort(
            key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}[x['impact']], 
                x['score_contribution']
            ), 
            reverse=True
        )
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_gaps(self, candidate: Dict, job: Dict, scores: Dict) -> List[Dict]:
        """Identify gaps between candidate and job requirements."""
        gaps = []
        
        # 1. Missing required skills
        required_skills = job.get('required_skills', [])
        candidate_skills = set(
            s.lower() for s in candidate.get('skills', {}).get('all_skills', [])
        )
        
        for skill in required_skills:
            if skill.lower() not in candidate_skills:
                # Determine criticality
                critical_skills = job.get('critical_skills', [])
                is_critical = skill in critical_skills
                
                gaps.append({
                    'type': 'missing_skill',
                    'description': f"Missing required skill: {skill}",
                    'severity': 'critical' if is_critical else 'important',
                    'remediation': f"Would need training in {skill}",
                    'estimated_time_to_close': '3-6 months' if is_critical else '1-3 months'
                })
        
        # 2. Experience gap
        min_exp = job.get('min_experience_years', 0)
        candidate_exp = candidate.get('total_experience_years', 0)
        if candidate_exp < min_exp:
            gap_years = min_exp - candidate_exp
            gaps.append({
                'type': 'experience_gap',
                'description': f"Has {candidate_exp} years experience, role requires {min_exp} years",
                'severity': 'critical' if gap_years > 2 else 'important',
                'remediation': "May need additional mentoring and support",
                'estimated_time_to_close': f"{gap_years} years"
            })
        
        # 3. Education gap
        if job.get('required_degree'):
            has_degree = False
            for edu in candidate.get('education', []):
                if self._degree_meets_requirement(edu.get('degree', ''), job['required_degree']):
                    has_degree = True
                    break
            
            if not has_degree:
                gaps.append({
                    'type': 'education_gap',
                    'description': f"Missing required degree: {job['required_degree']}",
                    'severity': 'important',
                    'remediation': "Consider equivalent experience or certification",
                    'estimated_time_to_close': 'N/A'
                })
        
        # 4. Job hopping concern
        job_hopping_score = candidate.get('job_hopping_score', 0)
        if job_hopping_score > 0.7:
            avg_tenure = candidate.get('avg_tenure_months', 0)
            gaps.append({
                'type': 'retention_risk',
                'description': f"Short average tenure of {avg_tenure:.0f} months",
                'severity': 'minor',
                'remediation': "Discuss career goals and commitment during interview",
                'estimated_time_to_close': 'Ongoing assessment'
            })
        
        # 5. Career gaps
        career_gaps = candidate.get('career_gaps', [])
        if len(career_gaps) > 0:
            total_gap_months = sum(g.get('duration_months', 0) for g in career_gaps)
            if total_gap_months > 6:
                gaps.append({
                    'type': 'employment_gap',
                    'description': f"{len(career_gaps)} employment gap(s) totaling {total_gap_months} months",
                    'severity': 'minor',
                    'remediation': "Discuss reasons for gaps during interview",
                    'estimated_time_to_close': 'N/A'
                })
        
        # Sort by severity
        severity_order = {'critical': 0, 'important': 1, 'minor': 2}
        gaps.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return gaps
    
    def _generate_recommendations(self, candidate: Dict, job: Dict, gaps: List[Dict]) -> Dict:
        """Generate actionable recommendations."""
        recommendations = {
            'for_employer': [],
            'for_candidate': []
        }
        
        # For employer
        if not gaps:
            recommendations['for_employer'].append({
                'action': 'Fast-track to interview',
                'rationale': 'Candidate meets all requirements with no significant gaps',
                'priority': 'high'
            })
        else:
            critical_gaps = [g for g in gaps if g['severity'] == 'critical']
            if critical_gaps:
                recommendations['for_employer'].append({
                    'action': 'Assess critical skill gaps in interview',
                    'rationale': f"Candidate has {len(critical_gaps)} critical gaps but shows potential",
                    'priority': 'high'
                })
            else:
                recommendations['for_employer'].append({
                    'action': 'Consider with training plan',
                    'rationale': 'No critical gaps; minor gaps addressable with onboarding',
                    'priority': 'medium'
                })
            
            recommendations['for_employer'].append({
                'action': 'Conduct technical assessment',
                'rationale': 'Verify claimed skills and assess learning ability',
                'priority': 'high'
            })
        
        # For candidate
        if gaps:
            skill_gaps = [g for g in gaps if g['type'] == 'missing_skill']
            if skill_gaps:
                top_skills = ', '.join([
                    g['description'].replace('Missing required skill: ', '') 
                    for g in skill_gaps[:3]
                ])
                recommendations['for_candidate'].append({
                    'action': f'Upskill in {top_skills}',
                    'rationale': 'These are critical requirements for the role',
                    'priority': 'high',
                    'resources': ['Online courses', 'Certifications', 'Hands-on projects']
                })
        
        return recommendations
    
    def _generate_assessment(self, match_category: str, strengths_count: int, gaps_count: int) -> str:
        """Generate overall hiring assessment."""
        assessments = {
            'excellent_match': "**Strong Hire Recommendation** - This candidate exceeds expectations and should be prioritized for interview.",
            'strong_match': "**Recommended for Interview** - Strong alignment with requirements; conduct technical assessment.",
            'good_match': "**Consider with Conditions** - Good potential but requires skills development in specific areas.",
            'potential_match': "**Proceed with Caution** - Significant gaps exist; assess cultural fit and learning ability.",
            'weak_match': "**Not Recommended** - Insufficient alignment with role requirements at this time."
        }
        
        return assessments.get(match_category, "Assessment unavailable")
    
    def _degree_meets_requirement(self, candidate_degree: str, required_degree: str) -> bool:
        """Check if candidate's degree meets requirements."""
        degree_hierarchy = {
            'phd': 4, 'doctorate': 4, 'doctor': 4,
            'masters': 3, 'mba': 3, 'ms': 3, 'ma': 3, 'master': 3,
            'bachelors': 2, 'bs': 2, 'ba': 2, 'bachelor': 2,
            'associates': 1, 'associate': 1, 'diploma': 1
        }
        
        candidate_level = 0
        required_level = 0
        
        candidate_lower = candidate_degree.lower()
        required_lower = required_degree.lower()
        
        for degree, level in degree_hierarchy.items():
            if degree in candidate_lower:
                candidate_level = max(candidate_level, level)
            if degree in required_lower:
                required_level = max(required_level, level)
        
        return candidate_level >= required_level
    
    def _load_templates(self) -> Dict:
        """Load explanation templates."""
        return {
            'strengths': {
                'skill_match': "Strong technical alignment with {skill_count} matching skills",
                'experience': "Extensive experience of {years} years exceeds requirements",
                'education': "Educational background perfectly aligns with requirements",
                'achievements': "Proven track record with {achievement_count} quantified achievements"
            },
            'gaps': {
                'skill_gap': "Missing {skill_count} required technical skills",
                'experience_gap': "Falls short of experience requirement by {years} years",
                'education_gap': "Lacks required educational qualification"
            }
        }


# Quick integration helper
def explain_match(candidate_data: Dict, job_requirements: Dict, match_scores: Dict) -> Dict:
    """
    Convenience function for quick match explanation.
    
    Usage:
        explanation = explain_match(candidate, job, scores)
        print(explanation['summary'])
        print(f"Match category: {explanation['match_category']}")
        print(f"Strengths: {len(explanation['strengths'])}")
        print(f"Gaps: {len(explanation['gaps'])}")
    """
    explainer = EnhancedMatchExplainer()
    return explainer.generate_comprehensive_explanation(
        candidate_data, job_requirements, match_scores
    )
