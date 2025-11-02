"""
Skill Extractor Service - Extract and normalize skills from resumes
Uses comprehensive skill database with fuzzy matching and categorization
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from fuzzywuzzy import fuzz
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents an extracted skill"""
    name: str  # Normalized name
    original: str  # Original text from resume
    category: str  # Category (programming, web_framework, etc.)
    confidence: float  # 0.0 to 1.0
    mentions: int = 1  # Number of times mentioned


class SkillExtractor:
    """
    Extract and normalize skills from resume text
    """
    
    def __init__(self, skills_db_path: Optional[str] = None):
        """
        Initialize Skill Extractor
        
        Args:
            skills_db_path: Path to skills database JSON (optional)
        """
        self.skills_db = {}
        self.skill_aliases = {}  # alias -> normalized name
        self.skill_categories = {}  # normalized name -> category
        
        # Load skills database
        if skills_db_path is None:
            # Default path - go up to project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
            skills_db_path = project_root / "data" / "skills" / "skills_database.json"
        
        self.load_skills_database(str(skills_db_path))
    
    def load_skills_database(self, db_path: str):
        """
        Load skills database from JSON file
        
        Args:
            db_path: Path to skills database JSON
        """
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.skills_db = json.load(f)
            
            # Build alias lookup
            for category, skills in self.skills_db.items():
                for skill in skills:
                    normalized_name = skill['name']
                    category_type = skill['category']
                    
                    # Store category
                    self.skill_categories[normalized_name.lower()] = category_type
                    
                    # Store all aliases
                    for alias in skill['aliases']:
                        self.skill_aliases[alias.lower()] = normalized_name
            
            total_skills = sum(len(skills) for skills in self.skills_db.values())
            logger.info(f"Loaded {total_skills} skills from database")
            
        except FileNotFoundError:
            logger.warning(f"Skills database not found at {db_path}. Using empty database.")
        except Exception as e:
            logger.error(f"Error loading skills database: {e}")
    
    def normalize_skill(self, skill_text: str) -> Optional[str]:
        """
        Normalize a skill name using the alias database
        
        Args:
            skill_text: Raw skill text
            
        Returns:
            Normalized skill name or None if not found
        """
        skill_lower = skill_text.lower().strip()
        
        # Direct match
        if skill_lower in self.skill_aliases:
            return self.skill_aliases[skill_lower]
        
        # Try fuzzy matching
        best_match = self.fuzzy_match_skill(skill_text)
        if best_match:
            return best_match
        
        return None
    
    def fuzzy_match_skill(self, skill_text: str, threshold: int = 85) -> Optional[str]:
        """
        Fuzzy match a skill name against known skills
        
        Args:
            skill_text: Raw skill text
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Normalized skill name or None
        """
        skill_lower = skill_text.lower().strip()
        best_score = 0
        best_match = None
        
        for alias, normalized in self.skill_aliases.items():
            score = fuzz.ratio(skill_lower, alias)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = normalized
        
        return best_match
    
    def get_skill_category(self, skill_name: str) -> Optional[str]:
        """
        Get the category of a skill
        
        Args:
            skill_name: Normalized skill name
            
        Returns:
            Category name or None
        """
        return self.skill_categories.get(skill_name.lower())
    
    def extract_skills_from_text(self, text: str) -> List[Skill]:
        """
        Extract skills from text using pattern matching
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of Skill objects
        """
        found_skills = {}  # normalized_name -> Skill
        text_lower = text.lower()
        
        # Check each skill alias
        for alias, normalized in self.skill_aliases.items():
            # Word boundary pattern for exact matches
            pattern = r'\b' + re.escape(alias) + r'\b'
            
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            
            if matches:
                if normalized not in found_skills:
                    category = self.skill_categories.get(normalized.lower(), 'other')
                    found_skills[normalized] = Skill(
                        name=normalized,
                        original=matches[0].group(),  # First match original text
                        category=category,
                        confidence=1.0,  # Direct match = high confidence
                        mentions=len(matches)
                    )
                else:
                    # Increment mention count
                    found_skills[normalized].mentions += len(matches)
        
        return list(found_skills.values())
    
    def extract_skills_from_sections(self, sections: Dict[str, str]) -> List[Skill]:
        """
        Extract skills from resume sections with weighted importance
        
        Args:
            sections: Dictionary of section_type -> section_text
            
        Returns:
            List of Skill objects
        """
        all_skills = {}  # normalized_name -> Skill
        
        # Section weights (skills section is most important)
        section_weights = {
            'skills': 1.0,
            'experience': 0.8,
            'projects': 0.9,
            'summary': 0.7,
            'education': 0.6,
        }
        
        for section_type, section_text in sections.items():
            if not section_text:
                continue
            
            skills = self.extract_skills_from_text(section_text)
            weight = section_weights.get(section_type, 0.5)
            
            for skill in skills:
                if skill.name not in all_skills:
                    # New skill
                    skill.confidence *= weight
                    all_skills[skill.name] = skill
                else:
                    # Already found - increase confidence and mentions
                    existing = all_skills[skill.name]
                    existing.mentions += skill.mentions
                    # Boost confidence (capped at 1.0)
                    existing.confidence = min(1.0, existing.confidence + (0.1 * weight))
        
        return list(all_skills.values())
    
    def categorize_skills(self, skills: List[Skill]) -> Dict[str, List[Skill]]:
        """
        Group skills by category
        
        Args:
            skills: List of Skill objects
            
        Returns:
            Dictionary of category -> List[Skill]
        """
        categorized = defaultdict(list)
        
        for skill in skills:
            categorized[skill.category].append(skill)
        
        return dict(categorized)
    
    def get_top_skills(self, skills: List[Skill], top_n: int = 10) -> List[Skill]:
        """
        Get top N skills sorted by confidence and mentions
        
        Args:
            skills: List of Skill objects
            top_n: Number of top skills to return
            
        Returns:
            Sorted list of top skills
        """
        # Sort by confidence * mentions (weighted score)
        sorted_skills = sorted(
            skills,
            key=lambda s: s.confidence * (1 + s.mentions * 0.1),
            reverse=True
        )
        
        return sorted_skills[:top_n]
    
    def extract_and_categorize(self, text: str = None, sections: Dict[str, str] = None) -> Dict:
        """
        Complete skill extraction and categorization pipeline
        
        Args:
            text: Resume text (optional if sections provided)
            sections: Resume sections dict (optional if text provided)
            
        Returns:
            Dictionary with categorized skills and statistics
        """
        # Extract skills
        if sections:
            skills = self.extract_skills_from_sections(sections)
        elif text:
            skills = self.extract_skills_from_text(text)
        else:
            return {}
        
        # Categorize
        categorized = self.categorize_skills(skills)
        top_skills = self.get_top_skills(skills, top_n=15)
        
        # Build result
        result = {
            'total_skills': len(skills),
            'categories': {},
            'top_skills': [
                {
                    'name': s.name,
                    'category': s.category,
                    'confidence': round(s.confidence, 2),
                    'mentions': s.mentions
                }
                for s in top_skills
            ],
            'all_skills': [s.name for s in skills]
        }
        
        # Add category breakdowns
        for category, category_skills in categorized.items():
            result['categories'][category] = [
                {
                    'name': s.name,
                    'confidence': round(s.confidence, 2),
                    'mentions': s.mentions
                }
                for s in category_skills
            ]
        
        return result


def test_skill_extractor():
    """Test skill extractor"""
    extractor = SkillExtractor()
    
    print(f"✅ Loaded {len(extractor.skill_aliases)} skill aliases")
    print()
    
    # Test text
    test_text = """
    I have 5 years of experience in Python, Java, and JavaScript development.
    I'm proficient in Django, Flask, and React frameworks.
    I've worked with AWS (EC2, S3, Lambda), Docker, and Kubernetes.
    Strong skills in Machine Learning using TensorFlow and PyTorch.
    Experienced with PostgreSQL, MongoDB, and Redis databases.
    Familiar with Git, GitHub Actions, and CI/CD pipelines.
    """
    
    print("="*60)
    print("Test Text:")
    print("="*60)
    print(test_text)
    
    print("\n" + "="*60)
    print("Extracted Skills:")
    print("="*60)
    
    skills = extractor.extract_skills_from_text(test_text)
    
    for skill in sorted(skills, key=lambda s: s.name):
        print(f"  {skill.name:25s} | {skill.category:20s} | Mentions: {skill.mentions}")
    
    print(f"\nTotal: {len(skills)} skills extracted")
    
    print("\n" + "="*60)
    print("Skills by Category:")
    print("="*60)
    
    categorized = extractor.categorize_skills(skills)
    
    for category, category_skills in categorized.items():
        print(f"\n{category.upper()}:")
        for skill in category_skills:
            print(f"  - {skill.name} (confidence: {skill.confidence:.2f})")
    
    print("\n" + "="*60)
    print("Top 10 Skills:")
    print("="*60)
    
    top_skills = extractor.get_top_skills(skills, top_n=10)
    
    for i, skill in enumerate(top_skills, 1):
        score = skill.confidence * (1 + skill.mentions * 0.1)
        print(f"{i:2d}. {skill.name:20s} | Score: {score:.2f}")
    
    # Test normalization
    print("\n" + "="*60)
    print("Skill Normalization Test:")
    print("="*60)
    
    test_normalize = ["py", "js", "k8s", "ML", "postgres"]
    for skill in test_normalize:
        normalized = extractor.normalize_skill(skill)
        print(f"  '{skill}' → '{normalized}'")


if __name__ == "__main__":
    test_skill_extractor()
