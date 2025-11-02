"""
Feature Importance Analyzer
Analyzes which features (skills, experience, education) have the most impact on matching
Uses SHAP-like approach to compute feature importance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Dict, Any, List
import numpy as np


class FeatureImportanceAnalyzer:
    """
    Analyzes feature importance for match scoring
    Shows which candidate attributes contribute most to the match score
    """
    
    def __init__(self):
        """Initialize feature importance analyzer"""
        self.feature_names = [
            'semantic_similarity',
            'technical_skills',
            'soft_skills',
            'years_experience',
            'experience_level',
            'education_degree',
            'education_field',
            'certifications'
        ]
    
    def analyze_importance(self,
                          match_result: Dict[str, Any],
                          candidate_data: Dict[str, Any],
                          job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze feature importance for a specific match
        
        Args:
            match_result: Result from MatchScorer
            candidate_data: Candidate information
            job_data: Job requirements
            
        Returns:
            Dict with feature importance scores and rankings
        """
        # Extract features from candidate and job
        features = self._extract_features(candidate_data, job_data, match_result)
        
        # Calculate importance scores
        importance_scores = self._calculate_importance(features, match_result)
        
        # Rank features
        ranked_features = sorted(
            importance_scores.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Generate insights
        insights = self._generate_insights(ranked_features, features)
        
        return {
            'feature_importance': importance_scores,
            'ranked_features': [
                {
                    'feature': name,
                    'importance': round(score, 3),
                    'impact': 'positive' if score > 0 else 'negative'
                }
                for name, score in ranked_features
            ],
            'top_3_features': ranked_features[:3],
            'insights': insights
        }
    
    def _extract_features(self,
                         candidate_data: Dict[str, Any],
                         job_data: Dict[str, Any],
                         match_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant features from candidate and job data"""
        
        scores = match_result['scores']
        details = match_result['details']
        
        # Semantic similarity
        semantic_score = scores.get('semantic', 50)
        
        # Skills breakdown
        skill_details = details.get('skills', {})
        technical_skills_match = len(skill_details.get('required_matches', []))
        technical_skills_total = skill_details.get('total_required', 1)
        technical_skills_ratio = technical_skills_match / max(technical_skills_total, 1)
        
        # Experience breakdown
        exp_details = details.get('experience', {})
        years_experience = exp_details.get('candidate_years', 0)
        required_years = exp_details.get('required_years', 0)
        experience_level = exp_details.get('candidate_level', 'entry')
        
        # Education breakdown
        edu_details = details.get('education', {})
        education_degree = edu_details.get('highest_degree', '')
        education_field_match = edu_details.get('field_match', False)
        
        return {
            'semantic_similarity': semantic_score / 100.0,  # Normalize to 0-1
            'technical_skills_ratio': technical_skills_ratio,
            'years_experience': years_experience,
            'required_years': required_years,
            'experience_level': experience_level,
            'education_degree': education_degree,
            'education_field_match': 1.0 if education_field_match else 0.0,
            'overall_score': match_result['final_score']
        }
    
    def _calculate_importance(self,
                            features: Dict[str, Any],
                            match_result: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate importance scores for each feature
        Uses contribution to final score as a proxy for importance
        """
        scores = match_result['scores']
        weights = match_result['weights']
        final_score = match_result['final_score']
        
        importance = {}
        
        # Semantic similarity importance
        semantic_contribution = scores['semantic'] * weights['semantic']
        importance['semantic_similarity'] = semantic_contribution / max(final_score, 1)
        
        # Skills importance
        skills_contribution = scores['skills'] * weights['skills']
        importance['technical_skills'] = skills_contribution / max(final_score, 1)
        importance['soft_skills'] = 0.0  # Placeholder for future
        
        # Experience importance
        exp_contribution = scores['experience'] * weights['experience']
        years_importance = exp_contribution * 0.6  # 60% from years
        level_importance = exp_contribution * 0.4  # 40% from level
        importance['years_experience'] = years_importance / max(final_score, 1)
        importance['experience_level'] = level_importance / max(final_score, 1)
        
        # Education importance
        edu_contribution = scores['education'] * weights['education']
        degree_importance = edu_contribution * 0.6  # 60% from degree
        field_importance = edu_contribution * 0.4  # 40% from field
        importance['education_degree'] = degree_importance / max(final_score, 1)
        importance['education_field'] = field_importance / max(final_score, 1)
        
        # Certifications (placeholder)
        importance['certifications'] = 0.0
        
        return importance
    
    def _generate_insights(self,
                          ranked_features: List[tuple],
                          features: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from feature importance"""
        insights = []
        
        if not ranked_features:
            return insights
        
        # Top feature
        top_feature, top_score = ranked_features[0]
        if top_score > 0.25:  # Contributes more than 25%
            insights.append(
                f"🎯 **{top_feature.replace('_', ' ').title()}** is the strongest factor, "
                f"contributing {top_score*100:.1f}% to the match score."
            )
        
        # Identify weak spots
        weak_features = [(name, score) for name, score in ranked_features if score < 0.1]
        if weak_features:
            weak_feature = weak_features[0][0]
            insights.append(
                f"⚠️  **{weak_feature.replace('_', ' ').title()}** is a weak point - "
                f"improving this could significantly boost the match."
            )
        
        # Experience insights
        if 'years_experience' in dict(ranked_features):
            years_importance = dict(ranked_features)['years_experience']
            if years_importance > 0.15:
                insights.append(
                    "💼 **Years of experience** is a key differentiator for this match."
                )
        
        # Skills insights
        if 'technical_skills' in dict(ranked_features):
            skills_importance = dict(ranked_features)['technical_skills']
            if skills_importance > 0.30:
                insights.append(
                    "🛠️  **Technical skills** are the most critical factor - "
                    "skill overlap is heavily weighted."
                )
        
        return insights
    
    def compare_candidates(self,
                          candidates_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare feature importance across multiple candidates
        Shows which features matter most for this job
        
        Args:
            candidates_analyses: List of analysis results from analyze_importance()
            
        Returns:
            Dict with comparison insights
        """
        if not candidates_analyses:
            return {}
        
        # Aggregate importance scores
        feature_avg_importance = {}
        for analysis in candidates_analyses:
            for feature_info in analysis['ranked_features']:
                feature = feature_info['feature']
                importance = feature_info['importance']
                
                if feature not in feature_avg_importance:
                    feature_avg_importance[feature] = []
                feature_avg_importance[feature].append(importance)
        
        # Calculate averages
        avg_importance = {
            feature: np.mean(scores)
            for feature, scores in feature_avg_importance.items()
        }
        
        # Rank by average importance
        ranked_avg = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'average_feature_importance': avg_importance,
            'most_important_features': ranked_avg[:3],
            'least_important_features': ranked_avg[-3:],
            'candidates_analyzed': len(candidates_analyses)
        }


if __name__ == "__main__":
    print("=" * 80)
    print("📊 Testing Feature Importance Analyzer")
    print("=" * 80)
    
    # Test with sample data
    match_result = {
        'final_score': 78.5,
        'scores': {
            'semantic': 82.0,
            'skills': 85.0,
            'experience': 70.0,
            'education': 75.0
        },
        'weights': {
            'semantic': 0.30,
            'skills': 0.40,
            'experience': 0.20,
            'education': 0.10
        },
        'details': {
            'skills': {
                'required_matches': ['Python', 'Django', 'PostgreSQL'],
                'total_required': 4
            },
            'experience': {
                'candidate_years': 5,
                'required_years': 5,
                'candidate_level': 'senior'
            },
            'education': {
                'highest_degree': 'Bachelor',
                'field_match': True
            }
        }
    }
    
    candidate_data = {
        'skills': ['Python', 'Django', 'PostgreSQL'],
        'experience': [{'duration_months': 60}],
        'education': [{'degree': 'Bachelor', 'field': 'Computer Science'}]
    }
    
    job_data = {
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'Kubernetes'],
        'experience_years': 5
    }
    
    analyzer = FeatureImportanceAnalyzer()
    analysis = analyzer.analyze_importance(match_result, candidate_data, job_data)
    
    print("\n📊 Feature Importance Analysis:")
    print("=" * 80)
    
    for i, feature_info in enumerate(analysis['ranked_features'], 1):
        feature = feature_info['feature']
        importance = feature_info['importance']
        impact = feature_info['impact']
        
        # Create visual bar
        bar_length = int(importance * 50)
        bar = "█" * bar_length
        
        print(f"{i:2d}. {feature:25s} {importance:6.3f} {bar} ({impact})")
    
    print("\n💡 Insights:")
    print("=" * 80)
    for insight in analysis['insights']:
        print(f"   {insight}")
    
    print("\n🎯 Top 3 Most Important Features:")
    print("=" * 80)
    for i, (feature, importance) in enumerate(analysis['top_3_features'], 1):
        print(f"   {i}. {feature.replace('_', ' ').title()}: {importance:.3f}")
    
    print("\n" + "=" * 80)
    print("✅ Feature Importance Analyzer Test Complete!")
    print("=" * 80)
