"""
Matching Engine
Main integration service that orchestrates the complete matching pipeline
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.ml.embedding_generator import EmbeddingGenerator
from src.ml.vector_store import VectorStore
from src.ml.semantic_search import SemanticSearch
from src.ml.match_scorer import MatchScorer
from src.ml.candidate_ranker import CandidateRanker
from src.ml.match_explainer import MatchExplainer
from src.ml.resume_quality_scorer import ResumeQualityScorer
from src.services.job_description_parser import JobDescriptionParser
from src.ml.experience_classifier import ExperienceLevelClassifier


class MatchingEngine:
    """
    Complete matching engine that orchestrates:
    1. Resume indexing
    2. Job parsing
    3. Semantic search
    4. Multi-factor scoring
    5. Candidate ranking
    6. Match explanations
    """
    
    def __init__(self,
                 model_name: str = 'mini',
                 embedding_dim: int = 384,
                 storage_path: str = 'data/embeddings'):
        """
        Initialize matching engine
        
        Args:
            model_name: Sentence transformer model name
            embedding_dim: Embedding dimension
            storage_path: Path to store embeddings and indexes
        """
        print("🚀 Initializing Matching Engine...")
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator(model_name=model_name)
        self.vector_store = VectorStore(
            embedding_dim=self.embedding_generator.embedding_dim,
            metric='cosine'
        )
        self.semantic_search = SemanticSearch(
            embedding_model=model_name,
            vector_store=self.vector_store
        )
        self.job_parser = JobDescriptionParser()
        self.scorer = MatchScorer()
        self.ranker = CandidateRanker()
        self.explainer = MatchExplainer()
        self.quality_scorer = ResumeQualityScorer()
        # Experience level classifier (Entry/Mid/Senior/Expert)
        try:
            self.experience_classifier = ExperienceLevelClassifier()
        except Exception:
            self.experience_classifier = None
        
        # Storage
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.stats = {
            'resumes_indexed': 0,
            'jobs_processed': 0,
            'matches_generated': 0,
            'last_updated': None
        }
        
        print("✅ Matching Engine ready!")
        print(f"   Model: {model_name}")
        print(f"   Embedding dim: {embedding_dim}")
        print(f"   Storage: {storage_path}")
    
    def index_resume(self,
                    resume_data: Dict[str, Any],
                    resume_id: Optional[str] = None) -> str:
        """
        Index a single resume
        
        Args:
            resume_data: Parsed resume data
            resume_id: Unique resume identifier
            
        Returns:
            Resume ID
        """
        if resume_id is None:
            resume_id = resume_data.get('id', f"resume_{datetime.now().timestamp()}")
        
        # Add resume_id to data if not present
        resume_data['id'] = resume_id
        
        # Index in semantic search
        self.semantic_search.index_resume(resume_data)
        
        # Update stats
        self.stats['resumes_indexed'] += 1
        self.stats['last_updated'] = datetime.now().isoformat()
        
        return resume_id
    
    def index_resumes_batch(self, resumes_data: List[Dict[str, Any]]) -> List[str]:
        """
        Index multiple resumes in batch
        
        Args:
            resumes_data: List of parsed resume data
            
        Returns:
            List of resume IDs
        """
        print(f"📊 Indexing {len(resumes_data)} resumes...")
        
        resume_ids = self.semantic_search.index_resumes_batch(resumes_data)
        
        # Update stats
        self.stats['resumes_indexed'] += len(resume_ids)
        self.stats['last_updated'] = datetime.now().isoformat()
        
        print(f"✅ Indexed {len(resume_ids)} resumes")
        
        return resume_ids
    
    def parse_job(self, job_text: str) -> Dict[str, Any]:
        """
        Parse job description text
        
        Args:
            job_text: Raw job description text
            
        Returns:
            Parsed job data
        """
        job_data = self.job_parser.parse(job_text)
        
        # Update stats
        self.stats['jobs_processed'] += 1
        
        return job_data
    
    def find_matches(self,
                    job_data: Dict[str, Any],
                    top_k: int = 50,
                    min_score: Optional[float] = None,
                    filters: Optional[Dict[str, Any]] = None,
                    scoring_weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Find matching candidates for a job
        
        Args:
            job_data: Parsed job description data
            top_k: Number of candidates to retrieve from semantic search
            min_score: Minimum match score threshold
            filters: Optional filters (experience, skills, education, quality)
            scoring_weights: Custom scoring weights (semantic, skills, experience, education)
            
        Returns:
            List of ranked candidates with match details
        """
        # Convert JobDescription object to dict if needed
        if hasattr(job_data, 'to_dict'):
            job_data = job_data.to_dict()
        
        print(f"\n🔍 Finding matches for: {job_data.get('title', 'Unknown Job')}")
        
        # Step 1: Semantic search to get initial candidates
        print(f"   Step 1: Semantic search (top {top_k} candidates)...")
        candidates = self.semantic_search.search_for_job(
            job_data=job_data,
            k=top_k,
            filters=filters
        )
        
        if not candidates:
            print("   ⚠️  No candidates found matching filters")
            return []
        
        print(f"   ✅ Found {len(candidates)} candidates from semantic search")
        
        # Step 2: Multi-factor scoring
        print("   Step 2: Multi-factor scoring...")
        
        # Use custom weights if provided
        if scoring_weights:
            scorer = MatchScorer(**scoring_weights)
        else:
            scorer = self.scorer
        
        scored_candidates = []
        for candidate in candidates:
            # Get semantic score from search
            semantic_score = candidate['score']
            
            # Calculate resume quality score
            quality_result = self.quality_scorer.score_resume(candidate)

            # Predict experience level (if classifier available)
            experience_pred = {'level': None, 'confidence': 0.0}
            try:
                if self.experience_classifier:
                    experience_pred = self.experience_classifier.predict(candidate.get('experience', ''))
            except Exception:
                experience_pred = {'level': None, 'confidence': 0.0}
            
            # Calculate comprehensive match
            match_result = scorer.calculate_match(
                candidate_data=candidate,
                job_data=job_data,
                semantic_score=semantic_score
            )
            
            # Combine candidate data with match result
            scored_candidate = {
                'resume_id': candidate['resume_id'],
                'name': candidate.get('name', 'Unknown'),
                'email': candidate.get('email', ''),
                'skills': candidate.get('skills', []),
                'experience_years': candidate.get('experience_years', 0),
                'experience_level': experience_pred.get('level'),
                'experience_confidence': experience_pred.get('confidence', 0.0),
                'education': candidate.get('education', []),
                'match_score': match_result['final_score'],
                'quality_score': quality_result['overall_score'],
                'quality_grade': quality_result['grade'],
                'match_details': match_result,
                'quality_details': quality_result
            }
            
            scored_candidates.append(scored_candidate)
        
        print(f"   ✅ Scored {len(scored_candidates)} candidates")
        
        # Step 3: Ranking
        print("   Step 3: Ranking candidates...")
        ranked_candidates = self.ranker.rank_candidates(
            scored_candidates,
            min_score=min_score
        )
        
        print(f"   ✅ Ranked {len(ranked_candidates)} candidates")
        
        # Step 4: Generate explanations for top candidates
        print("   Step 4: Generating explanations...")
        for i, candidate in enumerate(ranked_candidates[:10]):  # Top 10 only
            explanation = self.explainer.explain_match(candidate['match_details'])
            candidate['explanation'] = explanation
        
        # Update stats
        self.stats['matches_generated'] += len(ranked_candidates)
        
        print(f"\n✅ Matching complete! Found {len(ranked_candidates)} candidates")
        
        return ranked_candidates
    
    def compare_candidates(self,
                          candidate_ids: List[str],
                          job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Side-by-side comparison of multiple candidates
        
        Args:
            candidate_ids: List of resume IDs to compare
            job_data: Job data for comparison context
            
        Returns:
            Comparison report
        """
        print(f"\n📊 Comparing {len(candidate_ids)} candidates...")
        
        candidates = []
        for resume_id in candidate_ids:
            # Get candidate data from vector store
            candidate_data = self.semantic_search.vector_store.get_by_resume_id(resume_id)
            
            if candidate_data:
                # Calculate match
                match_result = self.scorer.calculate_match(
                    candidate_data=candidate_data,
                    job_data=job_data
                )
                
                candidates.append({
                    'resume_id': resume_id,
                    'name': candidate_data.get('name', 'Unknown'),
                    'match_score': match_result['final_score'],
                    'match_details': match_result,
                    'explanation': self.explainer.explain_match(match_result)
                })
        
        # Sort by score
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Generate comparison summary
        comparison = {
            'job_title': job_data.get('title', 'Unknown'),
            'candidates': candidates,
            'best_candidate': candidates[0] if candidates else None,
            'comparison_matrix': self._generate_comparison_matrix(candidates)
        }
        
        print(f"✅ Comparison complete!")
        
        return comparison
    
    def _generate_comparison_matrix(self, candidates: List[Dict]) -> Dict[str, Any]:
        """Generate comparison matrix for candidates"""
        if not candidates:
            return {}
        
        matrix = {
            'names': [c['name'] for c in candidates],
            'overall_scores': [c['match_score'] for c in candidates],
            'semantic_scores': [c['match_details']['scores']['semantic'] for c in candidates],
            'skill_scores': [c['match_details']['scores']['skills'] for c in candidates],
            'experience_scores': [c['match_details']['scores']['experience'] for c in candidates],
            'education_scores': [c['match_details']['scores']['education'] for c in candidates],
            'strengths': [c['match_details']['strengths'] for c in candidates],
            'weaknesses': [c['match_details']['weaknesses'] for c in candidates]
        }
        
        return matrix
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            **self.stats,
            'indexed_resumes': self.vector_store.size(),
            'semantic_search_stats': self.semantic_search.stats()
        }
    
    def save_state(self, name: str = 'matching_engine'):
        """
        Save engine state to disk
        
        Args:
            name: Name for saved state
        """
        print(f"\n💾 Saving matching engine state: {name}")
        
        # Save vector store
        self.semantic_search.save(name)
        
        # Save stats
        stats_file = self.storage_path / f"{name}_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"✅ State saved!")
    
    def load_state(self, name: str = 'matching_engine'):
        """
        Load engine state from disk
        
        Args:
            name: Name of saved state
        """
        print(f"\n📂 Loading matching engine state: {name}")
        
        # Load vector store
        self.semantic_search.load(name)
        
        # Load stats
        stats_file = self.storage_path / f"{name}_stats.json"
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                self.stats = json.load(f)
        
        print(f"✅ State loaded!")
        print(f"   Resumes indexed: {self.stats['resumes_indexed']}")
        print(f"   Jobs processed: {self.stats['jobs_processed']}")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Matching Engine")
    print("=" * 70)
    
    # Initialize engine
    engine = MatchingEngine()
    
    # Test 1: Index sample resumes
    print("\n1️⃣ Test: Index resumes")
    
    sample_resumes = [
        {
            'metadata': {'file_name': 'john_doe.pdf', 'quality_score': 95},
            'personal_info': {'name': 'John Doe', 'email': 'john.doe@email.com'},
            'skills': {
                'all_skills': ['Python', 'Django', 'AWS', 'PostgreSQL', 'Docker'],
                'top_skills': ['Python', 'Django', 'AWS']
            },
            'experience': [
                {'title': 'Senior Software Engineer', 'company': 'Tech Corp', 'duration_months': 36, 'achievements': ['Built scalable APIs', 'Led team of 5']},
                {'title': 'Software Engineer', 'company': 'Startup Inc', 'duration_months': 24, 'achievements': ['Migrated to microservices']}
            ],
            'education': [
                {'degree': 'Bachelor of Science', 'field_of_study': 'Computer Science', 'institution': 'MIT'}
            ]
        },
        {
            'metadata': {'file_name': 'jane_smith.pdf', 'quality_score': 92},
            'personal_info': {'name': 'Jane Smith', 'email': 'jane.smith@email.com'},
            'skills': {
                'all_skills': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'SQL'],
                'top_skills': ['Python', 'Machine Learning', 'TensorFlow']
            },
            'experience': [
                {'title': 'Data Scientist', 'company': 'AI Labs', 'duration_months': 24, 'achievements': ['Built ML pipeline', 'Deployed 5 models']}
            ],
            'education': [
                {'degree': 'Master of Science', 'field_of_study': 'Data Science', 'institution': 'Stanford'}
            ]
        },
        {
            'metadata': {'file_name': 'bob_johnson.pdf', 'quality_score': 88},
            'personal_info': {'name': 'Bob Johnson', 'email': 'bob.j@email.com'},
            'skills': {
                'all_skills': ['React', 'JavaScript', 'TypeScript', 'Node.js', 'CSS'],
                'top_skills': ['React', 'JavaScript', 'TypeScript']
            },
            'experience': [
                {'title': 'Frontend Developer', 'company': 'Web Co', 'duration_months': 48, 'achievements': ['Built 10+ web apps']}
            ],
            'education': [
                {'degree': 'Bachelor', 'field_of_study': 'Computer Science', 'institution': 'UC Berkeley'}
            ]
        }
    ]
    
    resume_ids = engine.index_resumes_batch(sample_resumes)
    print(f"\n   Indexed resume IDs: {resume_ids}")
    
    # Test 2: Parse job and find matches
    print("\n" + "=" * 70)
    print("\n2️⃣ Test: Find matches for job")
    
    job_text = """
    Senior Backend Engineer
    
    TechCorp Inc. is seeking a Senior Backend Engineer to join our growing team.
    
    Location: San Francisco, CA (Hybrid)
    Salary: $150,000 - $180,000
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and Django
    - Experience with PostgreSQL and database design
    - AWS cloud experience
    - Docker and containerization knowledge
    
    Nice to have:
    - Kubernetes experience
    - Microservices architecture
    - CI/CD pipeline setup
    
    Responsibilities:
    - Design and develop scalable backend systems
    - Lead technical discussions and code reviews
    - Mentor junior engineers
    - Collaborate with product team
    
    Education: Bachelor's degree in Computer Science or related field
    """
    
    # Parse job
    job_data = engine.parse_job(job_text)
    print(f"\n   Job parsed: {job_data.title}")
    print(f"   Required skills: {', '.join(job_data.required_skills)}")
    
    # Find matches
    matches = engine.find_matches(
        job_data=job_data.__dict__,
        top_k=10,
        min_score=30
    )
    
    print(f"\n   📊 Top Matches:")
    for match in matches:
        print(f"\n   #{match['rank']} {match['name']} ({match['tier']})")
        print(f"      Match Score: {match['match_score']:.1f}/100")
        print(f"      Quality Score: {match.get('quality_score', 0):.1f}/10 ({match.get('quality_grade', 'N/A')})")
        print(f"      Skills: {', '.join(match['skills'][:3])}")
        print(f"      Experience: {match['experience_years']} years")
        
        if 'explanation' in match:
            print(f"      Summary: {match['explanation']['summary']}")
    
    # Test 3: Compare top 2 candidates
    print("\n" + "=" * 70)
    print("\n3️⃣ Test: Compare candidates")
    
    if len(matches) >= 2:
        comparison = engine.compare_candidates(
            candidate_ids=[matches[0]['resume_id'], matches[1]['resume_id']],
            job_data=job_data.__dict__
        )
        
        print(f"\n   Comparing: {comparison['candidates'][0]['name']} vs {comparison['candidates'][1]['name']}")
        print(f"   Scores: {comparison['candidates'][0]['match_score']:.1f} vs {comparison['candidates'][1]['match_score']:.1f}")
        print(f"   Best: {comparison['best_candidate']['name']}")
    
    # Test 4: Get stats
    print("\n" + "=" * 70)
    print("\n4️⃣ Test: Engine statistics")
    
    stats = engine.get_stats()
    print(f"\n   📊 Engine Stats:")
    print(f"      Resumes indexed: {stats['resumes_indexed']}")
    print(f"      Jobs processed: {stats['jobs_processed']}")
    print(f"      Matches generated: {stats['matches_generated']}")
    print(f"      Last updated: {stats['last_updated']}")
    
    # Test 5: Save state
    print("\n" + "=" * 70)
    print("\n5️⃣ Test: Save/Load state")
    
    engine.save_state('test_engine')
    
    # Create new engine and load
    engine2 = MatchingEngine()
    engine2.load_state('test_engine')
    
    stats2 = engine2.get_stats()
    print(f"\n   ✅ State loaded successfully!")
    print(f"      Resumes indexed: {stats2['resumes_indexed']}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
