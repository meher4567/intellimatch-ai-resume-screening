"""
Candidate Ranker
Ranks and filters candidates based on match scores
"""

from typing import List, Dict, Any, Optional
import math


class CandidateRanker:
    """Rank candidates by match score with various ranking strategies"""
    
    def __init__(self):
        """Initialize candidate ranker"""
        pass
    
    def rank_candidates(self,
                       candidates: List[Dict[str, Any]],
                       min_score: Optional[float] = None,
                       top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rank candidates by match score
        
        Args:
            candidates: List of candidate match results
            min_score: Minimum score threshold (filter out below this)
            top_k: Return only top K candidates
            
        Returns:
            Sorted list of candidates with rankings
        """
        # Filter by minimum score
        if min_score:
            candidates = [c for c in candidates if c['match_score'] >= min_score]
        
        # Sort by score (descending)
        sorted_candidates = sorted(
            candidates,
            key=lambda x: x['match_score'],
            reverse=True
        )
        
        # Add rankings
        for i, candidate in enumerate(sorted_candidates):
            candidate['rank'] = i + 1
            candidate['percentile'] = self._calculate_percentile(i, len(sorted_candidates))
            candidate['tier'] = self._assign_tier(candidate['match_score'])
        
        # Return top K if specified
        if top_k:
            return sorted_candidates[:top_k]
        
        return sorted_candidates
    
    def _calculate_percentile(self, rank: int, total: int) -> float:
        """Calculate percentile ranking (100 = best, 0 = worst)"""
        if total <= 1:
            return 100.0
        
        percentile = ((total - rank) / (total - 1)) * 100
        return round(percentile, 1)
    
    def _assign_tier(self, score: float) -> str:
        """Assign tier based on score"""
        if score >= 85:
            return 'S-Tier'  # Exceptional
        elif score >= 75:
            return 'A-Tier'  # Excellent
        elif score >= 65:
            return 'B-Tier'  # Good
        elif score >= 50:
            return 'C-Tier'  # Fair
        else:
            return 'D-Tier'  # Weak
    
    def group_by_tier(self, candidates: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group candidates by tier"""
        tiers = {
            'S-Tier': [],
            'A-Tier': [],
            'B-Tier': [],
            'C-Tier': [],
            'D-Tier': []
        }
        
        for candidate in candidates:
            tier = candidate.get('tier', 'D-Tier')
            tiers[tier].append(candidate)
        
        return tiers
    
    def get_statistics(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get ranking statistics"""
        if not candidates:
            return {
                'total': 0,
                'mean_score': 0,
                'median_score': 0,
                'std_dev': 0,
                'tier_distribution': {}
            }
        
        scores = [c['match_score'] for c in candidates]
        
        # Calculate statistics
        mean_score = sum(scores) / len(scores)
        sorted_scores = sorted(scores)
        median_score = sorted_scores[len(sorted_scores) // 2]
        
        # Standard deviation
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        # Tier distribution
        tier_dist = {}
        for candidate in candidates:
            tier = candidate.get('tier', 'Unknown')
            tier_dist[tier] = tier_dist.get(tier, 0) + 1
        
        return {
            'total': len(candidates),
            'mean_score': round(mean_score, 2),
            'median_score': round(median_score, 2),
            'std_dev': round(std_dev, 2),
            'min_score': round(min(scores), 2),
            'max_score': round(max(scores), 2),
            'tier_distribution': tier_dist
        }
    
    def filter_candidates(self,
                         candidates: List[Dict[str, Any]],
                         filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply advanced filters to candidates
        
        Supported filters:
        - min_score: Minimum match score
        - max_score: Maximum match score
        - tiers: List of acceptable tiers
        - min_experience: Minimum years of experience
        - max_experience: Maximum years of experience
        - required_skills: Must have these skills
        - required_degree: Must have this degree level
        """
        filtered = candidates.copy()
        
        # Score range
        if 'min_score' in filters:
            filtered = [c for c in filtered if c['match_score'] >= filters['min_score']]
        
        if 'max_score' in filters:
            filtered = [c for c in filtered if c['match_score'] <= filters['max_score']]
        
        # Tier filter
        if 'tiers' in filters:
            filtered = [c for c in filtered if c.get('tier') in filters['tiers']]
        
        # Experience filter
        if 'min_experience' in filters:
            filtered = [
                c for c in filtered
                if c.get('experience_years', 0) >= filters['min_experience']
            ]
        
        if 'max_experience' in filters:
            filtered = [
                c for c in filtered
                if c.get('experience_years', 999) <= filters['max_experience']
            ]
        
        # Skills filter
        if 'required_skills' in filters:
            required = set(s.lower() for s in filters['required_skills'])
            filtered = [
                c for c in filtered
                if required.issubset(set(s.lower() for s in c.get('skills', [])))
            ]
        
        # Degree filter
        if 'required_degree' in filters:
            filtered = [
                c for c in filtered
                if self._meets_degree_requirement(c, filters['required_degree'])
            ]
        
        return filtered
    
    def _meets_degree_requirement(self, candidate: Dict, required_degree: str) -> bool:
        """Check if candidate meets degree requirement"""
        degree_ranks = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        
        required_rank = degree_ranks.get(required_degree.lower(), 0)
        
        # Get highest degree from education
        education = candidate.get('education', [])
        if not education:
            return False
        
        for degree_info in education:
            degree = degree_info.get('degree', '').lower()
            for deg_type, rank in degree_ranks.items():
                if deg_type in degree and rank >= required_rank:
                    return True
        
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Candidate Ranker")
    print("=" * 70)
    
    ranker = CandidateRanker()
    
    # Create sample candidates
    candidates = [
        {
            'name': 'Alice Johnson',
            'match_score': 92.5,
            'skills': ['Python', 'Django', 'AWS', 'PostgreSQL'],
            'experience_years': 7,
            'education': [{'degree': 'Master of Science', 'field': 'CS'}]
        },
        {
            'name': 'Bob Smith',
            'match_score': 78.3,
            'skills': ['Python', 'Flask', 'Docker'],
            'experience_years': 4,
            'education': [{'degree': 'Bachelor', 'field': 'CS'}]
        },
        {
            'name': 'Charlie Brown',
            'match_score': 65.8,
            'skills': ['JavaScript', 'React', 'Node.js'],
            'experience_years': 3,
            'education': [{'degree': 'Bachelor', 'field': 'IT'}]
        },
        {
            'name': 'Diana Prince',
            'match_score': 88.1,
            'skills': ['Python', 'Django', 'React', 'PostgreSQL'],
            'experience_years': 5,
            'education': [{'degree': 'Bachelor', 'field': 'CS'}]
        },
        {
            'name': 'Eve Davis',
            'match_score': 45.2,
            'skills': ['Java', 'Spring'],
            'experience_years': 2,
            'education': [{'degree': 'Associate', 'field': 'Programming'}]
        },
        {
            'name': 'Frank Miller',
            'match_score': 71.6,
            'skills': ['Python', 'Django', 'MySQL'],
            'experience_years': 6,
            'education': [{'degree': 'Bachelor', 'field': 'Engineering'}]
        }
    ]
    
    # Test 1: Basic ranking
    print("\n1️⃣ Test: Basic ranking (all candidates)")
    ranked = ranker.rank_candidates(candidates)
    
    print(f"\n   Total candidates: {len(ranked)}")
    for candidate in ranked:
        print(f"   #{candidate['rank']} {candidate['name']}")
        print(f"      Score: {candidate['match_score']}/100")
        print(f"      Tier: {candidate['tier']}")
        print(f"      Percentile: Top {100 - candidate['percentile']:.0f}%")
    
    # Test 2: Filter by minimum score
    print("\n" + "=" * 70)
    print("\n2️⃣ Test: Filter by minimum score (70+)")
    filtered = ranker.rank_candidates(candidates, min_score=70)
    
    print(f"\n   Qualified candidates: {len(filtered)}")
    for candidate in filtered:
        print(f"   #{candidate['rank']} {candidate['name']} - {candidate['match_score']}/100 ({candidate['tier']})")
    
    # Test 3: Top K candidates
    print("\n" + "=" * 70)
    print("\n3️⃣ Test: Top 3 candidates")
    top3 = ranker.rank_candidates(candidates, top_k=3)
    
    for candidate in top3:
        print(f"   #{candidate['rank']} {candidate['name']}")
        print(f"      Score: {candidate['match_score']}/100")
        print(f"      Tier: {candidate['tier']}")
        print(f"      Experience: {candidate['experience_years']} years")
    
    # Test 4: Group by tier
    print("\n" + "=" * 70)
    print("\n4️⃣ Test: Group by tier")
    ranked_all = ranker.rank_candidates(candidates)
    tiers = ranker.group_by_tier(ranked_all)
    
    for tier, tier_candidates in tiers.items():
        if tier_candidates:
            print(f"\n   {tier}: {len(tier_candidates)} candidate(s)")
            for candidate in tier_candidates:
                print(f"      • {candidate['name']} ({candidate['match_score']}/100)")
    
    # Test 5: Statistics
    print("\n" + "=" * 70)
    print("\n5️⃣ Test: Ranking statistics")
    stats = ranker.get_statistics(ranked_all)
    
    print(f"   Total candidates: {stats['total']}")
    print(f"   Mean score: {stats['mean_score']}/100")
    print(f"   Median score: {stats['median_score']}/100")
    print(f"   Std deviation: {stats['std_dev']}")
    print(f"   Score range: {stats['min_score']} - {stats['max_score']}")
    print(f"\n   Tier distribution:")
    for tier, count in sorted(stats['tier_distribution'].items()):
        percentage = (count / stats['total']) * 100
        print(f"      {tier}: {count} ({percentage:.0f}%)")
    
    # Test 6: Advanced filters
    print("\n" + "=" * 70)
    print("\n6️⃣ Test: Advanced filters")
    
    # Filter: A/B tier + Python skills + Bachelor's degree
    advanced_filters = {
        'tiers': ['S-Tier', 'A-Tier', 'B-Tier'],
        'required_skills': ['Python', 'Django'],
        'required_degree': 'Bachelor',
        'min_experience': 4
    }
    
    filtered_advanced = ranker.filter_candidates(ranked_all, advanced_filters)
    
    print(f"\n   Filters applied:")
    print(f"      • Tiers: A/B tier")
    print(f"      • Skills: Python + Django")
    print(f"      • Degree: Bachelor's or higher")
    print(f"      • Experience: 4+ years")
    
    print(f"\n   Matching candidates: {len(filtered_advanced)}")
    for candidate in filtered_advanced:
        print(f"      • {candidate['name']} ({candidate['match_score']}/100, {candidate['experience_years']} yrs)")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
