"""
Enhanced Dynamic Skill Extractor with ESCO Validation and Proficiency Detection
Extracts skills from resume text using multiple methods:
1. NER (Named Entity Recognition) for technical terms
2. Pattern matching for skill-like phrases
3. Section-based extraction (from Skills section)
4. Context-aware extraction (from experience descriptions)
5. Validation against curated skill taxonomy (ESCO-based)
6. Proficiency level detection (Expert/Advanced/Intermediate/Beginner)
7. Years of experience tracking per skill
8. Skill-to-experience mapping and context analysis
"""

import re
import spacy
import json
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DynamicSkillExtractor:
    """
    Extract skills dynamically from text and validate against taxonomy
    """
    
    def __init__(self):
        """Initialize with spaCy model and skill taxonomy"""
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            logger.warning("en_core_web_md not found, downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"])
            self.nlp = spacy.load("en_core_web_md")
        
        # Load validated skills taxonomy
        self.validated_skills = self._load_skill_taxonomy()
        logger.info(f"Loaded {len(self.validated_skills)} validated skills")
        
        # Proficiency level patterns (from ref.md)
        self.proficiency_patterns = {
            'expert': [
                r'expert\s+(?:in|with|at)',
                r'mastery\s+(?:in|of)',
                r'extensive\s+experience',
                r'deep\s+(?:knowledge|expertise)',
                r'advanced\s+proficiency',
                r'highly\s+proficient',
                r'\d{4,}\+?\s+years?',  # 4+ years
                r'lead\s+(?:developer|engineer)',
                r'architect',
                r'subject\s+matter\s+expert',
            ],
            'advanced': [
                r'advanced\s+(?:knowledge|skills)',
                r'proficient\s+(?:in|with)',
                r'strong\s+(?:knowledge|experience|skills)',
                r'\d{2,3}\+?\s+years?',  # 2-3+ years
                r'senior\s+(?:developer|engineer)',
                r'experienced\s+(?:in|with)',
            ],
            'intermediate': [
                r'intermediate\s+(?:knowledge|level)',
                r'working\s+knowledge',
                r'familiar\s+with',
                r'competent\s+(?:in|with)',
                r'solid\s+understanding',
                r'moderate\s+experience',
                r'1-2\s+years?',
            ],
            'beginner': [
                r'basic\s+(?:knowledge|understanding)',
                r'fundamental\s+knowledge',
                r'beginner\s+level',
                r'learning',
                r'coursework\s+in',
                r'exposure\s+to',
                r'introduced\s+to',
                r'less\s+than\s+1\s+year',
            ]
        }
        
        # Compile proficiency patterns
        self.compiled_proficiency = {
            level: [re.compile(p, re.IGNORECASE) for p in patterns]
            for level, patterns in self.proficiency_patterns.items()
        }
        
        # Temporal indicators for years extraction
        self.temporal_patterns = [
            r'(\d+)\+?\s+years?(?:\s+of)?\s+experience',
            r'(\d+)\s+yrs?',
            r'(\d{4})\s*-\s*(\d{4}|present)',  # Date ranges
            r'since\s+(\d{4})',
            r'over\s+(\d+)\s+years?',
        ]
        
        # Common skill patterns
        self.skill_patterns = [
            # Programming languages with version numbers
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Go|Rust|Scala|R|MATLAB|Perl)\s*(?:[\d.]+)?\b',
            
            # Frameworks and libraries
            r'\b(React(?:\.js)?|Angular(?:\.js)?|Vue(?:\.js)?|Node(?:\.js)?|Express(?:\.js)?|Next(?:\.js)?|Django|Flask|FastAPI|Spring\s*Boot?|Laravel|Rails|\.NET(?:\s*Core)?)\b',
            
            # Databases
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|Cassandra|Oracle|SQL\s*Server|SQLite|DynamoDB|Elasticsearch|Neo4j|Firebase)\b',
            
            # Cloud platforms
            r'\b(AWS|Azure|GCP|Google\s*Cloud|Amazon\s*Web\s*Services|Heroku|DigitalOcean|Vercel|Netlify)\b',
            
            # DevOps and tools
            r'\b(Docker|Kubernetes|K8s|Jenkins|GitHub\s*Actions|GitLab\s*CI|CircleCI|Terraform|Ansible|Chef|Puppet)\b',
            
            # Version control
            r'\b(Git|GitHub|GitLab|Bitbucket|SVN|Mercurial)\b',
            
            # ML/AI
            r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Machine\s*Learning|Deep\s*Learning|Neural\s*Networks?|NLP|Computer\s*Vision|AI|Artificial\s*Intelligence)\b',
            
            # Testing
            r'\b(Jest|Mocha|Pytest|JUnit|Selenium|Cypress|TestNG|Unit\s*Testing|Integration\s*Testing)\b',
            
            # Project management
            r'\b(JIRA|Confluence|Trello|Asana|Monday\.com|Slack|MS\s*Teams|Agile|Scrum|Kanban)\b',
            
            # Design tools
            r'\b(Figma|Adobe\s*(?:XD|Photoshop|Illustrator)|Sketch|InVision|Canva)\b',
            
            # Operating systems
            r'\b(Linux|Unix|Ubuntu|CentOS|Windows|macOS|iOS|Android)\b',
            
            # Web technologies
            r'\b(HTML5?|CSS3?|SASS|SCSS|LESS|Bootstrap|Tailwind(?:\s*CSS)?|Material(?:-|\s)?UI|jQuery)\b',
            
            # APIs and protocols
            r'\b(REST(?:ful)?(?:\s*API)?|GraphQL|gRPC|WebSocket|SOAP|OAuth|JWT|HTTP[S]?)\b',
            
            # Methodologies
            r'\b(Agile|Scrum|Kanban|Waterfall|TDD|BDD|CI/CD|DevOps|Microservices|Serverless)\b',
        ]
        
        # Compile all patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.skill_patterns]
        
        # Soft skills keywords
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'team collaboration', 'problem solving',
            'critical thinking', 'time management', 'project management', 'adaptability',
            'creativity', 'public speaking', 'presentation', 'negotiation', 'conflict resolution',
            'analytical', 'organization', 'attention to detail', 'multitasking', 'decision making'
        }
        
        # Words to exclude (too generic)
        self.exclude_words = {
            'experience', 'work', 'project', 'team', 'company', 'role', 'position',
            'responsible', 'developed', 'managed', 'created', 'worked', 'using',
            'including', 'various', 'multiple', 'several', 'different', 'new', 'old',
            'state', 'city', 'name', 'company name', 'name city', 'additional information',
            'core qualifications', 'gpa', 'usa', 'united states', 'time', 'go',
            'less', 'sales', 'clients', 'quality', 'meetings', 'client', 'processes',
            'marketing', 'budget', 'inventory', 'assisted', 'personnel', 'financial',
            'materials', 'office', 'contracts', 'managing', 'delivery', 'senior management',
            'safety', 'database', 'budgets', 'presentations', 'credit', 'market',
            'progress', 'phone', 'strategic', 'benefits', 'billing'
        }
    
    def _load_skill_taxonomy(self) -> Set[str]:
        """Load validated skills from taxonomy file"""
        taxonomy_path = Path('data/skills/validated_skills.json')
        
        if not taxonomy_path.exists():
            logger.warning(f"Skill taxonomy not found at {taxonomy_path}")
            return set()
        
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create case-insensitive lookup set
            skills = set()
            for skill in data.get('skills', []):
                skills.add(skill.lower())  # Store lowercase for matching
            
            return skills
        except Exception as e:
            logger.error(f"Error loading skill taxonomy: {e}")
            return set()
    
    def _validate_skill(self, skill: str) -> bool:
        """
        Validate if extracted text is a real skill
        
        Args:
            skill: Extracted skill text
        
        Returns:
            True if skill is validated, False otherwise
        """
        skill_lower = skill.lower().strip()
        
        # Check against validated taxonomy
        if skill_lower in self.validated_skills:
            return True
        
        # Check if it's a variation (e.g., "Python 3", "React.js")
        base_skill = re.sub(r'[\d.\s]+$', '', skill_lower).strip()  # Remove version numbers
        base_skill = re.sub(r'\.(js|py|ts)$', '', base_skill)  # Remove extensions
        
        if base_skill in self.validated_skills:
            return True
        
        # Reject if too short (< 2 chars)
        if len(skill_lower) < 2:
            return False
        
        # Reject if in exclude list
        if skill_lower in self.exclude_words:
            return False
        
        # Reject common verbs
        if skill_lower in {'go', 'do', 'make', 'get', 'use', 'work', 'help'}:
            return False
        
        # Allow if it matches technical patterns (even if not in taxonomy)
        # This catches new/emerging skills
        tech_indicators = ['api', 'sdk', 'framework', 'library', '.js', '.py', 'ql']
        if any(indicator in skill_lower for indicator in tech_indicators):
            return True
        
        # Reject generic business terms
        generic_terms = {
            'the', 'and', 'for', 'with', 'policies', 'reporting', 'documentation',
            'meetings', 'clients', 'customers', 'processes', 'procedures'
        }
        if skill_lower in generic_terms:
            return False
        
        return False  # Default: reject if not validated
    
    def extract_skills(self, text: str, sections: Dict = None) -> Dict[str, List[str]]:
        """
        Extract skills from resume text using multiple methods
        
        Args:
            text: Full resume text
            sections: Parsed sections (optional, for section-based extraction)
        
        Returns:
            Dict with:
                - all_skills: Combined list of unique skills
                - technical_skills: Programming, frameworks, tools
                - soft_skills: Communication, leadership, etc.
                - tools: Software and tools
                - methodologies: Agile, Scrum, etc.
        """
        all_skills = set()
        
        # Method 1: Pattern-based extraction (technical skills)
        technical_skills = self._extract_with_patterns(text)
        all_skills.update(technical_skills)
        
        # Method 2: NER-based extraction
        ner_skills = self._extract_with_ner(text)
        all_skills.update(ner_skills)
        
        # Method 3: Skills section extraction (if available)
        if sections and 'skills' in sections:
            section_skills = self._extract_from_skills_section(sections['skills'])
            all_skills.update(section_skills)
        
        # Method 4: Experience section extraction
        if sections and 'experience' in sections:
            exp_skills = self._extract_from_experience(sections['experience'])
            all_skills.update(exp_skills)
        
        # Method 5: Soft skills
        soft_skills_found = self._extract_soft_skills(text)
        all_skills.update(soft_skills_found)
        
        # Clean and normalize
        all_skills = self._clean_and_normalize(all_skills)
        
        # Categorize skills
        categorized = self._categorize_skills(all_skills)
        
        return {
            'all_skills': sorted(list(all_skills)),
            'technical_skills': sorted(categorized['technical']),
            'soft_skills': sorted(categorized['soft']),
            'tools': sorted(categorized['tools']),
            'methodologies': sorted(categorized['methodologies']),
            'count': len(all_skills)
        }
    
    def _extract_with_patterns(self, text: str) -> Set[str]:
        """Extract skills using regex patterns"""
        skills = set()
        
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                skill = match.strip()
                if len(skill) > 1 and skill.lower() not in self.exclude_words:
                    skills.add(skill)
        
        return skills
    
    def _extract_with_ner(self, text: str) -> Set[str]:
        """Extract skills using spaCy NER and noun phrase extraction"""
        skills = set()
        
        # Process text with spaCy
        doc = self.nlp(text[:100000])  # Limit to prevent memory issues
        
        # Extract named entities (ORG, PRODUCT, etc.)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'LANGUAGE']:
                # Filter out common non-skill entities
                if len(ent.text) > 2 and ent.text.lower() not in self.exclude_words:
                    # Check if it looks like a skill (has capital letters or numbers)
                    if any(c.isupper() for c in ent.text) or any(c.isdigit() for c in ent.text):
                        skills.add(ent.text.strip())
        
        # Extract noun chunks that might be skills
        for chunk in doc.noun_chunks:
            # Look for skill-like noun phrases (2-4 words, has tech indicators)
            text_lower = chunk.text.lower()
            if (2 <= len(chunk.text.split()) <= 4 and
                any(keyword in text_lower for keyword in ['programming', 'development', 'analysis', 'management', 'design', 'testing', 'learning'])):
                skills.add(chunk.text.strip())
        
        return skills
    
    def _extract_from_skills_section(self, skills_text) -> Set[str]:
        """Extract from dedicated skills section"""
        skills = set()
        
        # Handle different input types
        if isinstance(skills_text, dict):
            # If it's a dict, try to get text from common keys
            skills_text = skills_text.get('text', '') or skills_text.get('content', '') or str(skills_text)
        elif not isinstance(skills_text, str):
            skills_text = str(skills_text)
        
        # Common separators
        separators = [',', ';', '|', '•', '●', '·', '-', '\n']
        
        # Try each separator
        items = [skills_text]
        for sep in separators:
            new_items = []
            for item in items:
                if isinstance(item, str):
                    new_items.extend(item.split(sep))
                else:
                    new_items.append(str(item))
            items = new_items
        
        # Clean and filter
        for item in items:
            item = item.strip()
            # Remove bullets and numbers
            item = re.sub(r'^[\d\W]+', '', item)
            
            if 2 <= len(item) <= 50 and item.lower() not in self.exclude_words:
                # Check if it's a valid skill (not a sentence)
                if len(item.split()) <= 5:
                    skills.add(item)
        
        return skills
    
    def _extract_from_experience(self, experience_text) -> Set[str]:
        """Extract technical terms from experience descriptions"""
        skills = set()
        
        # Handle different input types
        if isinstance(experience_text, (list, dict)):
            experience_text = str(experience_text)
        elif not isinstance(experience_text, str):
            experience_text = str(experience_text)
        
        # Look for "using X", "with X", "in X" patterns
        patterns = [
            r'using\s+([A-Z][A-Za-z0-9\s\.\-]{2,30})',
            r'with\s+([A-Z][A-Za-z0-9\s\.\-]{2,30})',
            r'in\s+([A-Z][A-Za-z0-9\s\.\-]{2,30})',
            r'including\s+([A-Z][A-Za-z0-9\s\.\-]{2,30})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, experience_text)
            for match in matches:
                skill = match.strip()
                if len(skill) > 2 and skill.lower() not in self.exclude_words:
                    skills.add(skill)
        
        return skills
    
    def _extract_soft_skills(self, text: str) -> Set[str]:
        """Extract soft skills"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.soft_skills:
            if skill in text_lower:
                # Capitalize first letter of each word
                found_skills.add(skill.title())
        
        return found_skills
    
    def _clean_and_normalize(self, skills: Set[str]) -> Set[str]:
        """
        Clean, normalize, and VALIDATE skill names
        This is where we apply ESCO validation!
        """
        cleaned = set()
        
        for skill in skills:
            # Remove extra whitespace
            skill = ' '.join(skill.split())
            
            # Remove trailing/leading punctuation
            skill = skill.strip('.,;:!?')
            
            # Skip very short or very long
            if not (2 <= len(skill) <= 50):
                continue
            
            # Skip pure numbers
            if skill.isdigit():
                continue
            
            # **KEY VALIDATION STEP**: Check against taxonomy
            if not self._validate_skill(skill):
                continue
            
            cleaned.add(skill)
        
        return cleaned
    
    def _categorize_skills(self, skills: Set[str]) -> Dict[str, List[str]]:
        """Categorize skills into types"""
        categories = {
            'technical': [],
            'soft': [],
            'tools': [],
            'methodologies': []
        }
        
        technical_keywords = {'python', 'java', 'javascript', 'react', 'angular', 'node', 
                            'django', 'flask', 'spring', 'sql', 'nosql', 'mongodb', 
                            'tensorflow', 'pytorch', 'ml', 'ai', 'learning'}
        
        tool_keywords = {'jira', 'git', 'docker', 'kubernetes', 'jenkins', 'figma', 
                        'photoshop', 'excel', 'powerpoint', 'slack', 'teams'}
        
        methodology_keywords = {'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 
                               'waterfall', 'microservices', 'serverless'}
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check category
            if any(kw in skill_lower for kw in technical_keywords):
                categories['technical'].append(skill)
            elif any(kw in skill_lower for kw in tool_keywords):
                categories['tools'].append(skill)
            elif any(kw in skill_lower for kw in methodology_keywords):
                categories['methodologies'].append(skill)
            elif skill in {s.title() for s in self.soft_skills}:
                categories['soft'].append(skill)
            else:
                # Default to technical
                categories['technical'].append(skill)
        
        return categories
    
    # ======================== NEW: PROFICIENCY DETECTION ========================
    
    def extract_skills_with_proficiency(self, resume_data: Dict) -> Dict:
        """
        Extract skills with proficiency levels and years of experience
        
        Args:
            resume_data: Parsed resume with 'text' and optional 'sections'
        
        Returns:
            Dict with:
                - skills_with_proficiency: List of {skill, proficiency, years, confidence, context}
                - skill_portfolio_analysis: Portfolio statistics
                - basic_skills: Backward compatible simple list
        """
        text = resume_data.get('text', '')
        sections = resume_data.get('sections', {})
        
        # First, extract basic skills (backward compatible)
        basic_extraction = self.extract_skills(text, sections)
        
        # Now enhance with proficiency
        skills_with_prof = []
        for skill in basic_extraction['all_skills']:
            proficiency, confidence = self.detect_skill_proficiency(text, skill)
            years = self.estimate_skill_years(text, skill, sections)
            context = self.extract_skill_context(text, skill)
            
            skills_with_prof.append({
                'skill': skill,
                'proficiency': proficiency,
                'confidence': confidence,
                'years': years,
                'context': context[:200] if context else None  # Limit context
            })
        
        # Analyze skill portfolio
        portfolio = self.analyze_skill_portfolio({'skills': skills_with_prof})
        
        return {
            'skills_with_proficiency': skills_with_prof,
            'skill_portfolio_analysis': portfolio,
            'basic_skills': basic_extraction,  # Backward compatible
            'total_skills': len(skills_with_prof)
        }
    
    def detect_skill_proficiency(self, text: str, skill: str) -> Tuple[str, float]:
        """
        Detect proficiency level for a specific skill
        
        Args:
            text: Full resume text
            skill: Skill name to analyze
        
        Returns:
            Tuple of (proficiency_level, confidence_score)
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Find contexts where skill is mentioned (50 chars before/after)
        skill_contexts = []
        for match in re.finditer(re.escape(skill_lower), text_lower):
            start = max(0, match.start() - 100)
            end = min(len(text_lower), match.end() + 100)
            skill_contexts.append(text_lower[start:end])
        
        if not skill_contexts:
            return 'intermediate', 0.3  # Default if not found
        
        # Score each proficiency level
        scores = defaultdict(float)
        
        for context in skill_contexts:
            for level, patterns in self.compiled_proficiency.items():
                for pattern in patterns:
                    if pattern.search(context):
                        scores[level] += 1.0
        
        # No explicit proficiency mentioned
        if not scores:
            # Infer from years if available
            years = self.estimate_skill_years(text, skill)
            if years and years >= 4:
                return 'expert', 0.6
            elif years and years >= 2:
                return 'advanced', 0.6
            elif years and years >= 1:
                return 'intermediate', 0.5
            else:
                return 'intermediate', 0.3  # Default
        
        # Get level with highest score
        max_level = max(scores, key=scores.get)
        max_score = scores[max_level]
        
        # Confidence based on number of matches
        confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1
        
        return max_level, confidence
    
    def estimate_skill_years(self, text: str, skill: str, sections: Dict = None) -> Optional[float]:
        """
        Estimate years of experience with a specific skill
        
        Args:
            text: Full resume text
            skill: Skill name
            sections: Parsed sections (optional)
        
        Returns:
            Estimated years or None
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Look for explicit mentions near the skill
        skill_contexts = []
        for match in re.finditer(re.escape(skill_lower), text_lower):
            start = max(0, match.start() - 150)
            end = min(len(text_lower), match.end() + 150)
            skill_contexts.append(text_lower[start:end])
        
        years_found = []
        
        for context in skill_contexts:
            # Pattern 1: "X years of experience"
            match = re.search(r'(\d+)\+?\s+years?(?:\s+of)?\s+experience', context)
            if match:
                years_found.append(float(match.group(1)))
            
            # Pattern 2: "X yrs"
            match = re.search(r'(\d+)\s+yrs?', context)
            if match:
                years_found.append(float(match.group(1)))
            
            # Pattern 3: Date range "2020-2023"
            match = re.search(r'(\d{4})\s*-\s*(\d{4}|present|current)', context)
            if match:
                start_year = int(match.group(1))
                end_year = datetime.now().year if match.group(2) in ['present', 'current'] else int(match.group(2))
                years_found.append(float(end_year - start_year))
        
        if years_found:
            # Return maximum (most experience mentioned)
            return max(years_found)
        
        # If we have experience sections, try to sum up durations
        if sections and 'experience' in sections:
            # This is a simplified approach
            # In production, you'd parse job dates properly
            return None
        
        return None
    
    def extract_skill_context(self, text: str, skill: str) -> Optional[str]:
        """
        Extract context where skill is mentioned
        
        Args:
            text: Full resume text
            skill: Skill name
        
        Returns:
            Context string or None
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Find first occurrence
        match = re.search(re.escape(skill_lower), text_lower)
        if not match:
            return None
        
        # Extract context (100 chars before/after)
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        
        context = text[start:end].strip()
        # Clean up
        context = ' '.join(context.split())
        
        return context
    
    def analyze_skill_portfolio(self, skills_data: Dict) -> Dict:
        """
        Analyze skill portfolio for breadth, depth, and balance
        
        Args:
            skills_data: Dict with 'skills' list (each has proficiency)
        
        Returns:
            Portfolio analysis with metrics
        """
        skills = skills_data.get('skills', [])
        
        if not skills:
            return {
                'total_skills': 0,
                'breadth_score': 0,
                'depth_score': 0,
                'balance_score': 0
            }
        
        # Count by proficiency
        proficiency_counts = Counter(s['proficiency'] for s in skills)
        
        # Breadth: number of unique skills
        breadth_score = min(len(skills) / 30.0, 1.0)  # Normalize to 0-1, 30 is excellent
        
        # Depth: proportion of expert/advanced skills
        expert_advanced = proficiency_counts.get('expert', 0) + proficiency_counts.get('advanced', 0)
        depth_score = expert_advanced / len(skills) if skills else 0
        
        # Balance: distribution across levels
        # Ideal is pyramid: some expert, more advanced, most intermediate
        ideal_distribution = {'expert': 0.2, 'advanced': 0.3, 'intermediate': 0.4, 'beginner': 0.1}
        actual_distribution = {level: proficiency_counts.get(level, 0) / len(skills) for level in ideal_distribution}
        
        # Calculate balance (lower difference = better balance)
        balance_diff = sum(abs(ideal_distribution[level] - actual_distribution[level]) for level in ideal_distribution)
        balance_score = max(1.0 - balance_diff, 0)
        
        return {
            'total_skills': len(skills),
            'breadth_score': round(breadth_score, 2),
            'depth_score': round(depth_score, 2),
            'balance_score': round(balance_score, 2),
            'proficiency_distribution': dict(proficiency_counts),
            'expert_skills': [s['skill'] for s in skills if s['proficiency'] == 'expert'],
            'advanced_skills': [s['skill'] for s in skills if s['proficiency'] == 'advanced'],
        }


# Convenience function
def extract_skills_from_text(text: str, sections: Dict = None) -> Dict[str, List[str]]:
    """
    Convenience function to extract skills
    
    Args:
        text: Resume text
        sections: Parsed sections (optional)
    
    Returns:
        Dict with categorized skills
    """
    extractor = DynamicSkillExtractor()
    return extractor.extract_skills(text, sections)
