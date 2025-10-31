"""
Skill Extraction Service
Uses NLP to identify and extract skills from resume text.
"""
from typing import List, Set, Dict
import re


class SkillExtractor:
    """Extract and normalize skills from text using NLP and keyword matching."""
    
    def __init__(self):
        # Comprehensive skill database (expand this)
        self.skill_database = self._load_skill_database()
        self.skill_patterns = self._compile_skill_patterns()
    
    def extract_skills(self, text: str, use_nlp: bool = False) -> List[Dict[str, any]]:
        """
        Extract skills from text.
        
        Args:
            text: Resume or job description text
            use_nlp: Whether to use spaCy NLP (requires model download)
            
        Returns:
            List of skill dictionaries with name, category, and confidence
        """
        found_skills = []
        text_lower = text.lower()
        
        # Method 1: Keyword matching (fast, reliable for known skills)
        for skill_name, skill_info in self.skill_database.items():
            # Check exact match and variations
            patterns = [skill_name.lower()] + skill_info.get('variations', [])
            
            for pattern in patterns:
                if self._match_skill(text_lower, pattern):
                    found_skills.append({
                        'name': skill_info['canonical_name'],
                        'category': skill_info['category'],
                        'confidence': 0.9,
                        'matched_text': pattern
                    })
                    break
        
        # Method 2: Pattern-based extraction (for compound skills)
        pattern_skills = self._extract_pattern_based(text)
        found_skills.extend(pattern_skills)
        
        # Method 3: NLP-based extraction (optional, requires spaCy model)
        if use_nlp:
            try:
                nlp_skills = self._extract_with_spacy(text)
                found_skills.extend(nlp_skills)
            except Exception as e:
                print(f"NLP extraction failed: {e}")
        
        # Deduplicate and sort by confidence
        unique_skills = self._deduplicate_skills(found_skills)
        return sorted(unique_skills, key=lambda x: x['confidence'], reverse=True)
    
    def normalize_skill(self, skill_text: str) -> str:
        """Normalize a skill name to its canonical form."""
        skill_lower = skill_text.lower().strip()
        
        # Check if it matches a known skill
        for skill_name, skill_info in self.skill_database.items():
            variations = [skill_name.lower()] + skill_info.get('variations', [])
            if skill_lower in variations:
                return skill_info['canonical_name']
        
        # Return title case if no match
        return skill_text.title()
    
    def categorize_skill(self, skill_name: str) -> str:
        """Get the category of a skill."""
        skill_lower = skill_name.lower()
        
        for skill, info in self.skill_database.items():
            if skill.lower() == skill_lower or skill_lower in info.get('variations', []):
                return info['category']
        
        return 'Other'
    
    def _match_skill(self, text: str, skill: str) -> bool:
        """Check if skill appears in text with word boundaries."""
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _extract_pattern_based(self, text: str) -> List[Dict[str, any]]:
        """Extract skills using regex patterns for compound skills."""
        skills = []
        
        # Pattern: "X years of Y" or "Y (X years)"
        experience_pattern = r'(\d+)\+?\s*years?\s+(?:of\s+)?(\w+(?:\s+\w+)?)'
        matches = re.finditer(experience_pattern, text, re.IGNORECASE)
        
        for match in matches:
            years, skill = match.groups()
            if self._is_valid_skill(skill):
                skills.append({
                    'name': skill.title(),
                    'category': 'Technical',
                    'confidence': 0.7,
                    'matched_text': match.group(0),
                    'years': int(years)
                })
        
        return skills
    
    def _extract_with_spacy(self, text: str) -> List[Dict[str, any]]:
        """
        Extract skills using spaCy NLP.
        Requires: python -m spacy download en_core_web_sm
        """
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
        except:
            return []
        
        doc = nlp(text)
        skills = []
        
        # Extract noun phrases that might be skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            if self._is_valid_skill(chunk_text):
                skills.append({
                    'name': chunk.text.title(),
                    'category': 'Technical',
                    'confidence': 0.6,
                    'matched_text': chunk.text
                })
        
        return skills
    
    def _is_valid_skill(self, text: str) -> bool:
        """Check if text looks like a valid skill."""
        text = text.strip().lower()
        
        # Filter out common non-skill words
        stopwords = {'the', 'and', 'or', 'of', 'in', 'to', 'a', 'is', 'for', 'with', 'on'}
        words = text.split()
        
        if not words or len(words) > 4:
            return False
        
        if all(word in stopwords for word in words):
            return False
        
        return True
    
    def _deduplicate_skills(self, skills: List[Dict]) -> List[Dict]:
        """Remove duplicate skills, keeping highest confidence."""
        seen = {}
        
        for skill in skills:
            name = skill['name'].lower()
            if name not in seen or skill['confidence'] > seen[name]['confidence']:
                seen[name] = skill
        
        return list(seen.values())
    
    def _load_skill_database(self) -> Dict[str, Dict]:
        """Load comprehensive skill database with categories and variations."""
        return {
            # Programming Languages
            'Python': {
                'canonical_name': 'Python',
                'category': 'Programming Language',
                'variations': ['python3', 'python 3', 'py']
            },
            'Java': {
                'canonical_name': 'Java',
                'category': 'Programming Language',
                'variations': ['java se', 'java ee', 'j2ee']
            },
            'JavaScript': {
                'canonical_name': 'JavaScript',
                'category': 'Programming Language',
                'variations': ['js', 'javascript', 'ecmascript', 'es6']
            },
            'TypeScript': {
                'canonical_name': 'TypeScript',
                'category': 'Programming Language',
                'variations': ['ts', 'typescript']
            },
            'C++': {
                'canonical_name': 'C++',
                'category': 'Programming Language',
                'variations': ['cpp', 'c plus plus']
            },
            'C#': {
                'canonical_name': 'C#',
                'category': 'Programming Language',
                'variations': ['csharp', 'c sharp']
            },
            'Go': {
                'canonical_name': 'Go',
                'category': 'Programming Language',
                'variations': ['golang']
            },
            'Ruby': {
                'canonical_name': 'Ruby',
                'category': 'Programming Language',
                'variations': []
            },
            'PHP': {
                'canonical_name': 'PHP',
                'category': 'Programming Language',
                'variations': []
            },
            'Swift': {
                'canonical_name': 'Swift',
                'category': 'Programming Language',
                'variations': []
            },
            'Kotlin': {
                'canonical_name': 'Kotlin',
                'category': 'Programming Language',
                'variations': []
            },
            
            # Web Frameworks
            'React': {
                'canonical_name': 'React',
                'category': 'Web Framework',
                'variations': ['reactjs', 'react.js', 'react js']
            },
            'Angular': {
                'canonical_name': 'Angular',
                'category': 'Web Framework',
                'variations': ['angularjs', 'angular.js']
            },
            'Vue': {
                'canonical_name': 'Vue.js',
                'category': 'Web Framework',
                'variations': ['vue', 'vuejs', 'vue.js']
            },
            'Django': {
                'canonical_name': 'Django',
                'category': 'Web Framework',
                'variations': []
            },
            'Flask': {
                'canonical_name': 'Flask',
                'category': 'Web Framework',
                'variations': []
            },
            'FastAPI': {
                'canonical_name': 'FastAPI',
                'category': 'Web Framework',
                'variations': ['fast api']
            },
            'Spring': {
                'canonical_name': 'Spring',
                'category': 'Web Framework',
                'variations': ['spring boot', 'spring framework', 'springboot']
            },
            'Node.js': {
                'canonical_name': 'Node.js',
                'category': 'Runtime',
                'variations': ['node', 'nodejs', 'node js']
            },
            'Express': {
                'canonical_name': 'Express.js',
                'category': 'Web Framework',
                'variations': ['express', 'expressjs']
            },
            
            # Databases
            'PostgreSQL': {
                'canonical_name': 'PostgreSQL',
                'category': 'Database',
                'variations': ['postgres', 'psql']
            },
            'MySQL': {
                'canonical_name': 'MySQL',
                'category': 'Database',
                'variations': ['my sql']
            },
            'MongoDB': {
                'canonical_name': 'MongoDB',
                'category': 'Database',
                'variations': ['mongo']
            },
            'Redis': {
                'canonical_name': 'Redis',
                'category': 'Database',
                'variations': []
            },
            'Elasticsearch': {
                'canonical_name': 'Elasticsearch',
                'category': 'Database',
                'variations': ['elastic search', 'elastic']
            },
            'Oracle': {
                'canonical_name': 'Oracle Database',
                'category': 'Database',
                'variations': ['oracle db', 'oracle sql']
            },
            'SQL Server': {
                'canonical_name': 'SQL Server',
                'category': 'Database',
                'variations': ['mssql', 'ms sql', 'microsoft sql server']
            },
            
            # Cloud & DevOps
            'AWS': {
                'canonical_name': 'Amazon Web Services',
                'category': 'Cloud',
                'variations': ['amazon web services']
            },
            'Azure': {
                'canonical_name': 'Microsoft Azure',
                'category': 'Cloud',
                'variations': ['ms azure']
            },
            'GCP': {
                'canonical_name': 'Google Cloud Platform',
                'category': 'Cloud',
                'variations': ['google cloud', 'gcloud']
            },
            'Docker': {
                'canonical_name': 'Docker',
                'category': 'DevOps',
                'variations': []
            },
            'Kubernetes': {
                'canonical_name': 'Kubernetes',
                'category': 'DevOps',
                'variations': ['k8s']
            },
            'Jenkins': {
                'canonical_name': 'Jenkins',
                'category': 'DevOps',
                'variations': []
            },
            'Terraform': {
                'canonical_name': 'Terraform',
                'category': 'DevOps',
                'variations': []
            },
            'Git': {
                'canonical_name': 'Git',
                'category': 'DevOps',
                'variations': ['github', 'gitlab', 'gitflow']
            },
            
            # AI/ML
            'Machine Learning': {
                'canonical_name': 'Machine Learning',
                'category': 'AI/ML',
                'variations': ['ml', 'machine-learning']
            },
            'Deep Learning': {
                'canonical_name': 'Deep Learning',
                'category': 'AI/ML',
                'variations': ['dl', 'deep-learning']
            },
            'TensorFlow': {
                'canonical_name': 'TensorFlow',
                'category': 'AI/ML',
                'variations': ['tensor flow']
            },
            'PyTorch': {
                'canonical_name': 'PyTorch',
                'category': 'AI/ML',
                'variations': ['torch']
            },
            'Scikit-learn': {
                'canonical_name': 'Scikit-learn',
                'category': 'AI/ML',
                'variations': ['sklearn', 'scikit learn']
            },
            'NLP': {
                'canonical_name': 'Natural Language Processing',
                'category': 'AI/ML',
                'variations': ['natural language processing', 'nlp']
            },
            'Computer Vision': {
                'canonical_name': 'Computer Vision',
                'category': 'AI/ML',
                'variations': ['cv', 'image processing']
            },
            
            # Data Science
            'Pandas': {
                'canonical_name': 'Pandas',
                'category': 'Data Science',
                'variations': []
            },
            'NumPy': {
                'canonical_name': 'NumPy',
                'category': 'Data Science',
                'variations': ['numpy']
            },
            'Matplotlib': {
                'canonical_name': 'Matplotlib',
                'category': 'Data Science',
                'variations': []
            },
            'Data Analysis': {
                'canonical_name': 'Data Analysis',
                'category': 'Data Science',
                'variations': ['data analytics']
            },
            
            # Soft Skills
            'Agile': {
                'canonical_name': 'Agile',
                'category': 'Methodology',
                'variations': ['agile methodology']
            },
            'Scrum': {
                'canonical_name': 'Scrum',
                'category': 'Methodology',
                'variations': []
            },
            'Leadership': {
                'canonical_name': 'Leadership',
                'category': 'Soft Skill',
                'variations': ['team leadership']
            },
            'Communication': {
                'canonical_name': 'Communication',
                'category': 'Soft Skill',
                'variations': []
            }
        }
    
    def _compile_skill_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for efficient matching."""
        patterns = {}
        for skill in self.skill_database.keys():
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            patterns[skill] = re.compile(pattern, re.IGNORECASE)
        return patterns
