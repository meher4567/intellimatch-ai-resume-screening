"""
Context-Aware Skill Extractor
Maps skills to specific experiences, projects, and time periods
Provides richer skill context than simple skill lists
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContextAwareSkillExtractor:
    """
    Extract skills with context: where used, when used, how used
    """
    
    def __init__(self):
        """Initialize context-aware extractor"""
        # Context indicators
        self.usage_indicators = {
            'primary': [
                r'using\s+{skill}',
                r'with\s+{skill}',
                r'{skill}\s+(?:developer|engineer|architect)',
                r'expertise in\s+{skill}',
                r'specialized in\s+{skill}'
            ],
            'secondary': [
                r'including\s+{skill}',
                r'also\s+{skill}',
                r'familiar\s+with\s+{skill}',
                r'knowledge\s+of\s+{skill}'
            ],
            'learning': [
                r'learning\s+{skill}',
                r'training\s+in\s+{skill}',
                r'coursework\s+in\s+{skill}',
                r'studying\s+{skill}'
            ]
        }
        
        # Achievement indicators
        self.achievement_indicators = [
            r'developed',
            r'built',
            r'created',
            r'implemented',
            r'designed',
            r'architected',
            r'led',
            r'managed',
            r'optimized',
            r'improved'
        ]
    
    def extract_skills_with_context(self, resume_data: Dict, skills_list: List[str]) -> Dict:
        """
        Extract skills with rich context
        
        Args:
            resume_data: Parsed resume with sections
            skills_list: List of skills to analyze
        
        Returns:
            Dict with contextual skill information
        """
        skills_context = []
        
        for skill in skills_list:
            context = self._get_skill_context(resume_data, skill)
            if context:
                skills_context.append(context)
        
        # Generate insights
        insights = self._generate_insights(skills_context)
        
        return {
            'skills_with_context': skills_context,
            'insights': insights,
            'skill_count': len(skills_context)
        }
    
    def _get_skill_context(self, resume_data: Dict, skill: str) -> Optional[Dict]:
        """
        Get context for a specific skill
        
        Returns:
            Dict with skill context or None
        """
        context = {
            'skill': skill,
            'usage_level': 'unknown',
            'experiences': [],
            'projects': [],
            'achievements': [],
            'time_periods': [],
            'context_score': 0.0
        }
        
        text = resume_data.get('text', '')
        
        if not text:
            return None
        
        # Find where skill is mentioned
        skill_pattern = re.compile(rf'\b{re.escape(skill)}\b', re.IGNORECASE)
        matches = list(skill_pattern.finditer(text))
        
        if not matches:
            return None
        
        # Analyze each mention
        for match in matches:
            start = max(0, match.start() - 200)
            end = min(len(text), match.end() + 200)
            context_text = text[start:end]
            
            # Determine usage level
            usage_level = self._detect_usage_level(context_text, skill)
            if usage_level and usage_level != 'unknown':
                context['usage_level'] = usage_level
            
            # Extract achievements
            achievements = self._extract_achievements(context_text, skill)
            context['achievements'].extend(achievements)
        
        # Map to experiences
        if resume_data.get('experience'):
            for exp in resume_data['experience']:
                exp_text = str(exp.get('description', '')) + ' ' + str(exp.get('title', ''))
                
                if skill_pattern.search(exp_text):
                    context['experiences'].append({
                        'title': exp.get('title', 'Unknown'),
                        'company': exp.get('company', 'Unknown'),
                        'start_date': exp.get('start_date'),
                        'end_date': exp.get('end_date')
                    })
                    
                    # Extract time period
                    if exp.get('start_date'):
                        context['time_periods'].append(exp.get('start_date'))
        
        # Map to projects
        if resume_data.get('projects'):
            for proj in resume_data['projects']:
                proj_text = str(proj.get('description', '')) + ' ' + str(proj.get('name', ''))
                
                if skill_pattern.search(proj_text):
                    context['projects'].append({
                        'name': proj.get('name', 'Unknown Project'),
                        'description': proj.get('description', '')[:100]
                    })
        
        # Calculate context score
        context['context_score'] = self._calculate_context_score(context)
        
        # Only return if we found meaningful context
        if context['context_score'] > 0:
            return context
        
        return None
    
    def _detect_usage_level(self, text: str, skill: str) -> str:
        """
        Detect how skill was used (primary, secondary, learning)
        
        Returns:
            Usage level: 'primary', 'secondary', 'learning', or 'unknown'
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Check each usage level
        for level, patterns in self.usage_indicators.items():
            for pattern_template in patterns:
                pattern = pattern_template.replace('{skill}', re.escape(skill_lower))
                if re.search(pattern, text_lower):
                    return level
        
        return 'unknown'
    
    def _extract_achievements(self, text: str, skill: str) -> List[str]:
        """
        Extract achievements mentioning the skill
        
        Returns:
            List of achievement descriptions
        """
        achievements = []
        
        # Look for sentences with achievement verbs and the skill
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            skill_lower = skill.lower()
            
            if skill_lower in sentence_lower:
                # Check for achievement indicators
                for indicator in self.achievement_indicators:
                    if re.search(rf'\b{indicator}\b', sentence_lower):
                        # Clean up the sentence
                        cleaned = sentence.strip()
                        if len(cleaned) > 20 and len(cleaned) < 200:
                            achievements.append(cleaned)
                        break
        
        return achievements[:3]  # Top 3
    
    def _calculate_context_score(self, context: Dict) -> float:
        """
        Calculate richness of context (0-1)
        
        Returns:
            Context score
        """
        score = 0.0
        
        # Usage level known
        if context['usage_level'] != 'unknown':
            score += 0.2
            if context['usage_level'] == 'primary':
                score += 0.1
        
        # Has experiences
        if context['experiences']:
            score += min(len(context['experiences']) * 0.15, 0.3)
        
        # Has projects
        if context['projects']:
            score += min(len(context['projects']) * 0.1, 0.2)
        
        # Has achievements
        if context['achievements']:
            score += min(len(context['achievements']) * 0.1, 0.2)
        
        return min(score, 1.0)
    
    def _generate_insights(self, skills_context: List[Dict]) -> Dict:
        """
        Generate insights from contextual skill data
        
        Returns:
            Dict with insights
        """
        insights = {
            'primary_skills': [],
            'secondary_skills': [],
            'skills_with_achievements': [],
            'recent_skills': [],
            'long_term_skills': [],
            'avg_context_score': 0.0
        }
        
        if not skills_context:
            return insights
        
        # Categorize by usage level
        for skill_ctx in skills_context:
            skill = skill_ctx['skill']
            
            if skill_ctx['usage_level'] == 'primary':
                insights['primary_skills'].append(skill)
            elif skill_ctx['usage_level'] == 'secondary':
                insights['secondary_skills'].append(skill)
            
            if skill_ctx['achievements']:
                insights['skills_with_achievements'].append({
                    'skill': skill,
                    'achievements': len(skill_ctx['achievements'])
                })
            
            # Time-based categorization
            if skill_ctx['time_periods']:
                # Simple heuristic: check if any mention is recent
                # In production, you'd parse dates properly
                insights['recent_skills'].append(skill)
            
            if len(skill_ctx['experiences']) >= 2:
                insights['long_term_skills'].append(skill)
        
        # Calculate average context score
        context_scores = [s['context_score'] for s in skills_context]
        insights['avg_context_score'] = round(sum(context_scores) / len(context_scores), 2)
        
        return insights
    
    def generate_skill_narrative(self, skill_context: Dict) -> str:
        """
        Generate natural language narrative for a skill
        
        Args:
            skill_context: Context dict for a skill
        
        Returns:
            Narrative string
        """
        skill = skill_context['skill']
        parts = []
        
        # Usage level
        if skill_context['usage_level'] == 'primary':
            parts.append(f"{skill} is a core skill")
        elif skill_context['usage_level'] == 'secondary':
            parts.append(f"{skill} is used as a supporting skill")
        else:
            parts.append(f"{skill} appears in the profile")
        
        # Experience count
        exp_count = len(skill_context['experiences'])
        if exp_count > 0:
            parts.append(f"used across {exp_count} position{'s' if exp_count > 1 else ''}")
        
        # Achievements
        ach_count = len(skill_context['achievements'])
        if ach_count > 0:
            parts.append(f"with {ach_count} notable achievement{'s' if ach_count > 1 else ''}")
        
        # Projects
        proj_count = len(skill_context['projects'])
        if proj_count > 0:
            parts.append(f"applied in {proj_count} project{'s' if proj_count > 1 else ''}")
        
        return ', '.join(parts) + '.'


def extract_contextual_skills(resume_data: Dict, skills_list: List[str]) -> Dict:
    """
    Convenience function for context-aware skill extraction
    
    Args:
        resume_data: Parsed resume
        skills_list: Skills to analyze
    
    Returns:
        Dict with contextual information
    """
    extractor = ContextAwareSkillExtractor()
    return extractor.extract_skills_with_context(resume_data, skills_list)


if __name__ == "__main__":
    print("=" * 80)
    print("🧪 Testing Context-Aware Skill Extractor")
    print("=" * 80)
    
    # Sample resume data
    sample_resume = {
        'text': """
        Senior Software Engineer
        
        EXPERIENCE:
        Tech Corp - Senior Engineer (2020-2024)
        Developed microservices architecture using Python and Django.
        Built REST APIs with Flask and integrated with PostgreSQL databases.
        Led a team using Agile methodologies and implemented CI/CD with Docker.
        
        StartUp Inc - Software Engineer (2018-2020)
        Created web applications with React and Node.js.
        Also familiar with AWS deployment and basic DevOps practices.
        """,
        'experience': [
            {
                'title': 'Senior Engineer',
                'company': 'Tech Corp',
                'start_date': '2020',
                'end_date': '2024',
                'description': 'Developed microservices using Python and Django. Led team.'
            },
            {
                'title': 'Software Engineer',
                'company': 'StartUp Inc',
                'start_date': '2018',
                'end_date': '2020',
                'description': 'Created web apps with React and Node.js'
            }
        ]
    }
    
    skills_list = ['Python', 'Django', 'React', 'AWS', 'Docker']
    
    extractor = ContextAwareSkillExtractor()
    result = extractor.extract_skills_with_context(sample_resume, skills_list)
    
    print(f"\n✅ Analyzed {result['skill_count']} skills with context")
    print(f"   Average context score: {result['insights']['avg_context_score']:.2f}")
    
    print(f"\n📊 Skill Categorization:")
    print(f"   Primary skills: {', '.join(result['insights']['primary_skills']) or 'None'}")
    print(f"   Secondary skills: {', '.join(result['insights']['secondary_skills']) or 'None'}")
    print(f"   Skills with achievements: {len(result['insights']['skills_with_achievements'])}")
    
    print(f"\n🎯 Detailed Skill Context:")
    for skill_ctx in result['skills_with_context'][:3]:  # Show first 3
        print(f"\n   {skill_ctx['skill']}:")
        print(f"      Usage Level: {skill_ctx['usage_level']}")
        print(f"      Experiences: {len(skill_ctx['experiences'])}")
        print(f"      Achievements: {len(skill_ctx['achievements'])}")
        print(f"      Context Score: {skill_ctx['context_score']:.2f}")
        
        if skill_ctx['achievements']:
            print(f"      Sample achievement: {skill_ctx['achievements'][0][:80]}...")
        
        # Generate narrative
        narrative = extractor.generate_skill_narrative(skill_ctx)
        print(f"      Narrative: {narrative}")
    
    print("\n" + "=" * 80)
    print("✅ Context-aware skill extraction working!")
    print("=" * 80)
