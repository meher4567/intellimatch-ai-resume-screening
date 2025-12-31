"""
Phase 3: Enhanced Skill Matcher with Fuzzy Matching
Combines semantic embeddings with RapidFuzz for maximum precision

Edge Cases Handled:
- Empty skill lists
- None values in skills
- Mixed data types in skill lists
- Unicode and special characters
- Extremely long skill names
- Duplicate skills
- Dict vs list skill formats
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Any, Tuple, Optional, Union
from rapidfuzz import fuzz, process
from src.ml.skill_embedder import SkillEmbedder
from src.utils.logger import get_logger
from src.ml.utils import (
    TextValidator, 
    with_fallback, 
    safe_list, 
    ErrorCategory,
    GracefulDegradation
)

logger = get_logger(__name__)


def _safe_extract_skills(skills_data: Any) -> List[str]:
    """
    Safely extract skills list from various input formats
    
    Handles:
    - None -> []
    - List of strings -> filtered list
    - Dict with 'all_skills' key -> extracted list
    - Single string -> [string]
    - Non-string items -> converted or filtered
    """
    if skills_data is None:
        return []
    
    # Handle dict format (new format)
    if isinstance(skills_data, dict):
        skills_data = skills_data.get('all_skills', 
                                     skills_data.get('top_skills', 
                                                    skills_data.get('skills', [])))
    
    # Handle single string
    if isinstance(skills_data, str):
        return [skills_data.strip()] if skills_data.strip() else []
    
    # Handle list/tuple/set
    if not isinstance(skills_data, (list, tuple, set)):
        return []
    
    # Filter and clean skills
    cleaned = []
    for skill in skills_data:
        if skill is None:
            continue
        if isinstance(skill, str):
            cleaned_skill = skill.strip()
            if cleaned_skill and len(cleaned_skill) <= 100:  # Max skill length
                cleaned.append(cleaned_skill)
        elif isinstance(skill, dict):
            # Handle skill dict format {'name': 'Python', 'level': 'expert'}
            skill_name = skill.get('name', skill.get('skill', ''))
            if isinstance(skill_name, str) and skill_name.strip():
                cleaned.append(skill_name.strip())
        else:
            # Try to convert to string
            try:
                skill_str = str(skill).strip()
                if skill_str and len(skill_str) <= 100:
                    cleaned.append(skill_str)
            except:
                pass
    
    return cleaned


class EnhancedSkillMatcher:
    """
    Advanced skill matching using three strategies:
    1. Exact matching (fastest, 100% precision)
    2. Fuzzy matching with RapidFuzz (catches typos/variations)
    3. Semantic matching with embeddings (catches synonyms/related skills)
    """
    
    # Common abbreviations and variations
    SKILL_ALIASES = {
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
        'dl': 'deep learning',
        'ci/cd': 'continuous integration',
        'cicd': 'continuous integration',
        'aws': 'amazon web services',
        'gcp': 'google cloud platform',
        'azure': 'microsoft azure',
        'k8s': 'kubernetes',
        'js': 'javascript',
        'ts': 'typescript',
        'postgres': 'postgresql',
        'mongo': 'mongodb',
        'api': 'application programming interface',
        'rest api': 'restful api',
        'restful api': 'restful api',
        'rest apis': 'restful api',
        'llm': 'large language model',
        'cnn': 'convolutional neural network',
        'rnn': 'recurrent neural network',
        # Node.js variations
        'node js': 'node.js',
        'nodejs': 'node.js',
        'node': 'node.js',
        # React variations
        'react js': 'reactjs',
        'react.js': 'reactjs',
        # Vue variations
        'vue js': 'vuejs',
        'vue.js': 'vuejs',
        # Python variations
        'python3': 'python',
        'python 3': 'python',
        'python 3.x': 'python',
        # SQL variations
        'mysql': 'mysql',
        'mssql': 'sql server',
        'ms sql': 'sql server',
        'sql server': 'sql server',
    }
    
    def __init__(self,
                 use_fuzzy: bool = True,
                 fuzzy_threshold: int = 85,
                 use_semantic: bool = True,
                 semantic_threshold: float = 0.70):
        """
        Initialize enhanced skill matcher
        
        Args:
            use_fuzzy: Enable fuzzy matching for typos/variations (default: True)
            fuzzy_threshold: Minimum fuzzy score (0-100, default: 85)
            use_semantic: Enable semantic matching with embeddings (default: True)
            semantic_threshold: Minimum semantic similarity (0-1, default: 0.70)
        """
        self.use_fuzzy = use_fuzzy
        self.fuzzy_threshold = max(0, min(100, fuzzy_threshold))  # Clamp to valid range
        self.use_semantic = use_semantic
        self.semantic_threshold = max(0.0, min(1.0, semantic_threshold))  # Clamp to valid range
        
        # Lazy load embedder to avoid initialization failures
        self._embedder = None
        self._embedder_initialized = False
        
        if use_semantic:
            try:
                self._embedder = SkillEmbedder()
                self._embedder_initialized = True
                logger.info("Enhanced SkillMatcher initialized with semantic matching")
            except Exception as e:
                logger.warning(f"Failed to initialize semantic embedder: {e}. Using fuzzy+exact only.")
                self.use_semantic = False
        else:
            logger.info("Enhanced SkillMatcher initialized without semantic matching")
    
    @property
    def embedder(self) -> Optional[SkillEmbedder]:
        """Lazy access to embedder with fallback"""
        if not self.use_semantic:
            return None
        if not self._embedder_initialized:
            try:
                self._embedder = SkillEmbedder()
                self._embedder_initialized = True
            except Exception as e:
                logger.warning(f"Embedder initialization failed: {e}")
                self.use_semantic = False
                return None
        return self._embedder
    
    def calculate_match_score(self,
                             candidate_skills: Union[List[str], Dict, Any],
                             required_skills: Union[List[str], Dict, Any],
                             optional_skills: Union[List[str], Dict, Any] = None) -> Dict[str, Any]:
        """
        Calculate skill match score using multi-strategy approach
        
        Handles edge cases:
        - Empty skill lists (returns 100% for no requirements, 0% for no candidate skills)
        - None values (treated as empty lists)
        - Mixed formats (dict with 'all_skills', single strings, etc.)
        - Invalid data types (safely converted or filtered)
        
        Args:
            candidate_skills: Skills from candidate resume (list, dict, or None)
            required_skills: Required skills from job posting (list, dict, or None)
            optional_skills: Optional/nice-to-have skills (list, dict, or None)
            
        Returns:
            Dict with score and detailed breakdown
        """
        # Edge Case: Safely extract and clean all skill lists
        candidate_skills = _safe_extract_skills(candidate_skills)
        required_skills = _safe_extract_skills(required_skills)
        optional_skills = _safe_extract_skills(optional_skills) if optional_skills else []
        
        # Edge Case: No required skills = 100% match (any candidate qualifies)
        if not required_skills and not optional_skills:
            logger.debug("No skills required - returning 100% match")
            return self._create_empty_result(score=100.0, message="No skills required")
        
        # Edge Case: Candidate has no skills
        if not candidate_skills:
            logger.debug("Candidate has no skills - returning 0% match")
            return self._create_empty_result(
                score=0.0, 
                message="Candidate has no skills",
                missing_required=required_skills,
                missing_optional=optional_skills
            )
        
        logger.debug(f"Matching {len(candidate_skills)} candidate skills against "
                    f"{len(required_skills)} required + {len(optional_skills)} optional")
        
        # Normalize and prepare skills with error handling
        try:
            normalized_candidates = {s: self._normalize_skill(s) for s in candidate_skills}
            normalized_required = {s: self._normalize_skill(s) for s in required_skills}
            normalized_optional = {s: self._normalize_skill(s) for s in optional_skills}
        except Exception as e:
            logger.error(f"Skill normalization failed: {e}")
            return self._create_empty_result(score=50.0, message=f"Normalization error: {e}")
        
        # Match required skills with graceful degradation
        try:
            required_results = self._match_skills(
                candidate_skills,
                required_skills,
                normalized_candidates,
                normalized_required
            )
        except Exception as e:
            logger.error(f"Required skills matching failed: {e}")
            required_results = {'matches': [], 'missing': required_skills, 'details': {}}
        
        # Match optional skills with graceful degradation
        try:
            optional_results = self._match_skills(
                candidate_skills,
                optional_skills,
                normalized_candidates,
                normalized_optional
            )
        except Exception as e:
            logger.warning(f"Optional skills matching failed: {e}")
            optional_results = {'matches': [], 'missing': optional_skills, 'details': {}}
        
        # Calculate coverage with safe division
        required_count = len(required_skills)
        optional_count = len(optional_skills)
        required_matched = len(required_results.get('matches', []))
        optional_matched = len(optional_results.get('matches', []))
        
        required_coverage = (required_matched / required_count * 100) if required_count > 0 else 100
        optional_coverage = (optional_matched / optional_count * 100) if optional_count > 0 else 0
        
        # Calculate weighted score (required: 80%, optional: 20%)
        if required_count > 0:
            score = (required_coverage * 0.8) + (optional_coverage * 0.2)
        else:
            score = optional_coverage
        
        # Clamp score to valid range
        score = max(0.0, min(100.0, score))
        
        # Aggregate results
        result = {
            'score': round(score, 2),
            'required_matches': required_results.get('matches', []),
            'optional_matches': optional_results.get('matches', []),
            'missing_required': required_results.get('missing', []),
            'missing_optional': optional_results.get('missing', []),
            'required_coverage': round(required_coverage, 2),
            'optional_coverage': round(optional_coverage, 2),
            'total_matched': len(required_results['matches']) + len(optional_results['matches']),
            'total_required': len(required_skills),
            'total_optional': len(optional_skills),
            'match_details': {
                'required': required_results['details'],
                'optional': optional_results['details']
            },
            'matching_strategies_used': {
                'exact': True,
                'fuzzy': self.use_fuzzy,
                'semantic': self.use_semantic
            }
        }
        
        logger.debug(f"Match score: {score:.2f}%, Required: {required_coverage:.1f}%, Optional: {optional_coverage:.1f}%")
        
        return result
    
    def _create_empty_result(self, 
                            score: float = 0.0, 
                            message: str = "",
                            missing_required: List[str] = None,
                            missing_optional: List[str] = None) -> Dict[str, Any]:
        """Create a standard empty/default result structure"""
        return {
            'score': round(max(0.0, min(100.0, score)), 2),
            'required_matches': [],
            'optional_matches': [],
            'missing_required': missing_required or [],
            'missing_optional': missing_optional or [],
            'required_coverage': 100.0 if score == 100.0 else 0.0,
            'optional_coverage': 0.0,
            'total_matched': 0,
            'total_required': len(missing_required) if missing_required else 0,
            'total_optional': len(missing_optional) if missing_optional else 0,
            'match_details': {'required': {}, 'optional': {}},
            'matching_strategies_used': {
                'exact': True,
                'fuzzy': self.use_fuzzy,
                'semantic': self.use_semantic
            },
            'message': message
        }
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill using alias dictionary with edge case handling"""
        if not skill or not isinstance(skill, str):
            return ""
        
        # Clean and normalize
        normalized = skill.lower().strip()
        
        # Remove excessive whitespace
        normalized = ' '.join(normalized.split())
        
        # Limit length
        if len(normalized) > 100:
            normalized = normalized[:100]
        
        return self.SKILL_ALIASES.get(normalized, normalized)
    
    def _match_skills(self,
                     candidate_skills: List[str],
                     target_skills: List[str],
                     normalized_candidates: Dict[str, str],
                     normalized_targets: Dict[str, str]) -> Dict[str, Any]:
        """
        Match skills using three-tier strategy:
        1. Exact match (after normalization)
        2. Fuzzy match (for typos)
        3. Semantic match (for synonyms)
        
        Edge cases handled:
        - Empty target list -> returns empty matches
        - Empty candidate list -> returns all as missing
        - Single skill strings
        """
        # Handle empty targets
        if not target_skills:
            return {'matches': [], 'missing': [], 'details': {}}
        
        # Handle empty candidates
        if not candidate_skills:
            return {'matches': [], 'missing': list(target_skills), 'details': {}}
        
        matches = []
        match_details = {}
        remaining_targets = list(target_skills)
        
        # Strategy 1: Exact matching (after normalization)
        for target_orig in list(remaining_targets):
            target_norm = normalized_targets[target_orig]
            for cand_orig, cand_norm in normalized_candidates.items():
                if target_norm == cand_norm:
                    matches.append(target_orig)
                    match_details[target_orig] = {
                        'matched_with': cand_orig,
                        'method': 'exact',
                        'confidence': 1.0,
                        'score': 100
                    }
                    remaining_targets.remove(target_orig)
                    break
        
        # Strategy 2: Fuzzy matching (for typos and close variations)
        if self.use_fuzzy and remaining_targets:
            for target_orig in list(remaining_targets):
                target_norm = normalized_targets[target_orig]
                
                # Find best fuzzy match
                cand_norms = list(normalized_candidates.values())
                best_match = process.extractOne(
                    target_norm,
                    cand_norms,
                    scorer=fuzz.token_sort_ratio,
                    score_cutoff=self.fuzzy_threshold
                )
                
                if best_match:
                    matched_norm, score, _ = best_match
                    # Find original candidate skill
                    cand_orig = [k for k, v in normalized_candidates.items() if v == matched_norm][0]
                    
                    matches.append(target_orig)
                    match_details[target_orig] = {
                        'matched_with': cand_orig,
                        'method': 'fuzzy',
                        'confidence': score / 100,
                        'score': score
                    }
                    remaining_targets.remove(target_orig)
        
        # Strategy 3: Semantic matching (for synonyms and related skills)
        if self.use_semantic and self.embedder and remaining_targets:
            for target_orig in list(remaining_targets):
                target_norm = normalized_targets[target_orig]
                best_cand_orig = None
                best_sim = 0
                
                for cand_orig, cand_norm in normalized_candidates.items():
                    sim = self.embedder.calculate_similarity(target_norm, cand_norm)
                    if sim > best_sim:
                        best_sim = sim
                        best_cand_orig = cand_orig
                
                if best_sim >= self.semantic_threshold:
                    matches.append(target_orig)
                    match_details[target_orig] = {
                        'matched_with': best_cand_orig,
                        'method': 'semantic',
                        'confidence': best_sim,
                        'score': int(best_sim * 100)
                    }
                    remaining_targets.remove(target_orig)
        
        return {
            'matches': sorted(matches),
            'missing': sorted(remaining_targets),
            'details': match_details
        }


def test_enhanced_skill_matcher():
    """Test enhanced skill matcher"""
    print("\\n" + "="*70)
    print("TESTING ENHANCED SKILL MATCHER")
    print("="*70)
    
    matcher = EnhancedSkillMatcher(
        use_fuzzy=True,
        fuzzy_threshold=85,
        use_semantic=True,
        semantic_threshold=0.70
    )
    
    # Test case 1: Typos and variations
    print("\\n📝 Test 1: Typos and Variations")
    candidate_skills = [
        "Python",  # exact
        "Javascrpt",  # typo
        "machinelearning",  # no space
        "Kubernetes",  # exact
        "nodejs"  # variation
    ]
    required_skills = [
        "Python",
        "JavaScript",
        "Machine Learning",
        "k8s",
        "Node.js"
    ]
    
    result = matcher.calculate_match_score(candidate_skills, required_skills)
    print(f"Score: {result['score']:.1f}%")
    print(f"Matched: {result['required_matches']}")
    print(f"Missing: {result['missing_required']}")
    print("\\nMatch Details:")
    for skill, details in result['match_details']['required'].items():
        print(f"  {skill} → {details['matched_with']} ({details['method']}, {details['confidence']:.2f})")
    
    # Test case 2: Abbreviations
    print("\\n📝 Test 2: Abbreviations")
    candidate_skills = ["AWS", "ML", "CI/CD", "REST API"]
    required_skills = ["Amazon Web Services", "Machine Learning", "Continuous Integration", "RESTful API"]
    
    result = matcher.calculate_match_score(candidate_skills, required_skills)
    print(f"Score: {result['score']:.1f}%")
    print(f"Matched: {result['required_matches']}")
    
    # Test case 3: Semantic similarity
    print("\\n📝 Test 3: Semantic Similarity")
    candidate_skills = ["Deep Learning", "Neural Networks", "TensorFlow"]
    required_skills = ["AI", "Machine Learning", "PyTorch"]
    
    result = matcher.calculate_match_score(candidate_skills, required_skills)
    print(f"Score: {result['score']:.1f}%")
    print(f"Matched: {result['required_matches']}")
    print("\\nMatch Details:")
    for skill, details in result['match_details']['required'].items():
        print(f"  {skill} → {details['matched_with']} ({details['method']}, {details['confidence']:.2f})")
    
    print("\\n" + "="*70)
    print("✅ All tests complete!")


if __name__ == "__main__":
    test_enhanced_skill_matcher()
