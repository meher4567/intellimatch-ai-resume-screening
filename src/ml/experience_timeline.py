"""
Advanced Experience Timeline Builder with Gap Detection and Career Progression Analysis

Per ref.md recommendations - provides comprehensive career analysis including gaps,
progression patterns, job-hopping indicators, and industry transitions.
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import dateparser
from dateutil.relativedelta import relativedelta
import re
import logging

logger = logging.getLogger(__name__)


class ExperienceTimelineBuilder:
    """
    Build comprehensive career timeline with gap detection and progression analysis.
    Quick Win implementation from ref.md Phase 1A enhancements.
    """
    
    def __init__(self):
        self.current_date = datetime.now()
        
        # Seniority level indicators
        self.seniority_keywords = {
            'junior': 1, 'associate': 2, 'mid': 3, 'intermediate': 3,
            'senior': 4, 'lead': 5, 'principal': 6, 'staff': 6,
            'manager': 5, 'director': 6, 'vp': 7, 'vice president': 7,
            'executive': 8, 'chief': 9, 'ceo': 10, 'cto': 10, 'cfo': 10
        }
        
        # Industry indicators
        self.industry_keywords = {
            'tech': ['software', 'technology', 'tech', 'digital', 'IT', 'computing', 'startup'],
            'finance': ['bank', 'financial', 'investment', 'trading', 'insurance', 'fintech'],
            'healthcare': ['health', 'medical', 'hospital', 'clinical', 'pharma', 'biotech'],
            'retail': ['retail', 'store', 'shop', 'ecommerce', 'commerce', 'sales'],
            'consulting': ['consulting', 'advisory', 'consultant', 'professional services'],
            'education': ['university', 'college', 'school', 'education', 'academic', 'teaching'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial', 'automotive'],
            'government': ['government', 'federal', 'state', 'public sector', 'agency'],
            'nonprofit': ['nonprofit', 'non-profit', 'ngo', 'charity', 'foundation']
        }
    
    def build_timeline(self, resume_data: Dict) -> Dict:
        """
        Build complete career timeline with comprehensive analysis.
        
        Returns:
            Dict with:
                - timeline: List of experiences sorted by date
                - total_experience_years: Total years of experience
                - career_gaps: List of gaps > 3 months
                - career_progression: Analysis of role progression
                - current_role: Most recent role (if still active)
                - industry_changes: Detected industry switches
                - job_hopping_score: 0-1, higher means more job hopping
                - avg_tenure_months: Average time spent per role
        """
        timeline_data = {
            'timeline': [],
            'total_experience_years': 0,
            'career_gaps': [],
            'career_progression': {},
            'current_role': None,
            'industry_changes': [],
            'job_hopping_score': 0,
            'avg_tenure_months': 0
        }
        
        if not resume_data.get('experience'):
            return timeline_data
        
        # Parse and normalize dates
        experiences = self._normalize_dates(resume_data['experience'].copy())
        
        # Sort by start date (most recent first for display)
        experiences.sort(key=lambda x: x.get('start_date_parsed') or datetime.min, reverse=True)
        
        # Build timeline
        timeline_data['timeline'] = experiences
        
        # Calculate total experience
        timeline_data['total_experience_years'] = self._calculate_total_experience(experiences)
        
        # Detect gaps
        timeline_data['career_gaps'] = self._detect_career_gaps(experiences)
        
        # Analyze progression
        timeline_data['career_progression'] = self._analyze_progression(experiences)
        
        # Find current role
        timeline_data['current_role'] = self._find_current_role(experiences)
        
        # Detect industry changes
        timeline_data['industry_changes'] = self._detect_industry_changes(experiences)
        
        # Calculate job hopping score
        tenures = [exp.get('duration_months', 0) for exp in experiences if exp.get('duration_months')]
        if tenures:
            avg_tenure = sum(tenures) / len(tenures)
            timeline_data['avg_tenure_months'] = round(avg_tenure, 1)
            
            # Job hopping: frequent if avg tenure < 18 months
            if avg_tenure < 12:
                timeline_data['job_hopping_score'] = 0.9
            elif avg_tenure < 18:
                timeline_data['job_hopping_score'] = 0.7
            elif avg_tenure < 24:
                timeline_data['job_hopping_score'] = 0.5
            else:
                timeline_data['job_hopping_score'] = 0.2
        
        return timeline_data
    
    def _normalize_dates(self, experiences: List[Dict]) -> List[Dict]:
        """
        Parse and normalize all dates in experiences.
        """
        for exp in experiences:
            # Parse start date
            start_date_str = exp.get('start_date', '')
            exp['start_date_parsed'] = self._parse_date(start_date_str)
            
            # Parse end date
            end_date_str = exp.get('end_date', '')
            if end_date_str and 'present' not in end_date_str.lower() and 'current' not in end_date_str.lower():
                exp['end_date_parsed'] = self._parse_date(end_date_str)
                exp['is_current'] = False
            else:
                exp['end_date_parsed'] = self.current_date
                exp['is_current'] = True
            
            # Calculate duration in months
            if exp.get('start_date_parsed') and exp.get('end_date_parsed'):
                delta = relativedelta(exp['end_date_parsed'], exp['start_date_parsed'])
                exp['duration_months'] = max(1, delta.years * 12 + delta.months)
            else:
                exp['duration_months'] = 0
        
        return experiences
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse various date formats.
        """
        if not date_str:
            return None
        
        # Try dateparser first (handles many formats)
        try:
            parsed = dateparser.parse(date_str)
            if parsed:
                return parsed
        except:
            pass
        
        # Handle special cases
        patterns = [
            (r'(\d{4})', lambda m: datetime(int(m.group(1)), 1, 1)),  # Just year
            (r'(\d{1,2})/(\d{4})', lambda m: datetime(int(m.group(2)), int(m.group(1)), 1)),  # MM/YYYY
            (r'(\w+)\s+(\d{4})', lambda m: self._parse_month_year(m.group(1), m.group(2))),  # Month YYYY
        ]
        
        for pattern, parser in patterns:
            match = re.search(pattern, str(date_str))
            if match:
                try:
                    return parser(match)
                except:
                    continue
        
        return None
    
    def _parse_month_year(self, month_str: str, year_str: str) -> Optional[datetime]:
        """Parse month name and year."""
        try:
            month_parsed = dateparser.parse(month_str)
            if month_parsed:
                return datetime(int(year_str), month_parsed.month, 1)
        except:
            pass
        return None
    
    def _calculate_total_experience(self, experiences: List[Dict]) -> float:
        """
        Calculate total years considering overlaps.
        """
        if not experiences:
            return 0
        
        # Create timeline segments
        segments = []
        for exp in experiences:
            if exp.get('start_date_parsed') and exp.get('end_date_parsed'):
                segments.append((exp['start_date_parsed'], exp['end_date_parsed']))
        
        if not segments:
            return 0
        
        # Merge overlapping segments
        segments.sort()
        merged = [segments[0]]
        
        for start, end in segments[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end:  # Overlap
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        
        # Calculate total duration
        total_months = 0
        for start, end in merged:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months
        
        return round(total_months / 12, 1)
    
    def _detect_career_gaps(self, experiences: List[Dict]) -> List[Dict]:
        """
        Detect gaps > 3 months between roles.
        """
        gaps = []
        
        # Sort by end date (oldest first for gap detection)
        sorted_exp = sorted(experiences, key=lambda x: x.get('end_date_parsed') or datetime.max)
        
        for i in range(len(sorted_exp) - 1):
            current_end = sorted_exp[i].get('end_date_parsed')
            next_start = sorted_exp[i + 1].get('start_date_parsed')
            
            if current_end and next_start and next_start > current_end:
                gap_delta = relativedelta(next_start, current_end)
                gap_months = gap_delta.years * 12 + gap_delta.months
                
                if gap_months > 3:
                    gaps.append({
                        'start': current_end.strftime('%Y-%m-%d'),
                        'end': next_start.strftime('%Y-%m-%d'),
                        'duration_months': gap_months,
                        'after_role': sorted_exp[i].get('title', 'Unknown'),
                        'after_company': sorted_exp[i].get('company', 'Unknown'),
                        'before_role': sorted_exp[i + 1].get('title', 'Unknown'),
                        'before_company': sorted_exp[i + 1].get('company', 'Unknown')
                    })
        
        return gaps
    
    def _analyze_progression(self, experiences: List[Dict]) -> Dict:
        """
        Analyze career progression patterns.
        """
        if len(experiences) < 2:
            return {
                'progression_type': 'early_career',
                'changes': [],
                'promotions': 0,
                'lateral_moves': 0
            }
        
        progression = {
            'progression_type': 'lateral',
            'changes': [],
            'promotions': 0,
            'lateral_moves': 0
        }
        
        # Sort by start date (oldest first for progression analysis)
        sorted_exp = sorted(experiences, key=lambda x: x.get('start_date_parsed') or datetime.min)
        
        # Analyze title progression
        for i in range(len(sorted_exp) - 1):
            current = sorted_exp[i]
            next_exp = sorted_exp[i + 1]
            
            current_level = self._extract_seniority_level(current.get('title', ''))
            next_level = self._extract_seniority_level(next_exp.get('title', ''))
            
            if next_level > current_level:
                change_type = 'promotion'
                progression['promotions'] += 1
            elif next_level < current_level:
                change_type = 'step_back'
            else:
                change_type = 'lateral'
                progression['lateral_moves'] += 1
            
            progression['changes'].append({
                'from': current.get('title', 'Unknown'),
                'from_company': current.get('company', 'Unknown'),
                'to': next_exp.get('title', 'Unknown'),
                'to_company': next_exp.get('company', 'Unknown'),
                'type': change_type,
                'duration_at_role': current.get('duration_months', 0)
            })
        
        # Determine overall progression type
        if progression['promotions'] >= len(progression['changes']) * 0.5:
            progression['progression_type'] = 'upward'
        elif progression['promotions'] >= len(progression['changes']) * 0.3:
            progression['progression_type'] = 'mixed'
        else:
            progression['progression_type'] = 'lateral'
        
        return progression
    
    def _extract_seniority_level(self, title: str) -> int:
        """
        Extract seniority level from job title (1-10 scale).
        """
        title_lower = title.lower()
        
        for keyword, level in self.seniority_keywords.items():
            if keyword in title_lower:
                return level
        
        # Default to mid-level
        return 3
    
    def _find_current_role(self, experiences: List[Dict]) -> Optional[Dict]:
        """
        Find the current active role.
        """
        for exp in experiences:
            if exp.get('is_current'):
                return {
                    'title': exp.get('title'),
                    'company': exp.get('company'),
                    'start_date': exp.get('start_date'),
                    'duration_months': exp.get('duration_months', 0)
                }
        return None
    
    def _detect_industry_changes(self, experiences: List[Dict]) -> List[Dict]:
        """
        Detect when candidate changed industries.
        """
        changes = []
        last_industry = None
        
        # Sort by start date (oldest first)
        sorted_exp = sorted(experiences, key=lambda x: x.get('start_date_parsed') or datetime.min)
        
        for exp in sorted_exp:
            company_desc = (exp.get('company', '') + ' ' + exp.get('description', '')).lower()
            
            current_industry = None
            for industry, keywords in self.industry_keywords.items():
                if any(kw.lower() in company_desc for kw in keywords):
                    current_industry = industry
                    break
            
            if last_industry and current_industry and last_industry != current_industry:
                changes.append({
                    'from_industry': last_industry,
                    'to_industry': current_industry,
                    'at_role': exp.get('title'),
                    'company': exp.get('company'),
                    'date': exp.get('start_date')
                })
            
            if current_industry:
                last_industry = current_industry
        
        return changes


# Quick integration helper
def analyze_career_timeline(resume_data: Dict) -> Dict:
    """
    Convenience function for quick timeline analysis.
    
    Usage:
        timeline = analyze_career_timeline(parsed_resume)
        print(f"Total experience: {timeline['total_experience_years']} years")
        print(f"Career gaps: {len(timeline['career_gaps'])}")
        print(f"Progression: {timeline['career_progression']['progression_type']}")
    """
    builder = ExperienceTimelineBuilder()
    return builder.build_timeline(resume_data)
