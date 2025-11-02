"""
Organization/Company Extractor using NER
Extracts companies, institutions, and organizations from resumes
"""

from typing import List, Dict, Set, Optional, Tuple
import logging
from dataclasses import dataclass
import re
from .ner_extractor import NERExtractor

logger = logging.getLogger(__name__)


@dataclass
class OrganizationMatch:
    """Represents an extracted organization with metadata"""
    name: str
    category: str  # 'company', 'university', 'institution', 'other'
    confidence: float
    context: str  # Surrounding text for validation
    section: Optional[str] = None  # Which section it was found in


class OrganizationExtractor:
    """
    Extract companies and organizations using NER + context rules
    
    Features:
    - NER-based organization extraction
    - Context-aware categorization (company vs university)
    - Section-aware extraction (work vs education)
    - Confidence scoring
    - Deduplication and normalization
    """
    
    def __init__(self):
        """Initialize organization extractor"""
        self.ner_extractor = NERExtractor()
        
        # Known organization types/patterns
        self.company_indicators = {
            'inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co',
            'group', 'technologies', 'tech', 'software', 'systems',
            'solutions', 'services', 'consulting', 'partners', 'labs'
        }
        
        self.university_indicators = {
            'university', 'college', 'institute', 'school', 'academy',
            'iit', 'nit', 'mit', 'stanford', 'berkeley', 'cambridge'
        }
        
        # Section keywords for context
        self.work_section_keywords = {
            'experience', 'work', 'employment', 'professional', 'career',
            'internship', 'position', 'role', 'job'
        }
        
        self.education_section_keywords = {
            'education', 'academic', 'qualification', 'degree', 'university',
            'college', 'school', 'learning'
        }
        
        # Common false positives to filter
        self.false_positives = {
            'resume', 'cv', 'curriculum vitae', 'profile', 'summary',
            'skills', 'projects', 'references', 'languages', 'interests',
            'objective', 'github', 'linkedin', 'email', 'phone',
            # Technical skills that NER mistakes for orgs
            'python', 'java', 'javascript', 'sql', 'c++', 'c#', 'ruby', 'php',
            'react', 'angular', 'vue', 'django', 'flask', 'spring',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
            'git', 'svn', 'github', 'gitlab', 'bitbucket',
            # Generic action words
            'conducted', 'implemented', 'developed', 'created', 'built',
            'designed', 'managed', 'led', 'presented', 'analyzed',
            'collaborated', 'worked', 'assisted', 'helped', 'supported',
            # Generic educational terms
            'coursework', 'courses', 'mathematics', 'physics', 'chemistry',
            'biology', 'economics', 'statistics', 'calculus', 'algebra',
            'quantum mechanics', 'classical mechanics', 'thermodynamics',
            'electromagnetism', 'optics', 'discrete structures',
            # Tools/products (not companies)
            'matlab', 'labview', 'excel', 'word', 'powerpoint',
            'photoshop', 'illustrator', 'figma', 'sketch',
            'jupyter', 'pycharm', 'vscode', 'eclipse', 'visual studio',
            'tableau', 'power bi', 'looker', 'metabase',
            # Cloud services (not companies)
            'ec2', 's3', 'sagemaker', 'lambda', 'bigquery', 'vertex ai',
            # Generic concepts
            'data science', 'data analysis', 'software engineering',
            'web development', 'mobile development', 'database management',
            'operating systems', 'computer science', 'artificial intelligence',
            # Date/time related
            'last updated', 'updated on', 'current', 'present',
            # Other
            'experience', 'education', 'awards', 'publications',
            'technical skills', 'programming', 'tools', 'utilities'
        }
        
        logger.info("OrganizationExtractor initialized")
    
    def extract_organizations(
        self, 
        text: str, 
        sections: Optional[Dict[str, str]] = None
    ) -> List[OrganizationMatch]:
        """
        Extract organizations from resume text
        
        Args:
            text: Resume text
            sections: Optional dict of section_name -> section_content
            
        Returns:
            List of OrganizationMatch objects
        """
        logger.info("Extracting organizations from text")
        
        # Extract ORG entities using NER
        org_entities = self.ner_extractor.extract_organizations(text)
        
        if not org_entities:
            logger.warning("No organizations found by NER")
            return []
        
        matches = []
        seen = set()
        
        for entity in org_entities:
            # Clean the organization name
            org_name = self._clean_org_name(entity.text)
            
            if not org_name:
                continue
            
            # Get context for validation
            context = self._get_context(text, entity.text, window=100)
            
            # Validate it's actually an organization
            if not self._is_valid_organization(org_name, context):
                continue
            
            # Skip duplicates (case-insensitive)
            if org_name.lower() in seen:
                continue
            seen.add(org_name.lower())
            
            # Categorize the organization (context already retrieved above)
            category = self._categorize_organization(org_name, context)
            
            # Determine which section it's from
            section = self._identify_section(context, sections) if sections else None
            
            # Calculate confidence
            confidence = self._calculate_confidence(org_name, context, category, entity.confidence)
            
            matches.append(OrganizationMatch(
                name=org_name,
                category=category,
                confidence=confidence,
                context=context[:100],  # First 100 chars of context
                section=section
            ))
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"Extracted {len(matches)} organizations")
        return matches
    
    def extract_companies(
        self, 
        text: str, 
        sections: Optional[Dict[str, str]] = None
    ) -> List[OrganizationMatch]:
        """
        Extract only companies (not universities)
        
        Args:
            text: Resume text
            sections: Optional dict of sections
            
        Returns:
            List of companies
        """
        all_orgs = self.extract_organizations(text, sections)
        companies = [org for org in all_orgs if org.category == 'company']
        logger.info(f"Filtered to {len(companies)} companies")
        return companies
    
    def extract_universities(
        self, 
        text: str, 
        sections: Optional[Dict[str, str]] = None
    ) -> List[OrganizationMatch]:
        """
        Extract only universities/educational institutions
        
        Args:
            text: Resume text
            sections: Optional dict of sections
            
        Returns:
            List of universities
        """
        all_orgs = self.extract_organizations(text, sections)
        universities = [org for org in all_orgs if org.category == 'university']
        logger.info(f"Filtered to {len(universities)} universities")
        return universities
    
    def _clean_org_name(self, name: str) -> str:
        """Clean organization name"""
        if not name:
            return ""
        
        # Remove special characters but keep alphanumeric, spaces, hyphens, dots, ampersands
        name = re.sub(r'[^a-zA-Z0-9\s\-\.&,]', '', name)
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Capitalize properly
        name = name.strip()
        
        return name
    
    def _is_valid_organization(self, org_name: str, context: str) -> bool:
        """
        Validate if extracted text is actually an organization
        
        Args:
            org_name: Organization name
            context: Surrounding text
            
        Returns:
            True if valid organization, False otherwise
        """
        org_lower = org_name.lower()
        
        # Filter false positives
        if org_lower in self.false_positives:
            return False
        
        # Check if any false positive is a substring
        for fp in self.false_positives:
            if fp in org_lower:
                return False
        
        # Too short (single letter or very short acronyms are usually not orgs)
        if len(org_name) <= 2:
            return False
        
        # All uppercase single words are likely acronyms/skills (AWS, SQL, NLP)
        # Unless they have clear company indicators
        if org_name.isupper() and ' ' not in org_name:
            if not any(ind in org_lower for ind in self.company_indicators | self.university_indicators):
                return False
        
        # Starting with lowercase is suspicious
        if org_name[0].islower():
            return False
        
        # Common skill/tech terms that slip through
        tech_patterns = [
            r'^[A-Z]+\d+$',  # CS4, EC2, S3
            r'^\d+',  # Starts with number
            r'^(The|A|An)\s+(Google|Microsoft|Amazon|Apple)',  # "The Google Maps SDK"
        ]
        
        for pattern in tech_patterns:
            if re.match(pattern, org_name):
                return False
        
        # If it's a single word, check for company indicators
        if ' ' not in org_name:
            # Single words need strong indicators
            has_company_ind = any(ind in org_lower for ind in self.company_indicators)
            has_university_ind = any(ind in org_lower for ind in self.university_indicators)
            
            if not (has_company_ind or has_university_ind):
                # Reject unless it's a well-known company pattern
                # (All caps with 3+ letters, ends with Inc/Corp/Ltd)
                if not (org_name.isupper() and len(org_name) >= 3):
                    return False
        
        return True
    
    def _categorize_organization(self, org_name: str, context: str) -> str:
        """
        Categorize organization as company, university, or institution
        
        Args:
            org_name: Organization name
            context: Surrounding text
            
        Returns:
            Category: 'company', 'university', 'institution', or 'other'
        """
        org_lower = org_name.lower()
        context_lower = context.lower()
        
        # Check for university indicators
        if any(indicator in org_lower for indicator in self.university_indicators):
            return 'university'
        
        # Check context for education keywords
        if any(keyword in context_lower for keyword in self.education_section_keywords):
            if 'degree' in context_lower or 'bachelor' in context_lower or 'master' in context_lower:
                return 'university'
        
        # Check for company indicators
        if any(indicator in org_lower for indicator in self.company_indicators):
            return 'company'
        
        # Check context for work keywords
        if any(keyword in context_lower for keyword in self.work_section_keywords):
            return 'company'
        
        # Default to institution
        return 'institution'
    
    def _identify_section(self, context: str, sections: Dict[str, str]) -> Optional[str]:
        """
        Identify which section the organization is from
        
        Args:
            context: Context around the organization
            sections: Dict of section_name -> section_content
            
        Returns:
            Section name or None
        """
        if not sections:
            return None
        
        # Check if context appears in any section
        for section_name, section_content in sections.items():
            if context in section_content:
                return section_name
        
        return None
    
    def _get_context(self, text: str, entity_text: str, window: int = 100) -> str:
        """
        Get context around an entity
        
        Args:
            text: Full text
            entity_text: Entity to find
            window: Characters before/after
            
        Returns:
            Context string
        """
        # Find the entity in text
        idx = text.find(entity_text)
        if idx == -1:
            return ""
        
        # Get surrounding context
        start = max(0, idx - window)
        end = min(len(text), idx + len(entity_text) + window)
        
        return text[start:end]
    
    def _calculate_confidence(
        self, 
        org_name: str, 
        context: str, 
        category: str,
        ner_confidence: float
    ) -> float:
        """
        Calculate confidence score for organization extraction
        
        Args:
            org_name: Organization name
            context: Surrounding text
            category: Categorization (company, university, etc.)
            ner_confidence: Confidence from NER model
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        confidence = ner_confidence  # Start with NER confidence
        
        org_lower = org_name.lower()
        context_lower = context.lower()
        
        # Boost if has clear indicators
        if category == 'company':
            if any(ind in org_lower for ind in self.company_indicators):
                confidence = min(1.0, confidence + 0.1)
        
        if category == 'university':
            if any(ind in org_lower for ind in self.university_indicators):
                confidence = min(1.0, confidence + 0.1)
        
        # Boost if context has relevant keywords
        if category == 'company' and any(kw in context_lower for kw in self.work_section_keywords):
            confidence = min(1.0, confidence + 0.05)
        
        if category == 'university' and any(kw in context_lower for kw in self.education_section_keywords):
            confidence = min(1.0, confidence + 0.05)
        
        # Penalize very short names (likely false positives)
        if len(org_name) < 3:
            confidence *= 0.5
        
        # Penalize single words without indicators
        if ' ' not in org_name and not any(ind in org_lower for ind in self.company_indicators | self.university_indicators):
            confidence *= 0.7
        
        return round(confidence, 2)
    
    def get_organization_summary(self, matches: List[OrganizationMatch]) -> Dict:
        """
        Get summary statistics about extracted organizations
        
        Args:
            matches: List of OrganizationMatch objects
            
        Returns:
            Summary dict with counts and categories
        """
        return {
            'total': len(matches),
            'companies': sum(1 for m in matches if m.category == 'company'),
            'universities': sum(1 for m in matches if m.category == 'university'),
            'institutions': sum(1 for m in matches if m.category == 'institution'),
            'other': sum(1 for m in matches if m.category == 'other'),
            'avg_confidence': sum(m.confidence for m in matches) / len(matches) if matches else 0,
            'by_category': {
                category: [m.name for m in matches if m.category == category]
                for category in ['company', 'university', 'institution', 'other']
            }
        }


# Convenience function
def extract_organizations_from_text(text: str) -> List[str]:
    """
    Extract organization names from text
    
    Args:
        text: Resume text
        
    Returns:
        List of organization names
    """
    extractor = OrganizationExtractor()
    matches = extractor.extract_organizations(text)
    return [m.name for m in matches]
