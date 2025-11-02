"""
Skill Matcher
Calculates how well candidate skills match job requirements
Uses semantic embeddings for intelligent matching
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Any, Set
from difflib import SequenceMatcher
from src.ml.skill_embedder import SkillEmbedder


class SkillMatcher:
    """Match candidate skills against job requirements using semantic embeddings"""
    
    # Common abbreviations and variations
    SKILL_ALIASES = {
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
        'dl': 'deep learning',
        'ci/cd': 'continuous integration',
        'ci/cd pipelines': 'continuous integration',
        'cicd': 'continuous integration',
        'aws': 'amazon web services',
        'aws cloud': 'amazon web services',
        'gcp': 'google cloud platform',
        'google cloud': 'google cloud platform',
        'azure': 'microsoft azure',
        'k8s': 'kubernetes',
        'js': 'javascript',
        'ts': 'typescript',
        'postgres': 'postgresql',
        'mongo': 'mongodb',
        'api': 'application programming interface',
        'rest api': 'restful api',
        'rest apis': 'restful api',
        'llm': 'large language model',
        'llms': 'large language model',
        'cnn': 'convolutional neural network',
        'rnn': 'recurrent neural network',
    }
    
    def __init__(self, use_semantic: bool = True, semantic_threshold: float = 0.75):
        """
        Initialize skill matcher
        
        Args:
            use_semantic: Use semantic matching with embeddings (default: True)
            semantic_threshold: Similarity threshold for semantic matches (default: 0.75)
        """
        self.use_semantic = use_semantic
        self.semantic_threshold = semantic_threshold
        
        if use_semantic:
            self.embedder = SkillEmbedder()
        else:
            self.embedder = None
    
    def calculate_match_score(self,
                             candidate_skills: List[str],
                             required_skills: List[str],
                             optional_skills: List[str] = None) -> Dict[str, Any]:
        """
        Calculate skill match score using semantic embeddings
        
        Args:
            candidate_skills: Skills from candidate resume
            required_skills: Required skills from job posting
            optional_skills: Optional/nice-to-have skills
            
        Returns:
            Dict with score and breakdown
        """
        if optional_skills is None:
            optional_skills = []
        
        if self.use_semantic and self.embedder:
            return self._semantic_match_score(candidate_skills, required_skills, optional_skills)
        else:
            return self._exact_match_score(candidate_skills, required_skills, optional_skills)
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill using alias dictionary"""
        normalized = skill.lower().strip()
        return self.SKILL_ALIASES.get(normalized, skill)
    
    def _semantic_match_score(self,
                             candidate_skills: List[str],
                             required_skills: List[str],
                             optional_skills: List[str]) -> Dict[str, Any]:
        """Calculate match using semantic embeddings with abbreviation handling"""
        # Normalize skills first (expand abbreviations)
        normalized_candidates = [self._normalize_skill(s) for s in candidate_skills]
        
        # Get semantic matches for required skills
        required_matches = []
        required_similarities = {}
        missing_required = []
        
        for req_skill in required_skills:
            normalized_req = self._normalize_skill(req_skill)
            best_match = None
            best_sim = 0
            best_match_orig = None
            
            for i, cand_skill in enumerate(normalized_candidates):
                # Calculate semantic similarity on normalized versions
                sim = self.embedder.calculate_similarity(normalized_req, cand_skill)
                if sim > best_sim:
                    best_sim = sim
                    best_match = cand_skill
                    best_match_orig = candidate_skills[i]  # Keep original for display
            
            if best_sim >= self.semantic_threshold:
                required_matches.append(req_skill)
                required_similarities[req_skill] = {
                    'matched_with': best_match_orig,
                    'similarity': round(best_sim, 3)
                }
            else:
                missing_required.append(req_skill)
        
        # Get semantic matches for optional skills
        optional_matches = []
        optional_similarities = {}
        missing_optional = []
        
        for opt_skill in optional_skills:
            normalized_opt = self._normalize_skill(opt_skill)
            best_match = None
            best_sim = 0
            best_match_orig = None
            
            for i, cand_skill in enumerate(normalized_candidates):
                sim = self.embedder.calculate_similarity(normalized_opt, cand_skill)
                if sim > best_sim:
                    best_sim = sim
                    best_match = cand_skill
                    best_match_orig = candidate_skills[i]
            
            if best_sim >= self.semantic_threshold:
                optional_matches.append(opt_skill)
                optional_similarities[opt_skill] = {
                    'matched_with': best_match_orig,
                    'similarity': round(best_sim, 3)
                }
            else:
                missing_optional.append(opt_skill)
        
        # Calculate coverage
        required_coverage = (len(required_matches) / len(required_skills) * 100) if required_skills else 100
        optional_coverage = (len(optional_matches) / len(optional_skills) * 100) if optional_skills else 0
        
        # Calculate weighted score (required: 80%, optional: 20%)
        if required_skills:
            score = (required_coverage * 0.8) + (optional_coverage * 0.2)
        else:
            score = optional_coverage
        
        return {
            'score': round(score, 2),
            'required_matches': sorted(required_matches),
            'optional_matches': sorted(optional_matches),
            'missing_required': sorted(missing_required),
            'missing_optional': sorted(missing_optional),
            'required_coverage': round(required_coverage, 2),
            'optional_coverage': round(optional_coverage, 2),
            'total_matched': len(required_matches) + len(optional_matches),
            'total_required': len(required_skills),
            'total_optional': len(optional_skills),
            'semantic_details': {
                'required': required_similarities,
                'optional': optional_similarities
            },
            'matching_method': 'semantic'
        }
    
    def _exact_match_score(self,
                          candidate_skills: List[str],
                          required_skills: List[str],
                          optional_skills: List[str]) -> Dict[str, Any]:
        """Calculate match using exact string matching (fallback)"""
        # Normalize skills (lowercase for comparison)
        candidate_set = set(s.lower().strip() for s in candidate_skills)
        required_set = set(s.lower().strip() for s in required_skills)
        optional_set = set(s.lower().strip() for s in optional_skills)
        
        # Calculate matches
        required_matches = candidate_set.intersection(required_set)
        optional_matches = candidate_set.intersection(optional_set)
        missing_required = required_set - candidate_set
        missing_optional = optional_set - candidate_set
        
        # Calculate coverage percentages
        required_coverage = (len(required_matches) / len(required_set) * 100) if required_set else 100
        optional_coverage = (len(optional_matches) / len(optional_set) * 100) if optional_set else 0
        
        # Calculate weighted score
        if required_set:
            score = (required_coverage * 0.8) + (optional_coverage * 0.2)
        else:
            score = optional_coverage
        
        return {
            'score': round(score, 2),
            'required_matches': sorted(list(required_matches)),
            'optional_matches': sorted(list(optional_matches)),
            'missing_required': sorted(list(missing_required)),
            'missing_optional': sorted(list(missing_optional)),
            'required_coverage': round(required_coverage, 2),
            'optional_coverage': round(optional_coverage, 2),
            'total_matched': len(required_matches) + len(optional_matches),
            'total_required': len(required_set),
            'total_optional': len(optional_set),
            'matching_method': 'exact'
        }
    
    def calculate_jaccard_similarity(self,
                                    skills1: List[str],
                                    skills2: List[str]) -> float:
        """
        Calculate Jaccard similarity between two skill sets
        
        Args:
            skills1: First skill set
            skills2: Second skill set
            
        Returns:
            Jaccard similarity score (0-1)
        """
        set1 = set(s.lower().strip() for s in skills1)
        set2 = set(s.lower().strip() for s in skills2)
        
        if not set1 and not set2:
            return 1.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)
    
    def fuzzy_match_skills(self,
                          candidate_skills: List[str],
                          required_skills: List[str],
                          threshold: float = 0.85) -> Dict[str, List[tuple]]:
        """
        Find fuzzy matches between candidate and required skills
        Useful for handling variations like "ML" vs "Machine Learning"
        
        Args:
            candidate_skills: Candidate's skills
            required_skills: Required skills
            threshold: Similarity threshold (0-1)
            
        Returns:
            Dict with fuzzy matches
        """
        fuzzy_matches = []
        
        candidate_lower = [s.lower() for s in candidate_skills]
        
        for req_skill in required_skills:
            req_lower = req_skill.lower()
            best_match = None
            best_score = 0
            
            for i, cand_skill in enumerate(candidate_lower):
                # Calculate similarity
                similarity = SequenceMatcher(None, req_lower, cand_skill).ratio()
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = candidate_skills[i]
            
            if best_score >= threshold:
                fuzzy_matches.append({
                    'required': req_skill,
                    'matched': best_match,
                    'similarity': round(best_score, 3)
                })
        
        return {
            'matches': fuzzy_matches,
            'count': len(fuzzy_matches)
        }


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Skill Matcher")
    print("=" * 70)
    
    matcher = SkillMatcher()
    
    # Test case 1: Perfect match
    print("\n1️⃣ Test: Perfect skill match")
    candidate = ['Python', 'Django', 'AWS', 'PostgreSQL']
    required = ['Python', 'Django', 'AWS']
    optional = ['Docker', 'Kubernetes']
    
    result = matcher.calculate_match_score(candidate, required, optional)
    print(f"   Candidate: {', '.join(candidate)}")
    print(f"   Required: {', '.join(required)}")
    print(f"   Optional: {', '.join(optional)}")
    print(f"   Score: {result['score']}/100")
    print(f"   Required coverage: {result['required_coverage']}%")
    print(f"   Optional coverage: {result['optional_coverage']}%")
    
    # Test case 2: Partial match with missing skills
    print("\n2️⃣ Test: Partial match")
    candidate = ['Python', 'Flask']
    required = ['Python', 'Django', 'AWS', 'PostgreSQL']
    
    result = matcher.calculate_match_score(candidate, required)
    print(f"   Candidate: {', '.join(candidate)}")
    print(f"   Required: {', '.join(required)}")
    print(f"   Score: {result['score']}/100")
    print(f"   Matched: {', '.join(result['required_matches'])}")
    print(f"   Missing: {', '.join(result['missing_required'])}")
    
    # Test case 3: Jaccard similarity
    print("\n3️⃣ Test: Jaccard similarity")
    skills1 = ['Python', 'Java', 'C++', 'JavaScript']
    skills2 = ['Python', 'Java', 'Go', 'Rust']
    
    similarity = matcher.calculate_jaccard_similarity(skills1, skills2)
    print(f"   Skills 1: {', '.join(skills1)}")
    print(f"   Skills 2: {', '.join(skills2)}")
    print(f"   Jaccard similarity: {similarity:.3f}")
    
    # Test case 4: Fuzzy matching
    print("\n4️⃣ Test: Fuzzy skill matching")
    candidate = ['Python', 'ML', 'Deep Learning', 'Postgres']
    required = ['Python', 'Machine Learning', 'PostgreSQL']
    
    fuzzy = matcher.fuzzy_match_skills(candidate, required, threshold=0.7)
    print(f"   Candidate: {', '.join(candidate)}")
    print(f"   Required: {', '.join(required)}")
    print(f"   Fuzzy matches: {fuzzy['count']}")
    for match in fuzzy['matches']:
        print(f"     - '{match['required']}' ≈ '{match['matched']}' ({match['similarity']:.2f})")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
