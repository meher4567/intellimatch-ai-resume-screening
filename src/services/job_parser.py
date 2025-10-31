"""
Job Description Parser

Extracts structured information from job descriptions:
- Job title
- Company information
- Required skills
- Experience requirements
- Education requirements
- Job responsibilities
- Qualifications
- Location
- Salary (if mentioned)
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class JobDescription:
    """Structured job description data"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    salary_range: Optional[str] = None
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    responsibilities: List[str] = None
    qualifications: List[str] = None
    benefits: List[str] = None
    raw_text: str = ""
    
    def __post_init__(self):
        """Initialize empty lists"""
        if self.required_skills is None:
            self.required_skills = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.responsibilities is None:
            self.responsibilities = []
        if self.qualifications is None:
            self.qualifications = []
        if self.benefits is None:
            self.benefits = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_type': self.job_type,
            'experience_required': self.experience_required,
            'education_required': self.education_required,
            'salary_range': self.salary_range,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'responsibilities': self.responsibilities,
            'qualifications': self.qualifications,
            'benefits': self.benefits,
            'raw_text': self.raw_text
        }


class JobParser:
    """Parse job descriptions into structured data"""
    
    def __init__(self):
        """Initialize job parser with patterns"""
        
        # Job title patterns (often at the beginning)
        self.title_indicators = [
            r'(?:Job Title|Position|Role):\s*(.+?)(?:\n|$)',
            r'^(.+?)\s*(?:Job Description|Description|Overview)',
        ]
        
        # Company patterns
        self.company_patterns = [
            r'(?:Company|Organization|Employer):\s*(.+?)(?:\n|$)',
            r'(?:About|Join)\s+(.+?)(?:\s+team|\s+is)',
        ]
        
        # Location patterns
        self.location_patterns = [
            r'(?:Location|Office|Based in):\s*(.+?)(?:\n|$)',
            r'(?:Remote|Hybrid|On-site)\s*[-–]\s*(.+?)(?:\n|$)',
        ]
        
        # Job type patterns
        self.job_type_patterns = [
            r'(?:Employment Type|Job Type):\s*(.+?)(?:\n|$)',
            r'\b(Full[- ]?time|Part[- ]?time|Contract|Freelance|Temporary|Internship)\b',
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+\+?)\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'(?:Experience|Experience Level):\s*(.+?)(?:\n|$)',
            r'(?:minimum|at least)\s+(\d+)\s+years?',
        ]
        
        # Education patterns
        self.education_patterns = [
            r'(?:Bachelor|Master|PhD|BS|MS|MBA|Doctorate)(?:\'s)?(?:\s+(?:degree|in))?',
            r'(?:Education|Degree):\s*(.+?)(?:\n|$)',
        ]
        
        # Salary patterns
        self.salary_patterns = [
            r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*(?:per|\/)\s*(?:year|hour|month))?',
            r'(?:Salary|Compensation):\s*(.+?)(?:\n|$)',
        ]
        
        # Section headers to identify different parts
        self.section_headers = {
            'responsibilities': [
                'responsibilities', 'duties', 'what you\'ll do', 
                'you will', 'key responsibilities', 'job duties'
            ],
            'qualifications': [
                'qualifications', 'requirements', 'what we\'re looking for',
                'you have', 'must have', 'required qualifications'
            ],
            'preferred': [
                'preferred', 'nice to have', 'bonus', 'plus',
                'preferred qualifications', 'nice-to-have'
            ],
            'skills': [
                'skills', 'technical skills', 'required skills',
                'technologies', 'tech stack'
            ],
            'benefits': [
                'benefits', 'perks', 'what we offer', 'we offer',
                'compensation and benefits', 'why join us'
            ]
        }
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract job title from text"""
        lines = text.split('\n')
        
        # Try explicit patterns first
        for pattern in self.title_indicators:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                logger.debug(f"Found title via pattern: {title}")
                return title
        
        # If not found, assume first non-empty line is the title
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 100:  # Reasonable title length
                logger.debug(f"Using first line as title: {line}")
                return line
        
        return None
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text"""
        for pattern in self.company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                logger.debug(f"Found company: {company}")
                return company
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location from text"""
        for pattern in self.location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                logger.debug(f"Found location: {location}")
                return location
        return None
    
    def _extract_job_type(self, text: str) -> Optional[str]:
        """Extract job type (full-time, part-time, etc.)"""
        for pattern in self.job_type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                job_type = match.group(1).strip()
                logger.debug(f"Found job type: {job_type}")
                return job_type
        return None
    
    def _extract_experience(self, text: str) -> Optional[str]:
        """Extract experience requirements"""
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                experience = match.group(0).strip()
                logger.debug(f"Found experience requirement: {experience}")
                return experience
        return None
    
    def _extract_education(self, text: str) -> Optional[str]:
        """Extract education requirements"""
        for pattern in self.education_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education = match.group(0).strip()
                logger.debug(f"Found education requirement: {education}")
                return education
        return None
    
    def _extract_salary(self, text: str) -> Optional[str]:
        """Extract salary information"""
        for pattern in self.salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary = match.group(0).strip()
                logger.debug(f"Found salary: {salary}")
                return salary
        return None
    
    def _find_section_start(self, lines: List[str], keywords: List[str], start_idx: int = 0) -> int:
        """Find the start index of a section based on keywords"""
        for i in range(start_idx, len(lines)):
            line_lower = lines[i].lower().strip()
            for keyword in keywords:
                if keyword in line_lower:
                    logger.debug(f"Found section '{keyword}' at line {i}")
                    return i
        return -1
    
    def _extract_bullet_points(self, lines: List[str], start_idx: int, end_idx: int) -> List[str]:
        """Extract bullet points from a section"""
        bullet_points = []
        bullet_chars = ['•', '-', '*', '○', '●', '·']
        
        for i in range(start_idx + 1, min(end_idx, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
            
            # Check if line starts with bullet or number
            starts_with_bullet = any(line.startswith(char) for char in bullet_chars)
            starts_with_number = re.match(r'^\d+[\.)]\s+', line)
            
            if starts_with_bullet or starts_with_number:
                # Remove bullet/number
                clean_line = re.sub(r'^[•\-*○●·\d+\.)]\s*', '', line).strip()
                if clean_line:
                    bullet_points.append(clean_line)
            elif line and i > start_idx + 1 and len(line) > 20:
                # Might be a continuation or non-bulleted item
                bullet_points.append(line)
        
        return bullet_points
    
    def _extract_sections(self, text: str) -> Dict[str, List[str]]:
        """Extract different sections (responsibilities, qualifications, etc.)"""
        lines = text.split('\n')
        sections = {
            'responsibilities': [],
            'qualifications': [],
            'preferred': [],
            'skills': [],
            'benefits': []
        }
        
        # Find section positions
        section_positions = {}
        for section_name, keywords in self.section_headers.items():
            pos = self._find_section_start(lines, keywords)
            if pos != -1:
                section_positions[section_name] = pos
        
        # Sort sections by position
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
        
        # Extract content for each section
        for i, (section_name, start_pos) in enumerate(sorted_sections):
            # Determine end position (start of next section or end of text)
            if i + 1 < len(sorted_sections):
                end_pos = sorted_sections[i + 1][1]
            else:
                end_pos = len(lines)
            
            # Extract bullet points
            items = self._extract_bullet_points(lines, start_pos, end_pos)
            sections[section_name] = items
            logger.debug(f"Extracted {len(items)} items for section '{section_name}'")
        
        return sections
    
    def parse(self, text: str) -> JobDescription:
        """
        Parse job description text into structured data
        
        Args:
            text: Job description text
            
        Returns:
            JobDescription object with extracted information
        """
        if not text:
            logger.warning("Empty text provided for job parsing")
            return JobDescription(raw_text="")
        
        logger.info("Parsing job description")
        
        # Extract basic information
        title = self._extract_title(text)
        company = self._extract_company(text)
        location = self._extract_location(text)
        job_type = self._extract_job_type(text)
        experience = self._extract_experience(text)
        education = self._extract_education(text)
        salary = self._extract_salary(text)
        
        # Extract sections
        sections = self._extract_sections(text)
        
        # Combine skills from different sections
        required_skills = sections['skills'] + sections['qualifications']
        preferred_skills = sections['preferred']
        
        job_desc = JobDescription(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            experience_required=experience,
            education_required=education,
            salary_range=salary,
            required_skills=required_skills[:20],  # Limit to 20 skills
            preferred_skills=preferred_skills[:10],
            responsibilities=sections['responsibilities'][:15],  # Limit to 15
            qualifications=sections['qualifications'][:15],
            benefits=sections['benefits'][:10],
            raw_text=text
        )
        
        logger.info(f"Parsed job: {title or 'Unknown'} at {company or 'Unknown company'}")
        logger.info(f"Found: {len(job_desc.required_skills)} skills, "
                   f"{len(job_desc.responsibilities)} responsibilities")
        
        return job_desc


# Convenience function for quick parsing
def parse_job_description(text: str) -> JobDescription:
    """
    Quick function to parse job description
    
    Args:
        text: Job description text
        
    Returns:
        JobDescription object
    """
    parser = JobParser()
    return parser.parse(text)
