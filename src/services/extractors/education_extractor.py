"""
Education Extractor Service - Extract structured education information
Parses degrees, institutions, dates, GPA, and honors
"""

import re
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict
from datetime import date

# Import date parser
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.date_parser import DateParser

logger = logging.getLogger(__name__)


@dataclass
class Education:
    """Represents education entry"""
    degree: str
    institution: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    field_of_study: Optional[str] = None
    honors: List[str] = None
    
    def __post_init__(self):
        if self.honors is None:
            self.honors = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert dates to strings
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data


class EducationExtractor:
    """
    Extract education information from resume sections
    """
    
    # Degree patterns
    DEGREE_PATTERNS = [
        # Full names
        r'\b(Bachelor\s+of\s+(Science|Arts|Engineering|Technology|Business|Commerce))\b',
        r'\b(Master\s+of\s+(Science|Arts|Engineering|Technology|Business|Commerce))\b',
        r'\b(Doctor\s+of\s+Philosophy|Ph\.?D\.?|Doctorate)\b',
        r'\b(Master\s+of\s+Business\s+Administration|MBA)\b',
        r'\b(Master\s+of\s+Technology|M\.?Tech\.?|MTech)\b',
        r'\b(Bachelor\s+of\s+Technology|B\.?Tech\.?|BTech)\b',
        # Abbreviations
        r'\b(B\.?S\.?|B\.?A\.?|B\.?E\.?|B\.?Tech\.?)\b',
        r'\b(M\.?S\.?|M\.?A\.?|M\.?E\.?|M\.?Tech\.?)\b',
        r'\b(Ph\.?D\.?|D\.?Phil\.?)\b',
        r'\bMBA\b',
        # General
        r'\b(Associate\s+Degree|Diploma)\b',
    ]
    
    # Field of study patterns
    FIELD_PATTERNS = [
        r'\bin\s+([A-Z][A-Za-z\s]+(?:Science|Engineering|Studies|Arts|Technology))',
        r'\bof\s+([A-Z][A-Za-z\s]+(?:Science|Engineering|Studies|Arts|Technology))',
        r'\b(Computer Science|Electrical Engineering|Mechanical Engineering|Business Administration)\b',
    ]
    
    # Honor patterns
    HONOR_PATTERNS = [
        r'\b(Cum\s+Laude|Magna\s+Cum\s+Laude|Summa\s+Cum\s+Laude)\b',
        r'\b(With\s+Honors?|With\s+Distinction)\b',
        r'\b(Dean\'s\s+List|Honor\s+Roll)\b',
        r'\b(First\s+Class|Second\s+Class|Third\s+Class)\b',
        r'\b(Gold\s+Medal(?:ist)?|Silver\s+Medal(?:ist)?)\b',
    ]
    
    # GPA patterns
    GPA_PATTERNS = [
        r'\bGPA[:\s]+([0-4]\.\d+)\b',
        r'\b([0-4]\.\d+)\s*(?:/|out of)\s*4\.0\b',
        r'\b([0-4]\.\d+)\s+GPA\b',
    ]
    
    def __init__(self):
        """Initialize Education Extractor"""
        self.date_parser = DateParser()
    
    def extract_degree(self, text: str) -> Optional[str]:
        """
        Extract degree name from text
        
        Args:
            text: Text to extract from
            
        Returns:
            Degree name or None
        """
        for pattern in self.DEGREE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None
    
    def extract_field_of_study(self, text: str) -> Optional[str]:
        """
        Extract field of study from text
        
        Args:
            text: Text to extract from
            
        Returns:
            Field name or None
        """
        for pattern in self.FIELD_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1 if '(' in pattern else 0).strip()
        
        return None
    
    def extract_gpa(self, text: str) -> Optional[float]:
        """
        Extract GPA from text
        
        Args:
            text: Text to extract from
            
        Returns:
            GPA value or None
        """
        for pattern in self.GPA_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    gpa = float(match.group(1))
                    if 0.0 <= gpa <= 4.0:
                        return gpa
                except ValueError:
                    continue
        
        return None
    
    def extract_honors(self, text: str) -> List[str]:
        """
        Extract honors and distinctions from text
        
        Args:
            text: Text to extract from
            
        Returns:
            List of honors
        """
        honors = []
        
        for pattern in self.HONOR_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                honor = match.group().strip()
                if honor not in honors:
                    honors.append(honor)
        
        return honors
    
    def extract_education_entries(self, text: str, institution_names: List[str] = None) -> List[Education]:
        """
        Extract all education entries from text
        
        Args:
            text: Education section text
            institution_names: List of known institution names (optional)
            
        Returns:
            List of Education objects
        """
        entries = []
        
        # Split by common delimiters (double newline, bullets, etc.)
        blocks = re.split(r'\n\s*\n|•|▪', text)
        
        for block in blocks:
            if len(block.strip()) < 20:  # Too short to be valid
                continue
            
            # Extract components
            degree = self.extract_degree(block)
            if not degree:
                continue  # Must have a degree
            
            field = self.extract_field_of_study(block)
            gpa = self.extract_gpa(block)
            honors = self.extract_honors(block)
            
            # Extract dates
            start_date, end_date, is_current = self.date_parser.parse_date_range(block)
            
            # Extract institution name (if provided)
            institution = "Unknown Institution"
            if institution_names:
                for inst in institution_names:
                    if inst.lower() in block.lower():
                        institution = inst
                        break
            else:
                # Try to extract organization name (capitalized words)
                # Look for patterns like "University of X", "X College"
                inst_pattern = r'\b([A-Z][A-Za-z\s]+(?:University|Institute|College|School))\b'
                inst_match = re.search(inst_pattern, block)
                if inst_match:
                    institution = inst_match.group().strip()
            
            # Create education entry
            entry = Education(
                degree=degree,
                institution=institution,
                start_date=start_date,
                end_date=end_date,
                gpa=gpa,
                field_of_study=field,
                honors=honors
            )
            
            entries.append(entry)
        
        return entries
    
    def extract_from_section(self, section_text: str, organizations: List[str] = None) -> List[Education]:
        """
        Extract education from education section
        
        Args:
            section_text: Education section text
            organizations: List of organization names from NER (optional)
            
        Returns:
            List of Education objects
        """
        return self.extract_education_entries(section_text, organizations)


def test_education_extractor():
    """Test education extractor"""
    extractor = EducationExtractor()
    
    test_text = """
    Master of Technology (M.Tech) in Computer Science
    University of Hyderabad, Hyderabad, India
    2024 - 2026 (Expected)
    GPA: 8.5/10
    Merit Scholarship Recipient
    
    Bachelor of Technology (B.Tech) in Electronics and Communication Engineering
    JNTUH College of Engineering, Hyderabad
    2020 - 2024
    CGPA: 8.2/10
    First Class with Distinction
    Dean's List (2022, 2023)
    """
    
    print("="*60)
    print("Test Text:")
    print("="*60)
    print(test_text)
    
    print("\n" + "="*60)
    print("Extracted Education:")
    print("="*60)
    
    entries = extractor.extract_education_entries(test_text)
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i}. {entry.degree}")
        print(f"   Institution: {entry.institution}")
        if entry.field_of_study:
            print(f"   Field: {entry.field_of_study}")
        if entry.start_date or entry.end_date:
            print(f"   Duration: {entry.start_date} to {entry.end_date}")
        if entry.gpa:
            print(f"   GPA: {entry.gpa}")
        if entry.honors:
            print(f"   Honors: {', '.join(entry.honors)}")


if __name__ == "__main__":
    test_education_extractor()
