"""
Skill Recommendation Engine
Suggests skills based on candidate's existing skills, career trajectory, and market demand
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter, defaultdict


class SkillRecommendationEngine:
    """
    Recommends skills based on:
    1. Skill co-occurrence patterns (skills that frequently appear together)
    2. Career progression patterns (skills needed for advancement)
    3. Skill gaps relative to target roles
    4. Industry trends and high-demand skills
    """
    
    def __init__(self):
        self.skill_cooccurrence: Dict[str, Counter] = defaultdict(Counter)
        self.skill_frequency: Counter = Counter()
        self.skill_by_level: Dict[str, Set[str]] = {
            'entry': set(),
            'mid': set(),
            'senior': set(),
            'expert': set()
        }
        self.complementary_skills: Dict[str, List[str]] = {}
        self.is_trained = False
        
    def train_from_resumes(self, resumes: List[Dict]) -> Dict:
        """
        Train the recommendation engine from resume data
        
        Args:
            resumes: List of parsed resumes
            
        Returns:
            Training statistics
        """
        print("🔧 Training Skill Recommendation Engine...")
        
        total_resumes = len(resumes)
        skills_analyzed = 0
        
        for resume in resumes:
            # Get skills
            skills = set()
            if resume.get('skills'):
                if isinstance(resume['skills'], dict):
                    skills = set(resume['skills'].get('all_skills', []))
                elif isinstance(resume['skills'], list):
                    skills = set(resume['skills'])
            
            if not skills:
                continue
                
            skills_analyzed += len(skills)
            
            # Update skill frequency
            for skill in skills:
                self.skill_frequency[skill] += 1
            
            # Update skill co-occurrence
            skill_list = list(skills)
            for i, skill1 in enumerate(skill_list):
                for skill2 in skill_list[i+1:]:
                    self.skill_cooccurrence[skill1][skill2] += 1
                    self.skill_cooccurrence[skill2][skill1] += 1
            
            # Categorize by experience level
            exp_level = self._get_experience_level(resume)
            for skill in skills:
                self.skill_by_level[exp_level].add(skill)
        
        # Calculate complementary skills
        self._calculate_complementary_skills()
        
        self.is_trained = True
        
        stats = {
            'resumes_processed': total_resumes,
            'unique_skills': len(self.skill_frequency),
            'total_skill_instances': skills_analyzed,
            'skill_pairs': sum(len(v) for v in self.skill_cooccurrence.values()) // 2,
            'entry_level_skills': len(self.skill_by_level['entry']),
            'mid_level_skills': len(self.skill_by_level['mid']),
            'senior_level_skills': len(self.skill_by_level['senior']),
            'expert_level_skills': len(self.skill_by_level['expert'])
        }
        
        print(f"✅ Training complete!")
        print(f"   Resumes: {stats['resumes_processed']}")
        print(f"   Unique skills: {stats['unique_skills']}")
        print(f"   Skill pairs: {stats['skill_pairs']}")
        
        return stats
    
    def _get_experience_level(self, resume: Dict) -> str:
        """Determine experience level from resume"""
        # Try from timeline analysis
        if resume.get('timeline_analysis'):
            years = resume['timeline_analysis'].get('total_experience_years', 0)
            if years < 2:
                return 'entry'
            elif years < 5:
                return 'mid'
            elif years < 10:
                return 'senior'
            else:
                return 'expert'
        
        # Try from experience details
        if resume.get('experience_details'):
            level = resume['experience_details'].get('candidate_level', '').lower()
            if 'junior' in level or 'entry' in level:
                return 'entry'
            elif 'senior' in level or 'lead' in level or 'principal' in level:
                return 'senior'
            elif 'expert' in level or 'architect' in level or 'director' in level:
                return 'expert'
            else:
                return 'mid'
        
        # Default
        return 'mid'
    
    def _calculate_complementary_skills(self):
        """Calculate which skills frequently appear together"""
        print("   Calculating complementary skills...")
        
        for skill, cooccurring in self.skill_cooccurrence.items():
            # Get top co-occurring skills
            # Normalize by frequency to avoid bias towards common skills
            normalized_scores = {}
            for other_skill, count in cooccurring.items():
                # Lift: P(A & B) / (P(A) * P(B))
                total_resumes = sum(self.skill_frequency.values()) / len(self.skill_frequency)
                lift = (count / total_resumes) / (
                    (self.skill_frequency[skill] / total_resumes) *
                    (self.skill_frequency[other_skill] / total_resumes)
                )
                normalized_scores[other_skill] = lift * count
            
            # Top 10 complementary skills
            top_complementary = sorted(
                normalized_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            self.complementary_skills[skill] = [s for s, _ in top_complementary]
    
    def recommend_skills(
        self,
        current_skills: List[str],
        target_level: str = None,
        target_role: str = None,
        num_recommendations: int = 10
    ) -> Dict:
        """
        Recommend skills for a candidate
        
        Args:
            current_skills: List of candidate's current skills
            target_level: Target experience level (entry/mid/senior/expert)
            target_role: Target job role (optional)
            num_recommendations: Number of recommendations to return
            
        Returns:
            Dictionary with recommendations and reasoning
        """
        if not self.is_trained:
            raise ValueError("Engine not trained. Call train_from_resumes() first.")
        
        current_skills_set = set(s.lower() for s in current_skills)
        recommendations = []
        
        # 1. Complementary skills (based on co-occurrence)
        complementary = self._get_complementary_recommendations(current_skills_set)
        
        # 2. Level progression skills
        level_based = []
        if target_level:
            level_based = self._get_level_based_recommendations(
                current_skills_set,
                target_level
            )
        
        # 3. High-demand skills (frequent but not possessed)
        high_demand = self._get_high_demand_recommendations(current_skills_set)
        
        # 4. Combine and rank
        all_recommendations = {}
        
        # Weight by category
        for skill, score in complementary:
            all_recommendations[skill] = all_recommendations.get(skill, 0) + score * 1.5
        
        for skill, score in level_based:
            all_recommendations[skill] = all_recommendations.get(skill, 0) + score * 1.2
        
        for skill, score in high_demand:
            all_recommendations[skill] = all_recommendations.get(skill, 0) + score * 1.0
        
        # Sort and format
        sorted_recommendations = sorted(
            all_recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_recommendations]
        
        result = {
            'recommendations': [],
            'summary': {
                'total_recommendations': len(sorted_recommendations),
                'current_skills_count': len(current_skills),
                'target_level': target_level,
                'recommendation_sources': {
                    'complementary': len(complementary),
                    'level_progression': len(level_based),
                    'high_demand': len(high_demand)
                }
            }
        }
        
        for skill, score in sorted_recommendations:
            # Determine reason
            reasons = []
            if skill in [s for s, _ in complementary]:
                reasons.append("complements current skills")
            if skill in [s for s, _ in level_based]:
                reasons.append(f"needed for {target_level} level")
            if skill in [s for s, _ in high_demand]:
                reasons.append("high market demand")
            
            # Get related skills
            related = self.complementary_skills.get(skill, [])[:3]
            
            result['recommendations'].append({
                'skill': skill,
                'score': round(score, 2),
                'reasons': reasons,
                'related_skills': related,
                'frequency': self.skill_frequency.get(skill, 0)
            })
        
        return result
    
    def _get_complementary_recommendations(
        self,
        current_skills: Set[str]
    ) -> List[Tuple[str, float]]:
        """Get skills that complement current skills"""
        complementary_scores = Counter()
        
        for skill in current_skills:
            if skill in self.complementary_skills:
                for comp_skill in self.complementary_skills[skill]:
                    if comp_skill.lower() not in current_skills:
                        # Score based on co-occurrence strength
                        cooccur_count = self.skill_cooccurrence[skill].get(comp_skill, 0)
                        complementary_scores[comp_skill] += cooccur_count
        
        return complementary_scores.most_common(20)
    
    def _get_level_based_recommendations(
        self,
        current_skills: Set[str],
        target_level: str
    ) -> List[Tuple[str, float]]:
        """Get skills needed for target experience level"""
        if target_level not in self.skill_by_level:
            return []
        
        target_skills = self.skill_by_level[target_level]
        missing_skills = []
        
        for skill in target_skills:
            if skill.lower() not in current_skills:
                # Score based on how common the skill is at that level
                frequency = self.skill_frequency.get(skill, 0)
                missing_skills.append((skill, frequency))
        
        return sorted(missing_skills, key=lambda x: x[1], reverse=True)[:15]
    
    def _get_high_demand_recommendations(
        self,
        current_skills: Set[str]
    ) -> List[Tuple[str, float]]:
        """Get high-demand skills not currently possessed"""
        high_demand = []
        
        # Top 50 most frequent skills
        for skill, freq in self.skill_frequency.most_common(50):
            if skill.lower() not in current_skills:
                high_demand.append((skill, freq))
        
        return high_demand[:15]
    
    def get_skill_pathway(
        self,
        current_skills: List[str],
        target_skills: List[str],
        max_steps: int = 3
    ) -> Dict:
        """
        Find learning pathway from current skills to target skills
        
        Args:
            current_skills: Current skill set
            target_skills: Desired skills to acquire
            max_steps: Maximum intermediate steps
            
        Returns:
            Learning pathway with intermediate skills
        """
        current_set = set(s.lower() for s in current_skills)
        target_set = set(s.lower() for s in target_skills)
        
        # Skills already have
        already_have = current_set & target_set
        
        # Skills to acquire
        to_acquire = target_set - current_set
        
        if not to_acquire:
            return {
                'status': 'complete',
                'message': 'You already have all target skills!',
                'skills_have': list(already_have)
            }
        
        # Find intermediate skills that bridge current to target
        pathway = []
        
        for target_skill in to_acquire:
            # Find skills that connect current skills to this target
            bridge_skills = []
            
            for current_skill in current_set:
                # Check if there's a strong connection
                if (current_skill in self.skill_cooccurrence and
                    target_skill in self.skill_cooccurrence[current_skill]):
                    
                    connection_strength = self.skill_cooccurrence[current_skill][target_skill]
                    bridge_skills.append({
                        'from': current_skill,
                        'to': target_skill,
                        'strength': connection_strength
                    })
            
            # Find intermediate skills
            intermediates = []
            if target_skill in self.complementary_skills:
                for comp_skill in self.complementary_skills[target_skill][:5]:
                    if comp_skill.lower() in current_set:
                        intermediates.append(comp_skill)
            
            pathway.append({
                'target_skill': target_skill,
                'direct_connections': len(bridge_skills),
                'related_current_skills': intermediates[:3],
                'learning_order': 'intermediate' if intermediates else 'foundational'
            })
        
        # Sort by learning order
        pathway.sort(key=lambda x: x['direct_connections'], reverse=True)
        
        return {
            'status': 'pathway_found',
            'skills_to_acquire': len(to_acquire),
            'skills_already_have': list(already_have),
            'learning_pathway': pathway[:max_steps * 2],
            'recommendations': [
                p['target_skill'] for p in pathway[:max_steps]
            ]
        }
    
    def analyze_skill_gaps(
        self,
        candidate_skills: List[str],
        job_requirements: List[str]
    ) -> Dict:
        """
        Analyze skill gaps between candidate and job requirements
        
        Args:
            candidate_skills: Candidate's current skills
            job_requirements: Required skills for job
            
        Returns:
            Gap analysis with recommendations
        """
        candidate_set = set(s.lower() for s in candidate_skills)
        required_set = set(s.lower() for s in job_requirements)
        
        # Direct matches
        matched = candidate_set & required_set
        missing = required_set - candidate_set
        extra = candidate_set - required_set
        
        # Analyze missing skills
        missing_analysis = []
        for skill in missing:
            analysis = {
                'skill': skill,
                'difficulty': 'unknown',
                'related_skills_you_have': [],
                'learning_resources': []
            }
            
            # Check if candidate has related skills
            if skill in self.complementary_skills:
                related = [
                    s for s in self.complementary_skills[skill][:5]
                    if s.lower() in candidate_set
                ]
                analysis['related_skills_you_have'] = related
                
                if related:
                    analysis['difficulty'] = 'moderate'
                else:
                    analysis['difficulty'] = 'challenging'
            
            # Check frequency (popular skills are easier to learn)
            freq = self.skill_frequency.get(skill, 0)
            if freq > 100:
                analysis['popularity'] = 'high'
            elif freq > 50:
                analysis['popularity'] = 'medium'
            else:
                analysis['popularity'] = 'low'
            
            missing_analysis.append(analysis)
        
        # Sort by difficulty (easier first)
        missing_analysis.sort(
            key=lambda x: (
                0 if x['difficulty'] == 'moderate' else 1,
                -len(x['related_skills_you_have'])
            )
        )
        
        return {
            'match_rate': len(matched) / len(required_set) if required_set else 1.0,
            'matched_skills': list(matched),
            'missing_skills': list(missing),
            'extra_skills': list(extra),
            'missing_analysis': missing_analysis,
            'recommendations': {
                'immediate_focus': [m['skill'] for m in missing_analysis[:3]],
                'stretch_goals': [m['skill'] for m in missing_analysis[3:6]],
                'transferable_skills': list(extra)[:5]
            }
        }


# ============================================================================
# SELF-TEST
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("🧪 TESTING SKILL RECOMMENDATION ENGINE")
    print("=" * 80)
    
    # Load training data
    data_path = Path('data/training/parsed_resumes_all.json')
    
    if data_path.exists():
        print(f"\n📂 Loading resumes from: {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            resumes = json.load(f)
        
        print(f"   Loaded {len(resumes)} resumes")
        
        # Train engine
        engine = SkillRecommendationEngine()
        stats = engine.train_from_resumes(resumes)
        
        # Test recommendations
        print("\n" + "=" * 80)
        print("TEST 1: Skill Recommendations for Python Developer")
        print("=" * 80)
        
        current_skills = ['Python', 'Django', 'PostgreSQL', 'Git']
        result = engine.recommend_skills(
            current_skills,
            target_level='senior',
            num_recommendations=10
        )
        
        print(f"\n🎯 Top 10 Recommended Skills:")
        for i, rec in enumerate(result['recommendations'], 1):
            reasons = ', '.join(rec['reasons'])
            related = ', '.join(rec['related_skills'][:3])
            print(f"\n{i}. {rec['skill']}")
            print(f"   Score: {rec['score']}")
            print(f"   Why: {reasons}")
            if related:
                print(f"   Related: {related}")
        
        # Test pathway
        print("\n" + "=" * 80)
        print("TEST 2: Learning Pathway")
        print("=" * 80)
        
        target_skills = ['Kubernetes', 'Docker', 'AWS', 'CI/CD', 'Microservices']
        pathway = engine.get_skill_pathway(
            current_skills,
            target_skills,
            max_steps=3
        )
        
        print(f"\n🛤️ Learning Pathway to DevOps Skills:")
        print(f"   Status: {pathway['status']}")
        print(f"   Skills to acquire: {pathway['skills_to_acquire']}")
        
        if pathway.get('learning_pathway'):
            print(f"\n   Recommended learning order:")
            for i, step in enumerate(pathway['learning_pathway'][:5], 1):
                related = ', '.join(step['related_current_skills'])
                print(f"   {i}. {step['target_skill']}")
                if related:
                    print(f"      (builds on: {related})")
        
        # Test gap analysis
        print("\n" + "=" * 80)
        print("TEST 3: Skill Gap Analysis")
        print("=" * 80)
        
        job_requirements = [
            'Python', 'React', 'TypeScript', 'AWS',
            'Docker', 'PostgreSQL', 'REST API', 'Git'
        ]
        
        gaps = engine.analyze_skill_gaps(current_skills, job_requirements)
        
        print(f"\n📊 Gap Analysis:")
        print(f"   Match rate: {gaps['match_rate']:.1%}")
        print(f"   Matched: {len(gaps['matched_skills'])} skills")
        print(f"   Missing: {len(gaps['missing_skills'])} skills")
        
        if gaps['missing_analysis']:
            print(f"\n   ⚠️ Skills to develop:")
            for i, missing in enumerate(gaps['missing_analysis'][:5], 1):
                print(f"   {i}. {missing['skill']}")
                print(f"      Difficulty: {missing['difficulty']}")
                if missing['related_skills_you_have']:
                    related = ', '.join(missing['related_skills_you_have'][:3])
                    print(f"      You know: {related}")
        
        if gaps['recommendations']['immediate_focus']:
            print(f"\n   🎯 Immediate focus:")
            for skill in gaps['recommendations']['immediate_focus']:
                print(f"      • {skill}")
        
        print("\n" + "=" * 80)
        print("✅ SKILL RECOMMENDATION ENGINE WORKING!")
        print("=" * 80)
    
    else:
        print(f"\n❌ Data file not found: {data_path}")
        print("   Run training script first to generate parsed resumes")
