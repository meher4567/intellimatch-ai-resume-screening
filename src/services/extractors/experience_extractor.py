"""
Experience Extractor Service - Extract structured work experience
Parses company names, job titles, dates, descriptions, and achievements
"""

import re
import logging
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, asdict, field
from datetime import date

# Import date parser
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.date_parser import DateParser

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Represents work experience entry"""
    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = ""
    achievements: List[str] = field(default_factory=list)
    duration_months: Optional[int] = None
    
    def __post_init__(self):
        # Calculate duration if dates available
        if self.start_date and self.end_date:
            months = (self.end_date.year - self.start_date.year) * 12
            months += self.end_date.month - self.start_date.month
            self.duration_months = max(0, months)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert dates to strings
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data


class ExperienceExtractor:
    """
    Extract work experience information from resume sections
    """
    
    # Job title indicators
    TITLE_PATTERNS = [
        r'\b(Senior|Junior|Lead|Principal|Staff|Chief)\s+',
        r'\b(Software|Web|Frontend|Backend|Full[\s-]?Stack|Mobile)\s+(Developer|Engineer)',
        r'\b(Data|ML|Machine Learning|AI)\s+(Scientist|Engineer|Analyst)',
        r'\b(DevOps|Site Reliability)\s+Engineer',
        r'\b(Product|Project|Program)\s+Manager',
        r'\b(Intern|Internship|Research\s+(?:Intern|Assistant))',
        r'\b(Consultant|Analyst|Specialist|Architect|Designer)',
    ]
    
    def __init__(self):
        """Initialize Experience Extractor"""
        self.date_parser = DateParser()
    
    def extract_job_title(self, text: str) -> Optional[str]:
        """
        Extract job title from text
        
        Args:
            text: Text to extract from
            
        Returns:
            Job title or None
        """
        # Try pattern matching
        for pattern in self.TITLE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract full title (look for capitalized words around match)
                start = match.start()
                # Look backwards and forwards for capitalized words
                words_before = text[:start].split()
                words_after = text[start:].split()[:5]  # Take up to 5 words
                
                title_words = []
                # Add capitalized words before
                for word in reversed(words_before[-3:]):
                    if word and word[0].isupper():
                        title_words.insert(0, word)
                    else:
                        break
                
                # Add matched words and words after
                for word in words_after:
                    if word and (word[0].isupper() or word.lower() in ['and', 'of', '&']):
                        title_words.append(word)
                    else:
                        break
                
                if title_words:
                    return ' '.join(title_words).strip(',-.')
        
        # Fallback: look for lines with mostly capitalized words at start
        lines = text.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if len(line) > 5 and line[0].isupper() and len(line) < 80:
                # Check if it's mostly title case
                words = line.split()
                if len(words) <= 6:  # Titles are usually short
                    capitalized = sum(1 for w in words if w and w[0].isupper())
                    if capitalized / len(words) >= 0.5:
                        return line.strip(',-.')
        
        return None
    
    def extract_bullet_points(self, text: str) -> List[str]:
        """
        Extract bullet points/achievements from text
        
        Args:
            text: Text containing bullets
            
        Returns:
            List of bullet point strings
        """
        bullets = []
        
        # Common bullet indicators
        bullet_patterns = [
            r'^[\s]*[•●○▪▫■□◦◘◙‣⁃⦾⦿]+\s*(.+)$',  # Bullet symbols
            r'^[\s]*[-–—]\s*(.+)$',  # Dashes
            r'^[\s]*\d+[\.)]\s*(.+)$',  # Numbered
            r'^[\s]*[a-z][\.)]\s*(.+)$',  # Lettered
        ]
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Too short
                continue
            
            # Check if line matches bullet pattern
            for pattern in bullet_patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    bullet_text = match.group(1).strip()
                    if len(bullet_text) > 15:  # Meaningful content
                        bullets.append(bullet_text)
                    break
        
        return bullets
    
    def split_experience_blocks(self, text: str) -> List[str]:
        """
        Split experience text into individual job blocks
        
        Args:
            text: Experience section text
            
        Returns:
            List of text blocks (one per job)
        """
        blocks = []
        
        # Strategy 1: Look for job title indicators (bullet + capitalized title + date pattern below)
        # Pattern: bullet/marker followed by title, then date range on next line
        job_start_pattern = r'(?:^|\n)(?:•|\-|\*|\d+\.)?\s*([A-Z][^\n]+(?:Intern|Engineer|Developer|Manager|Analyst|Scientist|Researcher|Assistant|Consultant|Specialist|Architect|Designer)[^\n]*)\s*\n\s*([A-Za-z]{3}\s+\d{4}\s*[-–—]\s*(?:[A-Za-z]{3}\s+\d{4}|Present|Current))'
        
        matches = list(re.finditer(job_start_pattern, text, re.MULTILINE))
        
        if len(matches) > 1:
            # Split at each match
            blocks = []
            for i, match in enumerate(matches):
                start_pos = match.start()
                end_pos = matches[i+1].start() if i < len(matches) - 1 else len(text)
                block = text[start_pos:end_pos].strip()
                if len(block) > 50:
                    blocks.append(block)
            return blocks
        
        # Strategy 2: Try to split by date patterns (common separator)
        date_pattern = r'\n(?=[A-Za-z]{3}\s+\d{4}\s*[-–—]\s*(?:[A-Za-z]{3}\s+\d{4}|Present|Current))'
        potential_blocks = re.split(date_pattern, text)
        
        if len(potential_blocks) > 1:
            return [b.strip() for b in potential_blocks if len(b.strip()) > 50]
        
        # Strategy 3: Fallback - split by double newlines
        blocks = text.split('\n\n')
        return [b.strip() for b in blocks if len(b.strip()) > 50]
    
    def extract_experience_entry(self, text: str, company_names: List[str] = None) -> Optional[Experience]:
        """
        Extract single experience entry from text block
        
        Args:
            text: Text block for one job
            company_names: List of known company names (from NER)
            
        Returns:
            Experience object or None
        """
        # Extract job title
        title = self.extract_job_title(text)
        if not title:
            # Try first line as title
            lines = text.split('\n')
            if lines:
                title = lines[0].strip()
        
        # Extract company name
        company = None
        if company_names:
            text_lower = text.lower()
            for comp in company_names:
                if comp.lower() in text_lower:
                    company = comp
                    break
        
        # If still not found, look for company patterns
        if not company:
            # Look for capitalized company names (usually after job title and dates)
            lines = text.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                # Company names are usually:
                # 1. Capitalized
                # 2. Not too long (< 50 chars)
                # 3. Come after dates or job titles
                # 4. May have Inc, Ltd, Corp, etc.
                
                if len(line) > 3 and len(line) < 80:
                    # Check for company indicators
                    if any(indicator in line for indicator in ['Inc.', 'Ltd', 'Corp', 'LLC', 'Institute', 'University', 'Laboratory']):
                        company = line.strip('•-,')
                        break
                    # Or just a capitalized name after dates
                    elif line and line[0].isupper() and not any(c.isdigit() for c in line[:10]):
                        words = line.split()
                        if 2 <= len(words) <= 6:  # Company names usually 2-6 words
                            capitalized_words = sum(1 for w in words if w and w[0].isupper())
                            if capitalized_words >= len(words) * 0.7:  # Mostly capitalized
                                company = line.strip('•-,')
                                break
        
        # Last resort: look for "at Company" pattern
        if not company:
            at_pattern = r'\bat\s+([A-Z][A-Za-z\s&,.]+?)(?:\s*[,\n]|\s+\d{4})'
            match = re.search(at_pattern, text)
            if match:
                company = match.group(1).strip()
        
        if not company:
            company = "Unknown Company"
        
        # Extract dates
        start_date, end_date, is_current = self.date_parser.parse_date_range(text)
        
        # Extract bullet points
        bullets = self.extract_bullet_points(text)
        
        # Full description
        description = text
        
        # Create experience entry
        entry = Experience(
            title=title,
            company=company,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            description=description,
            achievements=bullets
        )
        
        return entry
    
    def extract_experience_entries(self, text: str, company_names: List[str] = None) -> List[Experience]:
        """
        Extract all experience entries from experience section
        
        Args:
            text: Experience section text
            company_names: List of company names from NER (optional)
            
        Returns:
            List of Experience objects
        """
        blocks = self.split_experience_blocks(text)
        entries = []
        
        for block in blocks:
            entry = self.extract_experience_entry(block, company_names)
            if entry:
                entries.append(entry)
        
        return entries
    
    def extract_from_section(self, section_text: str, organizations: List[str] = None) -> List[Experience]:
        """
        Extract experience from experience section
        
        Args:
            section_text: Experience section text
            organizations: List of organization names from NER (optional)
            
        Returns:
            List of Experience objects
        """
        return self.extract_experience_entries(section_text, organizations)


def test_experience_extractor():
    """Test experience extractor"""
    extractor = ExperienceExtractor()
    
    test_text = """
    Research Intern
    Indian Statistical Institute, Kolkata, India
    May 2024 - July 2024
    
    • Worked on post-quantum cryptography research
    • Implemented Kyber algorithm in Python
    • Published research paper in IEEE conference
    • Collaborated with team of 5 researchers
    
    Software Engineering Intern
    Tech Solutions Pvt Ltd, Hyderabad, India
    June 2023 - August 2023
    
    - Developed REST APIs using Django and PostgreSQL
    - Improved application performance by 40%
    - Wrote unit tests achieving 85% coverage
    - Worked in Agile team of 8 developers
    """
    
    print("="*60)
    print("Test Text:")
    print("="*60)
    print(test_text)
    
    print("\n" + "="*60)
    print("Extracted Experience:")
    print("="*60)
    
    entries = extractor.extract_experience_entries(test_text)
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i}. {entry.title}")
        print(f"   Company: {entry.company}")
        if entry.start_date or entry.end_date:
            duration = ""
            if entry.duration_months:
                duration = f" ({entry.duration_months} months)"
            print(f"   Duration: {entry.start_date} to {entry.end_date}{duration}")
            if entry.is_current:
                print(f"   Status: Current Position")
        
        if entry.achievements:
            print(f"   Achievements ({len(entry.achievements)}):")
            for achievement in entry.achievements:
                print(f"      • {achievement[:80]}...")


if __name__ == "__main__":
    test_experience_extractor()
