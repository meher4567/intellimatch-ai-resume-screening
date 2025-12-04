"""
Enhanced Skill Extraction with Proficiency Detection and Context Awareness

Per ref.md recommendations - adds proficiency levels, years of experience tracking,
and contextual information about where skills were used.
"""

from typing import List, Dict, Tuple, Optional
import re
from datetime import datetime
import json

class EnhancedSkillExtractor:
    """
    Advanced skill extraction with proficiency detection and context awareness.
    Quick Win implementation from ref.md Phase 1A/1B enhancements.
    """
    
    def __init__(self, validated_skills_path: str = "data/skills/validated_skills.json"):
        self.validated_skills = self._load_validated_skills(validated_skills_path)
        
    def extract_skills_with_metadata(self, resume_data: Dict) -> Dict:
        """
        Enhanced extraction with proficiency and context.
        
        Returns:
            Dict with:
                - skills_with_proficiency: List of dicts {skill, proficiency, years, confidence}
                - skill_sources: Dict mapping skills to where they were found
                - skill_years: Dict mapping skills to total years of experience
                - skill_timeline: Dict mapping skills to when first used
        """
        results = {
            'skills_with_proficiency': [],
            'skill_sources': {},  # Where each skill was found
            'skill_years': {},    # Years of experience per skill
            'skill_timeline': {}   # When skill was first used
        }
        
        # Process experience section for contextual skills
        if resume_data.get('experience'):
            for exp in resume_data['experience']:
                duration = exp.get('duration_months', 0) / 12
                start_date = exp.get('start_date', '')
                
                # Extract skills from experience description
                skills_in_exp = self._extract_from_text(
                    exp.get('description', '') + ' ' + ' '.join(exp.get('technologies', []))
                )
                
                for skill in skills_in_exp:
                    # Track source
                    if skill not in results['skill_sources']:
                        results['skill_sources'][skill] = []
                    results['skill_sources'][skill].append({
                        'company': exp.get('company'),
                        'role': exp.get('title'),
                        'years': round(duration, 1)
                    })
                    
                    # Accumulate years
                    if skill not in results['skill_years']:
                        results['skill_years'][skill] = 0
                    results['skill_years'][skill] += duration
                    
                    # Track timeline (first occurrence)
                    if skill not in results['skill_timeline'] and start_date:
                        results['skill_timeline'][skill] = start_date
        
        # Extract from skills section if available
        if resume_data.get('skills'):
            skills_section = resume_data['skills']
            if isinstance(skills_section, dict):
                all_skills = skills_section.get('all_skills', [])
            elif isinstance(skills_section, list):
                all_skills = skills_section
            else:
                all_skills = []
            
            for skill in all_skills:
                if self._validate_skill(skill):
                    if skill not in results['skill_years']:
                        results['skill_years'][skill] = 0  # Listed but no context
        
        # Determine proficiency based on accumulated experience
        for skill, years in results['skill_years'].items():
            if years >= 5:
                proficiency = 'expert'
                confidence = min(0.9, 0.7 + years * 0.05)
            elif years >= 3:
                proficiency = 'proficient'
                confidence = min(0.85, 0.65 + years * 0.05)
            elif years >= 1:
                proficiency = 'intermediate'
                confidence = 0.7
            else:
                proficiency = 'beginner'
                confidence = 0.5
            
            results['skills_with_proficiency'].append({
                'skill': skill,
                'proficiency': proficiency,
                'years': round(years, 1),
                'confidence': round(confidence, 2)
            })
        
        # Sort by years (most experienced first)
        results['skills_with_proficiency'].sort(key=lambda x: x['years'], reverse=True)
        
        return results
    
    def _extract_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using patterns and validation.
        """
        extracted = []
        text_lower = text.lower()
        
        # Check each validated skill
        for skill in self.validated_skills:
            skill_lower = skill.lower()
            
            # Look for skill mentions (word boundaries to avoid partial matches)
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                extracted.append(skill)
        
        return extracted
    
    def _validate_skill(self, skill: str) -> bool:
        """
        Validate skill against known skills database.
        """
        skill_lower = skill.lower().strip()
        
        # Check exact match
        if skill in self.validated_skills:
            return True
        
        # Check case-insensitive match
        for valid_skill in self.validated_skills:
            if skill_lower == valid_skill.lower():
                return True
        
        return False
    
    def _load_validated_skills(self, path: str) -> List[str]:
        """
        Load validated skills from JSON file.
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get('skills', [])
        except Exception as e:
            print(f"Warning: Could not load validated skills: {e}")
            return []
    
    def detect_skill_proficiency(self, text: str, skill: str) -> Tuple[str, float]:
        """
        Quick proficiency detection from context patterns.
        
        Returns:
            Tuple of (proficiency_level, confidence)
        """
        proficiency_patterns = {
            'expert': ['expert', 'advanced', 'mastery', '5+ years', '10+ years', 
                      'authority', 'specialist', 'deep expertise'],
            'proficient': ['proficient', 'experienced', '3+ years', 'skilled',
                          'strong', 'solid', 'extensive'],
            'intermediate': ['intermediate', 'familiar', '1-2 years', 'working knowledge',
                           'moderate', 'competent'],
            'beginner': ['beginner', 'basic', 'learning', 'exposure', 'introductory',
                        'fundamental']
        }
        
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Check context around skill mention
        for level, patterns in proficiency_patterns.items():
            for pattern in patterns:
                if pattern in text_lower and skill_lower in text_lower:
                    # Check proximity (within 50 characters)
                    try:
                        pattern_idx = text_lower.find(pattern)
                        skill_idx = text_lower.find(skill_lower)
                        if abs(pattern_idx - skill_idx) < 50:
                            return level, 0.8
                    except:
                        pass
        
        # Check for years of experience patterns
        year_pattern = rf'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:with|in|using)?\s+{re.escape(skill_lower)}'
        match = re.search(year_pattern, text_lower)
        if match:
            years = int(match.group(1))
            if years >= 5:
                return 'expert', 0.85
            elif years >= 3:
                return 'proficient', 0.8
            elif years >= 1:
                return 'intermediate', 0.75
            else:
                return 'beginner', 0.7
        
        # Default
        return 'intermediate', 0.5
    
    def analyze_skill_portfolio(self, skills_with_proficiency: List[Dict]) -> Dict:
        """
        Analyze skill depth vs breadth (specialist vs generalist).
        """
        analysis = {}
        
        # Count skills by proficiency
        prof_counts = {'expert': 0, 'proficient': 0, 'intermediate': 0, 'beginner': 0}
        for skill_data in skills_with_proficiency:
            prof = skill_data.get('proficiency', 'intermediate')
            prof_counts[prof] += 1
        
        total_skills = sum(prof_counts.values())
        
        # Determine profile type
        if prof_counts['expert'] >= 3 and total_skills <= 15:
            analysis['profile_type'] = 'specialist'
            analysis['description'] = 'Deep expertise in specific areas'
        elif total_skills >= 20 and prof_counts['expert'] <= 2:
            analysis['profile_type'] = 'generalist'
            analysis['description'] = 'Broad skill set across multiple areas'
        else:
            analysis['profile_type'] = 'balanced'
            analysis['description'] = 'Mix of depth and breadth'
        
        analysis['proficiency_distribution'] = prof_counts
        analysis['total_skills'] = total_skills
        
        return analysis
