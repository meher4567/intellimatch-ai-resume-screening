"""
Name Extractor

Extracts candidate name from resume text using multiple strategies:
1. Header detection (first few lines)
2. Pattern matching (common name formats)
3. Title/section exclusion (avoid extracting section headers as names)
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NameExtractor:
    """Extract candidate name from resume text"""
    
    def __init__(self):
        """Initialize name extractor with patterns"""
        
        # Words to exclude (not part of names)
        self.exclude_words = {
            'resume', 'cv', 'curriculum', 'vitae', 'profile', 'summary',
            'objective', 'email', 'phone', 'address', 'location',
            'experience', 'education', 'skills', 'projects', 'certifications',
            'achievements', 'publications', 'languages', 'interests',
            'professional', 'personal', 'technical', 'about', 'contact',
            'page', 'of', 'updated', 'last', 'modified', 'candidate',
            # Common suffixes/prefixes
            'mr', 'mrs', 'ms', 'dr', 'prof', 'professor',
        }
        
        # Name patterns (more restrictive to avoid false positives)
        self.name_patterns = [
            # FirstName LastName (2 capitalized words)
            re.compile(r'^([A-Z][a-z]+)\s+([A-Z][a-z]+)$'),
            # FirstName MiddleName LastName (3 capitalized words)
            re.compile(r'^([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)$'),
            # FirstName M. LastName (with middle initial)
            re.compile(r'^([A-Z][a-z]+)\s+([A-Z]\.)\s+([A-Z][a-z]+)$'),
            # ALL CAPS names (common in resumes)
            re.compile(r'^([A-Z]+)\s+([A-Z]+)$'),
            re.compile(r'^([A-Z]+)\s+([A-Z]+)\s+([A-Z]+)$'),
        ]
    
    def _clean_line(self, line: str) -> str:
        """Clean a line of text"""
        # Remove extra whitespace
        line = ' '.join(line.split())
        # Remove common separators at start/end
        line = line.strip('|•-_:')
        return line.strip()
    
    def _is_valid_name(self, text: str) -> bool:
        """
        Check if text looks like a valid name
        
        Args:
            text: Text to check
            
        Returns:
            True if text looks like a name
        """
        if not text or len(text) < 3:
            return False
        
        # Check length (names are typically 5-50 chars)
        if len(text) > 50:
            return False
        
        # Check word count (2-4 words typical)
        words = text.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Check for exclude words
        text_lower = text.lower()
        for word in words:
            if word.lower() in self.exclude_words:
                return False
        
        # Check if contains @ or common non-name characters
        if '@' in text or 'http' in text_lower or 'www' in text_lower:
            return False
        
        # Check for too many special characters
        special_char_count = sum(1 for c in text if not c.isalnum() and c != ' ' and c != '.')
        if special_char_count > 2:
            return False
        
        return True
    
    def _extract_from_header(self, text: str, max_lines: int = 10) -> Optional[str]:
        """
        Extract name from resume header (first few lines)
        
        Args:
            text: Resume text
            max_lines: Maximum number of lines to check in header
            
        Returns:
            Extracted name or None
        """
        lines = text.split('\n')[:max_lines]
        
        for i, line in enumerate(lines):
            line = self._clean_line(line)
            
            if not line or len(line) < 3:
                continue
            
            # Skip lines with common header indicators
            line_lower = line.lower()
            if any(word in line_lower for word in ['resume', 'curriculum vitae', 'cv', 'page']):
                continue
            
            # Try pattern matching
            for pattern in self.name_patterns:
                if pattern.match(line):
                    if self._is_valid_name(line):
                        logger.info(f"Extracted name from header (line {i+1}): {line}")
                        return line
            
            # Check if line looks like a name (even without exact pattern match)
            # Must be early in document (first 3 lines) and pass validation
            if i < 3 and self._is_valid_name(line):
                # Additional check: should start with capital letter
                if line[0].isupper():
                    # Check if it's mostly letters
                    letter_count = sum(1 for c in line if c.isalpha())
                    if letter_count / len(line) > 0.7:  # 70% letters
                        logger.info(f"Extracted name from header (line {i+1}, heuristic): {line}")
                        return line
        
        return None
    
    def _extract_from_patterns(self, text: str) -> Optional[str]:
        """
        Extract name using pattern matching throughout text
        
        Args:
            text: Resume text
            
        Returns:
            Extracted name or None
        """
        # Look for explicit name declarations
        name_indicators = [
            r'(?:Name|Full Name|Candidate|Applicant):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z\.]+)+)',
            r'(?:Name|Full Name|Candidate|Applicant)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z\.]+)+)',
        ]
        
        for pattern in name_indicators:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if self._is_valid_name(name):
                    logger.info(f"Extracted name from pattern: {name}")
                    return name
        
        return None
    
    def extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name from resume text
        
        Tries multiple strategies:
        1. Header detection (first few lines)
        2. Explicit name patterns ("Name: John Doe")
        3. Fallback to first valid name-like text
        
        Args:
            text: Resume text
            
        Returns:
            Extracted name or None if not found
        """
        if not text:
            logger.warning("Empty text provided for name extraction")
            return None
        
        logger.info("Extracting name from resume text")
        
        # Strategy 1: Extract from header (most reliable)
        name = self._extract_from_header(text)
        if name:
            return name
        
        # Strategy 2: Look for explicit name patterns
        name = self._extract_from_patterns(text)
        if name:
            return name
        
        logger.warning("Could not extract name from resume")
        return None


# Convenience function for quick extraction
def extract_name(text: str) -> Optional[str]:
    """
    Quick function to extract name from text
    
    Args:
        text: Resume text
        
    Returns:
        Extracted name or None
    """
    extractor = NameExtractor()
    return extractor.extract_name(text)
