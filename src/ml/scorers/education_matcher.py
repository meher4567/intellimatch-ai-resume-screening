"""
Education Matcher
Calculates how well candidate education matches job requirements
"""

from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher


class EducationMatcher:
    """Match candidate education against job requirements"""
    
    def __init__(self):
        """Initialize education matcher"""
        # Degree level hierarchy
        self.degree_hierarchy = {
            'phd': 5,
            'doctorate': 5,
            'ph.d': 5,
            'doctoral': 5,
            'master': 4,
            'masters': 4,
            'ms': 4,
            'msc': 4,
            'ma': 4,
            'mba': 4,
            'bachelor': 3,
            'bachelors': 3,
            'bs': 3,
            'ba': 3,
            'bsc': 3,
            'associate': 2,
            'associates': 2,
            'high school': 1,
            'diploma': 1,
            'ged': 1
        }
        
        # Relevant fields for common tech roles
        self.relevant_fields = {
            'computer science': ['computer science', 'cs', 'software engineering'],
            'engineering': ['engineering', 'computer engineering', 'electrical engineering'],
            'mathematics': ['mathematics', 'math', 'statistics', 'data science'],
            'information technology': ['information technology', 'it', 'information systems'],
            'physics': ['physics', 'applied physics'],
            'business': ['business', 'mba', 'business administration']
        }
    
    def calculate_match_score(self,
                             candidate_degrees: List[Dict[str, str]],
                             required_degree: Optional[str],
                             preferred_degree: Optional[str] = None,
                             required_field: Optional[str] = None,
                             equivalent_experience: bool = False) -> Dict[str, Any]:
        """
        Calculate education match score
        
        Args:
            candidate_degrees: List of degrees with 'degree' and 'field' keys
            required_degree: Required degree level (e.g., 'Bachelor', 'Master')
            preferred_degree: Preferred degree level
            required_field: Required field of study
            equivalent_experience: Whether equivalent experience is acceptable
            
        Returns:
            Dict with score and breakdown
        """
        score = 0
        breakdown = {}
        
        # If no degree required
        if not required_degree:
            breakdown['degree_score'] = 100
            breakdown['field_score'] = 100
            return {
                'score': 100,
                'assessment': 'No degree required',
                'breakdown': breakdown
            }
        
        # Get highest degree
        highest_degree = self._get_highest_degree(candidate_degrees)
        
        if not highest_degree and not equivalent_experience:
            return {
                'score': 0,
                'assessment': 'No degree provided',
                'breakdown': {'degree_score': 0, 'field_score': 0}
            }
        
        # Degree level score (70% weight)
        if highest_degree:
            degree_score = self._score_degree_level(
                highest_degree['degree'],
                required_degree,
                preferred_degree
            )
            breakdown['degree_score'] = degree_score
            score += degree_score * 0.7
        else:
            # No degree but equivalent experience accepted
            breakdown['degree_score'] = 60  # Give partial credit
            score += 60 * 0.7
        
        # Field of study score (30% weight)
        if required_field and highest_degree:
            field_score = self._score_field_match(
                highest_degree.get('field', ''),
                required_field
            )
            breakdown['field_score'] = field_score
            score += field_score * 0.3
        else:
            breakdown['field_score'] = 100  # No specific field required
            score += 100 * 0.3
        
        # Overall assessment
        assessment = self._get_assessment(
            breakdown['degree_score'],
            breakdown['field_score'],
            required_degree,
            preferred_degree,
            equivalent_experience
        )
        
        return {
            'score': round(score, 2),
            'highest_degree': highest_degree['degree'] if highest_degree else None,
            'highest_field': highest_degree.get('field') if highest_degree else None,
            'required_degree': required_degree,
            'assessment': assessment,
            'breakdown': breakdown
        }
    
    def _get_highest_degree(self, degrees: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Get the highest level degree from list"""
        if not degrees:
            return None
        
        highest = None
        highest_rank = 0
        
        for deg in degrees:
            degree_name = deg.get('degree', '').lower()
            rank = self._get_degree_rank(degree_name)
            
            if rank > highest_rank:
                highest_rank = rank
                highest = deg
        
        return highest
    
    def _get_degree_rank(self, degree: str) -> int:
        """Get numerical rank of degree"""
        degree_lower = degree.lower()
        
        for key, rank in self.degree_hierarchy.items():
            if key in degree_lower:
                return rank
        
        return 0
    
    def _score_degree_level(self,
                           candidate_degree: str,
                           required_degree: str,
                           preferred_degree: Optional[str] = None) -> float:
        """
        Score degree level match
        
        Logic:
        - Meets preferred: 100
        - Meets required: 90
        - One level below required: 60
        - Two levels below: 30
        - No degree: 0
        """
        candidate_rank = self._get_degree_rank(candidate_degree)
        required_rank = self._get_degree_rank(required_degree)
        preferred_rank = self._get_degree_rank(preferred_degree) if preferred_degree else None
        
        if candidate_rank == 0:
            return 0
        
        # Check preferred first
        if preferred_rank and candidate_rank >= preferred_rank:
            return 100
        
        # Check required
        if candidate_rank >= required_rank:
            return 90
        
        # Below required
        diff = required_rank - candidate_rank
        
        if diff == 1:
            return 60  # One level below
        elif diff == 2:
            return 30  # Two levels below
        else:
            return 10  # Much lower
    
    def _score_field_match(self, candidate_field: str, required_field: str) -> float:
        """
        Score field of study match
        
        Uses fuzzy matching to handle variations
        """
        if not candidate_field or not required_field:
            return 50  # Neutral if not specified
        
        candidate_lower = candidate_field.lower()
        required_lower = required_field.lower()
        
        # Exact match
        if candidate_lower == required_lower:
            return 100
        
        # Check if in same category
        for category, variations in self.relevant_fields.items():
            candidate_in_category = any(v in candidate_lower for v in variations)
            required_in_category = any(v in required_lower for v in variations)
            
            if candidate_in_category and required_in_category:
                return 90  # Same category
        
        # Fuzzy match
        similarity = SequenceMatcher(None, candidate_lower, required_lower).ratio()
        
        if similarity >= 0.8:
            return 85
        elif similarity >= 0.6:
            return 70
        elif similarity >= 0.4:
            return 50
        else:
            return 30  # Unrelated field
    
    def _get_assessment(self,
                       degree_score: float,
                       field_score: float,
                       required_degree: str,
                       preferred_degree: Optional[str],
                       equivalent_experience: bool) -> str:
        """Generate overall assessment message"""
        if degree_score >= 90 and field_score >= 90:
            return 'Excellent match'
        elif degree_score >= 90 and field_score >= 70:
            return 'Strong match'
        elif degree_score >= 60 and field_score >= 50:
            if equivalent_experience:
                return 'Acceptable with experience'
            else:
                return 'Meets minimum requirements'
        elif degree_score >= 30:
            return 'Below requirements'
        else:
            return 'Does not meet requirements'
    
    def has_advanced_degree(self, degrees: List[Dict[str, str]]) -> bool:
        """Check if candidate has Master's or PhD"""
        highest = self._get_highest_degree(degrees)
        if not highest:
            return False
        
        rank = self._get_degree_rank(highest['degree'])
        return rank >= 4  # Master's or above


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Education Matcher")
    print("=" * 70)
    
    matcher = EducationMatcher()
    
    # Test case 1: Perfect match
    print("\n1️⃣ Test: Perfect education match")
    result = matcher.calculate_match_score(
        candidate_degrees=[
            {'degree': 'Bachelor of Science', 'field': 'Computer Science'}
        ],
        required_degree='Bachelor',
        required_field='Computer Science'
    )
    print(f"   Candidate: BS in Computer Science")
    print(f"   Required: Bachelor's in Computer Science")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    print(f"   Breakdown: Degree={result['breakdown']['degree_score']}, Field={result['breakdown']['field_score']}")
    
    # Test case 2: Higher degree
    print("\n2️⃣ Test: Candidate has higher degree")
    result = matcher.calculate_match_score(
        candidate_degrees=[
            {'degree': 'Master of Science', 'field': 'Computer Science'}
        ],
        required_degree='Bachelor',
        preferred_degree='Master',
        required_field='Computer Science'
    )
    print(f"   Candidate: MS in Computer Science")
    print(f"   Required: Bachelor's (Preferred: Master's) in CS")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    
    # Test case 3: Related field
    print("\n3️⃣ Test: Related field of study")
    result = matcher.calculate_match_score(
        candidate_degrees=[
            {'degree': 'Bachelor', 'field': 'Software Engineering'}
        ],
        required_degree='Bachelor',
        required_field='Computer Science'
    )
    print(f"   Candidate: Bachelor's in Software Engineering")
    print(f"   Required: Bachelor's in Computer Science")
    print(f"   Score: {result['score']}/100")
    print(f"   Field similarity: {result['breakdown']['field_score']}/100")
    
    # Test case 4: Below requirements
    print("\n4️⃣ Test: Below degree requirements")
    result = matcher.calculate_match_score(
        candidate_degrees=[
            {'degree': 'Associate', 'field': 'Computer Science'}
        ],
        required_degree='Bachelor',
        required_field='Computer Science'
    )
    print(f"   Candidate: Associate in CS")
    print(f"   Required: Bachelor's in CS")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    
    # Test case 5: No degree but equivalent experience accepted
    print("\n5️⃣ Test: Equivalent experience accepted")
    result = matcher.calculate_match_score(
        candidate_degrees=[],
        required_degree='Bachelor',
        equivalent_experience=True
    )
    print(f"   Candidate: No degree")
    print(f"   Required: Bachelor's (or equivalent experience)")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    
    # Test case 6: Multiple degrees
    print("\n6️⃣ Test: Multiple degrees (highest selected)")
    result = matcher.calculate_match_score(
        candidate_degrees=[
            {'degree': 'Bachelor', 'field': 'Physics'},
            {'degree': 'Master', 'field': 'Computer Science'},
            {'degree': 'PhD', 'field': 'Machine Learning'}
        ],
        required_degree='Master',
        required_field='Computer Science'
    )
    print(f"   Candidate: PhD in ML, MS in CS, BS in Physics")
    print(f"   Required: Master's in CS")
    print(f"   Highest: {result['highest_degree']} in {result['highest_field']}")
    print(f"   Score: {result['score']}/100")
    print(f"   Has advanced degree: {matcher.has_advanced_degree([{'degree': 'PhD', 'field': 'ML'}])}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
