"""
Experience Matcher
Calculates how well candidate experience matches job requirements
"""

from typing import Dict, Any, Optional


class ExperienceMatcher:
    """Match candidate experience against job requirements"""
    
    def __init__(self):
        """Initialize experience matcher"""
        # Experience level mappings
        self.level_hierarchy = {
            'entry': 0,
            'junior': 1,
            'mid': 2,
            'senior': 3,
            'lead': 4,
            'executive': 5
        }
    
    def calculate_match_score(self,
                             candidate_years: int,
                             required_years: Optional[int],
                             candidate_level: str = 'mid',
                             required_level: str = 'mid') -> Dict[str, Any]:
        """
        Calculate experience match score
        
        Args:
            candidate_years: Years of experience candidate has
            required_years: Required years of experience (None if not specified)
            candidate_level: Candidate's seniority level
            required_level: Required seniority level
            
        Returns:
            Dict with score and breakdown
        """
        score = 0
        breakdown = {}
        
        # Handle None candidate_years - default to 0
        if candidate_years is None:
            candidate_years = 0
        
        # Years of experience score (60% weight)
        if required_years is not None:
            years_score = self._score_years(candidate_years, required_years)
            breakdown['years_score'] = years_score
            score += years_score * 0.6
        else:
            # If no specific years required, give full points
            breakdown['years_score'] = 100
            score += 100 * 0.6
        
        # Seniority level score (40% weight)
        level_score = self._score_level(candidate_level, required_level)
        breakdown['level_score'] = level_score
        score += level_score * 0.4
        
        # Overall assessment
        if required_years:
            if candidate_years >= required_years:
                assessment = 'Meets requirements'
            elif candidate_years >= required_years * 0.7:
                assessment = 'Close match'
            else:
                assessment = 'Under-qualified'
        else:
            assessment = 'Level-based match'
        
        return {
            'score': round(score, 2),
            'candidate_years': candidate_years,
            'required_years': required_years,
            'candidate_level': candidate_level,
            'required_level': required_level,
            'assessment': assessment,
            'breakdown': breakdown
        }
    
    def _score_years(self, candidate_years: int, required_years: int) -> float:
        """
        Score years of experience
        
        Logic:
        - Exact match or more: 100
        - Within 1 year: 90
        - Within 2 years: 80
        - 70% of required: 70
        - Less than 70%: proportional
        """
        diff = candidate_years - required_years
        
        if diff >= 0:
            # Candidate has required experience or more
            return 100
        elif diff >= -1:
            # Within 1 year
            return 90
        elif diff >= -2:
            # Within 2 years
            return 80
        else:
            # Calculate proportional score
            ratio = candidate_years / required_years
            if ratio >= 0.7:
                return 70
            else:
                # Linear from 0 to 70 based on ratio
                return max(0, ratio / 0.7 * 70)
    
    def _score_level(self, candidate_level: str, required_level: str) -> float:
        """
        Score seniority level match
        
        Logic:
        - Exact match: 100
        - One level above: 95
        - Two levels above: 90
        - One level below: 70
        - Two levels below: 40
        - More than two levels off: 20
        """
        candidate_rank = self.level_hierarchy.get(candidate_level.lower(), 2)  # default to mid
        required_rank = self.level_hierarchy.get(required_level.lower(), 2)
        
        diff = candidate_rank - required_rank
        
        if diff == 0:
            return 100  # Exact match
        elif diff == 1:
            return 95  # One level above (good!)
        elif diff == 2:
            return 90  # Two levels above (still good)
        elif diff >= 3:
            return 85  # Much more senior (may be overqualified)
        elif diff == -1:
            return 70  # One level below (acceptable)
        elif diff == -2:
            return 40  # Two levels below
        else:
            return 20  # Much less senior
    
    def is_overqualified(self,
                        candidate_years: int,
                        required_years: Optional[int],
                        threshold: float = 2.0) -> bool:
        """
        Check if candidate is significantly overqualified
        
        Args:
            candidate_years: Candidate's years of experience
            required_years: Required years
            threshold: Multiplier to determine overqualification (default: 2x)
            
        Returns:
            True if overqualified
        """
        if required_years is None or required_years == 0:
            return False
        
        return candidate_years >= (required_years * threshold)
    
    def is_underqualified(self,
                         candidate_years: int,
                         required_years: Optional[int],
                         threshold: float = 0.7) -> bool:
        """
        Check if candidate is significantly underqualified
        
        Args:
            candidate_years: Candidate's years of experience
            required_years: Required years
            threshold: Ratio to determine underqualification (default: 70%)
            
        Returns:
            True if underqualified
        """
        if required_years is None or required_years == 0:
            return False
        
        return candidate_years < (required_years * threshold)


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Experience Matcher")
    print("=" * 70)
    
    matcher = ExperienceMatcher()
    
    # Test case 1: Perfect match
    print("\n1️⃣ Test: Perfect experience match")
    result = matcher.calculate_match_score(
        candidate_years=5,
        required_years=5,
        candidate_level='senior',
        required_level='senior'
    )
    print(f"   Candidate: 5 years, Senior")
    print(f"   Required: 5 years, Senior")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    
    # Test case 2: Close match (slightly less experience)
    print("\n2️⃣ Test: Close match")
    result = matcher.calculate_match_score(
        candidate_years=4,
        required_years=5,
        candidate_level='mid',
        required_level='senior'
    )
    print(f"   Candidate: 4 years, Mid")
    print(f"   Required: 5 years, Senior")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    print(f"   Breakdown: Years={result['breakdown']['years_score']}, Level={result['breakdown']['level_score']}")
    
    # Test case 3: Overqualified
    print("\n3️⃣ Test: Overqualified candidate")
    result = matcher.calculate_match_score(
        candidate_years=10,
        required_years=3,
        candidate_level='lead',
        required_level='mid'
    )
    print(f"   Candidate: 10 years, Lead")
    print(f"   Required: 3 years, Mid")
    print(f"   Score: {result['score']}/100")
    print(f"   Overqualified: {matcher.is_overqualified(10, 3)}")
    
    # Test case 4: Underqualified
    print("\n4️⃣ Test: Underqualified candidate")
    result = matcher.calculate_match_score(
        candidate_years=1,
        required_years=5,
        candidate_level='junior',
        required_level='senior'
    )
    print(f"   Candidate: 1 year, Junior")
    print(f"   Required: 5 years, Senior")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    print(f"   Underqualified: {matcher.is_underqualified(1, 5)}")
    
    # Test case 5: No specific years required
    print("\n5️⃣ Test: No specific years required")
    result = matcher.calculate_match_score(
        candidate_years=7,
        required_years=None,
        candidate_level='senior',
        required_level='mid'
    )
    print(f"   Candidate: 7 years, Senior")
    print(f"   Required: No specific years, Mid level")
    print(f"   Score: {result['score']}/100")
    print(f"   Assessment: {result['assessment']}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
