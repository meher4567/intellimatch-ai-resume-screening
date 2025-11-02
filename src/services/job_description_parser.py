"""
Job Description Parser
Extracts structured information from job postings
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import re
from datetime import datetime


@dataclass
class JobDescription:
    """Structured job description data"""
    job_id: str
    title: str
    company: str
    location: Optional[str] = None
    remote_policy: str = "onsite"  # remote/hybrid/onsite/flexible
    description: str = ""
    responsibilities: List[str] = None
    required_skills: List[str] = None
    optional_skills: List[str] = None
    required_experience_years: Optional[int] = None
    experience_level: str = "mid"  # entry/junior/mid/senior/lead/executive
    education_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    benefits: List[str] = None
    posted_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.responsibilities is None:
            self.responsibilities = []
        if self.required_skills is None:
            self.required_skills = []
        if self.optional_skills is None:
            self.optional_skills = []
        if self.benefits is None:
            self.benefits = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.posted_date:
            data['posted_date'] = self.posted_date.isoformat()
        return data


class JobDescriptionParser:
    """Parse job descriptions to extract structured information"""
    
    def __init__(self):
        # Common section headers
        self.section_patterns = {
            'responsibilities': [
                r'(?:responsibilities|duties|what you[\'ll]? do|role description|day[- ]to[- ]day)',
                r'(?:you will|your role)'
            ],
            'requirements': [
                r'(?:requirements|qualifications|what we[\'re]? looking for|must have)',
                r'(?:skills? (?:and|&) qualifications?|required skills?)'
            ],
            'nice_to_have': [
                r'(?:nice[- ]to[- ]have|preferred|bonus|plus|optional)',
                r'(?:we[\'d]? love if you|ideal candidate)'
            ],
            'benefits': [
                r'(?:benefits|perks|what we offer|compensation)',
                r'(?:why join us|package)'
            ]
        }
        
        # Experience level indicators
        self.experience_levels = {
            'entry': ['entry', 'junior', 'graduate', 'fresh', 'beginner', '0-2 years', '0-1 year'],
            'junior': ['junior', '1-3 years', '1-2 years'],
            'mid': ['mid', 'intermediate', '3-5 years', '2-5 years'],
            'senior': ['senior', 'lead', '5+ years', '5-8 years', 'experienced'],
            'lead': ['lead', 'principal', 'staff', '8+ years'],
            'executive': ['executive', 'director', 'vp', 'head of', 'chief']
        }
        
        # Remote policy indicators
        self.remote_indicators = {
            'remote': ['remote', 'work from home', 'wfh', 'fully remote', '100% remote'],
            'hybrid': ['hybrid', 'flexible', 'remote-friendly', 'partial remote'],
            'onsite': ['onsite', 'on-site', 'in-office', 'office-based']
        }
    
    def parse(self, job_text: str, job_id: str = None, 
              title: str = None, company: str = None) -> JobDescription:
        """
        Parse job description text into structured format
        
        Args:
            job_text: Full job description text
            job_id: Optional job ID (generated if not provided)
            title: Optional job title (extracted if not provided)
            company: Optional company name (extracted if not provided)
            
        Returns:
            JobDescription object with extracted fields
        """
        if not job_id:
            job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract title if not provided
        if not title:
            title = self._extract_title(job_text)
        
        # Extract company if not provided
        if not company:
            company = self._extract_company(job_text)
        
        # Extract location and remote policy
        location, remote_policy = self._extract_location_and_remote(job_text)
        
        # Extract sections
        sections = self._split_into_sections(job_text)
        
        # Extract responsibilities
        responsibilities = self._extract_responsibilities(sections, job_text)
        
        # Extract skills (required and optional)
        required_skills, optional_skills = self._extract_skills(sections, job_text)
        
        # Extract experience requirements
        experience_years, experience_level = self._extract_experience(job_text)
        
        # Extract education requirements
        education_level = self._extract_education(job_text)
        
        # Extract salary
        salary_min, salary_max = self._extract_salary(job_text)
        
        # Extract benefits
        benefits = self._extract_benefits(sections, job_text)
        
        return JobDescription(
            job_id=job_id,
            title=title,
            company=company,
            location=location,
            remote_policy=remote_policy,
            description=job_text,
            responsibilities=responsibilities,
            required_skills=required_skills,
            optional_skills=optional_skills,
            required_experience_years=experience_years,
            experience_level=experience_level,
            education_level=education_level,
            salary_min=salary_min,
            salary_max=salary_max,
            benefits=benefits,
            posted_date=datetime.now()
        )
    
    def _extract_title(self, text: str) -> str:
        """Extract job title from text"""
        # Look for common title patterns in first few lines
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Skip empty lines and very long lines
            if not line or len(line) > 100:
                continue
            # Check if line looks like a title
            if any(keyword in line.lower() for keyword in ['engineer', 'developer', 'scientist', 'manager', 'analyst']):
                return line
        
        # Fallback: return first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()
        
        return "Unknown Position"
    
    def _extract_company(self, text: str) -> str:
        """Extract company name from text"""
        # Look for "Company:", "About us:", etc.
        patterns = [
            r'(?:Company|Organization|About us):?\s*([A-Z][A-Za-z0-9\s&,.-]+)',
            r'Join\s+([A-Z][A-Za-z0-9\s&,.-]+)',
            r'([A-Z][A-Za-z0-9\s&,.-]+)\s+is (?:hiring|looking for|seeking)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Company"
    
    def _extract_location_and_remote(self, text: str) -> tuple:
        """Extract location and remote policy"""
        location = None
        remote_policy = "onsite"  # default
        
        # Check for remote indicators first
        text_lower = text.lower()
        for policy, indicators in self.remote_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                remote_policy = policy
                break
        
        # Extract location (city, state, country)
        location_patterns = [
            r'Location:?\s*([A-Za-z\s,]+(?:, [A-Z]{2})?)',
            r'(?:in|at)\s+([A-Z][a-z]+,?\s+[A-Z]{2})',  # City, ST
            r'(?:in|at)\s+([A-Z][a-z]+,?\s+[A-Z][a-z]+)',  # City, Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                break
        
        return location, remote_policy
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split job description into sections"""
        sections = {}
        current_section = 'description'
        current_content = []
        
        for line in text.split('\n'):
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            found_section = False
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line_lower):
                        # Save previous section
                        if current_content:
                            sections[current_section] = '\n'.join(current_content)
                        # Start new section
                        current_section = section_name
                        current_content = []
                        found_section = True
                        break
                if found_section:
                    break
            
            if not found_section:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_responsibilities(self, sections: Dict[str, str], full_text: str) -> List[str]:
        """Extract job responsibilities as list"""
        # Look in responsibilities section first
        text = sections.get('responsibilities', full_text)
        
        # Extract bullet points or numbered lists
        bullets = []
        
        # Match bullet points (•, -, *, numbers)
        bullet_patterns = [
            r'[•\-\*]\s*(.+)',
            r'\d+\.\s*(.+)',
            r'[▪▫⚫]\s*(.+)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text)
            if matches:
                bullets.extend([m.strip() for m in matches])
        
        # If no bullets found, split by periods for sentences
        if not bullets:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
            bullets = sentences[:10]  # Limit to 10 responsibilities
        
        return bullets[:15]  # Max 15 responsibilities
    
    def _extract_skills(self, sections: Dict[str, str], full_text: str) -> tuple:
        """Extract required and optional skills"""
        # Get requirements and nice-to-have sections
        requirements_text = sections.get('requirements', full_text)
        optional_text = sections.get('nice_to_have', '')
        
        # Comprehensive skill list
        known_skills = [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 
            'Swift', 'Kotlin', 'PHP', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash',
            # Web Frameworks
            'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Spring Boot', 
            'Node.js', 'Express', 'FastAPI', 'Laravel', 'Rails', 'ASP.NET', 'Next.js',
            # Databases
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
            'DynamoDB', 'SQL Server', 'Oracle', 'SQLite', 'Neo4j', 'MariaDB',
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub',
            'GitLab', 'CircleCI', 'Terraform', 'Ansible', 'Chef', 'Puppet', 'Linux',
            # Data & ML
            'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'TensorFlow',
            'PyTorch', 'scikit-learn', 'Pandas', 'NumPy', 'Spark', 'Hadoop', 'Kafka',
            # Other Tools
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'CI/CD', 'ETL',
            'API', 'NoSQL', 'SQL', 'HTML', 'CSS', 'SASS', 'webpack', 'npm', 'yarn'
        ]
        
        required_skills = set()
        optional_skills = set()
        
        # Extract from requirements section
        requirements_lower = requirements_text.lower()
        for skill in known_skills:
            # Create regex pattern for word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, requirements_lower):
                required_skills.add(skill)
        
        # Extract from optional section
        if optional_text:
            optional_lower = optional_text.lower()
            for skill in known_skills:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, optional_lower):
                    optional_skills.add(skill)
        
        # Remove optional from required
        required_skills = required_skills - optional_skills
        
        return sorted(list(required_skills)), sorted(list(optional_skills))
    
    def _extract_experience(self, text: str) -> tuple:
        """Extract experience years and level"""
        # Look for experience patterns
        exp_patterns = [
            r'(\d+)\+\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'(\d+)-(\d+)\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'(?:minimum|at least)\s+(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s+(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)',
        ]
        
        experience_years = None
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # If range (e.g., 3-5 years), take the minimum
                experience_years = int(match.group(1))
                break
        
        # Detect experience level from text - check title first
        text_lower = text.lower()
        experience_level = 'mid'  # default
        
        # Check title/heading first for level indicators
        title_section = text[:200].lower()
        
        # Priority order: check specific levels
        if any(keyword in title_section for keyword in ['senior', 'sr.', 'lead', '5+ years', '5-8 years']):
            experience_level = 'senior'
        elif any(keyword in title_section for keyword in ['junior', 'jr.', 'entry', '1-3 years', '0-2 years']):
            experience_level = 'junior'
        elif any(keyword in title_section for keyword in ['principal', 'staff', '8+ years', 'lead']):
            experience_level = 'lead'
        elif any(keyword in title_section for keyword in ['executive', 'director', 'vp', 'chief', 'head of']):
            experience_level = 'executive'
        elif any(keyword in title_section for keyword in ['mid', 'intermediate', '3-5 years']):
            experience_level = 'mid'
        else:
            # Check full text
            for level, keywords in self.experience_levels.items():
                if any(keyword in text_lower for keyword in keywords):
                    experience_level = level
                    break
        
        return experience_years, experience_level
    
    def _extract_education(self, text: str) -> Optional[str]:
        """Extract education requirements"""
        education_patterns = [
            r"(PhD|Ph\.D\.|Doctorate|Doctoral)",
            r"(Master'?s?|MS|M\.S\.|MBA|M\.B\.A\.)",
            r"(Bachelor'?s?|BS|B\.S\.|BA|B\.A\.)",
            r"(Associate'?s?|AS|A\.S\.)"
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                degree = match.group(1)
                # Normalize
                if 'phd' in degree.lower() or 'doctor' in degree.lower():
                    return "PhD"
                elif 'master' in degree.lower() or 'mba' in degree.lower():
                    return "Master's"
                elif 'bachelor' in degree.lower():
                    return "Bachelor's"
                elif 'associate' in degree.lower():
                    return "Associate's"
        
        return None
    
    def _extract_salary(self, text: str) -> tuple:
        """Extract salary range"""
        # Patterns for salary (support $, k, K, USD, etc.)
        salary_patterns = [
            r'\$(\d{2,3})[kK]\s*-\s*\$(\d{2,3})[kK]',  # $100k - $150k
            r'\$(\d+),?(\d{3})\s*-\s*\$(\d+),?(\d{3})',  # $100,000 - $150,000
            r'(\d{2,3})[kK]?\s*-\s*(\d{2,3})[kK]'  # 100k - 150k
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if 'k' in match.group(0).lower():
                    # Convert to actual number (100k -> 100000)
                    salary_min = int(groups[0]) * 1000
                    salary_max = int(groups[1]) * 1000
                else:
                    # Already in full format
                    salary_min = int(groups[0] + groups[1]) if len(groups) == 4 else int(groups[0])
                    salary_max = int(groups[2] + groups[3]) if len(groups) == 4 else int(groups[2])
                
                return salary_min, salary_max
        
        return None, None
    
    def _extract_benefits(self, sections: Dict[str, str], full_text: str) -> List[str]:
        """Extract benefits and perks"""
        benefits_text = sections.get('benefits', '')
        
        if not benefits_text:
            return []
        
        # Common benefits
        benefit_keywords = [
            'health insurance', 'dental', 'vision', '401k', 'retirement',
            'pto', 'vacation', 'sick leave', 'parental leave', 'maternity',
            'remote work', 'flexible hours', 'stock options', 'equity',
            'bonus', 'learning budget', 'gym membership', 'free lunch'
        ]
        
        benefits = []
        text_lower = benefits_text.lower()
        
        for benefit in benefit_keywords:
            if benefit in text_lower:
                benefits.append(benefit.title())
        
        return benefits


# Helper function for quick parsing
def parse_job_description(text: str, **kwargs) -> JobDescription:
    """
    Quick helper to parse job description
    
    Usage:
        job = parse_job_description(job_text, title="Software Engineer", company="Acme Corp")
    """
    parser = JobDescriptionParser()
    return parser.parse(text, **kwargs)


if __name__ == "__main__":
    # Test with sample job description
    sample_job = """
    Senior Software Engineer - Backend
    
    Company: TechCorp Inc.
    Location: San Francisco, CA (Hybrid)
    
    About the Role:
    We're looking for an experienced backend engineer to join our growing team.
    
    Responsibilities:
    • Design and implement scalable backend services
    • Work with Python, Django, and PostgreSQL
    • Collaborate with frontend team on API design
    • Mentor junior engineers
    • Participate in code reviews and architecture decisions
    
    Requirements:
    • 5+ years of software engineering experience
    • Strong proficiency in Python and Django
    • Experience with PostgreSQL or similar databases
    • AWS experience required
    • Bachelor's degree in Computer Science or related field
    
    Nice to Have:
    • Experience with Kubernetes and Docker
    • Knowledge of microservices architecture
    • Contributions to open source projects
    
    Benefits:
    • Competitive salary ($150k - $180k)
    • Health, dental, and vision insurance
    • 401k matching
    • Flexible work hours
    • Remote-friendly environment
    """
    
    parser = JobDescriptionParser()
    job = parser.parse(sample_job)
    
    print("📋 Parsed Job Description:\n")
    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Location: {job.location}")
    print(f"Remote Policy: {job.remote_policy}")
    print(f"Experience: {job.required_experience_years} years ({job.experience_level})")
    print(f"Education: {job.education_level}")
    print(f"Salary: ${job.salary_min:,} - ${job.salary_max:,}")
    print(f"\nRequired Skills ({len(job.required_skills)}): {', '.join(job.required_skills[:10])}")
    print(f"Optional Skills ({len(job.optional_skills)}): {', '.join(job.optional_skills[:10])}")
    print(f"\nResponsibilities ({len(job.responsibilities)}):")
    for i, resp in enumerate(job.responsibilities[:5], 1):
        print(f"  {i}. {resp}")
    print(f"\nBenefits: {', '.join(job.benefits)}")
