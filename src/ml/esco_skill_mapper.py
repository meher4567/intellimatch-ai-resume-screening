"""
ESCO Skills Mapper - Maps extracted skills to ESCO taxonomy

This module provides functionality to:
1. Map raw extracted skills to standardized ESCO skills
2. Validate skills against ESCO taxonomy
3. Handle skill variants and aliases
4. Provide confidence scores for mappings
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class ESCOSkillMapper:
    """Maps extracted skills to ESCO taxonomy for validation and standardization"""
    
    def __init__(self, esco_path: str = "data/skills/validated_skills.json"):
        """
        Initialize ESCO mapper with taxonomy
        
        Args:
            esco_path: Path to ESCO skills JSON file
        """
        self.esco_path = Path(esco_path)
        self.esco_skills = {}
        self.skill_variants = {}  # Maps variants to canonical ESCO skills
        self.category_map = {}    # Maps skills to categories
        
        self._load_esco_taxonomy()
        self._build_variant_index()
        
        logger.info(f"Loaded {len(self.esco_skills)} ESCO skills")
    
    def _load_esco_taxonomy(self):
        """Load ESCO taxonomy from JSON file"""
        try:
            with open(self.esco_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                if 'skills' in data:
                    skills = data['skills']
                elif 'categories' in data:
                    # Flatten categorized skills
                    skills = []
                    for category, cat_skills in data['categories'].items():
                        for skill in cat_skills:
                            skill_data = skill if isinstance(skill, dict) else {'name': skill}
                            skill_data['category'] = category
                            skills.append(skill_data)
                else:
                    skills = list(data.values())[0] if data else []
            else:
                skills = data
            
            # Build skill index
            for idx, skill in enumerate(skills):
                if isinstance(skill, str):
                    skill_name = skill
                    self.esco_skills[skill_name.lower()] = {
                        'id': f'ESCO_{idx}',
                        'name': skill_name,
                        'category': 'General',
                        'aliases': []
                    }
                elif isinstance(skill, dict):
                    skill_name = skill.get('name', skill.get('skill', ''))
                    self.esco_skills[skill_name.lower()] = {
                        'id': skill.get('id', f'ESCO_{idx}'),
                        'name': skill_name,
                        'category': skill.get('category', 'General'),
                        'aliases': skill.get('aliases', [])
                    }
                    
                    # Map category
                    self.category_map[skill_name.lower()] = skill.get('category', 'General')
            
        except FileNotFoundError:
            logger.warning(f"ESCO file not found: {self.esco_path}")
            self.esco_skills = {}
        except Exception as e:
            logger.error(f"Error loading ESCO taxonomy: {e}")
            self.esco_skills = {}
    
    def _build_variant_index(self):
        """Build index of skill variants for fast lookup"""
        for skill_key, skill_data in self.esco_skills.items():
            # Add canonical name
            self.skill_variants[skill_key] = skill_key
            
            # Add aliases
            for alias in skill_data.get('aliases', []):
                self.skill_variants[alias.lower()] = skill_key
            
            # Add common variants
            skill_name = skill_data['name']
            
            # Without spaces: "JavaScript" -> "javascript"
            no_space = skill_name.replace(' ', '').lower()
            if no_space != skill_key:
                self.skill_variants[no_space] = skill_key
            
            # With dots: "Node.js" -> "nodejs"
            no_dots = skill_name.replace('.', '').lower()
            if no_dots != skill_key:
                self.skill_variants[no_dots] = skill_key
            
            # Common abbreviations
            if 'javascript' in skill_key:
                self.skill_variants['js'] = skill_key
            elif 'typescript' in skill_key:
                self.skill_variants['ts'] = skill_key
            elif 'python' in skill_key:
                self.skill_variants['py'] = skill_key
    
    def map_skill(self, skill: str, threshold: float = 0.8) -> Optional[Dict]:
        """
        Map a single skill to ESCO taxonomy
        
        Args:
            skill: Raw skill string (e.g., "python", "react")
            threshold: Minimum confidence for fuzzy matching
        
        Returns:
            Dict with mapping info or None if no match:
            {
                'original': 'python',
                'esco_skill': 'Python Programming',
                'esco_id': 'ESCO_123',
                'confidence': 0.95,
                'category': 'Programming Languages',
                'match_type': 'exact|variant|fuzzy'
            }
        """
        if not skill or not isinstance(skill, str):
            return None
        
        skill_lower = skill.strip().lower()
        
        # 1. Exact match
        if skill_lower in self.esco_skills:
            skill_data = self.esco_skills[skill_lower]
            return {
                'original': skill,
                'esco_skill': skill_data['name'],
                'esco_id': skill_data['id'],
                'confidence': 1.0,
                'category': skill_data['category'],
                'match_type': 'exact'
            }
        
        # 2. Variant match
        if skill_lower in self.skill_variants:
            canonical_key = self.skill_variants[skill_lower]
            skill_data = self.esco_skills[canonical_key]
            return {
                'original': skill,
                'esco_skill': skill_data['name'],
                'esco_id': skill_data['id'],
                'confidence': 0.95,
                'category': skill_data['category'],
                'match_type': 'variant'
            }
        
        # 3. Fuzzy match (for typos or variations)
        best_match, confidence = self._fuzzy_match(skill_lower)
        if best_match and confidence >= threshold:
            skill_data = self.esco_skills[best_match]
            return {
                'original': skill,
                'esco_skill': skill_data['name'],
                'esco_id': skill_data['id'],
                'confidence': confidence,
                'category': skill_data['category'],
                'match_type': 'fuzzy'
            }
        
        return None
    
    def _fuzzy_match(self, skill: str) -> Tuple[Optional[str], float]:
        """
        Find best fuzzy match for skill
        
        Returns:
            Tuple of (best_match_key, confidence_score)
        """
        best_match = None
        best_score = 0.0
        
        for esco_key in self.esco_skills.keys():
            score = SequenceMatcher(None, skill, esco_key).ratio()
            if score > best_score:
                best_score = score
                best_match = esco_key
        
        return best_match, best_score
    
    def map_skills_batch(self, skills: List[str], threshold: float = 0.8) -> List[Dict]:
        """
        Map multiple skills to ESCO taxonomy
        
        Args:
            skills: List of raw skill strings
            threshold: Minimum confidence for fuzzy matching
        
        Returns:
            List of mapping dicts (only successful matches)
        """
        results = []
        for skill in skills:
            mapping = self.map_skill(skill, threshold)
            if mapping:
                results.append(mapping)
        
        return results
    
    def is_valid_skill(self, skill: str, threshold: float = 0.8) -> bool:
        """
        Check if skill exists in ESCO taxonomy
        
        Args:
            skill: Skill string to validate
            threshold: Minimum confidence for fuzzy matching
        
        Returns:
            True if skill maps to ESCO, False otherwise
        """
        return self.map_skill(skill, threshold) is not None
    
    def filter_valid_skills(self, skills: List[str], threshold: float = 0.8) -> List[str]:
        """
        Filter list to only include ESCO-validated skills
        
        Args:
            skills: List of raw skills
            threshold: Minimum confidence for validation
        
        Returns:
            List of validated skill names (original or ESCO standardized)
        """
        valid_skills = []
        for skill in skills:
            mapping = self.map_skill(skill, threshold)
            if mapping:
                # Use ESCO standardized name
                valid_skills.append(mapping['esco_skill'])
        
        return valid_skills
    
    def get_skill_category(self, skill: str) -> Optional[str]:
        """Get ESCO category for a skill"""
        mapping = self.map_skill(skill)
        return mapping['category'] if mapping else None
    
    def get_statistics(self) -> Dict:
        """Get mapper statistics"""
        categories = {}
        for skill_data in self.esco_skills.values():
            cat = skill_data['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_skills': len(self.esco_skills),
            'total_variants': len(self.skill_variants),
            'categories': categories
        }


class SkillValidator:
    """Validates and filters skills using ESCO taxonomy"""
    
    def __init__(self, mapper: ESCOSkillMapper):
        """
        Initialize validator with ESCO mapper
        
        Args:
            mapper: ESCOSkillMapper instance
        """
        self.mapper = mapper
    
    def validate_skills(
        self, 
        skills: List[str], 
        threshold: float = 0.8,
        return_mappings: bool = False
    ) -> List[str] | List[Dict]:
        """
        Validate and standardize skills
        
        Args:
            skills: List of raw skills
            threshold: Minimum confidence for validation
            return_mappings: If True, return full mapping dicts
        
        Returns:
            List of validated skills (names or mapping dicts)
        """
        if return_mappings:
            return self.mapper.map_skills_batch(skills, threshold)
        else:
            return self.mapper.filter_valid_skills(skills, threshold)
    
    def validate_resume_skills(
        self, 
        resume_data: Dict,
        skill_key: str = 'skills',
        threshold: float = 0.8
    ) -> Dict:
        """
        Validate skills in resume data structure
        
        Args:
            resume_data: Resume dict with skills
            skill_key: Key containing skills (e.g., 'skills', 'all_skills')
            threshold: Minimum confidence
        
        Returns:
            Updated resume data with validated skills
        """
        # Handle nested skills structure
        if isinstance(resume_data.get(skill_key), dict):
            if 'all_skills' in resume_data[skill_key]:
                raw_skills = resume_data[skill_key]['all_skills']
            else:
                raw_skills = []
        elif isinstance(resume_data.get(skill_key), list):
            raw_skills = resume_data[skill_key]
        else:
            raw_skills = []
        
        # Validate
        validated_mappings = self.mapper.map_skills_batch(raw_skills, threshold)
        
        # Update resume data
        validated_skills = [m['esco_skill'] for m in validated_mappings]
        
        # Categorize by ESCO category
        by_category = {}
        for mapping in validated_mappings:
            cat = mapping['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(mapping['esco_skill'])
        
        # Build validated structure
        resume_data['validated_skills'] = {
            'all_skills': validated_skills,
            'by_category': by_category,
            'total_count': len(validated_skills),
            'validation_metadata': {
                'original_count': len(raw_skills),
                'validated_count': len(validated_skills),
                'threshold': threshold,
                'mappings': validated_mappings
            }
        }
        
        return resume_data
