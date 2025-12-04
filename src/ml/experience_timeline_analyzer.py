"""
Experience Timeline Analyzer
Analyzes career progression, detects gaps, identifies patterns, and assesses job stability
Based on advanced implementations from ref.md
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dateutil import parser as date_parser
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ExperienceTimelineAnalyzer:
    """
    Analyze employment timeline for career insights
    """
    
    def __init__(self):
        """Initialize timeline analyzer"""
        # Date patterns for parsing
        self.date_patterns = [
            r'(\w+\s+\d{4})\s*-\s*(\w+\s+\d{4}|present|current)',  # "Jan 2020 - Dec 2022"
            r'(\d{2}/\d{4})\s*-\s*(\d{2}/\d{4}|present)',  # "01/2020 - 12/2022"
            r'(\d{4})\s*-\s*(\d{4}|present)',  # "2020 - 2022"
        ]
        self.compiled_date_patterns = [re.compile(p, re.IGNORECASE) for p in self.date_patterns]
        
        # Job progression indicators
        self.progression_keywords = {
            'promotion': ['promoted', 'advanced to', 'elevated to', 'moved up to'],
            'lateral': ['transferred to', 'moved to', 'transitioned to'],
            'upward_titles': ['senior', 'lead', 'principal', 'manager', 'director', 'vp', 'chief', 'head of'],
            'entry_titles': ['junior', 'associate', 'intern', 'trainee', 'assistant'],
        }
        
    def analyze_timeline(self, experience_data: List[Dict]) -> Dict:
        """
        Comprehensive timeline analysis
        
        Args:
            experience_data: List of job entries with dates, titles, descriptions
            Each entry should have: {title, company, start_date, end_date, description}
        
        Returns:
            Dict with timeline analysis:
                - total_experience_years
                - gaps (list of gaps with duration and dates)
                - progression (career trajectory)
                - job_hopping_score
                - tenure_stats (avg, median, shortest, longest)
                - timeline_events (chronological list)
        """
        if not experience_data:
            return self._empty_analysis()
        
        # Parse and sort jobs chronologically
        jobs = self._parse_job_dates(experience_data)
        if not jobs:
            return self._empty_analysis()
        
        jobs.sort(key=lambda x: x['start_date'])
        
        # Analyze components
        total_years = self._calculate_total_years(jobs)
        gaps = self._detect_gaps(jobs)
        progression = self._analyze_progression(jobs)
        job_hopping = self._calculate_job_hopping_score(jobs)
        tenure_stats = self._calculate_tenure_stats(jobs)
        timeline_events = self._generate_timeline_events(jobs, gaps)
        
        return {
            'total_experience_years': round(total_years, 1),
            'gaps': gaps,
            'gap_count': len(gaps),
            'total_gap_months': sum(g['months'] for g in gaps),
            'progression': progression,
            'job_hopping_score': job_hopping,
            'tenure_stats': tenure_stats,
            'timeline_events': timeline_events,
            'job_count': len(jobs),
            'analysis_confidence': self._calculate_confidence(jobs)
        }
    
    def _parse_job_dates(self, experience_data: List[Dict]) -> List[Dict]:
        """
        Parse job dates from experience entries
        
        Returns:
            List of jobs with parsed datetime objects
        """
        jobs = []
        
        for i, job in enumerate(experience_data):
            try:
                # Try to get dates from structured data
                start_date = self._parse_date(job.get('start_date', ''))
                end_date = self._parse_date(job.get('end_date', ''))
                
                # If not found, try to extract from description
                if not start_date or not end_date:
                    dates_from_desc = self._extract_dates_from_text(
                        job.get('description', '') + ' ' + job.get('title', '')
                    )
                    if dates_from_desc:
                        start_date, end_date = dates_from_desc
                
                if start_date:
                    # If end_date is None, assume current job
                    if not end_date:
                        end_date = datetime.now()
                    
                    jobs.append({
                        'index': i,
                        'title': job.get('title', 'Unknown'),
                        'company': job.get('company', 'Unknown'),
                        'start_date': start_date,
                        'end_date': end_date,
                        'description': job.get('description', ''),
                        'is_current': end_date >= datetime.now() - timedelta(days=30)  # Within last month
                    })
            except Exception as e:
                logger.warning(f"Error parsing job {i}: {e}")
                continue
        
        return jobs
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string into datetime object
        
        Args:
            date_str: Date string (e.g., "Jan 2020", "2020", "present")
        
        Returns:
            datetime object or None
        """
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip().lower()
        
        # Handle "present" or "current"
        if date_str in ['present', 'current', 'now']:
            return datetime.now()
        
        try:
            # Try dateutil parser (handles many formats)
            return date_parser.parse(date_str, fuzzy=True)
        except:
            # Try just year
            year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
            if year_match:
                return datetime(int(year_match.group(0)), 1, 1)
        
        return None
    
    def _extract_dates_from_text(self, text: str) -> Optional[Tuple[datetime, datetime]]:
        """
        Extract date range from text using patterns
        
        Returns:
            Tuple of (start_date, end_date) or None
        """
        for pattern in self.compiled_date_patterns:
            match = pattern.search(text)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)
                
                start_date = self._parse_date(start_str)
                end_date = self._parse_date(end_str)
                
                if start_date and end_date:
                    return (start_date, end_date)
        
        return None
    
    def _calculate_total_years(self, jobs: List[Dict]) -> float:
        """Calculate total years of experience (excluding gaps)"""
        total_days = sum(
            (job['end_date'] - job['start_date']).days
            for job in jobs
        )
        return total_days / 365.25
    
    def _detect_gaps(self, jobs: List[Dict], min_gap_months: int = 3) -> List[Dict]:
        """
        Detect employment gaps
        
        Args:
            jobs: Sorted list of jobs
            min_gap_months: Minimum gap to report (default 3 months)
        
        Returns:
            List of gaps with dates and duration
        """
        gaps = []
        
        for i in range(len(jobs) - 1):
            current_end = jobs[i]['end_date']
            next_start = jobs[i + 1]['start_date']
            
            # Calculate gap
            gap_days = (next_start - current_end).days
            gap_months = gap_days / 30.44  # Average days per month
            
            if gap_months >= min_gap_months:
                gaps.append({
                    'start': current_end,
                    'end': next_start,
                    'months': round(gap_months, 1),
                    'after_company': jobs[i]['company'],
                    'before_company': jobs[i + 1]['company']
                })
        
        return gaps
    
    def _analyze_progression(self, jobs: List[Dict]) -> Dict:
        """
        Analyze career progression trajectory
        
        Returns:
            Dict with progression analysis
        """
        if len(jobs) < 2:
            return {
                'trajectory': 'insufficient_data',
                'direction': 'unknown',
                'progression_score': 0.5,
                'details': []
            }
        
        progression_events = []
        upward_count = 0
        lateral_count = 0
        downward_count = 0
        
        for i in range(len(jobs) - 1):
            current_job = jobs[i]
            next_job = jobs[i + 1]
            
            # Analyze title progression
            direction = self._compare_titles(current_job['title'], next_job['title'])
            
            progression_events.append({
                'from': f"{current_job['title']} at {current_job['company']}",
                'to': f"{next_job['title']} at {next_job['company']}",
                'direction': direction,
                'year': next_job['start_date'].year
            })
            
            if direction == 'upward':
                upward_count += 1
            elif direction == 'lateral':
                lateral_count += 1
            elif direction == 'downward':
                downward_count += 1
        
        # Determine overall trajectory
        if upward_count > lateral_count + downward_count:
            trajectory = 'upward'
        elif lateral_count > upward_count and downward_count == 0:
            trajectory = 'lateral'
        elif downward_count > 0:
            trajectory = 'mixed'
        else:
            trajectory = 'stable'
        
        # Calculate progression score (0-1, higher is better)
        total_transitions = len(progression_events)
        if total_transitions > 0:
            progression_score = (upward_count * 1.0 + lateral_count * 0.5) / total_transitions
        else:
            progression_score = 0.5
        
        return {
            'trajectory': trajectory,
            'direction': f"{upward_count} upward, {lateral_count} lateral, {downward_count} downward",
            'progression_score': round(progression_score, 2),
            'details': progression_events
        }
    
    def _compare_titles(self, title1: str, title2: str) -> str:
        """
        Compare two job titles to determine progression direction
        
        Returns:
            'upward', 'lateral', 'downward', or 'unknown'
        """
        title1_lower = title1.lower()
        title2_lower = title2.lower()
        
        # Check for explicit promotion keywords
        for keyword in self.progression_keywords['promotion']:
            if keyword in title2_lower:
                return 'upward'
        
        # Check seniority indicators
        seniority_levels = ['intern', 'junior', 'associate', 'mid', 'senior', 'lead', 'principal', 'staff', 'manager', 'director', 'vp', 'cto', 'ceo']
        
        title1_level = -1
        title2_level = -1
        
        for i, level in enumerate(seniority_levels):
            if level in title1_lower:
                title1_level = max(title1_level, i)
            if level in title2_lower:
                title2_level = max(title2_level, i)
        
        if title2_level > title1_level and title2_level != -1:
            return 'upward'
        elif title2_level < title1_level and title1_level != -1:
            return 'downward'
        elif title2_level == title1_level and title2_level != -1:
            return 'lateral'
        
        # If no clear indicators, check for lateral movement keywords
        for keyword in self.progression_keywords['lateral']:
            if keyword in title2_lower:
                return 'lateral'
        
        return 'unknown'
    
    def _calculate_job_hopping_score(self, jobs: List[Dict]) -> float:
        """
        Calculate job hopping tendency score (0-1, higher = more hopping)
        
        Industry standard: 2 years average tenure is typical
        < 1 year = high turnover
        > 3 years = stable
        """
        if len(jobs) < 2:
            return 0.0  # Not enough data
        
        tenures = [
            (job['end_date'] - job['start_date']).days / 365.25
            for job in jobs
        ]
        
        avg_tenure = sum(tenures) / len(tenures)
        
        # Score calculation (inverse of tenure)
        # < 1 year avg = 1.0 (high hopping)
        # 2 years avg = 0.5 (moderate)
        # > 4 years avg = 0.0 (stable)
        if avg_tenure < 1:
            score = 1.0
        elif avg_tenure > 4:
            score = 0.0
        else:
            score = 1.0 - (avg_tenure - 1.0) / 3.0
        
        return round(score, 2)
    
    def _calculate_tenure_stats(self, jobs: List[Dict]) -> Dict:
        """Calculate tenure statistics"""
        tenures_years = [
            (job['end_date'] - job['start_date']).days / 365.25
            for job in jobs
        ]
        
        if not tenures_years:
            return {}
        
        tenures_sorted = sorted(tenures_years)
        
        return {
            'average_tenure_years': round(sum(tenures_years) / len(tenures_years), 1),
            'median_tenure_years': round(tenures_sorted[len(tenures_sorted) // 2], 1),
            'shortest_tenure_years': round(min(tenures_years), 1),
            'longest_tenure_years': round(max(tenures_years), 1)
        }
    
    def _generate_timeline_events(self, jobs: List[Dict], gaps: List[Dict]) -> List[Dict]:
        """
        Generate chronological timeline of events
        
        Returns:
            List of events (jobs and gaps) in chronological order
        """
        events = []
        
        # Add job events
        for job in jobs:
            events.append({
                'type': 'job',
                'date': job['start_date'],
                'title': job['title'],
                'company': job['company'],
                'duration_years': round((job['end_date'] - job['start_date']).days / 365.25, 1),
                'is_current': job['is_current']
            })
        
        # Add gap events
        for gap in gaps:
            events.append({
                'type': 'gap',
                'date': gap['start'],
                'duration_months': gap['months'],
                'after': gap['after_company'],
                'before': gap['before_company']
            })
        
        # Sort by date
        events.sort(key=lambda x: x['date'], reverse=True)  # Most recent first
        
        return events
    
    def _calculate_confidence(self, jobs: List[Dict]) -> float:
        """
        Calculate confidence in the analysis based on data quality
        
        Returns:
            Confidence score (0-1)
        """
        if not jobs:
            return 0.0
        
        # Factors:
        # 1. Number of jobs parsed (more = better)
        # 2. Date completeness
        # 3. Title/company info completeness
        
        job_count_score = min(len(jobs) / 5.0, 1.0)  # 5+ jobs = full score
        
        complete_jobs = sum(
            1 for job in jobs
            if job['start_date'] and job['end_date'] and job['title'] != 'Unknown'
        )
        completeness_score = complete_jobs / len(jobs)
        
        confidence = (job_count_score * 0.4 + completeness_score * 0.6)
        
        return round(confidence, 2)
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'total_experience_years': 0,
            'gaps': [],
            'gap_count': 0,
            'total_gap_months': 0,
            'progression': {
                'trajectory': 'insufficient_data',
                'direction': 'unknown',
                'progression_score': 0,
                'details': []
            },
            'job_hopping_score': 0,
            'tenure_stats': {},
            'timeline_events': [],
            'job_count': 0,
            'analysis_confidence': 0
        }


# Convenience function
def analyze_experience_timeline(experience_data: List[Dict]) -> Dict:
    """
    Convenience function to analyze timeline
    
    Args:
        experience_data: List of job entries
    
    Returns:
        Timeline analysis
    """
    analyzer = ExperienceTimelineAnalyzer()
    return analyzer.analyze_timeline(experience_data)
