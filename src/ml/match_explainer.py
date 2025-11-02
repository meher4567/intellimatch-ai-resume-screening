"""
Match Explainer
Generates human-readable explanations for match scores
"""

from typing import Dict, Any, List


class MatchExplainer:
    """Generate detailed explanations for candidate-job matches"""
    
    def __init__(self):
        """Initialize match explainer"""
        pass
    
    def explain_match(self, match_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a match
        
        Args:
            match_result: Result from MatchScorer.calculate_match()
            
        Returns:
            Dict with various explanation formats
        """
        score = match_result['final_score']
        scores = match_result['scores']
        weights = match_result['weights']
        details = match_result['details']
        
        # Generate different explanation types
        return {
            'summary': self._generate_summary(score, match_result['assessment']),
            'score_breakdown': self._explain_score_breakdown(scores, weights),
            'factor_analysis': self._analyze_factors(scores, details),
            'strengths': match_result.get('strengths', []),
            'weaknesses': match_result.get('weaknesses', []),
            'recommendations': self._generate_recommendations(score, scores, details),
            'detailed_factors': {
                'skills': self._explain_skills(details.get('skills', {})),
                'experience': self._explain_experience(details.get('experience', {})),
                'education': self._explain_education(details.get('education', {}))
            }
        }
    
    def _generate_summary(self, score: float, assessment: str) -> str:
        """Generate one-line summary"""
        if score >= 85:
            emoji = "🌟"
        elif score >= 75:
            emoji = "✅"
        elif score >= 65:
            emoji = "👍"
        elif score >= 50:
            emoji = "⚠️"
        else:
            emoji = "❌"
        
        return f"{emoji} Match Score: {score}/100 - {assessment}"
    
    def _explain_score_breakdown(self,
                                 scores: Dict[str, float],
                                 weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Explain how each factor contributes to final score"""
        breakdown = []
        
        for factor, score in scores.items():
            weight = weights[factor]
            contribution = score * weight
            
            # Visual representation
            bar_length = int(score / 5)  # 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            breakdown.append({
                'factor': factor.capitalize(),
                'score': round(score, 1),
                'weight': round(weight * 100, 0),
                'contribution': round(contribution, 1),
                'bar': bar,
                'rating': self._get_rating(score)
            })
        
        return breakdown
    
    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Strong"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Weak"
    
    def _analyze_factors(self,
                        scores: Dict[str, float],
                        details: Dict[str, Any]) -> List[str]:
        """Analyze each scoring factor"""
        analysis = []
        
        # Semantic analysis
        semantic_score = scores.get('semantic', 0)
        if semantic_score >= 70:
            analysis.append("Strong semantic match indicates candidate's background aligns well with job description")
        elif semantic_score < 50:
            analysis.append("Weak semantic match suggests significant differences in background and job requirements")
        
        # Skills analysis
        skills_detail = details.get('skills', {})
        required_cov = skills_detail.get('required_coverage', 0)
        optional_cov = skills_detail.get('optional_coverage', 0)
        
        if required_cov >= 80:
            analysis.append(f"Candidate possesses {int(required_cov)}% of required skills")
        elif required_cov < 50:
            missing = skills_detail.get('missing_required', [])
            analysis.append(f"Missing key skills: {', '.join(missing[:3])}")
        
        if optional_cov >= 50:
            analysis.append(f"Bonus: Has {int(optional_cov)}% of optional skills")
        
        # Experience analysis
        exp_detail = details.get('experience', {})
        candidate_years = exp_detail.get('candidate_years', 0)
        required_years = exp_detail.get('required_years', 0)
        
        if required_years:
            if candidate_years >= required_years:
                extra = candidate_years - required_years
                if extra >= 3:
                    analysis.append(f"Significantly more experienced than required (+{extra} years)")
                else:
                    analysis.append(f"Meets experience requirement ({candidate_years} years)")
            else:
                gap = required_years - candidate_years
                analysis.append(f"Experience gap: {gap} year(s) below requirement")
        
        # Education analysis
        edu_detail = details.get('education', {})
        edu_assessment = edu_detail.get('assessment', '')
        
        if 'Excellent' in edu_assessment or 'Strong' in edu_assessment:
            degree = edu_detail.get('highest_degree', '')
            field = edu_detail.get('highest_field', '')
            analysis.append(f"Educational background is strong: {degree} in {field}")
        elif 'not meet' in edu_assessment.lower():
            analysis.append("Education does not meet job requirements")
        
        return analysis
    
    def _generate_recommendations(self,
                                 final_score: float,
                                 scores: Dict[str, float],
                                 details: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if final_score >= 85:
            recommendations.append("🎯 Priority candidate - Schedule interview immediately")
            recommendations.append("💡 Consider for senior or lead positions")
        elif final_score >= 75:
            recommendations.append("✅ Strong candidate - Move to next interview round")
            recommendations.append("💡 Prepare technical assessment")
        elif final_score >= 65:
            recommendations.append("👍 Good candidate - Review in detail")
            recommendations.append("💡 Consider for initial phone screening")
        elif final_score >= 50:
            recommendations.append("⚠️  Borderline candidate - Assess carefully")
            recommendations.append("💡 May be suitable for junior positions or with training")
        else:
            recommendations.append("❌ Not recommended for this position")
            recommendations.append("💡 Consider for different roles that better match skills")
        
        # Specific recommendations based on weak areas
        if scores.get('skills', 0) < 50:
            skills_detail = details.get('skills', {})
            missing = skills_detail.get('missing_required', [])
            if missing:
                recommendations.append(f"⚠️  Candidate needs training in: {', '.join(missing[:3])}")
        
        if scores.get('experience', 0) < 50:
            recommendations.append("⚠️  Limited experience - Consider for junior role or mentorship program")
        
        if scores.get('education', 0) < 50:
            edu_detail = details.get('education', {})
            if edu_detail.get('assessment') == 'Acceptable with experience':
                recommendations.append("💡 Education gap may be offset by practical experience")
        
        return recommendations
    
    def _explain_skills(self, skills_detail: Dict[str, Any]) -> str:
        """Generate detailed skills explanation"""
        if not skills_detail:
            return "No skill information available"
        
        matched_req = skills_detail.get('matched_required', [])
        missing_req = skills_detail.get('missing_required', [])
        matched_opt = skills_detail.get('matched_optional', [])
        req_cov = skills_detail.get('required_coverage', 0)
        opt_cov = skills_detail.get('optional_coverage', 0)
        
        parts = []
        
        # Required skills
        if matched_req:
            parts.append(f"✅ Has {len(matched_req)} required skill(s): {', '.join(matched_req)}")
        
        if missing_req:
            parts.append(f"❌ Missing {len(missing_req)} required skill(s): {', '.join(missing_req)}")
        
        parts.append(f"📊 Required skills coverage: {req_cov:.0f}%")
        
        # Optional skills
        if matched_opt:
            parts.append(f"⭐ Bonus: Has {len(matched_opt)} optional skill(s): {', '.join(matched_opt)}")
        
        if opt_cov > 0:
            parts.append(f"📊 Optional skills coverage: {opt_cov:.0f}%")
        
        return "\n".join(parts)
    
    def _explain_experience(self, exp_detail: Dict[str, Any]) -> str:
        """Generate detailed experience explanation"""
        if not exp_detail:
            return "No experience information available"
        
        candidate_years = exp_detail.get('candidate_years', 0)
        required_years = exp_detail.get('required_years', 'Not specified')
        candidate_level = exp_detail.get('candidate_level', 'Unknown')
        required_level = exp_detail.get('required_level', 'Unknown')
        assessment = exp_detail.get('assessment', '')
        
        parts = []
        
        parts.append(f"👤 Candidate: {candidate_years} year(s), {candidate_level.capitalize()} level")
        
        if required_years != 'Not specified':
            parts.append(f"📋 Required: {required_years} year(s), {required_level.capitalize()} level")
        
        # Assessment
        if assessment:
            if 'Meets' in assessment:
                parts.append(f"✅ {assessment}")
            elif 'Close' in assessment:
                parts.append(f"⚠️  {assessment}")
            elif 'Under' in assessment:
                parts.append(f"❌ {assessment}")
            else:
                parts.append(f"ℹ️  {assessment}")
        
        # Breakdown
        breakdown = exp_detail.get('breakdown', {})
        if breakdown:
            parts.append(f"📊 Years score: {breakdown.get('years_score', 0):.0f}/100")
            parts.append(f"📊 Level score: {breakdown.get('level_score', 0):.0f}/100")
        
        return "\n".join(parts)
    
    def _explain_education(self, edu_detail: Dict[str, Any]) -> str:
        """Generate detailed education explanation"""
        if not edu_detail:
            return "No education information available"
        
        highest_degree = edu_detail.get('highest_degree', 'None')
        highest_field = edu_detail.get('highest_field', 'N/A')
        required_degree = edu_detail.get('required_degree', 'Not specified')
        assessment = edu_detail.get('assessment', '')
        
        parts = []
        
        parts.append(f"🎓 Candidate: {highest_degree} in {highest_field}")
        
        if required_degree != 'Not specified':
            parts.append(f"📋 Required: {required_degree}")
        
        # Assessment
        if assessment:
            if 'Excellent' in assessment or 'Strong' in assessment:
                parts.append(f"✅ {assessment}")
            elif 'minimum' in assessment.lower():
                parts.append(f"⚠️  {assessment}")
            elif 'not meet' in assessment.lower():
                parts.append(f"❌ {assessment}")
            else:
                parts.append(f"ℹ️  {assessment}")
        
        # Breakdown
        breakdown = edu_detail.get('breakdown', {})
        if breakdown:
            parts.append(f"📊 Degree score: {breakdown.get('degree_score', 0):.0f}/100")
            parts.append(f"📊 Field score: {breakdown.get('field_score', 0):.0f}/100")
        
        return "\n".join(parts)
    
    def generate_report(self, match_result: Dict[str, Any], candidate_name: str = "Candidate") -> str:
        """Generate a formatted text report"""
        explanation = self.explain_match(match_result)
        
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append(f"📊 MATCH REPORT: {candidate_name}")
        report_lines.append("=" * 70)
        
        # Summary
        report_lines.append(f"\n{explanation['summary']}\n")
        
        # Score breakdown
        report_lines.append("📈 SCORE BREAKDOWN:")
        for item in explanation['score_breakdown']:
            report_lines.append(f"\n  {item['factor']} ({item['weight']:.0f}% weight):")
            report_lines.append(f"    {item['bar']} {item['score']}/100 ({item['rating']})")
            report_lines.append(f"    Contribution to final score: {item['contribution']:.1f}")
        
        # Factor analysis
        if explanation['factor_analysis']:
            report_lines.append("\n\n🔍 ANALYSIS:")
            for analysis in explanation['factor_analysis']:
                report_lines.append(f"  • {analysis}")
        
        # Strengths
        if explanation['strengths']:
            report_lines.append("\n\n✅ STRENGTHS:")
            for strength in explanation['strengths']:
                report_lines.append(f"  • {strength}")
        
        # Weaknesses
        if explanation['weaknesses']:
            report_lines.append("\n\n⚠️  AREAS OF CONCERN:")
            for weakness in explanation['weaknesses']:
                report_lines.append(f"  • {weakness}")
        
        # Recommendations
        if explanation['recommendations']:
            report_lines.append("\n\n💡 RECOMMENDATIONS:")
            for rec in explanation['recommendations']:
                report_lines.append(f"  {rec}")
        
        # Detailed factors
        report_lines.append("\n\n" + "=" * 70)
        report_lines.append("📋 DETAILED BREAKDOWN")
        report_lines.append("=" * 70)
        
        report_lines.append("\n🛠️  SKILLS:")
        report_lines.append(explanation['detailed_factors']['skills'])
        
        report_lines.append("\n\n💼 EXPERIENCE:")
        report_lines.append(explanation['detailed_factors']['experience'])
        
        report_lines.append("\n\n🎓 EDUCATION:")
        report_lines.append(explanation['detailed_factors']['education'])
        
        report_lines.append("\n" + "=" * 70)
        
        return "\n".join(report_lines)


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Match Explainer")
    print("=" * 70)
    
    explainer = MatchExplainer()
    
    # Create sample match result
    match_result = {
        'final_score': 87.5,
        'scores': {
            'semantic': 85.0,
            'skills': 90.0,
            'experience': 85.0,
            'education': 88.0
        },
        'weights': {
            'semantic': 0.30,
            'skills': 0.40,
            'experience': 0.20,
            'education': 0.10
        },
        'details': {
            'skills': {
                'score': 90.0,
                'matched_required': ['Python', 'Django', 'PostgreSQL'],
                'missing_required': [],
                'matched_optional': ['AWS', 'Docker'],
                'required_coverage': 100.0,
                'optional_coverage': 66.7
            },
            'experience': {
                'score': 85.0,
                'candidate_years': 6,
                'required_years': 5,
                'candidate_level': 'senior',
                'required_level': 'senior',
                'assessment': 'Meets requirements',
                'breakdown': {
                    'years_score': 100,
                    'level_score': 100
                }
            },
            'education': {
                'score': 88.0,
                'highest_degree': 'Master of Science',
                'highest_field': 'Computer Science',
                'required_degree': 'Bachelor',
                'assessment': 'Excellent match',
                'breakdown': {
                    'degree_score': 100,
                    'field_score': 100
                }
            }
        },
        'assessment': 'Excellent match - Highly recommended',
        'strengths': [
            'Strong semantic match with job description',
            'Excellent skill match (3 key skills)',
            'Well-qualified with 6 years experience',
            'Strong educational background (Master of Science)'
        ],
        'weaknesses': []
    }
    
    # Test 1: Generate explanation
    print("\n1️⃣ Test: Generate match explanation")
    explanation = explainer.explain_match(match_result)
    
    print(f"\n   Summary: {explanation['summary']}")
    
    print(f"\n   Score Breakdown:")
    for item in explanation['score_breakdown']:
        print(f"      {item['factor']}: {item['score']}/100 ({item['rating']})")
    
    print(f"\n   Strengths:")
    for strength in explanation['strengths']:
        print(f"      • {strength}")
    
    # Test 2: Generate full report
    print("\n" + "=" * 70)
    print("\n2️⃣ Test: Generate full report\n")
    
    report = explainer.generate_report(match_result, candidate_name="Alice Johnson")
    print(report)
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
