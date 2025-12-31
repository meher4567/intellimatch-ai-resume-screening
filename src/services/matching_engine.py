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
import time
from uuid import uuid4

from src.ml.embedding_generator import EmbeddingGenerator
from src.ml.vector_store import VectorStore
from src.ml.semantic_search import SemanticSearch
from src.ml.match_scorer import MatchScorer
from src.ml.candidate_ranker import CandidateRanker
from src.ml.match_explainer import MatchExplainer
from src.ml.enhanced_match_explainer import EnhancedMatchExplainer
from src.ml.resume_quality_scorer import ResumeQualityScorer
from src.services.job_description_parser import JobDescriptionParser
from src.ml.experience_classifier import ExperienceLevelClassifier
from src.utils.logger import get_logger, get_metrics, timed
from src.core.caching import MatchResultCache


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
                 storage_path: str = 'data/embeddings',
                 auto_load_index: bool = True,
                 enable_cache: bool = True):
        """
        Initialize matching engine
        
        Args:
            model_name: Sentence transformer model name
            embedding_dim: Embedding dimension
            storage_path: Path to store embeddings and indexes
            auto_load_index: Automatically load pre-built index if available
            enable_cache: Enable match result caching (default: True)
        """
        # Initialize logger
        self.logger = get_logger("matching_engine")
        self.metrics = get_metrics()
        self.logger.set_context(component="matching_engine")
        
        init_start = time.time()
        self.logger.info("initialization_started", model=model_name, cache_enabled=enable_cache)
        
        # Initialize match result cache
        self.enable_cache = enable_cache
        if enable_cache:
            self.match_cache = MatchResultCache(max_size=1000, ttl_seconds=3600)
            self.logger.info("Match result cache enabled", extra={
                "max_size": 1000,
                "ttl_seconds": 3600
            })
        else:
            self.match_cache = None
            self.logger.info("Match result cache disabled")
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator(model_name=model_name, enable_cache=enable_cache)
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
        # Initialize EnhancedMatchExplainer for comprehensive explanations
        self.enhanced_explainer = EnhancedMatchExplainer()
        self.logger.info("Enhanced match explainer initialized")
        self.quality_scorer = ResumeQualityScorer()
        # Experience level classifier (Entry/Mid/Senior/Expert)
        try:
            self.experience_classifier = ExperienceLevelClassifier()
            self.logger.info("experience_classifier_loaded")
        except Exception as e:
            self.experience_classifier = None
            self.logger.warning("experience_classifier_failed", error=str(e))
        
        # Storage
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Auto-load pre-built index if available
        if auto_load_index:
            self._load_prebuilt_index()
        
        # Stats
        self.stats = {
            'resumes_indexed': self.vector_store.size(),
            'jobs_processed': 0,
            'matches_generated': 0,
            'last_updated': None
        }
        
        init_time = (time.time() - init_start) * 1000
        self.logger.info("initialization_completed",
                        duration_ms=init_time,
                        resumes_indexed=self.stats['resumes_indexed'])
        self.metrics.record('initialization', init_time)
        
        print("✅ Matching Engine ready!")
        print(f"   Model: {model_name}")
        print(f"   Embedding dim: {self.embedding_generator.embedding_dim}")
        print(f"   Storage: {storage_path}")
        print(f"   Indexed Resumes: {self.stats['resumes_indexed']:,}")
    
    def _load_prebuilt_index(self):
        """Load pre-built FAISS index if available"""
        # Try standard naming convention first
        index_path = self.storage_path / "resume_index_index.faiss"
        metadata_path = self.storage_path / "resume_index_metadata.pkl"
        
        if index_path.exists() and metadata_path.exists():
            try:
                load_start = time.time()
                self.logger.info("loading_prebuilt_index", path=str(self.storage_path))
                
                # Load into semantic search's vector store
                self.semantic_search.vector_store = VectorStore.load(
                    name='resume_index',
                    storage_dir=str(self.storage_path)
                )
                # Also update the direct vector_store reference
                self.vector_store = self.semantic_search.vector_store
                
                load_time = (time.time() - load_start) * 1000
                self.logger.info("prebuilt_index_loaded",
                                duration_ms=load_time,
                                index_size=self.vector_store.size())
                self.metrics.record('index_load', load_time)
                
                print(f"✅ Loaded pre-built index ({self.vector_store.size():,} resumes) in {load_time:.0f}ms")
            except Exception as e:
                self.logger.error("index_load_failed", error=str(e))
                print(f"⚠️  Failed to load pre-built index: {e}")
        else:
            self.logger.info("no_prebuilt_index_found")
    
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
    
    @timed(logger=get_logger(__name__), event="find_matches")
    def find_matches(self,
                    job_data: Dict[str, Any],
                    top_k: int = 50,
                    min_score: Optional[float] = None,
                    filters: Optional[Dict[str, Any]] = None,
                    scoring_weights: Optional[Dict[str, float]] = None,
                    use_cache: bool = None) -> List[Dict[str, Any]]:
        """
        Find matching candidates for a job with caching support
        
        Args:
            job_data: Parsed job description data
            top_k: Number of candidates to retrieve from semantic search
            min_score: Minimum match score threshold
            filters: Optional filters (experience, skills, education, quality)
            scoring_weights: Custom scoring weights (semantic, skills, experience, education)
            use_cache: Override cache enable setting (default: use self.enable_cache)
            
        Returns:
            List of ranked candidates with match details
        """
        # Determine if cache should be used
        if use_cache is None:
            use_cache = self.enable_cache
        
        # Convert JobDescription object to dict if needed
        if hasattr(job_data, 'to_dict'):
            job_data = job_data.to_dict()
        
        # Try to get from cache
        if use_cache and self.match_cache is not None:
            cached_result = self.match_cache.get(job_data, top_k=top_k, filters=filters)
            if cached_result is not None:
                self.logger.info("Cache hit for job", extra={
                    "job_title": job_data.get('title', 'Unknown'),
                    "top_k": top_k,
                    "cached_matches": len(cached_result)
                })
                self.metrics.record("match_cache_hit", 1.0)
                return cached_result
            else:
                self.logger.debug("Cache miss for job", extra={
                    "job_title": job_data.get('title', 'Unknown')
                })
                self.metrics.record("match_cache_miss", 1.0)
        
        self.logger.info("Finding matches for job", extra={
            "job_title": job_data.get('title', 'Unknown Job'),
            "top_k": top_k
        })
        
        # Step 1: Semantic search to get initial candidates
        self.logger.info("Step 1: Semantic search", extra={"top_k": top_k})
        candidates = self.semantic_search.search_for_job(
            job_data=job_data,
            k=top_k,
            filters=filters
        )
        
        if not candidates:
            self.logger.warning("No candidates found matching filters")
            return []
        
        self.logger.info(f"Found candidates from semantic search", extra={
            "candidates_count": len(candidates)
        })
        
        # Step 2: Multi-factor scoring
        self.logger.info("Step 2: Multi-factor scoring")
        
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
                    experience_pred = self.experience_classifier.predict(candidate.get('experience', []))
            except Exception:
                experience_pred = {'level': None, 'confidence': 0.0}
            
            # Calculate comprehensive match
            match_result = scorer.calculate_match(
                candidate_data=candidate,
                job_data=job_data,
                semantic_score=semantic_score
            )
            
            # Combine candidate data with match result
            # Extract skills safely (handles both dict and list formats)
            skills_data = candidate.get('skills', [])
            if isinstance(skills_data, dict):
                skills_list = skills_data.get('all_skills', skills_data.get('top_skills', []))
            elif isinstance(skills_data, list):
                skills_list = skills_data
            else:
                skills_list = []
            
            scored_candidate = {
                'resume_id': candidate['resume_id'],
                'name': candidate.get('name', 'Unknown'),
                'email': candidate.get('email', ''),
                'skills': skills_list,
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
        
        self.logger.info(f"Scored candidates", extra={
            "candidates_scored": len(scored_candidates)
        })
        
        # Step 3: Ranking
        self.logger.info("Step 3: Ranking candidates")
        ranked_candidates = self.ranker.rank_candidates(
            scored_candidates,
            min_score=min_score
        )
        
        self.logger.info(f"Ranked candidates", extra={
            "candidates_ranked": len(ranked_candidates)
        })
        
        # Step 4: Generate explanations for top candidates using EnhancedMatchExplainer
        self.logger.info("Step 4: Generating enhanced explanations with recommendations")
        for i, candidate in enumerate(ranked_candidates[:10]):  # Top 10 only
            try:
                # Prepare match data for enhanced explainer
                # The enhanced explainer expects a dict with: final_score, scores, details
                match_details = candidate.get('match_details', {})
                
                # Check if we have the required fields
                if 'final_score' in match_details and 'scores' in match_details and 'details' in match_details:
                    # Generate comprehensive explanation with enhanced explainer
                    enhanced_explanation = self.enhanced_explainer.explain_match(match_details)
                    candidate['explanation'] = enhanced_explanation
                    
                    # Log the quality of explanations
                    self.logger.debug(f"Generated enhanced explanation for candidate {i+1}", extra={
                        "recommendation": enhanced_explanation.get('hiring_recommendation'),
                        "confidence": enhanced_explanation.get('confidence', {}).get('level')
                    })
                else:
                    # Fallback to basic explainer if structure doesn't match
                    self.logger.debug(f"Using basic explainer for candidate {i+1} - missing required fields")
                    explanation = self.explainer.explain_match(match_details)
                    candidate['explanation'] = explanation
                    
            except Exception as e:
                # Fallback to basic explainer if enhanced fails
                self.logger.warning(f"Enhanced explanation failed for candidate {i+1}: {str(e)}, using basic explainer")
                try:
                    explanation = self.explainer.explain_match(candidate['match_details'])
                    candidate['explanation'] = explanation
                except Exception as e2:
                    self.logger.error(f"Both explainers failed for candidate {i+1}: {str(e2)}")
                    candidate['explanation'] = {'summary': 'Explanation unavailable', 'recommendations': []}
        
        # Update stats
        self.stats['matches_generated'] += len(ranked_candidates)
        
        # Store in cache
        if use_cache and self.match_cache is not None:
            self.match_cache.put(job_data, ranked_candidates, top_k=top_k, filters=filters)
            self.logger.info("Cached match results", extra={
                "job_title": job_data.get('title', 'Unknown'),
                "matches_cached": len(ranked_candidates)
            })
        
        self.logger.info("Matching complete", extra={
            "total_matches": len(ranked_candidates)
        })
        
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
    
    def get_embedding_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics"""
        return self.embedding_generator.get_cache_stats()
    
    def get_match_cache_stats(self) -> Dict[str, Any]:
        """Get match result cache statistics"""
        if self.match_cache is not None:
            return self.match_cache.get_stats()
        return {"cache_enabled": False}
    
    def clear_caches(self):
        """Clear all caches (embedding + match results)"""
        self.embedding_generator.clear_cache()
        if self.match_cache is not None:
            self.match_cache.clear()
            self.logger.info("Match cache cleared")
        self.logger.info("All caches cleared")
    
    def save_caches(self):
        """Save all caches to disk"""
        self.embedding_generator.save_cache()
        if self.match_cache is not None:
            cache_path = str(Path("data/cache/match_cache.pkl"))
            self.match_cache.save_cache_to_disk(cache_path)
            self.logger.info(f"Match cache saved to {cache_path}")
        self.logger.info("All caches saved")
    
    def load_caches(self):
        """Load all caches from disk"""
        self.embedding_generator.load_cache()
        if self.match_cache is not None:
            cache_path = str(Path("data/cache/match_cache.pkl"))
            self.match_cache.load_cache_from_disk(cache_path)
            self.logger.info(f"Match cache loaded from {cache_path}")
        self.logger.info("All caches loaded")
    
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
    
    # Test 4: Get cache stats
    print("\n" + "=" * 70)
    print("\n4️⃣ Test: Cache statistics")
    
    embedding_stats = engine.get_embedding_cache_stats()
    match_stats = engine.get_match_cache_stats()
    print(f"\n   📊 Embedding Cache Stats:")
    print(f"      Hits: {embedding_stats.get('hits', 0)}")
    print(f"      Misses: {embedding_stats.get('misses', 0)}")
    print(f"      Hit Rate: {embedding_stats.get('hit_rate', 0):.1%}")
    print(f"      Size: {embedding_stats.get('size', 0)}")
    
    print(f"\n   📊 Match Cache Stats:")
    print(f"      Hits: {match_stats.get('hits', 0)}")
    print(f"      Misses: {match_stats.get('misses', 0)}")
    print(f"      Hit Rate: {match_stats.get('hit_rate', 0):.1%}")
    print(f"      Size: {match_stats.get('size', 0)}")
    
    # Test 5: Get stats
    print("\n" + "=" * 70)
    print("\n5️⃣ Test: Engine statistics")
    
    stats = engine.get_stats()
    print(f"\n   📊 Engine Stats:")
    print(f"      Resumes indexed: {stats['resumes_indexed']}")
    print(f"      Jobs processed: {stats['jobs_processed']}")
    print(f"      Matches generated: {stats['matches_generated']}")
    print(f"      Last updated: {stats['last_updated']}")
    
    # Test 6: Save state
    print("\n" + "=" * 70)
    print("\n6️⃣ Test: Save/Load state")
    
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
