"""
Enhanced Experience Extractor - Robust extraction of work experience
Handles multiple resume formats and edge cases
"""

import re
import logging
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import date, datetime

logger = logging.getLogger(__name__)


@dataclass
class ExperienceEntry:
    """Represents a work experience entry"""
    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = ""
    achievements: List[str] = field(default_factory=list)
    duration_months: Optional[int] = None
    raw_text: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        # Calculate duration if dates available
        if self.start_date and self.end_date:
            months = (self.end_date.year - self.start_date.year) * 12
            months += self.end_date.month - self.start_date.month
            self.duration_months = max(0, months)
        elif self.start_date and self.is_current:
            today = date.today()
            months = (today.year - self.start_date.year) * 12
            months += today.month - self.start_date.month
            self.duration_months = max(0, months)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data


class EnhancedExperienceExtractor:
    """
    Enhanced experience extractor with multiple parsing strategies
    """
    
    # Placeholder patterns to filter out (common in resume templates)
    PLACEHOLDER_PATTERNS = [
        r'^company\s*name\b',
        r'^company$',
        r'^your\s*company',
        r'^employer\s*name',
        r'^organization\s*name',
        r'^\[company\]',
        r'^\[employer\]',
        r'^xxx+',
        r'^city\s*,?\s*state$',
        r'^city\s*,?\s*st$',
        r'^location$',
        # Additional description-like patterns that shouldn't be companies
        r'\band\s+\w+\s+board\b',
        r'\bto\s+both\b',
        r'\bto\s+internal\b',
        r'\bincluding\s+but\b',
        r'^gail\s+l$',  # Common name in templates
        r'^farming\s+entity$',
        r'^meetings?$',
    ]
    
    # Common job titles
    JOB_TITLES = [
        # Engineering
        'software engineer', 'software developer', 'web developer', 'mobile developer',
        'frontend developer', 'backend developer', 'full stack developer', 'fullstack developer',
        'data engineer', 'machine learning engineer', 'ml engineer', 'ai engineer',
        'devops engineer', 'site reliability engineer', 'sre', 'cloud engineer',
        'systems engineer', 'network engineer', 'security engineer', 'qa engineer',
        'test engineer', 'automation engineer', 'embedded engineer', 'firmware engineer',
        
        # Data & Analytics
        'data scientist', 'data analyst', 'business analyst', 'research scientist',
        'research engineer', 'quantitative analyst', 'statistician',
        
        # Management & Leadership
        'engineering manager', 'technical lead', 'tech lead', 'team lead',
        'project manager', 'product manager', 'program manager', 'scrum master',
        'director', 'vp', 'vice president', 'cto', 'ceo', 'cfo', 'coo', 'cio',
        'head of engineering', 'head of product', 'chief', 'president',
        
        # Design
        'ux designer', 'ui designer', 'product designer', 'graphic designer',
        'visual designer', 'interaction designer',
        
        # Other Tech
        'consultant', 'architect', 'solutions architect', 'technical architect',
        'administrator', 'system administrator', 'database administrator', 'dba',
        
        # Entry Level
        'intern', 'internship', 'trainee', 'apprentice', 'associate', 'junior',
        'graduate', 'co-op', 'research assistant', 'teaching assistant',
        
        # Non-Tech Common
        'accountant', 'analyst', 'manager', 'coordinator', 'specialist',
        'representative', 'assistant', 'administrator', 'executive',
        'officer', 'supervisor', 'clerk', 'technician', 'operator',
        'cashier', 'receptionist', 'secretary', 'nurse', 'teacher', 'professor',
        'chef', 'cook', 'server', 'driver', 'mechanic', 'electrician',
    ]
    
    # Common company/organization indicators
    COMPANY_INDICATORS = [
        'inc', 'inc.', 'incorporated', 'corp', 'corp.', 'corporation',
        'ltd', 'ltd.', 'limited', 'llc', 'l.l.c.', 'llp', 'l.l.p.',
        'plc', 'p.l.c.', 'co', 'co.', 'company', 'companies',
        'group', 'holdings', 'partners', 'associates',
        'technologies', 'technology', 'tech', 'solutions', 'services',
        'systems', 'software', 'consulting', 'consultants',
        'university', 'college', 'institute', 'school', 'academy',
        'hospital', 'clinic', 'medical', 'health', 'healthcare',
        'bank', 'financial', 'insurance', 'capital',
        'laboratory', 'labs', 'research',
        # Government/Military organizations
        'department', 'agency', 'bureau', 'office', 'command',
        'division', 'branch', 'air force', 'army', 'navy', 'marine',
        'defense', 'federal', 'government', 'administration',
    ]
    
    # Location patterns
    LOCATION_PATTERNS = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s*([A-Z]{2})\b',  # City, ST
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s*(USA|India|UK|Canada|Australia|Germany|France)\b',  # City, Country
        r'\b([A-Z][a-z]+),?\s+([A-Z][a-z]+)\b',  # City, State/Country (full name)
    ]
    
    # Date patterns
    MONTH_NAMES = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    DATE_PATTERNS = [
        # "Jan 2020 - Present", "January 2020 - Dec 2022"
        rf'({MONTH_NAMES})\s+(\d{{4}})\s*(?:[-–—]|\bto\b)+\s*({MONTH_NAMES})?\s*(\d{{4}}|Present|Current|Now)',
        # "01/2020 - 12/2022", "1/2020 - Present"
        r'(\d{1,2})/(\d{4})\s*(?:[-–—]|\bto\b)+\s*(\d{1,2})?/?(\d{4}|Present|Current|Now)',
        # "2020 - 2022", "2020 - Present"
        r'\b(\d{4})\s*(?:[-–—]|\bto\b)+\s*(\d{4}|Present|Current|Now)\b',
        # "Since 2020", "From 2020"
        r'(?:Since|From)\s+(?:' + MONTH_NAMES + r')?\s*(\d{4})',
    ]
    
    def __init__(self):
        """Initialize the enhanced extractor"""
        self.job_title_set = set(t.lower() for t in self.JOB_TITLES)
        self.company_indicator_set = set(i.lower() for i in self.COMPANY_INDICATORS)
        self.placeholder_patterns = [re.compile(p, re.IGNORECASE) for p in self.PLACEHOLDER_PATTERNS]
    
    def _is_placeholder(self, text: str) -> bool:
        """Check if text is a placeholder (template text)"""
        text_clean = text.strip().lower()
        
        # Check against placeholder patterns
        for pattern in self.placeholder_patterns:
            if pattern.match(text_clean):
                return True
        
        # Check for common placeholder variations
        if text_clean in ['company name', 'employer name', 'organization name', 
                          'city, state', 'city, st', 'city , state', 'city , st']:
            return True
        
        # Check for "Company Name" with special characters (template markers)
        if re.match(r'^company\s*name\s*[ï¼\-–—,\|\•]', text_clean):
            return True
        
        return False
    
    def _clean_placeholder_text(self, text: str) -> str:
        """Remove placeholder patterns from text"""
        # Remove "Company Name" placeholder patterns
        text = re.sub(r'\bCompany\s+Name\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bEmployer\s+Name\b', '', text, flags=re.IGNORECASE)
        # Remove City, State placeholders
        text = re.sub(r'\bCity\s*,?\s*State\b', '', text, flags=re.IGNORECASE)
        # Clean up special unicode characters often used as separators
        text = re.sub(r'[ï¼​]+', '-', text)  # Replace unicode dash variations
        # Clean up multiple spaces and leading/trailing
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.strip(' -–—,|•')
        return text
        
    def extract_from_section(self, section_text: str, known_companies: List[str] = None) -> List[ExperienceEntry]:
        """
        Extract experience entries from an experience section
        
        Args:
            section_text: Text from experience section
            known_companies: List of company names from NER
            
        Returns:
            List of ExperienceEntry objects
        """
        if not section_text or len(section_text.strip()) < 20:
            return []
        
        # Split into blocks
        blocks = self._split_into_blocks(section_text)
        
        entries = []
        for block in blocks:
            entry = self._parse_experience_block(block, known_companies)
            if entry and self._validate_entry(entry):
                entries.append(entry)
        
        return entries
    
    def _split_into_blocks(self, text: str) -> List[str]:
        """Split experience section into individual job blocks"""
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Strategy 1: Split by blank lines (most common)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Group paragraphs that belong together (based on context)
        blocks = []
        current_block = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if this paragraph starts a new job entry
            # Indicators: starts with company name, job title, or date
            is_new_entry = False
            
            # Check for date at start
            if re.match(rf'^(?:{self.MONTH_NAMES}|\d{{1,2}}/)\s*\d{{4}}', para, re.IGNORECASE):
                is_new_entry = True
            
            # Check for job title pattern at start
            first_line = para.split('\n')[0].lower()
            if any(title in first_line for title in self.JOB_TITLES[:30]):
                is_new_entry = True
            
            # Check for company indicator at start  
            if any(ind in first_line for ind in ['inc', 'corp', 'ltd', 'llc', 'university', 'institute']):
                is_new_entry = True
            
            # Check for all-caps line at start (often job titles or company names)
            first_line_orig = para.split('\n')[0].strip()
            if first_line_orig and len(first_line_orig) < 60 and first_line_orig == first_line_orig.upper() and ' ' in first_line_orig:
                is_new_entry = True
            
            if is_new_entry and current_block:
                # Save previous block
                block_text = '\n\n'.join(current_block)
                if len(block_text) > 30:
                    blocks.append(block_text)
                current_block = [para]
            else:
                current_block.append(para)
        
        # Don't forget the last block
        if current_block:
            block_text = '\n\n'.join(current_block)
            if len(block_text) > 30:
                blocks.append(block_text)
        
        # If we only got one block but text is long, try more aggressive splitting
        if len(blocks) <= 1 and len(text) > 500:
            # Try splitting by date ranges anywhere in lines
            date_range_pattern = rf'\n(?=.*?{self.MONTH_NAMES}\s+\d{{4}}\s*(?:[-–—]|\bto\b)+)'
            split_blocks = re.split(date_range_pattern, text, flags=re.IGNORECASE)
            if len(split_blocks) > 1:
                blocks = [b.strip() for b in split_blocks if len(b.strip()) > 30]
        
        return blocks if blocks else [text.strip()]
    
    def _parse_experience_block(self, block: str, known_companies: List[str] = None) -> Optional[ExperienceEntry]:
        """Parse a single experience block"""
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            return None
        
        # Extract components
        title = self._extract_title(block, lines)
        company = self._extract_company(block, lines, known_companies)
        location = self._extract_location(block)
        start_date, end_date, is_current = self._extract_dates(block)
        achievements = self._extract_achievements(block)
        
        # Calculate confidence
        confidence = self._calculate_confidence(title, company, start_date, achievements)
        
        return ExperienceEntry(
            title=title or "Unknown Position",
            company=company or "Unknown Company",
            location=location,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            description=block[:500],
            achievements=achievements,
            raw_text=block,
            confidence=confidence
        )
    
    def _extract_title(self, block: str, lines: List[str]) -> Optional[str]:
        """Extract job title from block"""
        
        # First, clean placeholder text from block
        clean_block = self._clean_placeholder_text(block)
        clean_lines = [self._clean_placeholder_text(l) for l in lines if l.strip()]
        clean_lines = [l for l in clean_lines if l]  # Remove empty after cleaning
        
        # Strategy 0: Look for "Title – Company" pattern (common in modern resumes)
        for line in lines[:10]:
            line_clean = line.strip()
            # Pattern: "Title – Company" or "Title - Company"
            match = re.match(r'^([A-Za-z][A-Za-z\s]+(?:Intern|Engineer|Developer|Manager|Analyst|Designer|Director|Lead|Specialist|Coordinator|Consultant|Associate|Assistant))\s*[–—-]\s*', line_clean, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Strategy 1: Check first few lines for job title patterns
        for line in clean_lines[:5]:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            # Skip lines that are clearly not titles
            if len(line_clean) > 100:
                continue
            
            # Skip phone numbers
            if re.match(r'^[\+\d\s\-\(\)]+$', line_clean):
                continue
            
            # Check if line has dates - common format: "Title Dates" or "Company Dates Title"
            if re.search(r'\b(19|20)\d{2}\b', line_clean):
                # Try to extract title from around the dates
                # Pattern: dates followed by title
                match = re.search(r'(?:to|[-–—])\s*((?:19|20)\d{2})\s+([A-Za-z][A-Za-z\s]+?)$', line_clean)
                if match:
                    potential_title = match.group(2).strip()
                    if len(potential_title) > 3 and self._is_likely_title(potential_title):
                        return potential_title
                
                # Pattern: title before dates
                parts = re.split(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2}/)\s*\d{4}', line_clean, flags=re.IGNORECASE)
                if parts and len(parts[0].strip()) > 3:
                    potential_title = parts[0].strip().strip(',-–—|')
                    if self._is_likely_title(potential_title):
                        return potential_title
                continue
            
            # Skip lines that look like company names (have company indicators)
            if any(ind in line_lower for ind in ['inc.', 'corp.', 'ltd.', 'llc', 'university', 'institute', 'hospital', 'company']):
                continue
            
            # Skip location-only lines
            if re.match(r'^[A-Z][a-z]+,?\s*[A-Z]{2}$', line_clean):  # City, ST format
                continue
            
            # Check for known job title keywords
            if self._is_likely_title(line_clean):
                # Clean any remaining placeholder patterns and return
                cleaned = self._clean_placeholder_text(line_clean)
                if cleaned and len(cleaned) > 2:
                    return cleaned
                return line_clean
        
        # Strategy 2: Search for known job titles in first half of the text
        search_text = '\n'.join(clean_lines[:min(10, len(clean_lines))])  # Only search first 10 lines
        for title in self.JOB_TITLES:
            pattern = rf'\b({re.escape(title)})\b'
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                # Find the full line containing this title
                start_pos = match.start()
                line_start = search_text.rfind('\n', 0, start_pos)
                line_start = 0 if line_start == -1 else line_start + 1
                line_end = search_text.find('\n', match.end())
                line_end = len(search_text) if line_end == -1 else line_end
                
                full_line = search_text[line_start:line_end].strip()
                
                # Remove dates from the line
                full_line = re.sub(rf'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{{4}}', '', full_line, flags=re.IGNORECASE)
                full_line = re.sub(r'\b(19|20)\d{2}\b', '', full_line)
                full_line = re.sub(r'\s*(?:[-–—]|\bto\b)+\s*(Present|Current|Now)?\s*', ' ', full_line, flags=re.IGNORECASE)
                full_line = re.sub(r'\s+', ' ', full_line).strip()
                
                # Clean placeholder text
                full_line = self._clean_placeholder_text(full_line)
                
                # If result is reasonable, return it
                if full_line and 3 < len(full_line) < 70:
                    return full_line
                else:
                    # Just return the matched title
                    return match.group(1).title()
        
        return None
    
    def _is_likely_title(self, text: str) -> bool:
        """Check if text is likely a job title"""
        text_lower = text.lower().strip()
        
        # Reject placeholder patterns
        if self._is_placeholder(text):
            return False
        
        # Check length
        if len(text_lower) < 3 or len(text_lower) > 80:
            return False
        
        # Reject if it looks like a description (starts with a verb or has too many words)
        description_starters = ['reconciled', 'maintained', 'managed', 'prepared', 'performed',
                               'responsible', 'developed', 'created', 'processed', 'analyzed',
                               'reviewed', 'supported', 'assisted', 'provided', 'ensured',
                               'in this', 'experience in', 'worked with', 'worked on',
                               'collaborated', 'implemented', 'designed', 'built', 'handled',
                               'to both', 'internal', 'external', 'customer', 'client']
        if any(text_lower.startswith(word) for word in description_starters):
            return False
        
        # Reject if it ends with action words (likely a description sentence)
        description_enders = ['meetings.', 'reports.', 'systems.', 'processes.', 'clients.',
                             'customers.', 'prospects.', 'staff.', 'team.', 'role.']
        if any(text_lower.endswith(word) for word in description_enders):
            return False
        
        # Reject if it has too many words (likely a sentence)
        if len(text_lower.split()) > 8:
            return False
        
        # Check for job title keywords
        title_keywords = ['engineer', 'developer', 'manager', 'analyst', 'scientist',
                         'architect', 'designer', 'consultant', 'specialist', 'coordinator',
                         'director', 'lead', 'head', 'chief', 'officer', 'president',
                         'intern', 'assistant', 'associate', 'administrator', 'technician',
                         'accountant', 'supervisor', 'executive', 'representative']
        
        if any(kw in text_lower for kw in title_keywords):
            return True
        
        # Check if mostly capitalized (all-caps titles are common)
        if text == text.upper() and len(text.split()) <= 6:
            return True
        
        return False
    
    def _expand_title_simple(self, block: str, start: int, end: int) -> str:
        """Get a clean title from the matched position"""
        # Common prefixes to include
        prefixes = ['senior', 'junior', 'lead', 'principal', 'staff', 'chief', 
                    'associate', 'assistant', 'head', 'vp', 'vice']
        
        # Find line containing the match
        line_start = block.rfind('\n', 0, start)
        line_start = 0 if line_start == -1 else line_start + 1
        line_end = block.find('\n', end)
        line_end = len(block) if line_end == -1 else line_end
        
        title_line = block[line_start:line_end].strip()
        
        # Clean the line
        title_line = re.sub(rf'\b{self.MONTH_NAMES}\s+\d{{4}}', '', title_line, flags=re.IGNORECASE)
        title_line = re.sub(r'\b(19|20)\d{2}\b', '', title_line)
        title_line = re.sub(r'\s*[-–—to|]+\s*', ' ', title_line)
        title_line = re.sub(r'\s+', ' ', title_line).strip()
        
        return title_line if len(title_line) < 70 else block[start:end].title()
    
    def _extract_company(self, block: str, lines: List[str], known_companies: List[str] = None) -> Optional[str]:
        """Extract company name from block"""
        
        # Strategy 0: Look for "Title – Company (Abbrev)" pattern
        for line in lines[:10]:
            line_clean = line.strip()
            # Pattern: "Title – Company Name" or "Title – Company (ABBREV)"
            match = re.search(r'[–—-]\s*([A-Z][A-Za-z\s]+(?:\([A-Z]+\))?)\s*[,\n]?$', line_clean)
            if match:
                company = match.group(1).strip().rstrip(',')
                if len(company) > 3 and not self._is_likely_title(company):
                    return company
            # Also check standalone company line with abbreviation: "Company Name (ABBREV)"
            match = re.match(r'^([A-Z][A-Za-z\s]+)\s*\(([A-Z]{2,6})\)\s*$', line_clean)
            if match:
                return f"{match.group(1).strip()} ({match.group(2)})"
        
        # Pre-processing: Check for specific format "Company Name [Date to Date] Title"
        # This is a common template format where "Company Name" is literally the placeholder
        company_date_pattern = rf'Company\s+Name\s+(?:{self.MONTH_NAMES}|\d{{1,2}}/)\s*\d{{4}}'
        if re.search(company_date_pattern, block, re.IGNORECASE):
            # This resume uses "Company Name" as a placeholder - look for real org names
            # Strategy: Look for organization names with parenthetical abbreviations like "Enterprise Resource Planning Office (ERO)"
            paren_org_pattern = r'([A-Z][A-Za-z\s]+(?:Office|Department|Division|Center|Bureau|Agency|System|Service))\s*\(([A-Z]+)\)'
            for line in lines[:15]:
                match = re.search(paren_org_pattern, line.strip())
                if match:
                    org_name = f"{match.group(1).strip()} ({match.group(2)})"
                    return org_name
            
            # Also try to find organization names with indicators
            for line in lines[:10]:
                line_clean = line.strip()
                if re.search(r'\b(?:Inc\.|Corp\.|LLC|Ltd\.|Hospital|University|College|Bank|Group|Institute)\b', line_clean, re.IGNORECASE):
                    if not self._is_placeholder(line_clean):
                        company = self._clean_company_name(line_clean)
                        if company and len(company) > 3:
                            return company
        
        # Strategy 1: Use known companies from NER (if they're real companies, not placeholders)
        if known_companies:
            block_lower = block.lower()
            for company in known_companies:
                # Skip placeholder company names
                if self._is_placeholder(company):
                    continue
                # Validate by cleaning - if it returns empty, it's not a real company
                cleaned = self._clean_company_name(company)
                if not cleaned:
                    continue
                if company.lower() in block_lower:
                    return company
        
        # Strategy 2: Look for "at Company" pattern
        at_pattern = r'\bat\s+([A-Z][A-Za-z\s&,.\'-]+?)(?:\s*[,\n]|\s+(?:in|from|\d|' + self.MONTH_NAMES + '))'
        match = re.search(at_pattern, block, re.IGNORECASE)
        if match:
            company = self._clean_company_name(match.group(1))
            if company and len(company) > 2 and not self._is_likely_title(company) and not self._is_placeholder(company):
                return company
        
        # Strategy 3: Look for organization names in parentheses (like "Enterprise Resource Planning Office (ERO)")
        for line in lines[:10]:
            line_stripped = line.strip()
            # Skip lines that start with first-person descriptions
            if line_stripped.lower().startswith('i '):
                continue
            
            if '(' in line and ')' in line:
                # Organization name with abbreviation - broader pattern
                paren_org_pattern = r'([A-Z][A-Za-z\s]+(?:Office|Department|Division|Center|Bureau|Agency|System|Service|Organization|Program))\s*\(([A-Z]{2,6})\)'
                match = re.search(paren_org_pattern, line_stripped)
                if match:
                    org_name = f"{match.group(1).strip()} ({match.group(2)})"
                    # Validate it's not a description
                    if not self._clean_company_name(org_name) == '':
                        return org_name
                
                # General org pattern
                match = re.match(r'([A-Z][A-Za-z\s]+)\s*\([A-Z]+\)', line_stripped)
                if match:
                    company = self._clean_company_name(match.group(0))
                    if company and len(company) > 5 and not self._is_placeholder(company):
                        return company
        
        # Strategy 4: Look for lines with company indicators
        for line in lines[:7]:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            # Skip placeholder patterns
            if self._is_placeholder(line_clean):
                continue
            
            # Check for company indicators
            for indicator in ['inc.', 'inc', 'corp.', 'corp', 'ltd.', 'ltd', 'llc', 
                             'l.l.c', 'technologies', 'solutions', 
                             'university', 'institute', 'hospital', 'bank', 'group']:
                if indicator in line_lower:
                    company = self._clean_company_name(line_clean)
                    if company and len(company) > 2:
                        return company
        
        # Strategy 4: Look for capitalized company-like names
        # Usually company names appear in first few lines
        for line in lines[:5]:
            line_clean = line.strip()
            
            # Skip placeholder patterns
            if self._is_placeholder(line_clean):
                continue
            
            # Skip if it has dates
            if re.search(r'\b(19|20)\d{2}\b', line_clean):
                continue
            
            # Skip if it looks like a job title
            if self._is_likely_title(line_clean):
                continue
            
            # Skip single words
            words = line_clean.split()
            if len(words) < 2 or len(words) > 8:
                continue
            
            # Check if it looks like a company name (mostly capitalized)
            if len(line_clean) < 60:
                cap_count = sum(1 for w in words if w and w[0].isupper())
                if cap_count >= len(words) * 0.6:
                    company = self._clean_company_name(line_clean)
                    if company and len(company) > 3 and not self._is_placeholder(company):
                        return company
        
        # Strategy 5: Look for "Company Name | Location" pattern
        pipe_pattern = r'^([A-Z][A-Za-z\s&,.\'-]+?)\s*[|•]\s*[A-Z]'
        for line in lines[:5]:
            match = re.match(pipe_pattern, line.strip())
            if match:
                company = self._clean_company_name(match.group(1))
                if company and len(company) > 2 and not self._is_placeholder(company):
                    return company
        
        return None
    
    def _clean_company_name(self, text: str) -> str:
        """Clean up company name text"""
        # First remove placeholder patterns
        text = self._clean_placeholder_text(text)
        # Remove common prefixes/suffixes
        text = re.sub(r'^[\-–—•*\s]+', '', text)
        text = re.sub(r'[\-–—•*\s]+$', '', text)
        # Remove dates
        text = re.sub(r'\b\d{4}\b', '', text)
        text = re.sub(rf'\b{self.MONTH_NAMES}\b', '', text, flags=re.IGNORECASE)
        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.strip(',-–—.')
        
        # Filter out text that looks like descriptions (has too many common verbs/action words)
        text_lower = text.lower()
        
        # Reject if it starts with "I " (first person descriptions)
        if text_lower.startswith('i ') or text_lower.startswith('i\n'):
            return ''
        
        # Reject if text starts with common description words
        description_starters = ['i monitored', 'i orchestrated', 'i managed', 'i developed',
                               'that time', 'each base', 'during this', 'at this time',
                               'in this position', 'while working', 'when i']
        if any(text_lower.startswith(word) for word in description_starters):
            return ''
        
        description_words = ['reconciled', 'maintained', 'managed', 'prepared', 'performed', 
                             'responsible', 'developed', 'created', 'coordinated', 'processed',
                             'analyzed', 'reviewed', 'supported', 'assisted', 'provided',
                             'ensured', 'including', 'such as', 'limited to', 'accordance',
                             'reconciliation', 'coordination', 'coordinate', 'ensure',
                             'customer service', 'financial reporting', 'bank reconciliation',
                             'quality control', 'product development', 'human resources',
                             'all times', 'contracts', 'record', 'coach', 'state company',
                             'annual and monthly', 'board meetings', 'farming entity',
                             'internal and external', 'to both', 'prospects', 'clients',
                             'responsible for', 'in charge of', 'duties include',
                             'monitored the', 'orchestrated the', 'transition of']
        if any(word in text_lower for word in description_words):
            return ''  # This is a description, not a company name
        
        # Filter out text that's too long (likely a description)
        if len(text) > 60:
            return ''
        
        # Filter out single generic words that are not company names
        single_word_non_companies = ['coordinated', 'coordinate', 'record', 'coach', 'contracts']
        if text_lower in single_word_non_companies:
            return ''
        
        return text
    
    def _extract_location(self, block: str) -> Optional[str]:
        """Extract location from block"""
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, block)
            if match:
                groups = [g for g in match.groups() if g]
                return ', '.join(groups)
        return None
    
    def _extract_dates(self, block: str) -> Tuple[Optional[date], Optional[date], bool]:
        """Extract start date, end date, and whether position is current"""
        is_current = bool(re.search(r'\b(Present|Current|Now|Ongoing)\b', block, re.IGNORECASE))
        
        # Month name to number mapping
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
            'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
        }
        
        start_date = None
        end_date = None
        
        # Pattern 1: "Month Year - Month Year" or "Month Year - Present"
        pattern1 = rf'({self.MONTH_NAMES})\s+(\d{{4}})\s*(?:[-–—]|\bto\b)+\s*(?:({self.MONTH_NAMES})\s+)?(\d{{4}}|Present|Current|Now)'
        match = re.search(pattern1, block, re.IGNORECASE)
        if match:
            start_month = month_map.get(match.group(1).lower()[:3], 1)
            start_year = int(match.group(2))
            start_date = date(start_year, start_month, 1)
            
            if match.group(4) and match.group(4).isdigit():
                end_month = month_map.get(match.group(3).lower()[:3], 12) if match.group(3) else 12
                end_year = int(match.group(4))
                end_date = date(end_year, end_month, 28)
            elif is_current:
                end_date = date.today()
            
            return start_date, end_date, is_current
        
        # Pattern 2: "MM/YYYY - MM/YYYY"
        pattern2 = r'(\d{1,2})/(\d{4})\s*(?:[-–—]|\bto\b)+\s*(\d{1,2})?/?(\d{4}|Present|Current|Now)'
        match = re.search(pattern2, block, re.IGNORECASE)
        if match:
            start_month = int(match.group(1))
            start_year = int(match.group(2))
            if 1 <= start_month <= 12 and 1900 <= start_year <= 2100:
                start_date = date(start_year, start_month, 1)
                
                if match.group(4) and match.group(4).isdigit():
                    end_month = int(match.group(3)) if match.group(3) else 12
                    end_year = int(match.group(4))
                    if 1 <= end_month <= 12 and 1900 <= end_year <= 2100:
                        end_date = date(end_year, end_month, 28)
                elif is_current:
                    end_date = date.today()
            
            return start_date, end_date, is_current
        
        # Pattern 3: "YYYY - YYYY"
        pattern3 = r'\b(\d{4})\s*(?:[-–—]|\bto\b)+\s*(\d{4}|Present|Current|Now)\b'
        match = re.search(pattern3, block, re.IGNORECASE)
        if match:
            start_year = int(match.group(1))
            if 1900 <= start_year <= 2100:
                start_date = date(start_year, 1, 1)
                
                if match.group(2).isdigit():
                    end_year = int(match.group(2))
                    if 1900 <= end_year <= 2100:
                        end_date = date(end_year, 12, 28)
                elif is_current:
                    end_date = date.today()
            
            return start_date, end_date, is_current
        
        return start_date, end_date, is_current
    
    def _extract_achievements(self, block: str) -> List[str]:
        """Extract bullet points and achievements"""
        achievements = []
        
        bullet_patterns = [
            r'^[\s]*[•●○▪▫■□◦◘◙‣⁃⦾⦿]+\s*(.+)$',
            r'^[\s]*[-–—]\s+(.+)$',
            r'^[\s]*\*\s+(.+)$',
            r'^[\s]*\d+[\.)]\s*(.+)$',
        ]
        
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) < 15:
                continue
            
            for pattern in bullet_patterns:
                match = re.match(pattern, line)
                if match:
                    text = match.group(1).strip()
                    if len(text) > 15:
                        achievements.append(text)
                    break
        
        return achievements[:10]  # Limit to 10 achievements
    
    def _calculate_confidence(self, title: Optional[str], company: Optional[str], 
                             start_date: Optional[date], achievements: List[str]) -> float:
        """Calculate confidence score for the extraction"""
        score = 0.0
        
        if title and title != "Unknown Position":
            score += 0.3
            # Bonus for matching known job titles
            if any(t in title.lower() for t in self.JOB_TITLES):
                score += 0.1
        
        if company and company != "Unknown Company":
            score += 0.25
            # Bonus for having company indicator
            if any(ind in company.lower() for ind in self.company_indicator_set):
                score += 0.05
        
        if start_date:
            score += 0.2
        
        if achievements:
            score += min(0.1 * len(achievements), 0.2)
        
        return min(score, 1.0)
    
    def _validate_entry(self, entry: ExperienceEntry) -> bool:
        """Validate if an entry is valid enough to include"""
        # Must have either a real title or company
        has_title = entry.title and entry.title != "Unknown Position"
        has_company = entry.company and entry.company != "Unknown Company"
        
        if not has_title and not has_company:
            return False
        
        # Confidence threshold
        if entry.confidence < 0.2:
            return False
        
        return True


def test_enhanced_extractor():
    """Test the enhanced experience extractor"""
    extractor = EnhancedExperienceExtractor()
    
    test_cases = [
        """Company Name July 2011 to November 2012 Accountant
City , State
Enterprise Resource Planning Office (ERO)
In this position as an Accountant I was responsible for identifying and resolving issues.
- Worked with teammates to resolve daily challenges
- Implemented new accounting procedures""",
        
        """Senior Software Engineer
Google Inc. | Mountain View, CA
January 2020 - Present

• Led development of microservices architecture
• Managed team of 5 engineers
• Reduced latency by 40%""",
        
        """ABC Corporation
Software Developer
May 2018 - December 2019
New York, NY

Developed web applications using React and Node.js
* Built REST APIs serving 1M+ requests/day
* Implemented CI/CD pipeline with Jenkins""",
        
        """Research Intern at Indian Statistical Institute
Kolkata, India
Jun 2024 - Aug 2024
- Conducted research on machine learning algorithms
- Published paper at IEEE conference""",
    ]
    
    print("=" * 70)
    print("ENHANCED EXPERIENCE EXTRACTOR TEST")
    print("=" * 70)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST CASE {i}")
        print("=" * 70)
        print(f"Input:\n{test_text[:200]}...")
        
        entries = extractor.extract_from_section(test_text)
        
        print(f"\nExtracted {len(entries)} entries:")
        for j, entry in enumerate(entries, 1):
            print(f"\n  Entry {j} (confidence: {entry.confidence:.2f}):")
            print(f"    Title: {entry.title}")
            print(f"    Company: {entry.company}")
            print(f"    Location: {entry.location}")
            print(f"    Dates: {entry.start_date} - {entry.end_date}")
            print(f"    Current: {entry.is_current}")
            print(f"    Duration: {entry.duration_months} months")
            print(f"    Achievements: {len(entry.achievements)}")
            for ach in entry.achievements[:3]:
                print(f"      - {ach[:60]}...")


if __name__ == "__main__":
    test_enhanced_extractor()
