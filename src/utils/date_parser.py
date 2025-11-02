"""
Date Parser Utility - Parse and normalize dates from resumes
Handles various date formats commonly found in resumes
"""

import re
import logging
from datetime import datetime, date
from typing import Optional, Tuple
from dateutil import parser as date_parser
import dateparser

logger = logging.getLogger(__name__)


class DateParser:
    """
    Parse and normalize dates from various formats
    """
    
    # Common date patterns in resumes
    DATE_PATTERNS = [
        # Month Year formats
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,.\s]+\d{4}\b',
        r'\b\d{1,2}/\d{4}\b',  # 01/2024
        r'\b\d{4}\b',  # Just year
        # Range formats
        r'\b\d{4}\s*[-–—]\s*\d{4}\b',  # 2020-2024
        r'\b\d{4}\s*[-–—]\s*(Present|Current|Now|Ongoing)\b',  # 2020-Present
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*(Present|Current|Now)\b',
    ]
    
    # Keywords indicating current/ongoing
    CURRENT_KEYWORDS = ['present', 'current', 'now', 'ongoing', 'today']
    
    def __init__(self):
        """Initialize Date Parser"""
        pass
    
    def parse_date(self, date_string: str) -> Optional[date]:
        """
        Parse a date string into a date object
        
        Args:
            date_string: Date string to parse
            
        Returns:
            date object or None if parsing fails
        """
        if not date_string or not isinstance(date_string, str):
            return None
        
        date_string = date_string.strip()
        
        # Check for current/present keywords
        if date_string.lower() in self.CURRENT_KEYWORDS:
            return date.today()
        
        try:
            # Try dateparser first (handles many formats)
            parsed = dateparser.parse(
                date_string,
                settings={
                    'PREFER_DATES_FROM': 'past',
                    'RELATIVE_BASE': datetime.now()
                }
            )
            
            if parsed:
                return parsed.date()
            
            # Fallback to dateutil parser
            parsed = date_parser.parse(date_string, fuzzy=True)
            return parsed.date()
            
        except Exception as e:
            logger.debug(f"Could not parse date '{date_string}': {e}")
            
            # Try extracting just the year
            year_match = re.search(r'\b(19|20)\d{2}\b', date_string)
            if year_match:
                try:
                    year = int(year_match.group())
                    return date(year, 1, 1)  # Default to Jan 1st of that year
                except:
                    pass
            
            return None
    
    def parse_date_range(self, text: str) -> Tuple[Optional[date], Optional[date], bool]:
        """
        Parse a date range from text (e.g., "Jan 2020 - Dec 2023")
        
        Args:
            text: Text containing date range
            
        Returns:
            Tuple of (start_date, end_date, is_current)
            - start_date: Start date or None
            - end_date: End date or None
            - is_current: True if still ongoing (Present/Current)
        """
        if not text:
            return None, None, False
        
        # Check for current/ongoing position
        is_current = any(keyword in text.lower() for keyword in self.CURRENT_KEYWORDS)
        
        # Split on common separators
        separators = ['-', '–', '—', 'to', 'TO']
        parts = [text]
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep, 1)
                break
        
        if len(parts) == 2:
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            start_date = self.parse_date(start_str)
            
            if is_current:
                end_date = date.today()
            else:
                end_date = self.parse_date(end_str)
            
            return start_date, end_date, is_current
        
        elif len(parts) == 1:
            # Single date
            single_date = self.parse_date(parts[0])
            return single_date, single_date, False
        
        return None, None, False
    
    def extract_dates_from_text(self, text: str) -> list:
        """
        Extract all dates from text
        
        Args:
            text: Text to extract dates from
            
        Returns:
            List of date objects
        """
        dates = []
        
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                parsed_date = self.parse_date(date_str)
                if parsed_date:
                    dates.append(parsed_date)
        
        return dates
    
    def format_date(self, date_obj: date, format_str: str = "%Y-%m-%d") -> str:
        """
        Format a date object to string
        
        Args:
            date_obj: date object
            format_str: Format string (default: YYYY-MM-DD)
            
        Returns:
            Formatted date string
        """
        if not date_obj:
            return ""
        
        try:
            return date_obj.strftime(format_str)
        except:
            return str(date_obj)
    
    def calculate_duration_months(self, start_date: Optional[date], end_date: Optional[date]) -> Optional[int]:
        """
        Calculate duration in months between two dates
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of months or None
        """
        if not start_date or not end_date:
            return None
        
        try:
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            return max(0, months)
        except:
            return None
    
    def calculate_duration_years(self, start_date: Optional[date], end_date: Optional[date]) -> Optional[float]:
        """
        Calculate duration in years between two dates
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of years (float) or None
        """
        months = self.calculate_duration_months(start_date, end_date)
        if months is not None:
            return round(months / 12, 1)
        return None
    
    def normalize_date_string(self, date_string: str) -> str:
        """
        Normalize a date string to YYYY-MM-DD format
        
        Args:
            date_string: Date string to normalize
            
        Returns:
            Normalized date string or original if parsing fails
        """
        parsed = self.parse_date(date_string)
        if parsed:
            return self.format_date(parsed)
        return date_string


def test_date_parser():
    """Test date parser with various formats"""
    parser = DateParser()
    
    test_cases = [
        "January 2024",
        "Jan 2024",
        "01/2024",
        "2024",
        "2020 - 2024",
        "Jan 2020 - Dec 2023",
        "2020 - Present",
        "January 2020 - Current",
        "Present",
    ]
    
    print("Testing Date Parser:\n")
    
    for test_case in test_cases:
        parsed = parser.parse_date(test_case)
        print(f"Input: '{test_case:30s}' → Parsed: {parsed}")
    
    print("\n\nTesting Date Ranges:\n")
    
    range_cases = [
        "Jan 2020 - Dec 2023",
        "2020 - Present",
        "January 2020 - Current",
    ]
    
    for test_case in range_cases:
        start, end, is_current = parser.parse_date_range(test_case)
        print(f"Range: '{test_case:30s}' → Start: {start}, End: {end}, Current: {is_current}")
        
        if start and end:
            months = parser.calculate_duration_months(start, end)
            years = parser.calculate_duration_years(start, end)
            print(f"       Duration: {months} months ({years} years)")
        print()


if __name__ == "__main__":
    test_date_parser()
