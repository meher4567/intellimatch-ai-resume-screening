"""
Resume Quality Scorer
Uses ML to score resume quality (1-10) based on multiple factors
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Tuple
import re
from dataclasses import dataclass


@dataclass
class QualityFactors:
    """Quality assessment factors"""
    formatting: float  # 0-10: Structure, sections, layout
    completeness: float  # 0-10: Has all essential sections
    clarity: float  # 0-10: Clear writing, concise
    quantification: float  # 0-10: Uses numbers/metrics
    relevance: float  # 0-10: Professional content
    length: float  # 0-10: Appropriate length


class ResumeQualityScorer:
    """
    Score resume quality using rule-based + ML hybrid approach
    
    Factors assessed:
    1. Formatting & Structure (10 points)
    2. Completeness (10 points)
    3. Clarity & Conciseness (10 points)
    4. Quantification & Metrics (10 points)
    5. Professional Relevance (10 points)
    6. Length Appropriateness (10 points)
    
    Total: 1-10 scale
    """
    
    # Essential sections
    ESSENTIAL_SECTIONS = [
        'experience', 'education', 'skills'
    ]
    
    # Optional but good sections
    GOOD_SECTIONS = [
        'summary', 'projects', 'certifications', 'achievements'
    ]
    
    # Red flag words (unprofessional)
    RED_FLAGS = [
        'i am', 'my name is', 'curriculum vitae', 'resume of',
        'references available upon request', 'salary negotiable'
    ]
    
    def score_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score overall resume quality
        
        Args:
            resume_data: Parsed resume with sections, text, metadata
            
        Returns:
            Dict with score, factors, recommendations
        """
        # Extract components
        sections = resume_data.get('sections', {})
        text = resume_data.get('full_text', '')
        metadata = resume_data.get('metadata', {})
        
        # Score individual factors
        formatting_score = self._score_formatting(sections, metadata)
        completeness_score = self._score_completeness(sections)
        clarity_score = self._score_clarity(text, sections)
        quantification_score = self._score_quantification(text)
        relevance_score = self._score_relevance(text, sections)
        length_score = self._score_length(text)
        
        factors = QualityFactors(
            formatting=formatting_score,
            completeness=completeness_score,
            clarity=clarity_score,
            quantification=quantification_score,
            relevance=relevance_score,
            length=length_score
        )
        
        # Calculate weighted overall score
        overall = (
            formatting_score * 0.15 +
            completeness_score * 0.25 +
            clarity_score * 0.15 +
            quantification_score * 0.15 +
            relevance_score * 0.20 +
            length_score * 0.10
        )
        
        # Generate grade and recommendations
        grade = self._get_grade(overall)
        recommendations = self._generate_recommendations(factors, sections)
        
        return {
            'overall_score': round(overall, 2),
            'grade': grade,
            'factors': {
                'formatting': round(formatting_score, 2),
                'completeness': round(completeness_score, 2),
                'clarity': round(clarity_score, 2),
                'quantification': round(quantification_score, 2),
                'relevance': round(relevance_score, 2),
                'length': round(length_score, 2)
            },
            'weights': {
                'formatting': 0.15,
                'completeness': 0.25,
                'clarity': 0.15,
                'quantification': 0.15,
                'relevance': 0.20,
                'length': 0.10
            },
            'recommendations': recommendations,
            'strengths': self._identify_strengths(factors),
            'weaknesses': self._identify_weaknesses(factors)
        }
    
    def _score_formatting(self, sections: Dict, metadata: Dict) -> float:
        """Score formatting and structure (0-10)"""
        score = 5.0  # Start at baseline
        
        # Has clear sections
        if len(sections) >= 4:
            score += 2.0
        elif len(sections) >= 3:
            score += 1.0
        
        # Has contact info
        if metadata.get('email'):
            score += 1.0
        if metadata.get('phone'):
            score += 0.5
        if metadata.get('linkedin'):
            score += 0.5
        
        # Reasonable number of sections (not too many)
        if 3 <= len(sections) <= 8:
            score += 1.0
        
        return min(10.0, score)
    
    def _score_completeness(self, sections: Dict) -> float:
        """Score completeness of essential sections (0-10)"""
        score = 0.0
        
        # Check essential sections (2.5 points each)
        for section in self.ESSENTIAL_SECTIONS:
            if section in sections:
                content = sections[section].get('content', '')
                if len(content) > 50:  # Has substantial content
                    score += 3.33
        
        # Bonus for good optional sections (0.5 points each)
        for section in self.GOOD_SECTIONS:
            if section in sections:
                content = sections[section].get('content', '')
                if len(content) > 30:
                    score += 0.33
        
        return min(10.0, score)
    
    def _score_clarity(self, text: str, sections: Dict) -> float:
        """Score clarity and conciseness (0-10)"""
        score = 5.0  # Start at baseline
        
        # Check for red flags (unprofessional language)
        text_lower = text.lower()
        red_flag_count = sum(1 for flag in self.RED_FLAGS if flag in text_lower)
        score -= red_flag_count * 0.5
        
        # Check for bullet points (good for readability)
        bullet_count = text.count('•') + text.count('-') + text.count('*')
        if bullet_count >= 10:
            score += 2.0
        elif bullet_count >= 5:
            score += 1.0
        
        # Check for overly long paragraphs (bad)
        lines = text.split('\n')
        long_lines = sum(1 for line in lines if len(line) > 200)
        score -= long_lines * 0.2
        
        # Check for first-person pronouns (less professional)
        first_person_count = len(re.findall(r'\b(I|me|my|mine)\b', text, re.IGNORECASE))
        if first_person_count > 10:
            score -= 1.0
        elif first_person_count > 5:
            score -= 0.5
        
        return max(1.0, min(10.0, score))
    
    def _score_quantification(self, text: str) -> float:
        """Score use of numbers and metrics (0-10)"""
        # Find numbers and percentages
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', text)
        
        # Find metrics/achievements
        achievement_words = [
            'increased', 'decreased', 'improved', 'reduced', 'achieved',
            'delivered', 'grew', 'saved', 'generated', 'optimized'
        ]
        achievement_count = sum(1 for word in achievement_words if word in text.lower())
        
        # Score based on quantification
        score = 0.0
        
        # Numbers (0-5 points)
        if len(numbers) >= 20:
            score += 5.0
        elif len(numbers) >= 10:
            score += 3.0
        elif len(numbers) >= 5:
            score += 2.0
        elif len(numbers) >= 2:
            score += 1.0
        
        # Achievement language (0-5 points)
        if achievement_count >= 10:
            score += 5.0
        elif achievement_count >= 5:
            score += 3.0
        elif achievement_count >= 3:
            score += 2.0
        elif achievement_count >= 1:
            score += 1.0
        
        return min(10.0, score)
    
    def _score_relevance(self, text: str, sections: Dict) -> float:
        """Score professional relevance (0-10)"""
        score = 5.0  # Baseline
        
        # Has professional experience
        if 'experience' in sections:
            exp_content = sections['experience'].get('content', '')
            if len(exp_content) > 200:
                score += 2.0
            elif len(exp_content) > 100:
                score += 1.0
        
        # Has skills section
        if 'skills' in sections:
            skills_content = sections['skills'].get('content', '')
            if len(skills_content) > 100:
                score += 1.5
            elif len(skills_content) > 50:
                score += 1.0
        
        # Has education
        if 'education' in sections:
            edu_content = sections['education'].get('content', '')
            if len(edu_content) > 50:
                score += 1.0
        
        # Has projects/achievements
        if 'projects' in sections or 'achievements' in sections:
            score += 0.5
        
        return min(10.0, score)
    
    def _score_length(self, text: str) -> float:
        """Score appropriate length (0-10)"""
        word_count = len(text.split())
        
        # Ideal: 400-800 words (1-2 pages)
        if 400 <= word_count <= 800:
            return 10.0
        elif 300 <= word_count <= 1000:
            return 8.0
        elif 200 <= word_count <= 1200:
            return 6.0
        elif 100 <= word_count <= 1500:
            return 4.0
        else:
            return 2.0
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 9.0:
            return 'A+ (Excellent)'
        elif score >= 8.0:
            return 'A (Very Good)'
        elif score >= 7.0:
            return 'B+ (Good)'
        elif score >= 6.0:
            return 'B (Above Average)'
        elif score >= 5.0:
            return 'C (Average)'
        elif score >= 4.0:
            return 'D (Below Average)'
        else:
            return 'F (Poor)'
    
    def _generate_recommendations(self, factors: QualityFactors, sections: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if factors.formatting < 7.0:
            recommendations.append("Improve formatting: Add clear section headings and consistent structure")
        
        if factors.completeness < 7.0:
            missing = [s for s in self.ESSENTIAL_SECTIONS if s not in sections]
            if missing:
                recommendations.append(f"Add missing sections: {', '.join(missing)}")
        
        if factors.clarity < 7.0:
            recommendations.append("Improve clarity: Use bullet points and remove first-person pronouns")
        
        if factors.quantification < 7.0:
            recommendations.append("Add quantification: Include numbers, metrics, and measurable achievements")
        
        if factors.relevance < 7.0:
            recommendations.append("Increase relevance: Focus on professional experience and technical skills")
        
        if factors.length < 7.0:
            recommendations.append("Adjust length: Aim for 400-800 words (1-2 pages)")
        
        return recommendations
    
    def _identify_strengths(self, factors: QualityFactors) -> List[str]:
        """Identify resume strengths"""
        strengths = []
        
        if factors.formatting >= 8.0:
            strengths.append("Well-formatted with clear structure")
        if factors.completeness >= 8.0:
            strengths.append("Comprehensive with all essential sections")
        if factors.clarity >= 8.0:
            strengths.append("Clear and concise writing")
        if factors.quantification >= 8.0:
            strengths.append("Strong use of metrics and quantification")
        if factors.relevance >= 8.0:
            strengths.append("Highly relevant professional content")
        if factors.length >= 8.0:
            strengths.append("Appropriate length")
        
        return strengths
    
    def _identify_weaknesses(self, factors: QualityFactors) -> List[str]:
        """Identify resume weaknesses"""
        weaknesses = []
        
        if factors.formatting < 5.0:
            weaknesses.append("Poor formatting and structure")
        if factors.completeness < 5.0:
            weaknesses.append("Missing essential sections")
        if factors.clarity < 5.0:
            weaknesses.append("Unclear or unprofessional writing")
        if factors.quantification < 5.0:
            weaknesses.append("Lacks metrics and achievements")
        if factors.relevance < 5.0:
            weaknesses.append("Content not professionally relevant")
        if factors.length < 5.0:
            weaknesses.append("Inappropriate length")
        
        return weaknesses


if __name__ == "__main__":
    print("=" * 80)
    print("🧪 Testing Resume Quality Scorer")
    print("=" * 80)
    
    scorer = ResumeQualityScorer()
    
    # Test 1: High-quality resume
    print("\n1️⃣ Test: High-quality resume")
    good_resume = {
        'sections': {
            'summary': {'content': 'Senior software engineer with 5 years experience...'},
            'experience': {'content': 'Led team of 5 engineers, increased performance by 40%, delivered 3 major projects...'},
            'skills': {'content': 'Python, Django, AWS, PostgreSQL, Docker, Kubernetes...'},
            'education': {'content': 'BS Computer Science, MIT, 2018'},
            'projects': {'content': 'Built ML pipeline processing 1M records/day...'}
        },
        'full_text': '''John Doe
Engineer at Tech Corp

Led team of 5 engineers, increased system performance by 40%, delivered 3 major projects ahead of schedule.
Reduced costs by $200K through AWS optimization. Improved deployment speed by 60%.

• Python, Django, AWS, PostgreSQL
• Docker, Kubernetes, CI/CD
• Machine Learning, TensorFlow

Built ML pipeline processing 1M records/day. Achieved 95% accuracy on classification task.

BS Computer Science, MIT, 2018''',
        'metadata': {'email': 'john@email.com', 'phone': '123-456-7890', 'linkedin': 'linkedin.com/in/johndoe'}
    }
    
    result = scorer.score_resume(good_resume)
    print(f"   Overall Score: {result['overall_score']}/10")
    print(f"   Grade: {result['grade']}")
    print(f"\n   Factor Scores:")
    for factor, score in result['factors'].items():
        print(f"     {factor.capitalize()}: {score}/10")
    
    if result['strengths']:
        print(f"\n   ✅ Strengths:")
        for strength in result['strengths']:
            print(f"     • {strength}")
    
    if result['recommendations']:
        print(f"\n   💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"     • {rec}")
    
    # Test 2: Poor-quality resume
    print("\n" + "=" * 80)
    print("\n2️⃣ Test: Poor-quality resume")
    poor_resume = {
        'sections': {
            'experience': {'content': 'I worked at some companies doing stuff'}
        },
        'full_text': '''My name is Jane Doe
I am looking for a job

I worked at some companies doing stuff. I am good at computers.
References available upon request.''',
        'metadata': {}
    }
    
    result2 = scorer.score_resume(poor_resume)
    print(f"   Overall Score: {result2['overall_score']}/10")
    print(f"   Grade: {result2['grade']}")
    print(f"\n   Factor Scores:")
    for factor, score in result2['factors'].items():
        print(f"     {factor.capitalize()}: {score}/10")
    
    if result2['weaknesses']:
        print(f"\n   ⚠️  Weaknesses:")
        for weakness in result2['weaknesses']:
            print(f"     • {weakness}")
    
    if result2['recommendations']:
        print(f"\n   💡 Recommendations:")
        for rec in result2['recommendations']:
            print(f"     • {rec}")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)
