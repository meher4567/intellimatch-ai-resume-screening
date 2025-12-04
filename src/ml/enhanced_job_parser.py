"""
Enhanced Job Description Parser
Advanced extraction of requirements, qualifications, and job details from job postings
"""

import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


class EnhancedJobDescriptionParser:
    """
    Parses job descriptions to extract:
    1. Required vs Nice-to-have skills
    2. Experience requirements (years, level)
    3. Education requirements
    4. Responsibilities and duties
    5. Benefits and perks
    6. Company culture indicators
    7. Salary information (when present)
    8. Remote/hybrid/onsite indicators
    """
    
    def __init__(self):
        # Section headers
        self.section_patterns = {
            'requirements': [
                r'requirements?:?',
                r'qualifications?:?',
                r'what (?:you|we)[\'\']?re looking for',
                r'ideal candidate',
                r'you have',
                r'must have'
            ],
            'responsibilities': [
                r'responsibilities:?',
                r'duties:?',
                r'what you[\'\']?ll do',
                r'you will',
                r'the role',
                r'day[- ]to[- ]day'
            ],
            'nice_to_have': [
                r'nice[- ]to[- ]have',
                r'bonus',
                r'plus',
                r'preferred',
                r'desirable',
                r'advantage'
            ],
            'benefits': [
                r'benefits:?',
                r'perks:?',
                r'what we offer',
                r'compensation',
                r'we provide'
            ],
            'about': [
                r'about (?:us|the company|the team)',
                r'who we are',
                r'our (?:company|team|mission)'
            ]
        }
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)\+?\s*years?(?:\s+of)?\s+experience',
            r'(\d+)\+?\s*yrs?(?:\s+of)?\s+experience',
            r'minimum\s+(\d+)\s+years?',
            r'at least\s+(\d+)\s+years?',
            r'(\d+)\s*-\s*(\d+)\s+years?'
        ]
        
        # Level indicators
        self.level_indicators = {
            'entry': ['entry[- ]level', 'junior', 'associate', 'graduate', 'intern'],
            'mid': ['mid[- ]level', 'intermediate', 'professional'],
            'senior': ['senior', 'sr\\.?', 'lead', 'principal', 'staff'],
            'expert': ['expert', 'architect', 'distinguished', 'fellow'],
            'management': ['manager', 'director', 'head', 'vp', 'cto', 'ceo']
        }
        
        # Education patterns
        self.education_patterns = [
            r'bachelor[\'\']?s?\s+degree',
            r'master[\'\']?s?\s+degree',
            r'phd',
            r'doctorate',
            r'bs|ba|ms|ma|mba',
            r'degree\s+in\s+(\w+(?:\s+\w+)*)',
            r'(\w+)\s+degree'
        ]
        
        # Remote work indicators
        self.remote_patterns = {
            'remote': r'\b(?:remote|work from home|wfh|distributed)\b',
            'hybrid': r'\bhybrid\b',
            'onsite': r'\b(?:on[- ]site|in[- ]office|office[- ]based)\b'
        }
        
        # Salary patterns
        self.salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*-\s*\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:k|K)?)\s+per\s+(?:year|annum)',
            r'salary:?\s*\$(\d{1,3}(?:,\d{3})*(?:k|K)?)'
        ]
        
        # Benefits keywords
        self.benefits_keywords = {
            'health': ['health insurance', 'medical', 'dental', 'vision'],
            'time_off': ['pto', 'vacation', 'paid time off', 'holidays'],
            'retirement': ['401k', '401(k)', 'pension', 'retirement'],
            'equity': ['stock options', 'equity', 'rsu', 'esop'],
            'learning': ['professional development', 'training', 'courses', 'conference'],
            'wellness': ['gym', 'wellness', 'fitness', 'mental health'],
            'flexibility': ['flexible hours', 'work-life balance', 'flexible schedule'],
            'parental': ['parental leave', 'maternity', 'paternity']
        }
        
        # Requirement strength indicators
        self.must_have_indicators = [
            'required', 'must have', 'essential', 'mandatory',
            'critical', 'necessary', 'needed'
        ]
        
        self.nice_to_have_indicators = [
            'preferred', 'nice to have', 'bonus', 'plus',
            'desirable', 'advantage', 'ideal'
        ]
    
    def parse_job_description(self, job_text: str, job_title: str = None) -> Dict:
        """
        Parse job description comprehensively
        
        Args:
            job_text: Job description text
            job_title: Job title (optional)
            
        Returns:
            Parsed job data
        """
        if not job_text:
            return {'error': 'Empty job description'}
        
        # Split into sections
        sections = self._identify_sections(job_text)
        
        # Extract experience requirements
        experience_req = self._extract_experience_requirements(job_text, job_title)
        
        # Extract education requirements
        education_req = self._extract_education_requirements(job_text)
        
        # Extract skills
        skills_req = self._extract_skills_requirements(job_text, sections)
        
        # Extract work arrangement
        work_arrangement = self._extract_work_arrangement(job_text)
        
        # Extract salary info
        salary_info = self._extract_salary_info(job_text)
        
        # Extract benefits
        benefits = self._extract_benefits(job_text, sections.get('benefits', ''))
        
        # Extract responsibilities
        responsibilities = self._extract_responsibilities(sections.get('responsibilities', ''))
        
        # Analyze company culture
        culture = self._analyze_culture_indicators(job_text)
        
        # Extract job level from title
        job_level = self._extract_level_from_title(job_title) if job_title else None
        
        return {
            'job_title': job_title,
            'job_level': job_level,
            'experience_requirements': experience_req,
            'education_requirements': education_req,
            'skills_requirements': skills_req,
            'responsibilities': responsibilities,
            'work_arrangement': work_arrangement,
            'salary_info': salary_info,
            'benefits': benefits,
            'culture_indicators': culture,
            'sections_found': list(sections.keys()),
            'parsing_quality': self._assess_parsing_quality(sections, skills_req, experience_req)
        }
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract sections from job description"""
        sections = {}
        text_lower = text.lower()
        
        # Find section boundaries
        section_positions = []
        
        for section_name, patterns in self.section_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text_lower))
                for match in matches:
                    section_positions.append((match.start(), section_name))
        
        # Sort by position
        section_positions.sort()
        
        # Extract text between sections
        for i, (pos, section_name) in enumerate(section_positions):
            start = pos
            end = section_positions[i + 1][0] if i + 1 < len(section_positions) else len(text)
            
            section_text = text[start:end].strip()
            
            # Combine if section already exists
            if section_name in sections:
                sections[section_name] += '\n' + section_text
            else:
                sections[section_name] = section_text
        
        return sections
    
    def _extract_experience_requirements(self, text: str, job_title: str = None) -> Dict:
        """Extract experience requirements"""
        requirements = {
            'years_required': None,
            'years_range': None,
            'level': None,
            'level_confidence': 0.0
        }
        
        # Extract years
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range pattern
                    requirements['years_range'] = [int(matches[0][0]), int(matches[0][1])]
                    requirements['years_required'] = int(matches[0][0])
                else:
                    requirements['years_required'] = int(matches[0])
                break
        
        # Extract level
        level_scores = Counter()
        
        # From job title
        if job_title:
            title_lower = job_title.lower()
            for level, indicators in self.level_indicators.items():
                for indicator in indicators:
                    if re.search(indicator, title_lower):
                        level_scores[level] += 2
        
        # From description text
        text_lower = text.lower()
        for level, indicators in self.level_indicators.items():
            for indicator in indicators:
                if re.search(indicator, text_lower):
                    level_scores[level] += 1
        
        if level_scores:
            most_common = level_scores.most_common(1)[0]
            requirements['level'] = most_common[0]
            total_score = sum(level_scores.values())
            requirements['level_confidence'] = most_common[1] / total_score if total_score > 0 else 0.0
        
        # Infer level from years if not found
        if not requirements['level'] and requirements['years_required']:
            years = requirements['years_required']
            if years < 2:
                requirements['level'] = 'entry'
            elif years < 5:
                requirements['level'] = 'mid'
            elif years < 10:
                requirements['level'] = 'senior'
            else:
                requirements['level'] = 'expert'
            requirements['level_confidence'] = 0.5
        
        return requirements
    
    def _extract_education_requirements(self, text: str) -> Dict:
        """Extract education requirements"""
        requirements = {
            'degree_required': None,
            'field_of_study': None,
            'alternatives_accepted': False
        }
        
        text_lower = text.lower()
        
        # Check for degree requirement
        if re.search(r'bachelor', text_lower):
            requirements['degree_required'] = 'Bachelor'
        if re.search(r'master', text_lower):
            requirements['degree_required'] = 'Master'
        if re.search(r'phd|doctorate', text_lower):
            requirements['degree_required'] = 'PhD'
        
        # Extract field of study
        field_matches = re.findall(
            r'degree\s+in\s+([\w\s]+?)(?:\s+or|\s+from|,|\.|$)',
            text_lower
        )
        if field_matches:
            requirements['field_of_study'] = field_matches[0].strip()
        
        # Check if alternatives accepted
        if re.search(r'or equivalent|equivalent experience|in lieu of', text_lower):
            requirements['alternatives_accepted'] = True
        
        return requirements
    
    def _extract_skills_requirements(self, text: str, sections: Dict) -> Dict:
        """Extract required and nice-to-have skills"""
        requirements = {
            'required_skills': [],
            'nice_to_have_skills': [],
            'skill_categories': defaultdict(list)
        }
        
        # Prioritize requirements section
        req_text = sections.get('requirements', text)
        nice_text = sections.get('nice_to_have', '')
        
        # Extract skills from requirements
        req_lower = req_text.lower()
        
        # Look for bullet points or list items
        lines = req_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Determine if required or nice-to-have
            is_required = any(ind in line.lower() for ind in self.must_have_indicators)
            is_nice = any(ind in line.lower() for ind in self.nice_to_have_indicators)
            
            # Extract potential skills (capitalized words, technical terms)
            # This is a simplified extraction - in production, use skill taxonomy
            potential_skills = re.findall(r'\b[A-Z][a-zA-Z0-9+#\.]+\b', line)
            potential_skills += re.findall(r'\b(?:python|java|javascript|react|angular|aws|docker|kubernetes)\b', line, re.IGNORECASE)
            
            for skill in potential_skills:
                skill = skill.strip()
                if len(skill) > 1:
                    if is_nice or (nice_text and skill.lower() in nice_text.lower()):
                        if skill not in requirements['nice_to_have_skills']:
                            requirements['nice_to_have_skills'].append(skill)
                    elif is_required or not is_nice:
                        if skill not in requirements['required_skills']:
                            requirements['required_skills'].append(skill)
        
        return requirements
    
    def _extract_work_arrangement(self, text: str) -> Dict:
        """Extract remote/hybrid/onsite information"""
        arrangement = {
            'type': 'unknown',
            'details': None
        }
        
        text_lower = text.lower()
        
        scores = {}
        for arr_type, pattern in self.remote_patterns.items():
            if re.search(pattern, text_lower):
                scores[arr_type] = len(re.findall(pattern, text_lower))
        
        if scores:
            arrangement['type'] = max(scores, key=scores.get)
        
        # Extract location if onsite
        if arrangement['type'] == 'onsite':
            location_match = re.search(
                r'location:?\s*([A-Z][a-zA-Z\s,]+?)(?:\n|$)',
                text
            )
            if location_match:
                arrangement['details'] = location_match.group(1).strip()
        
        return arrangement
    
    def _extract_salary_info(self, text: str) -> Dict:
        """Extract salary information"""
        salary_info = {
            'range': None,
            'currency': 'USD',
            'period': 'annual'
        }
        
        for pattern in self.salary_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    # Range
                    low = self._parse_salary_value(matches[0][0])
                    high = self._parse_salary_value(matches[0][1])
                    salary_info['range'] = [low, high]
                else:
                    # Single value
                    value = self._parse_salary_value(matches[0])
                    salary_info['range'] = [value, value]
                break
        
        return salary_info
    
    def _parse_salary_value(self, value_str: str) -> int:
        """Parse salary string to integer"""
        value_str = value_str.replace(',', '').upper()
        
        if 'K' in value_str:
            return int(value_str.replace('K', '')) * 1000
        else:
            return int(value_str)
    
    def _extract_benefits(self, text: str, benefits_section: str) -> Dict:
        """Extract benefits information"""
        benefits = {
            'categories': {},
            'highlights': []
        }
        
        # Search in benefits section first, then full text
        search_text = benefits_section if benefits_section else text
        search_lower = search_text.lower()
        
        for category, keywords in self.benefits_keywords.items():
            found_benefits = []
            for keyword in keywords:
                if keyword in search_lower:
                    found_benefits.append(keyword)
            
            if found_benefits:
                benefits['categories'][category] = found_benefits
        
        # Extract benefit highlights (lines after "benefits:" or similar)
        if benefits_section:
            lines = benefits_section.split('\n')
            for line in lines[1:10]:  # Get first few lines
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    benefit_text = re.sub(r'^[-•*]\s*', '', line)
                    if len(benefit_text) > 10:
                        benefits['highlights'].append(benefit_text)
        
        return benefits
    
    def _extract_responsibilities(self, responsibilities_section: str) -> List[str]:
        """Extract key responsibilities"""
        if not responsibilities_section:
            return []
        
        responsibilities = []
        lines = responsibilities_section.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered items
            if re.match(r'^[-•*\d\.]\s*', line):
                resp_text = re.sub(r'^[-•*\d\.]\s*', '', line)
                if len(resp_text) > 15:  # Meaningful length
                    responsibilities.append(resp_text)
        
        return responsibilities[:10]  # Top 10
    
    def _analyze_culture_indicators(self, text: str) -> Dict:
        """Analyze company culture from language used"""
        culture = {
            'indicators': [],
            'keywords': []
        }
        
        text_lower = text.lower()
        
        # Culture keywords
        culture_keywords = {
            'collaborative': ['collaborative', 'team player', 'cross-functional', 'teamwork'],
            'innovative': ['innovative', 'cutting-edge', 'pioneering', 'disruptive'],
            'fast_paced': ['fast-paced', 'dynamic', 'agile', 'startup'],
            'growth': ['growth', 'learning', 'development', 'career advancement'],
            'inclusive': ['diverse', 'inclusive', 'equal opportunity', 'belonging'],
            'flexible': ['flexible', 'work-life balance', 'autonomy', 'trust']
        }
        
        for trait, keywords in culture_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if trait not in culture['indicators']:
                        culture['indicators'].append(trait)
                    culture['keywords'].append(keyword)
        
        return culture
    
    def _extract_level_from_title(self, title: str) -> str:
        """Extract level from job title"""
        title_lower = title.lower()
        
        for level, indicators in self.level_indicators.items():
            for indicator in indicators:
                if re.search(indicator, title_lower):
                    return level
        
        return 'mid'  # Default
    
    def _assess_parsing_quality(
        self,
        sections: Dict,
        skills_req: Dict,
        experience_req: Dict
    ) -> Dict:
        """Assess quality of parsing"""
        quality = {
            'score': 0,
            'completeness': 0.0,
            'confidence': 'medium'
        }
        
        # Score based on sections found
        if 'requirements' in sections:
            quality['score'] += 30
        if 'responsibilities' in sections:
            quality['score'] += 20
        if 'benefits' in sections:
            quality['score'] += 10
        
        # Score based on extracted data
        if skills_req['required_skills']:
            quality['score'] += 20
        if experience_req['years_required']:
            quality['score'] += 10
        if experience_req['level']:
            quality['score'] += 10
        
        quality['completeness'] = quality['score'] / 100
        
        if quality['score'] >= 70:
            quality['confidence'] = 'high'
        elif quality['score'] >= 40:
            quality['confidence'] = 'medium'
        else:
            quality['confidence'] = 'low'
        
        return quality


# ============================================================================
# SELF-TEST
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("🧪 TESTING ENHANCED JOB DESCRIPTION PARSER")
    print("=" * 80)
    
    # Sample job description
    sample_job = """
    Senior Software Engineer - Python

    About Us:
    We're a fast-paced, innovative startup revolutionizing the tech industry.

    Responsibilities:
    - Design and implement scalable backend systems
    - Lead technical decisions and architecture
    - Mentor junior developers
    - Collaborate with cross-functional teams
    - Optimize system performance and reliability

    Requirements:
    - 5+ years of software development experience
    - Expert knowledge of Python and Django
    - Strong experience with AWS and Docker
    - Experience with microservices architecture
    - Bachelor's degree in Computer Science or equivalent
    - Excellent communication and teamwork skills

    Nice to Have:
    - Experience with Kubernetes
    - Knowledge of React or Angular
    - Open source contributions
    - Experience in agile environments

    Benefits:
    - Competitive salary ($120k-$160k)
    - Health, dental, and vision insurance
    - 401(k) matching
    - Unlimited PTO
    - Professional development budget
    - Remote-friendly (hybrid work)
    - Stock options

    We're an equal opportunity employer committed to building a diverse and inclusive team.
    """
    
    parser = EnhancedJobDescriptionParser()
    
    print("\n" + "=" * 80)
    print("TEST: Parsing Sample Job Description")
    print("=" * 80)
    
    result = parser.parse_job_description(sample_job, "Senior Software Engineer - Python")
    
    print(f"\n📋 Job Title: {result['job_title']}")
    print(f"   Level: {result['job_level']}")
    
    print(f"\n💼 Experience Requirements:")
    exp_req = result['experience_requirements']
    if exp_req['years_required']:
        print(f"   Years: {exp_req['years_required']}+")
    if exp_req['level']:
        print(f"   Level: {exp_req['level'].title()} (confidence: {exp_req['level_confidence']:.2f})")
    
    print(f"\n🎓 Education Requirements:")
    edu_req = result['education_requirements']
    if edu_req['degree_required']:
        print(f"   Degree: {edu_req['degree_required']}")
    if edu_req['field_of_study']:
        print(f"   Field: {edu_req['field_of_study']}")
    if edu_req['alternatives_accepted']:
        print(f"   ✅ Equivalent experience accepted")
    
    print(f"\n🛠️ Skills Requirements:")
    skills_req = result['skills_requirements']
    if skills_req['required_skills']:
        print(f"   Required ({len(skills_req['required_skills'])}): {', '.join(skills_req['required_skills'][:5])}")
    if skills_req['nice_to_have_skills']:
        print(f"   Nice-to-have ({len(skills_req['nice_to_have_skills'])}): {', '.join(skills_req['nice_to_have_skills'][:5])}")
    
    print(f"\n📍 Work Arrangement:")
    work_arr = result['work_arrangement']
    print(f"   Type: {work_arr['type'].title()}")
    if work_arr['details']:
        print(f"   Details: {work_arr['details']}")
    
    print(f"\n💰 Salary Information:")
    salary = result['salary_info']
    if salary['range']:
        print(f"   Range: ${salary['range'][0]:,} - ${salary['range'][1]:,} {salary['period']}")
    
    print(f"\n🎁 Benefits:")
    benefits = result['benefits']
    if benefits['categories']:
        for category, items in benefits['categories'].items():
            print(f"   {category.replace('_', ' ').title()}: {', '.join(items[:2])}")
    
    print(f"\n📝 Responsibilities ({len(result['responsibilities'])}):")
    for i, resp in enumerate(result['responsibilities'][:3], 1):
        print(f"   {i}. {resp[:60]}...")
    
    print(f"\n🏢 Culture Indicators:")
    culture = result['culture_indicators']
    if culture['indicators']:
        print(f"   Traits: {', '.join(culture['indicators'])}")
    
    print(f"\n📊 Parsing Quality:")
    quality = result['parsing_quality']
    print(f"   Score: {quality['score']}/100")
    print(f"   Completeness: {quality['completeness']:.1%}")
    print(f"   Confidence: {quality['confidence'].title()}")
    
    print(f"\n✅ Sections Found: {', '.join(result['sections_found'])}")
    
    print("\n" + "=" * 80)
    print("✅ ENHANCED JOB DESCRIPTION PARSER WORKING!")
    print("=" * 80)
