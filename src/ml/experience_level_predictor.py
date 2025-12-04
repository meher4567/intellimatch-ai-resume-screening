"""
Experience Level Predictor
Enhanced classification of candidate seniority level with confidence scoring
"""

import re
from typing import Dict, List, Tuple
from collections import Counter


class ExperienceLevelPredictor:
    """
    Predicts candidate experience level (Entry/Junior/Mid/Senior/Expert/Lead)
    based on multiple factors:
    1. Years of experience
    2. Job titles and progression
    3. Skill breadth and depth
    4. Responsibilities and leadership indicators
    5. Project complexity indicators
    """
    
    def __init__(self):
        # Title indicators by level
        self.title_indicators = {
            'entry': {
                'keywords': ['intern', 'trainee', 'junior', 'associate', 'entry', 'assistant', 'graduate'],
                'weight': 1.0
            },
            'mid': {
                'keywords': ['developer', 'engineer', 'analyst', 'specialist', 'consultant'],
                'weight': 1.0
            },
            'senior': {
                'keywords': ['senior', 'sr.', 'lead', 'principal', 'staff'],
                'weight': 1.2
            },
            'expert': {
                'keywords': ['expert', 'architect', 'distinguished', 'fellow', 'chief'],
                'weight': 1.5
            },
            'lead': {
                'keywords': ['manager', 'director', 'vp', 'head', 'cto', 'ceo', 'president'],
                'weight': 1.5
            }
        }
        
        # Responsibility indicators
        self.responsibility_indicators = {
            'entry': [
                r'assisted', r'helped', r'supported', r'learned',
                r'shadowed', r'participated', r'contributed to'
            ],
            'mid': [
                r'developed', r'implemented', r'created', r'built',
                r'designed', r'maintained', r'delivered'
            ],
            'senior': [
                r'led\s+team', r'architected', r'designed\s+system',
                r'mentored', r'owned', r'drove', r'established'
            ],
            'expert': [
                r'defined\s+strategy', r'technical\s+vision', r'transformed',
                r'pioneered', r'industry\s+expert', r'thought\s+leader'
            ],
            'lead': [
                r'managed\s+team', r'directed', r'oversaw', r'hired',
                r'budget', r'P&L', r'strategy', r'roadmap'
            ]
        }
        
        # Leadership indicators
        self.leadership_patterns = [
            r'led\s+(?:team|project|initiative)',
            r'managed\s+\d+\s+(?:people|engineers|developers)',
            r'mentored\s+\d+',
            r'team\s+of\s+\d+',
            r'reporting\s+to\s+(?:ceo|cto|vp)',
            r'cross[- ]functional',
            r'stakeholder'
        ]
        
        # Complexity indicators
        self.complexity_patterns = [
            r'large[- ]scale',
            r'enterprise',
            r'distributed\s+system',
            r'microservices',
            r'\d+[kKmMbB]\s+(?:users|customers|requests)',
            r'high[- ]availability',
            r'scalability',
            r'performance\s+optimization'
        ]
    
    def predict_level(
        self,
        resume_data: Dict,
        include_reasoning: bool = True
    ) -> Dict:
        """
        Predict experience level with confidence scoring
        
        Args:
            resume_data: Parsed resume dictionary
            include_reasoning: Include detailed reasoning
            
        Returns:
            Level prediction with confidence and reasoning
        """
        # Collect signals
        signals = self._collect_signals(resume_data)
        
        # Calculate scores for each level
        level_scores = self._calculate_level_scores(signals)
        
        # Determine primary and alternative levels
        sorted_levels = sorted(
            level_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        primary_level = sorted_levels[0][0]
        primary_confidence = sorted_levels[0][1]
        
        # Normalize confidence to 0-1 range
        total_score = sum(score for _, score in sorted_levels)
        if total_score > 0:
            normalized_confidence = primary_confidence / total_score
        else:
            normalized_confidence = 0.5
        
        # Determine confidence tier
        if normalized_confidence >= 0.6:
            confidence_tier = 'High'
        elif normalized_confidence >= 0.4:
            confidence_tier = 'Medium'
        else:
            confidence_tier = 'Low'
        
        result = {
            'predicted_level': primary_level.title(),
            'confidence': round(normalized_confidence, 2),
            'confidence_tier': confidence_tier,
            'all_scores': {
                level.title(): round(score, 2)
                for level, score in sorted_levels
            }
        }
        
        if include_reasoning:
            result['reasoning'] = self._generate_reasoning(signals, primary_level)
            result['signals'] = signals
        
        return result
    
    def _collect_signals(self, resume_data: Dict) -> Dict:
        """Collect all signals for level prediction"""
        signals = {
            'years_experience': 0,
            'job_count': 0,
            'title_indicators': Counter(),
            'responsibility_indicators': Counter(),
            'leadership_count': 0,
            'complexity_count': 0,
            'skill_count': 0,
            'education_level': None,
            'has_certifications': False,
            'has_publications': False
        }
        
        # Years of experience
        if resume_data.get('timeline_analysis'):
            signals['years_experience'] = resume_data['timeline_analysis'].get('total_experience_years', 0)
        elif resume_data.get('experience_details'):
            signals['years_experience'] = resume_data['experience_details'].get('candidate_years', 0)
        
        # Job count and titles
        experience_list = resume_data.get('experience', [])
        if isinstance(experience_list, list):
            signals['job_count'] = len(experience_list)
            
            # Analyze titles
            for job in experience_list:
                title = job.get('title', '').lower()
                description = job.get('description', '').lower()
                
                # Check title indicators
                for level, data in self.title_indicators.items():
                    for keyword in data['keywords']:
                        if keyword in title:
                            signals['title_indicators'][level] += data['weight']
                
                # Check responsibility indicators
                for level, patterns in self.responsibility_indicators.items():
                    for pattern in patterns:
                        if re.search(pattern, description, re.IGNORECASE):
                            signals['responsibility_indicators'][level] += 1
                
                # Check leadership patterns
                for pattern in self.leadership_patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        signals['leadership_count'] += 1
                
                # Check complexity patterns
                for pattern in self.complexity_patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        signals['complexity_count'] += 1
        
        # Skills
        skills_data = resume_data.get('skills', {})
        if isinstance(skills_data, dict):
            signals['skill_count'] = len(skills_data.get('all_skills', []))
        elif isinstance(skills_data, list):
            signals['skill_count'] = len(skills_data)
        
        # Education
        education = resume_data.get('education', [])
        if education:
            if isinstance(education, list) and len(education) > 0:
                highest = education[0].get('degree', '').lower()
                if any(x in highest for x in ['phd', 'doctorate']):
                    signals['education_level'] = 'doctorate'
                elif any(x in highest for x in ['master', 'msc', 'mba', 'ms']):
                    signals['education_level'] = 'masters'
                elif any(x in highest for x in ['bachelor', 'bsc', 'ba', 'bs']):
                    signals['education_level'] = 'bachelors'
        
        # Certifications
        signals['has_certifications'] = bool(resume_data.get('certifications'))
        
        # Publications
        text = resume_data.get('text', '').lower()
        signals['has_publications'] = bool(re.search(r'\bpublication|paper|journal|conference', text))
        
        return signals
    
    def _calculate_level_scores(self, signals: Dict) -> Dict[str, float]:
        """Calculate scores for each experience level"""
        scores = {
            'entry': 0,
            'mid': 0,
            'senior': 0,
            'expert': 0,
            'lead': 0
        }
        
        years = signals['years_experience']
        
        # Years-based scoring
        if years < 1:
            scores['entry'] += 10
        elif years < 3:
            scores['entry'] += 5
            scores['mid'] += 5
        elif years < 5:
            scores['mid'] += 10
        elif years < 8:
            scores['mid'] += 5
            scores['senior'] += 5
        elif years < 12:
            scores['senior'] += 10
        else:
            scores['senior'] += 5
            scores['expert'] += 5
            scores['lead'] += 5
        
        # Title indicators
        for level, count in signals['title_indicators'].items():
            scores[level] += count * 5
        
        # Responsibility indicators
        for level, count in signals['responsibility_indicators'].items():
            scores[level] += count * 2
        
        # Leadership signals
        if signals['leadership_count'] >= 5:
            scores['senior'] += 5
            scores['lead'] += 10
        elif signals['leadership_count'] >= 2:
            scores['senior'] += 5
            scores['lead'] += 5
        
        # Complexity signals
        if signals['complexity_count'] >= 5:
            scores['senior'] += 5
            scores['expert'] += 5
        elif signals['complexity_count'] >= 2:
            scores['senior'] += 3
        
        # Skill breadth
        if signals['skill_count'] >= 20:
            scores['senior'] += 5
            scores['expert'] += 3
        elif signals['skill_count'] >= 10:
            scores['mid'] += 3
            scores['senior'] += 3
        elif signals['skill_count'] < 5:
            scores['entry'] += 3
        
        # Education
        if signals['education_level'] == 'doctorate':
            scores['expert'] += 5
            scores['senior'] += 3
        elif signals['education_level'] == 'masters':
            scores['senior'] += 3
            scores['mid'] += 2
        
        # Certifications
        if signals['has_certifications']:
            scores['mid'] += 2
            scores['senior'] += 2
        
        # Publications
        if signals['has_publications']:
            scores['expert'] += 5
            scores['senior'] += 3
        
        # Job count (career progression)
        if signals['job_count'] >= 5:
            scores['senior'] += 3
            scores['expert'] += 2
        elif signals['job_count'] >= 3:
            scores['mid'] += 3
            scores['senior'] += 2
        
        return scores
    
    def _generate_reasoning(self, signals: Dict, predicted_level: str) -> Dict:
        """Generate human-readable reasoning for the prediction"""
        reasoning = {
            'primary_factors': [],
            'supporting_factors': [],
            'level_indicators': {}
        }
        
        # Years
        years = signals['years_experience']
        if years > 0:
            reasoning['primary_factors'].append(
                f"{years:.1f} years of professional experience"
            )
        
        # Titles
        if signals['title_indicators']:
            top_title_level = signals['title_indicators'].most_common(1)[0][0]
            count = signals['title_indicators'][top_title_level]
            reasoning['primary_factors'].append(
                f"Job titles suggest {top_title_level} level ({count} indicators)"
            )
        
        # Responsibilities
        if signals['responsibility_indicators']:
            top_resp_level = signals['responsibility_indicators'].most_common(1)[0][0]
            count = signals['responsibility_indicators'][top_resp_level]
            reasoning['supporting_factors'].append(
                f"Responsibilities align with {top_resp_level} level ({count} indicators)"
            )
        
        # Leadership
        if signals['leadership_count'] > 0:
            reasoning['supporting_factors'].append(
                f"Shows leadership experience ({signals['leadership_count']} indicators)"
            )
        
        # Complexity
        if signals['complexity_count'] > 0:
            reasoning['supporting_factors'].append(
                f"Worked on complex systems ({signals['complexity_count']} indicators)"
            )
        
        # Skills
        if signals['skill_count'] >= 15:
            reasoning['supporting_factors'].append(
                f"Broad skill set ({signals['skill_count']} skills)"
            )
        elif signals['skill_count'] >= 8:
            reasoning['supporting_factors'].append(
                f"Solid skill base ({signals['skill_count']} skills)"
            )
        
        # Education
        if signals['education_level']:
            reasoning['supporting_factors'].append(
                f"Education: {signals['education_level'].title()}"
            )
        
        # Level-specific indicators
        reasoning['level_indicators'] = {
            'years': years,
            'jobs': signals['job_count'],
            'skills': signals['skill_count'],
            'leadership': signals['leadership_count'],
            'complexity': signals['complexity_count']
        }
        
        return reasoning
    
    def get_level_recommendations(self, current_level: str, target_level: str = None) -> Dict:
        """
        Get recommendations for advancing to next level
        
        Args:
            current_level: Current experience level
            target_level: Target level (optional)
            
        Returns:
            Recommendations for advancement
        """
        level_order = ['entry', 'mid', 'senior', 'expert', 'lead']
        
        if current_level.lower() not in level_order:
            return {'error': 'Invalid current level'}
        
        current_idx = level_order.index(current_level.lower())
        
        if target_level:
            if target_level.lower() not in level_order:
                return {'error': 'Invalid target level'}
            target_idx = level_order.index(target_level.lower())
        else:
            target_idx = min(current_idx + 1, len(level_order) - 1)
        
        if target_idx <= current_idx:
            return {
                'message': f'Already at or above {target_level} level',
                'current_level': current_level.title(),
                'target_level': target_level.title() if target_level else None
            }
        
        target = level_order[target_idx]
        
        # Generate recommendations
        recommendations = {
            'current_level': current_level.title(),
            'target_level': target.title(),
            'typical_timeline': self._get_typical_timeline(current_level.lower(), target),
            'key_actions': self._get_advancement_actions(target),
            'skills_to_develop': self._get_skills_for_level(target),
            'experience_needed': self._get_experience_for_level(target)
        }
        
        return recommendations
    
    def _get_typical_timeline(self, from_level: str, to_level: str) -> str:
        """Get typical time to advance between levels"""
        timelines = {
            ('entry', 'mid'): '2-3 years',
            ('mid', 'senior'): '3-5 years',
            ('senior', 'expert'): '5-8 years',
            ('expert', 'lead'): '3-5 years',
            ('entry', 'senior'): '5-7 years',
            ('mid', 'expert'): '8-12 years'
        }
        
        return timelines.get((from_level, to_level), 'Varies')
    
    def _get_advancement_actions(self, target_level: str) -> List[str]:
        """Get actions to advance to target level"""
        actions = {
            'mid': [
                'Take ownership of complete features/projects',
                'Demonstrate consistent delivery quality',
                'Start mentoring junior team members',
                'Expand technical skill breadth'
            ],
            'senior': [
                'Lead complex projects independently',
                'Mentor and guide team members regularly',
                'Drive technical decisions and architecture',
                'Contribute to team processes and standards',
                'Demonstrate cross-functional collaboration'
            ],
            'expert': [
                'Establish technical vision and strategy',
                'Solve organization-wide technical challenges',
                'Publish thought leadership (blogs, talks, papers)',
                'Mentor senior engineers and architects',
                'Drive adoption of best practices across teams'
            ],
            'lead': [
                'Build and manage high-performing teams',
                'Define roadmaps and strategic direction',
                'Manage budgets and resource allocation',
                'Partner with senior leadership',
                'Develop organizational processes and culture'
            ]
        }
        
        return actions.get(target_level, [])
    
    def _get_skills_for_level(self, level: str) -> List[str]:
        """Get skills typically needed for level"""
        skills = {
            'mid': [
                'Solid technical fundamentals in core technologies',
                'Problem-solving and debugging',
                'Code review and quality standards',
                'Agile development practices'
            ],
            'senior': [
                'System design and architecture',
                'Technical leadership and mentoring',
                'Cross-functional communication',
                'Performance optimization',
                'Security best practices'
            ],
            'expert': [
                'Advanced architectural patterns',
                'Technical strategy and vision',
                'Industry trends and innovations',
                'Thought leadership and influence',
                'Research and innovation'
            ],
            'lead': [
                'People management and development',
                'Strategic planning and execution',
                'Stakeholder management',
                'Budget and resource planning',
                'Organizational leadership'
            ]
        }
        
        return skills.get(level, [])
    
    def _get_experience_for_level(self, level: str) -> str:
        """Get typical experience description for level"""
        experience = {
            'mid': '3-5 years of hands-on development experience with consistent delivery',
            'senior': '5-8 years with proven track record of leading projects and mentoring',
            'expert': '10+ years with significant technical contributions and industry recognition',
            'lead': '10+ years with progression to management and strategic roles'
        }
        
        return experience.get(level, '')


# ============================================================================
# SELF-TEST
# ============================================================================
if __name__ == "__main__":
    import json
    from pathlib import Path
    
    print("=" * 80)
    print("🧪 TESTING EXPERIENCE LEVEL PREDICTOR")
    print("=" * 80)
    
    # Load real resumes
    data_path = Path('data/training/parsed_resumes_all.json')
    
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            resumes = json.load(f)
        
        print(f"\n📂 Loaded {len(resumes)} resumes")
        
        predictor = ExperienceLevelPredictor()
        
        # Test on sample resumes
        print("\n" + "=" * 80)
        print("TEST 1: Predicting Experience Levels")
        print("=" * 80)
        
        level_distribution = Counter()
        
        for i, resume in enumerate(resumes[:10]):
            result = predictor.predict_level(resume, include_reasoning=True)
            level_distribution[result['predicted_level']] += 1
            
            if i < 3:  # Show details for first 3
                print(f"\n📄 Resume {i+1}: {resume.get('file_path_original', 'Unknown')[:50]}...")
                print(f"   Predicted Level: {result['predicted_level']}")
                print(f"   Confidence: {result['confidence']:.2f} ({result['confidence_tier']})")
                
                if result['reasoning']['primary_factors']:
                    print(f"   Primary Factors:")
                    for factor in result['reasoning']['primary_factors'][:2]:
                        print(f"      • {factor}")
                
                print(f"   All Scores: {', '.join(f'{k}: {v:.2f}' for k, v in list(result['all_scores'].items())[:3])}")
        
        # Test on more resumes for distribution
        print("\n" + "=" * 80)
        print("TEST 2: Level Distribution (50 resumes)")
        print("=" * 80)
        
        for resume in resumes[10:60]:
            result = predictor.predict_level(resume, include_reasoning=False)
            level_distribution[result['predicted_level']] += 1
        
        print(f"\n📊 Level Distribution:")
        for level, count in level_distribution.most_common():
            percentage = (count / 60) * 100
            bar = '█' * int(percentage / 2)
            print(f"   {level:.<15} {bar} {count} ({percentage:.1f}%)")
        
        # Test recommendations
        print("\n" + "=" * 80)
        print("TEST 3: Advancement Recommendations")
        print("=" * 80)
        
        recommendations = predictor.get_level_recommendations('Mid', 'Senior')
        
        print(f"\n🎯 Advancing from {recommendations['current_level']} to {recommendations['target_level']}")
        print(f"   Typical Timeline: {recommendations['typical_timeline']}")
        
        print(f"\n   Key Actions:")
        for action in recommendations['key_actions'][:3]:
            print(f"      • {action}")
        
        print(f"\n   Skills to Develop:")
        for skill in recommendations['skills_to_develop'][:3]:
            print(f"      • {skill}")
        
        print("\n" + "=" * 80)
        print("✅ EXPERIENCE LEVEL PREDICTOR WORKING!")
        print("=" * 80)
    
    else:
        print(f"\n❌ Data file not found: {data_path}")
