"""
Resume Section Detector
Identifies and extracts key sections from resume text
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """Represents a resume section"""
    name: str  # Standardized name (e.g., 'experience')
    raw_header: str  # Original header text (e.g., 'Work Experience')
    content: str  # Section content
    start_line: int  # Line number where section starts
    end_line: int  # Line number where section ends
    confidence: float  # Confidence score (0-1)


class SectionDetector:
    """
    Detects and extracts sections from resume text
    
    Handles variations like:
    - EXPERIENCE / Work Experience / Professional Experience
    - EDUCATION / Academic Background / Qualifications
    - SKILLS / Technical Skills / Core Competencies
    """
    
    # Section patterns with variations
    SECTION_PATTERNS = {
        'experience': [
            r'\b(professional\s+)?experience\b',
            r'\bwork\s+(experience|history)\b',
            r'\bemployment(\s+history)?\b',
            r'\bcareer\s+(history|summary)\b',
            r'\bprofessional\s+background\b',
        ],
        'education': [
            r'\beducation(al\s+background)?\b',
            r'\bacademic\s+(background|qualifications)\b',
            r'\bqualifications?\b',
            r'\bdegrees?\b',
        ],
        'skills': [
            r'\b(technical\s+)?skills\b',
            r'\bcore\s+competenc(ies|y)\b',
            r'\bexpertise\b',
            r'\bproficienc(ies|y)\b',
            r'\bcapabilities\b',
            r'\btechnolog(ies|y)\b',
        ],
        'summary': [
            r'\b(professional\s+)?summary\b',
            r'\bprofile\b',
            r'\b(career\s+)?objective\b',
            r'\babout(\s+me)?\b',
            r'\boverview\b',
        ],
        'projects': [
            r'\bprojects?\b',
            r'\bkey\s+projects\b',
            r'\bportfolio\b',
        ],
        'certifications': [
            r'\bcertifications?\b',
            r'\blicenses?\b',
            r'\bprofessional\s+development\b',
        ],
        'achievements': [
            r'\bachievements?\b',
            r'\baccomplishments?\b',
            r'\bawards?\b',
            r'\bhonors?\b',
        ],
        'publications': [
            r'\bpublications?\b',
            r'\bpapers?\b',
            r'\bresearch\b',
        ],
        'languages': [
            r'\blanguages?\b',
        ],
        'interests': [
            r'\binterests?\b',
            r'\bhobbies\b',
        ],
    }
    
    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize section detector
        
        Args:
            min_confidence: Minimum confidence score to consider a section valid
        """
        self.min_confidence = min_confidence
        
        # Compile regex patterns
        self.compiled_patterns = {}
        for section_type, patterns in self.SECTION_PATTERNS.items():
            self.compiled_patterns[section_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def detect_sections(self, text: str) -> Dict[str, Section]:
        """
        Detect all sections in resume text
        
        Args:
            text: Resume text
            
        Returns:
            Dict mapping section type to Section object
        """
        lines = text.split('\n')
        
        # Find section headers
        section_headers = self._find_section_headers(lines)
        
        # Extract content for each section
        sections = self._extract_section_content(lines, section_headers)
        
        # Filter by confidence
        sections = {
            name: section for name, section in sections.items()
            if section.confidence >= self.min_confidence
        }
        
        logger.info(f"Detected {len(sections)} sections: {list(sections.keys())}")
        
        return sections
    
    def _find_section_headers(self, lines: List[str]) -> List[Tuple[int, str, str, float]]:
        """
        Find potential section headers in text
        
        Returns:
            List of (line_num, section_type, header_text, confidence)
        """
        headers = []
        
        for line_num, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines or very long lines (likely not headers)
            if not line_stripped or len(line_stripped) > 100:
                continue
            
            # Check if line matches any section pattern
            for section_type, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    match = pattern.search(line_stripped)
                    if match:
                        # Calculate confidence based on multiple factors
                        confidence = self._calculate_header_confidence(
                            line_stripped, section_type, match
                        )
                        
                        headers.append((line_num, section_type, line_stripped, confidence))
                        break  # Found match, no need to check other patterns
                
                # If we found a match, don't check other section types
                if headers and headers[-1][0] == line_num:
                    break
        
        return headers
    
    def _calculate_header_confidence(self, line: str, section_type: str, match: re.Match) -> float:
        """
        Calculate confidence that a line is a section header
        
        Factors:
        - Line length (shorter is better)
        - ALL CAPS (higher confidence)
        - Punctuation like colons or dashes
        - Position of match in line
        """
        confidence = 0.5  # Base confidence
        
        # Shorter lines are more likely to be headers
        if len(line) < 30:
            confidence += 0.2
        elif len(line) < 50:
            confidence += 0.1
        
        # ALL CAPS indicates a header
        if line.isupper():
            confidence += 0.2
        
        # Contains colon or dash separator
        if ':' in line or '-' in line or '—' in line:
            confidence += 0.1
        
        # Match is at the start of the line
        if match.start() < 5:
            confidence += 0.1
        
        # Line has few words (headers are usually 1-4 words)
        word_count = len(line.split())
        if word_count <= 4:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_section_content(
        self, 
        lines: List[str], 
        headers: List[Tuple[int, str, str, float]]
    ) -> Dict[str, Section]:
        """
        Extract content for each detected section
        
        Args:
            lines: All lines of text
            headers: Detected section headers
            
        Returns:
            Dict mapping section type to Section object
        """
        if not headers:
            return {}
        
        # Sort headers by line number
        headers = sorted(headers, key=lambda x: x[0])
        
        sections = {}
        
        for i, (line_num, section_type, header_text, confidence) in enumerate(headers):
            # Determine where this section ends
            if i < len(headers) - 1:
                end_line = headers[i + 1][0]  # Next section starts
            else:
                end_line = len(lines)  # Last section goes to end
            
            # Extract content (skip the header line itself)
            content_lines = lines[line_num + 1:end_line]
            content = '\n'.join(content_lines).strip()
            
            # If we already have this section type, keep the one with higher confidence
            if section_type in sections:
                if confidence > sections[section_type].confidence:
                    sections[section_type] = Section(
                        name=section_type,
                        raw_header=header_text,
                        content=content,
                        start_line=line_num,
                        end_line=end_line,
                        confidence=confidence
                    )
            else:
                sections[section_type] = Section(
                    name=section_type,
                    raw_header=header_text,
                    content=content,
                    start_line=line_num,
                    end_line=end_line,
                    confidence=confidence
                )
        
        return sections
    
    def get_section_text(self, sections: Dict[str, Section], section_name: str) -> Optional[str]:
        """
        Get text content for a specific section
        
        Args:
            sections: Dict of detected sections
            section_name: Name of section to retrieve
            
        Returns:
            Section content text or None if not found
        """
        section = sections.get(section_name)
        return section.content if section else None
    
    def has_section(self, sections: Dict[str, Section], section_name: str) -> bool:
        """Check if a section exists"""
        return section_name in sections


def detect_resume_sections(text: str, min_confidence: float = 0.5) -> Dict[str, Section]:
    """
    Convenience function to detect sections in resume text
    
    Args:
        text: Resume text
        min_confidence: Minimum confidence threshold
        
    Returns:
        Dict mapping section type to Section object
    """
    detector = SectionDetector(min_confidence=min_confidence)
    return detector.detect_sections(text)
