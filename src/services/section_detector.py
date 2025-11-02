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
            r'\bwork\b(?=\s*$)',  # Just "Work" as a header
        ],
        'education': [
            r'\beducation(al\s+background)?\b',
            r'\bacademic\s+(background|qualifications)\b',
            r'\bqualifications?\b',
            r'\bdegrees?\b',
            r'\bacademia\b',
        ],
        'skills': [
            r'\b(technical\s+)?skills\b',
            r'\bcore\s+competenc(ies|y)\b',
            r'\bexpertise\b',
            r'\bproficienc(ies|y)\b',
            r'\bcapabilities\b',
            r'\btechnolog(ies|y)\b',
            r'\btools?\b(?=\s*(&|and|$))',  # "Tools" or "Tools & Technologies"
        ],
        'summary': [
            r'\b(professional\s+)?summary\b',
            r'\bprofile\b',
            r'\b(career\s+)?objective\b',
            r'\babout(\s+me)?\b',
            r'\boverview\b',
            r'\bintroduction\b',
            r'\bpersonal\s+statement\b',
        ],
        'projects': [
            r'\bprojects?\b',
            r'\bkey\s+projects\b',
            r'\bportfolio\b',
            r'\bside\s+projects?\b',
            r'\bpersonal\s+projects?\b',
            r'\bopen\s+source\b',
            r'\bnotable\s+projects?\b',
        ],
        'certifications': [
            r'\bcertifications?\b',
            r'\blicenses?\b',
            r'\bprofessional\s+development\b',
            r'\bcredentials?\b',
            r'\btraining\b',
        ],
        'achievements': [
            r'\bachievements?\b',
            r'\baccomplishments?\b',
            r'\bawards?\b',
            r'\bhonors?\b',
            r'\brecognitions?\b',
            r'\bdistinctions?\b',
        ],
        'publications': [
            r'\bpublications?\b',
            r'\bpapers?\b',
            r'\bresearch(\s+papers?)?\b',
            r'\bpublished\s+works?\b',
            r'\bconference\s+papers?\b',
            r'\bjournal\s+articles?\b',
        ],
        'languages': [
            r'\blanguages?\b',
            r'\bspoken\s+languages?\b',
            r'\blinguistic\s+skills?\b',
        ],
        'interests': [
            r'\binterests?\b',
            r'\bhobbies\b',
            r'\bpersonal\s+interests?\b',
            r'\bextracurricular\b',
        ],
        'volunteer': [
            r'\bvolunteer(ing)?\b',
            r'\bcommunity\s+(service|involvement)\b',
            r'\bvolunteer\s+(work|experience)\b',
            r'\bsocial\s+impact\b',
        ],
        'leadership': [
            r'\bleadership(\s+experience)?\b',
            r'\bpositions\s+of\s+responsibility\b',
            r'\bmanagement\s+experience\b',
            r'\bteam\s+leadership\b',
        ],
        'conferences': [
            r'\bconferences?\b',
            r'\btalks?\b',
            r'\bpresentations?\b',
            r'\bspeaking\s+engagements?\b',
            r'\bworkshops?\b',
        ],
        'patents': [
            r'\bpatents?\b',
            r'\bintellectual\s+property\b',
            r'\binventions?\b',
        ],
        'references': [
            r'\breferences?\b',
            r'\breferees?\b',
            r'\brecommendations?\b',
            r'\bavailable\s+upon\s+request\b',
        ],
        'activities': [
            r'\b(extracurricular\s+)?activities\b',
            r'\borganizations?\b',
            r'\bmemberships?\b',
            r'\baffiliations?\b',
            r'\bprofessional\s+associations?\b',
        ],
        'coursework': [
            r'\b(relevant\s+)?coursework\b',
            r'\bacademic\s+projects?\b',
            r'\bcourses?\b(?=\s*(taken|completed|$))',
        ],
        'internships': [
            r'\binternships?\b',
            r'\bintern\s+experience\b',
            r'\bco-?op(\s+experience)?\b',
        ],
        'research': [
            r'\bresearch\s+experience\b',
            r'\bresearch\s+interests?\b',
            r'\bresearch\s+projects?\b',
            r'\bacademic\s+research\b',
        ],
        'teaching': [
            r'\bteaching\s+experience\b',
            r'\bteaching\s+assistant\b',
            r'\binstructor\s+experience\b',
            r'\bmentoring\b',
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
        
        # Filter headers by confidence BEFORE extracting content
        # This prevents low-confidence false positives from interfering with content extraction
        filtered_headers = [
            (line_num, section_type, header_text, confidence)
            for line_num, section_type, header_text, confidence in section_headers
            if confidence >= self.min_confidence
        ]
        
        # Extract content for each section
        sections = self._extract_section_content(lines, filtered_headers)
        
        # Double-check confidence (should already be filtered, but be safe)
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
        
        # ANTI-PATTERNS: Reduce confidence for lines that look like content, not headers
        
        # Contains pipe '|' character (often used in job titles: "Company | Position")
        # This is a STRONG indicator that it's NOT a section header
        if '|' in line:
            confidence -= 0.5  # Increased penalty from 0.3 to 0.5
        
        # Very long line (more than 50 chars) is probably content, not a header
        if len(line) > 50:
            confidence -= 0.3  # Increased penalty from 0.2 to 0.3
        
        # Contains many capital letters scattered (not a clean header)
        # E.g., "ROCKS LEADERSHIP COMMITTEE | REPRESENTATIVE"
        if line.isupper() and word_count > 5:
            confidence -= 0.3  # Increased penalty from 0.2 to 0.3
        
        # Line contains dates or date-like patterns (job titles have dates)
        date_patterns = [r'\d{4}', r'\d{1,2}/\d{1,2}', r'january|february|march|april|may|june|july|august|september|october|november|december']
        for pattern in date_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                confidence -= 0.4  # Increased penalty from 0.3 to 0.4
                break
        
        return max(min(confidence, 1.0), 0.0)  # Clamp between 0 and 1
    
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
        
        # Remove duplicate section types that are too close together
        # Keep the one with higher confidence OR the one that looks more like a real header
        filtered_headers = []
        seen_sections = {}
        
        for line_num, section_type, header_text, confidence in headers:
            if section_type in seen_sections:
                # Get the previously seen header for this section type
                prev_line_num, prev_section_type, prev_header_text, prev_confidence = seen_sections[section_type]
                
                # If they're very close together (within 10 lines), it's likely a false positive
                if abs(line_num - prev_line_num) < 10:
                    # Keep the one that's more likely to be a real header
                    # Prefer shorter headers that are simple section names
                    prev_is_simple = len(prev_header_text.split()) <= 3
                    curr_is_simple = len(header_text.split()) <= 3
                    
                    # If current header is simpler, replace the previous one
                    if curr_is_simple and not prev_is_simple:
                        # Remove previous from filtered list
                        filtered_headers = [h for h in filtered_headers if h[0] != prev_line_num]
                        filtered_headers.append((line_num, section_type, header_text, confidence))
                        seen_sections[section_type] = (line_num, section_type, header_text, confidence)
                    elif prev_is_simple and not curr_is_simple:
                        # Keep previous, skip current
                        continue
                    elif confidence > prev_confidence:
                        # Both complex or both simple - use confidence
                        filtered_headers = [h for h in filtered_headers if h[0] != prev_line_num]
                        filtered_headers.append((line_num, section_type, header_text, confidence))
                        seen_sections[section_type] = (line_num, section_type, header_text, confidence)
                    else:
                        # Keep previous, skip current
                        continue
                else:
                    # Far apart - treat as separate sections (but we'll still keep only one)
                    if confidence > prev_confidence:
                        filtered_headers = [h for h in filtered_headers if h[0] != prev_line_num]
                        filtered_headers.append((line_num, section_type, header_text, confidence))
                        seen_sections[section_type] = (line_num, section_type, header_text, confidence)
            else:
                # First time seeing this section type
                filtered_headers.append((line_num, section_type, header_text, confidence))
                seen_sections[section_type] = (line_num, section_type, header_text, confidence)
        
        # Sort filtered headers by line number
        filtered_headers = sorted(filtered_headers, key=lambda x: x[0])
        
        sections = {}
        
        for i, (line_num, section_type, header_text, confidence) in enumerate(filtered_headers):
            # Determine where this section ends
            if i < len(filtered_headers) - 1:
                end_line = filtered_headers[i + 1][0]  # Next section starts
            else:
                end_line = len(lines)  # Last section goes to end
            
            # Extract content (skip the header line itself)
            content_lines = lines[line_num + 1:end_line]
            content = '\n'.join(content_lines).strip()
            
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
