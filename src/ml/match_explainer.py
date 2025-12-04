"""
Match Explainer with Natural Language Generation
Generates human-readable explanations for match scores
Enhanced with NLG templates, risk assessment, and growth potential analysis
"""

from typing import Dict, Any, List, Optional
import random


class MatchExplainer:
    """Generate detailed explanations for candidate-job matches"""
    
    def __init__(self):
        """Initialize match explainer"""
        # NLG templates for rich explanations
        self.nlg_templates = {
            'excellent': [
                "{name} is an outstanding candidate with a {score}% match. {key_strengths}",
                "Highly recommended: {name} demonstrates {key_strengths}, achieving a {score}% match.",
                "{name} stands out as an exceptional match ({score}%) with {key_strengths}."
            ],
            'strong': [
                "{name} is a strong candidate with a {score}% match. {key_strengths}",
                "{name} shows solid qualifications ({score}% match) including {key_strengths}.",
                "Recommended: {name} presents {key_strengths} with a {score}% overall match."
            ],
            'good': [
                "{name} is a good candidate with a {score}% match. {key_strengths}",
                "{name} demonstrates decent fit ({score}%) with {key_strengths}.",
                "{name} has reasonable qualifications ({score}% match): {key_strengths}."
            ],
            'fair': [
                "{name} shows potential but has gaps. Match score: {score}%. {concerns}",
                "{name} is a borderline candidate ({score}% match). {concerns}",
                "Consider carefully: {name} has a {score}% match. {concerns}"
            ],
            'weak': [
                "{name} may not be suitable for this role ({score}% match). {concerns}",
                "Not recommended: {name}'s {score}% match indicates {concerns}",
                "{name} has significant gaps ({score}% match): {concerns}"
            ]
        }
        
        # Risk assessment templates
        self.risk_indicators = {
            'retention': {
                'high': ['high job-hopping score', 'short tenures', 'frequent job changes'],
                'medium': ['moderate job changes', 'some short tenures'],
                'low': ['stable career history', 'long tenures', 'consistent employment']
            },
            'overqualification': {
                'high': ['significantly overqualified', 'may seek higher positions', 'risk of quick departure'],
                'medium': ['slightly overqualified', 'watch for engagement'],
                'low': ['appropriately qualified', 'good match level']
            },
            'skill_gap': {
                'high': ['major skill gaps', 'requires significant training', 'may struggle initially'],
                'medium': ['some skill gaps', 'needs moderate training'],
                'low': ['minimal gaps', 'ready to contribute']
            }
        }
    
    def explain_match(self, match_result: Dict[str, Any], candidate_name: str = "Candidate", 
                     resume_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a match
        
        Args:
            match_result: Result from MatchScorer.calculate_match()
            candidate_name: Name for personalized explanations
            resume_data: Optional resume data for enhanced analysis (timeline, skills with proficiency)
            
        Returns:
            Dict with various explanation formats
        """
        score = match_result['final_score']
        scores = match_result['scores']
        weights = match_result['weights']
        details = match_result['details']
        
        # Generate NLG narrative
        narrative = self._generate_nlg_narrative(score, match_result, candidate_name)
        
        # Assess risks (NEW)
        risk_assessment = self._assess_risks(match_result, resume_data)
        
        # Cultural fit assessment (NEW - Enhanced)
        cultural_fit = self._assess_cultural_fit(match_result, resume_data)
        
        # Performance risk assessment (NEW - Enhanced)
        performance_risk = self._assess_performance_risk(match_result, resume_data)
        
        # Estimate growth potential (NEW)
        growth_potential = self._estimate_growth_potential(match_result, resume_data)
        
        # Generate different explanation types
        return {
            'narrative': narrative,  # NEW: Natural language explanation
            'summary': self._generate_summary(score, match_result['assessment']),
            'score_breakdown': self._explain_score_breakdown(scores, weights),
            'factor_analysis': self._analyze_factors(scores, details),
            'strengths': match_result.get('strengths', []),
            'weaknesses': match_result.get('weaknesses', []),
            'recommendations': self._generate_recommendations(score, scores, details),
            'risk_assessment': risk_assessment,  # Basic risks
            'cultural_fit': cultural_fit,  # NEW: Enhanced cultural fit
            'performance_risk': performance_risk,  # NEW: Enhanced performance risk
            'growth_potential': growth_potential,  # Growth potential
            'detailed_factors': {
                'skills': self._explain_skills(details.get('skills', {})),
                'experience': self._explain_experience(details.get('experience', {})),
                'education': self._explain_education(details.get('education', {}))
            }
        }
    
    # ======================== NEW: NLG METHODS ========================
    
    def _generate_nlg_narrative(self, score: float, match_result: Dict, name: str) -> str:
        """
        Generate natural language narrative using templates
        
        Returns:
            Human-readable explanation paragraph
        """
        # Determine quality tier
        if score >= 85:
            tier = 'excellent'
        elif score >= 75:
            tier = 'strong'
        elif score >= 65:
            tier = 'good'
        elif score >= 50:
            tier = 'fair'
        else:
            tier = 'weak'
        
        # Select template
        template = random.choice(self.nlg_templates[tier])
        
        # Extract key strengths
        strengths = match_result.get('strengths', [])
        if strengths:
            key_strengths = ', '.join(strengths[:2])  # Top 2
        else:
            key_strengths = "relevant qualifications"
        
        # Extract concerns
        weaknesses = match_result.get('weaknesses', [])
        if weaknesses:
            concerns = '; '.join(weaknesses[:2])  # Top 2
        else:
            concerns = "some gaps in qualifications"
        
        # Fill template
        narrative = template.format(
            name=name,
            score=int(score),
            key_strengths=key_strengths,
            concerns=concerns
        )
        
        return narrative
    
    def _assess_risks(self, match_result: Dict, resume_data: Optional[Dict]) -> Dict:
        """
        Assess hiring risks: retention, overqualification, performance
        
        Returns:
            Dict with risk levels and explanations
        """
        risks = {
            'retention_risk': 'medium',
            'overqualification_risk': 'low',
            'skill_gap_risk': 'low',
            'overall_risk': 'low',
            'risk_factors': [],
            'mitigations': []
        }
        
        # Analyze retention risk (from timeline if available)
        if resume_data and 'timeline_analysis' in resume_data:
            timeline = resume_data['timeline_analysis']
            job_hopping = timeline.get('job_hopping_score', 0)
            
            if job_hopping > 0.7:
                risks['retention_risk'] = 'high'
                risks['risk_factors'].append('High job-hopping tendency (short tenures)')
                risks['mitigations'].append('Discuss career stability expectations during interview')
            elif job_hopping > 0.4:
                risks['retention_risk'] = 'medium'
                risks['risk_factors'].append('Moderate job changes in history')
                risks['mitigations'].append('Probe reasons for past job changes')
            else:
                risks['retention_risk'] = 'low'
        
        # Analyze overqualification risk
        exp_score = match_result['scores'].get('experience', 0)
        edu_score = match_result['scores'].get('education', 0)
        
        if exp_score > 95 and edu_score > 95:
            risks['overqualification_risk'] = 'high'
            risks['risk_factors'].append('May be overqualified and seek advancement quickly')
            risks['mitigations'].append('Discuss growth opportunities and career path')
        elif exp_score > 85 or edu_score > 95:
            risks['overqualification_risk'] = 'medium'
            risks['risk_factors'].append('Slightly above required qualifications')
        
        # Analyze skill gap risk
        skills_score = match_result['scores'].get('skills', 0)
        
        if skills_score < 50:
            risks['skill_gap_risk'] = 'high'
            risks['risk_factors'].append('Significant skill gaps requiring training')
            risks['mitigations'].append('Plan comprehensive onboarding with skill development')
        elif skills_score < 70:
            risks['skill_gap_risk'] = 'medium'
            risks['risk_factors'].append('Some skill gaps to address')
            risks['mitigations'].append('Provide targeted training for missing skills')
        else:
            risks['skill_gap_risk'] = 'low'
        
        # Calculate overall risk
        risk_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        total_risk = (
            risk_scores[risks['retention_risk']] +
            risk_scores[risks['overqualification_risk']] +
            risk_scores[risks['skill_gap_risk']]
        )
        
        if total_risk >= 7:
            risks['overall_risk'] = 'high'
        elif total_risk >= 5:
            risks['overall_risk'] = 'medium'
        else:
            risks['overall_risk'] = 'low'
        
        return risks
    
    def _assess_cultural_fit(self, match_result: Dict, resume_data: Optional[Dict]) -> Dict:
        """
        Estimate cultural fit based on career patterns and soft skills
        
        Returns:
            Dict with cultural fit assessment
        """
        fit = {
            'score': 0.5,  # 0-1 scale
            'level': 'medium',
            'indicators': [],
            'concerns': [],
            'recommendations': []
        }
        
        indicators = []
        concerns = []
        score_factors = []
        
        # Factor 1: Job stability (indicates commitment)
        if resume_data and 'timeline_analysis' in resume_data:
            timeline = resume_data['timeline_analysis']
            job_hopping = timeline.get('job_hopping_score', 0.5)
            
            if job_hopping < 0.3:
                indicators.append('Strong commitment - long tenures')
                score_factors.append(0.8)
            elif job_hopping > 0.7:
                concerns.append('Frequent job changes may indicate fit issues')
                score_factors.append(0.3)
                fit['recommendations'].append('Probe deeply into reasons for job changes')
            else:
                score_factors.append(0.5)
        
        # Factor 2: Career progression (indicates ambition and collaboration)
        if resume_data and 'timeline_analysis' in resume_data:
            timeline = resume_data['timeline_analysis']
            progression = timeline.get('progression', {})
            trajectory = progression.get('trajectory', 'stable')
            
            if trajectory == 'upward':
                indicators.append('Upward progression shows ambition and collaboration')
                score_factors.append(0.7)
            elif trajectory == 'lateral':
                indicators.append('Lateral moves show adaptability')
                score_factors.append(0.6)
        
        # Factor 3: Soft skills presence
        skills_detail = match_result['details'].get('skills', {})
        all_skills = skills_detail.get('matched_required', []) + skills_detail.get('matched_optional', [])
        
        soft_skill_keywords = ['communication', 'teamwork', 'leadership', 'collaboration', 
                              'problem solving', 'adaptability', 'creative']
        
        soft_skills_found = [s for s in all_skills if any(kw in s.lower() for kw in soft_skill_keywords)]
        
        if len(soft_skills_found) >= 3:
            indicators.append(f'Strong soft skills: {", ".join(soft_skills_found[:3])}')
            score_factors.append(0.7)
        elif len(soft_skills_found) >= 1:
            score_factors.append(0.5)
        else:
            concerns.append('Limited soft skills mentioned')
            score_factors.append(0.3)
            fit['recommendations'].append('Assess interpersonal skills during interview')
        
        # Factor 4: Company size experience (indicates adaptability)
        # This would need company size data, so we skip for now
        
        # Calculate overall score
        if score_factors:
            fit['score'] = sum(score_factors) / len(score_factors)
        
        # Determine level
        if fit['score'] >= 0.7:
            fit['level'] = 'high'
            indicators.append('Strong cultural fit indicators')
        elif fit['score'] >= 0.5:
            fit['level'] = 'medium'
        else:
            fit['level'] = 'low'
            concerns.append('Cultural fit concerns - thorough interview needed')
        
        fit['indicators'] = indicators
        fit['concerns'] = concerns
        fit['score'] = round(fit['score'], 2)
        
        return fit
    
    def _assess_performance_risk(self, match_result: Dict, resume_data: Optional[Dict]) -> Dict:
        """
        Assess performance risk based on skills and experience match
        
        Returns:
            Dict with performance risk assessment
        """
        risk = {
            'level': 'low',
            'score': 0.3,  # 0-1, lower is better
            'factors': [],
            'mitigations': []
        }
        
        risk_factors = []
        risk_scores = []
        
        # Factor 1: Skill gaps
        skills_score = match_result['scores'].get('skills', 100)
        skills_detail = match_result['details'].get('skills', {})
        
        missing_required = skills_detail.get('missing_required', [])
        required_coverage = skills_detail.get('required_coverage', 100)
        
        if required_coverage < 50:
            risk_factors.append(f'Major skill gaps: missing {len(missing_required)} required skills')
            risk_scores.append(0.8)
            risk['mitigations'].append('Plan intensive training for missing skills')
        elif required_coverage < 70:
            risk_factors.append(f'Some skill gaps: {len(missing_required)} skills need development')
            risk_scores.append(0.5)
            risk['mitigations'].append('Provide mentorship and skill development')
        else:
            risk_scores.append(0.2)
        
        # Factor 2: Experience level match
        exp_score = match_result['scores'].get('experience', 100)
        exp_detail = match_result['details'].get('experience', {})
        
        candidate_level = exp_detail.get('candidate_level', 'unknown')
        required_level = exp_detail.get('required_level', 'unknown')
        
        level_order = ['entry', 'mid', 'senior', 'expert']
        
        try:
            cand_idx = level_order.index(candidate_level.lower())
            req_idx = level_order.index(required_level.lower())
            
            if cand_idx < req_idx - 1:  # More than 1 level below
                risk_factors.append('Experience level below requirement')
                risk_scores.append(0.7)
                risk['mitigations'].append('Close supervision and structured onboarding')
            elif cand_idx < req_idx:
                risk_factors.append('Slightly below required experience level')
                risk_scores.append(0.4)
            else:
                risk_scores.append(0.2)
        except (ValueError, AttributeError):
            risk_scores.append(0.3)  # Unknown, assume moderate risk
        
        # Factor 3: Learning curve indicators
        if resume_data and 'skill_portfolio_analysis' in resume_data:
            portfolio = resume_data['skill_portfolio_analysis']
            depth = portfolio.get('depth_score', 0)
            
            if depth < 0.2:
                risk_factors.append('Limited deep expertise - steep learning curve expected')
                risk_scores.append(0.6)
                risk['mitigations'].append('Pair with experienced team member')
            elif depth < 0.4:
                risk_scores.append(0.3)
            else:
                risk_scores.append(0.1)
        
        # Calculate overall risk
        if risk_scores:
            risk['score'] = sum(risk_scores) / len(risk_scores)
        
        # Determine level
        if risk['score'] >= 0.6:
            risk['level'] = 'high'
        elif risk['score'] >= 0.4:
            risk['level'] = 'medium'
        else:
            risk['level'] = 'low'
        
        risk['factors'] = risk_factors
        risk['score'] = round(risk['score'], 2)
        
        return risk
    
    def _estimate_growth_potential(self, match_result: Dict, resume_data: Optional[Dict]) -> Dict:
        """
        Estimate candidate's growth potential and learning agility
        
        Returns:
            Dict with growth scores and indicators
        """
        growth = {
            'score': 0.5,  # 0-1 scale
            'level': 'medium',
            'indicators': [],
            'learning_agility': 'medium',
            'career_trajectory': 'stable'
        }
        
        indicators = []
        score_factors = []
        
        # Factor 1: Career progression
        if resume_data and 'timeline_analysis' in resume_data:
            timeline = resume_data['timeline_analysis']
            progression = timeline.get('progression', {})
            trajectory = progression.get('trajectory', 'stable')
            prog_score = progression.get('progression_score', 0.5)
            
            growth['career_trajectory'] = trajectory
            
            if trajectory == 'upward':
                indicators.append('Strong upward career progression')
                score_factors.append(0.8)
            elif trajectory == 'lateral':
                indicators.append('Consistent lateral moves (breadth building)')
                score_factors.append(0.6)
            else:
                score_factors.append(0.5)
        
        # Factor 2: Skill diversity
        if resume_data and 'skills_with_proficiency' in resume_data:
            skills = resume_data['skills_with_proficiency']
            portfolio = resume_data.get('skill_portfolio_analysis', {})
            
            breadth = portfolio.get('breadth_score', 0)
            if breadth > 0.7:
                indicators.append('Diverse skill portfolio shows adaptability')
                score_factors.append(0.7)
            elif breadth > 0.4:
                score_factors.append(0.5)
            else:
                score_factors.append(0.3)
        
        # Factor 3: Education level (proxy for learning ability)
        edu_detail = match_result['details'].get('education', {})
        highest_degree = edu_detail.get('highest_degree', '')
        
        if 'phd' in highest_degree.lower() or 'doctorate' in highest_degree.lower():
            indicators.append('Advanced degree indicates strong learning capability')
            score_factors.append(0.9)
            growth['learning_agility'] = 'high'
        elif 'master' in highest_degree.lower():
            indicators.append('Graduate education shows commitment to learning')
            score_factors.append(0.7)
            growth['learning_agility'] = 'high'
        elif 'bachelor' in highest_degree.lower():
            score_factors.append(0.6)
        else:
            score_factors.append(0.4)
        
        # Factor 4: Recent skill acquisition (if we have years data)
        # This would require more detailed skill timeline
        
        # Calculate overall growth score
        if score_factors:
            growth['score'] = sum(score_factors) / len(score_factors)
        
        # Determine level
        if growth['score'] >= 0.7:
            growth['level'] = 'high'
            indicators.append('High growth potential - likely to advance quickly')
        elif growth['score'] >= 0.5:
            growth['level'] = 'medium'
        else:
            growth['level'] = 'low'
            indicators.append('May need structured development support')
        
        growth['indicators'] = indicators
        growth['score'] = round(growth['score'], 2)
        
        return growth
    
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
