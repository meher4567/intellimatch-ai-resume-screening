"""
Basic Skill Extractor

Extracts technical and professional skills from text using pattern matching
and predefined skill taxonomies. This is a foundational version that will be
enhanced with NER and ML models in Phase 1 Weeks 6-8.
"""

import re
from typing import List, Dict, Set
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Extract skills from resume or job description text"""
    
    def __init__(self):
        """Initialize skill extractor with skill taxonomy"""
        
        # Programming Languages
        self.programming_languages = {
            'python', 'java', 'javascript', 'js', 'typescript', 'ts', 'c++', 'cpp',
            'c#', 'csharp', 'ruby', 'go', 'golang', 'rust', 'swift', 'kotlin',
            'php', 'r', 'matlab', 'scala', 'perl', 'shell', 'bash', 'powershell',
            'sql', 'nosql', 'html', 'css', 'dart', 'objective-c', 'assembly'
        }
        
        # Frameworks & Libraries
        self.frameworks = {
            # Web Frontend
            'react', 'reactjs', 'react.js', 'angular', 'angularjs', 'vue', 'vuejs',
            'vue.js', 'svelte', 'next.js', 'nextjs', 'gatsby', 'nuxt', 'ember',
            'backbone', 'jquery', 'bootstrap', 'tailwind', 'material-ui', 'mui',
            
            # Web Backend
            'django', 'flask', 'fastapi', 'express', 'express.js', 'nest.js',
            'nestjs', 'spring', 'spring boot', 'springboot', 'asp.net', '.net',
            'rails', 'ruby on rails', 'laravel', 'symfony', 'gin', 'echo',
            
            # Mobile
            'react native', 'flutter', 'ionic', 'xamarin', 'swiftui',
            
            # Data Science & ML
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn',
            'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
            'opencv', 'nltk', 'spacy', 'huggingface', 'transformers',
            'xgboost', 'lightgbm', 'catboost',
            
            # Testing
            'jest', 'mocha', 'jasmine', 'pytest', 'unittest', 'junit',
            'selenium', 'cypress', 'testing library', 'enzyme'
        }
        
        # Cloud & DevOps
        self.cloud_devops = {
            # Cloud Platforms
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp',
            'google cloud', 'google cloud platform', 'alibaba cloud', 'ibm cloud',
            
            # AWS Services
            'ec2', 's3', 'lambda', 'rds', 'dynamodb', 'cloudfront', 'route53',
            'ecs', 'eks', 'fargate', 'sqs', 'sns', 'cloudwatch',
            
            # Azure Services
            'azure functions', 'azure devops', 'azure sql', 'cosmos db',
            
            # DevOps Tools
            'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github actions',
            'circleci', 'travis ci', 'terraform', 'ansible', 'puppet', 'chef',
            'vagrant', 'helm', 'argocd', 'prometheus', 'grafana', 'datadog',
            'new relic', 'splunk', 'elk stack', 'elasticsearch', 'logstash', 'kibana'
        }
        
        # Databases
        self.databases = {
            'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'cassandra',
            'oracle', 'sql server', 'mariadb', 'sqlite', 'dynamodb', 'couchdb',
            'neo4j', 'influxdb', 'timescaledb', 'snowflake', 'bigquery', 'redshift'
        }
        
        # Data & Analytics
        self.data_tools = {
            'spark', 'apache spark', 'hadoop', 'hive', 'pig', 'kafka', 'airflow',
            'dbt', 'tableau', 'power bi', 'powerbi', 'looker', 'qlik', 'excel',
            'google analytics', 'mixpanel', 'amplitude', 'segment'
        }
        
        # Methodologies & Practices
        self.methodologies = {
            'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd',
            'test-driven development', 'bdd', 'pair programming', 'code review',
            'microservices', 'restful', 'rest api', 'graphql', 'grpc', 'soap',
            'mvc', 'mvvm', 'clean architecture', 'solid principles'
        }
        
        # Soft Skills
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'problem-solving',
            'critical thinking', 'analytical', 'collaboration', 'adaptability',
            'time management', 'project management', 'mentoring', 'presentation',
            'negotiation', 'conflict resolution', 'decision making'
        }
        
        # Combine all technical skills
        self.all_technical_skills = (
            self.programming_languages |
            self.frameworks |
            self.cloud_devops |
            self.databases |
            self.data_tools |
            self.methodologies
        )
        
        # Create pattern for efficient matching
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for skill matching"""
        # Sort by length (longest first) to match multi-word skills first
        all_skills = sorted(
            self.all_technical_skills | self.soft_skills,
            key=len,
            reverse=True
        )
        
        # Escape special regex characters and create pattern
        escaped_skills = [re.escape(skill) for skill in all_skills]
        pattern = r'\b(' + '|'.join(escaped_skills) + r')\b'
        self.skill_pattern = re.compile(pattern, re.IGNORECASE)
    
    def extract_skills(self, text: str, include_soft_skills: bool = False) -> Dict[str, List[str]]:
        """
        Extract skills from text
        
        Args:
            text: Resume or job description text
            include_soft_skills: Whether to include soft skills
            
        Returns:
            Dict with categorized skills
        """
        if not text:
            logger.warning("Empty text provided for skill extraction")
            return self._empty_result()
        
        logger.info("Extracting skills from text")
        
        # Find all skill matches
        matches = self.skill_pattern.findall(text.lower())
        
        # Count occurrences
        skill_counts = Counter(matches)
        
        # Categorize skills
        categorized = {
            'programming_languages': [],
            'frameworks': [],
            'cloud_devops': [],
            'databases': [],
            'data_tools': [],
            'methodologies': [],
            'soft_skills': [],
            'all_technical': []
        }
        
        for skill, count in skill_counts.items():
            # Normalize skill
            skill_normalized = skill.lower().strip()
            
            # Categorize
            if skill_normalized in self.programming_languages:
                categorized['programming_languages'].append(skill)
            if skill_normalized in self.frameworks:
                categorized['frameworks'].append(skill)
            if skill_normalized in self.cloud_devops:
                categorized['cloud_devops'].append(skill)
            if skill_normalized in self.databases:
                categorized['databases'].append(skill)
            if skill_normalized in self.data_tools:
                categorized['data_tools'].append(skill)
            if skill_normalized in self.methodologies:
                categorized['methodologies'].append(skill)
            if include_soft_skills and skill_normalized in self.soft_skills:
                categorized['soft_skills'].append(skill)
        
        # Remove duplicates and sort
        for category in categorized:
            categorized[category] = sorted(list(set(categorized[category])))
        
        # Combine all technical skills
        categorized['all_technical'] = sorted(list(set(
            categorized['programming_languages'] +
            categorized['frameworks'] +
            categorized['cloud_devops'] +
            categorized['databases'] +
            categorized['data_tools'] +
            categorized['methodologies']
        )))
        
        logger.info(f"Extracted {len(categorized['all_technical'])} technical skills")
        
        return categorized
    
    def _empty_result(self) -> Dict[str, List[str]]:
        """Return empty result structure"""
        return {
            'programming_languages': [],
            'frameworks': [],
            'cloud_devops': [],
            'databases': [],
            'data_tools': [],
            'methodologies': [],
            'soft_skills': [],
            'all_technical': []
        }
    
    def match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        """
        Match resume skills against job requirements
        
        Args:
            resume_skills: List of skills from resume
            job_skills: List of required skills from job
            
        Returns:
            Dict with matching statistics
        """
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        
        matched = resume_set & job_set
        missing = job_set - resume_set
        extra = resume_set - job_set
        
        match_percentage = (len(matched) / len(job_set) * 100) if job_set else 0
        
        result = {
            'matched_skills': sorted(list(matched)),
            'missing_skills': sorted(list(missing)),
            'extra_skills': sorted(list(extra)),
            'match_count': len(matched),
            'total_required': len(job_set),
            'match_percentage': round(match_percentage, 1)
        }
        
        logger.info(f"Skill match: {len(matched)}/{len(job_set)} ({match_percentage:.1f}%)")
        
        return result


# Convenience function for quick extraction
def extract_skills(text: str, include_soft_skills: bool = False) -> Dict[str, List[str]]:
    """
    Quick function to extract skills from text
    
    Args:
        text: Resume or job description text
        include_soft_skills: Whether to include soft skills
        
    Returns:
        Dict with categorized skills
    """
    extractor = SkillExtractor()
    return extractor.extract_skills(text, include_soft_skills)
