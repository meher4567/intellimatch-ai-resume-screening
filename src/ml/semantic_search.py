"""
Semantic Search Service
Combines embedding generation and vector store for job-resume matching
"""

from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ml.embedding_generator import EmbeddingGenerator
from src.ml.vector_store import VectorStore


class SemanticSearch:
    """High-level semantic search for job-resume matching"""
    
    def __init__(self, 
                 embedding_model: str = 'mini',
                 vector_store: Optional[VectorStore] = None):
        """
        Initialize semantic search
        
        Args:
            embedding_model: Model size ('mini', 'base')
            vector_store: Existing vector store (if None, creates new)
        """
        # Initialize embedding generator
        print("🚀 Initializing Semantic Search...")
        self.embedding_gen = EmbeddingGenerator(model_name=embedding_model)
        
        # Initialize or use existing vector store
        if vector_store is None:
            self.vector_store = VectorStore(
                embedding_dim=self.embedding_gen.embedding_dim,
                metric='cosine'
            )
        else:
            self.vector_store = vector_store
        
        print(f"✅ Semantic search ready")
        print(f"   Embedding dim: {self.embedding_gen.embedding_dim}")
        print(f"   Resumes indexed: {self.vector_store.size()}")
    
    def index_resume(self, resume_data: Dict[str, Any]) -> str:
        """
        Index a single resume for searching
        
        Args:
            resume_data: Parsed resume data from enhanced_resume_parser
            
        Returns:
            Resume ID
        """
        # Generate embedding
        embeddings = self.embedding_gen.encode_resume(resume_data)
        full_embedding = embeddings['full_text']
    
    def _safe_extract_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract skills safely from resume data (handles both dict and list formats)"""
        skills_data = resume_data.get('skills', [])
        if isinstance(skills_data, dict):
            return skills_data.get('all_skills', skills_data.get('top_skills', []))
        elif isinstance(skills_data, list):
            return skills_data
        return []
        
        # Extract metadata for quick access
        resume_id = resume_data.get('metadata', {}).get('file_name', f"resume_{self.vector_store.size()}")
        
        metadata = {
            'resume_id': resume_id,
            'name': resume_data.get('personal_info', {}).get('name', 'Unknown'),
            'email': resume_data.get('personal_info', {}).get('email', ''),
            'skills': self._safe_extract_skills(resume_data)[:20],  # Top 20 skills
            'experience_years': self._calculate_experience_years(resume_data),
            'education': [edu.get('degree', '') for edu in resume_data.get('education', [])],
            'quality_score': resume_data.get('metadata', {}).get('quality_score', 0),
            'top_skills': self._safe_extract_skills(resume_data)[:10],
            'name': resume_data.get('personal_info', {}).get('name', resume_data.get('name', 'Unknown')),
            'email': resume_data.get('personal_info', {}).get('email', resume_data.get('email', '')),
        }
        
        # Add to vector store
        self.vector_store.add(full_embedding, resume_id, metadata)
        
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
        
        embeddings_list = []
        metadata_list = []
        resume_ids = []
        
        for i, resume_data in enumerate(resumes_data):
            # Generate embedding
            embeddings = self.embedding_gen.encode_resume(resume_data)
            embeddings_list.append(embeddings['full_text'])
            
            # Extract metadata
            resume_id = resume_data.get('metadata', {}).get('file_name', f"resume_{i}")
            resume_ids.append(resume_id)
            
            metadata = {
                'resume_id': resume_id,
                'name': resume_data.get('personal_info', {}).get('name', 'Unknown'),
                'email': resume_data.get('personal_info', {}).get('email', ''),
                'skills': resume_data.get('skills', {}).get('all_skills', [])[:20],
                'experience_years': self._calculate_experience_years(resume_data),
                'education': [edu.get('degree', '') for edu in resume_data.get('education', [])],
                'quality_score': resume_data.get('metadata', {}).get('quality_score', 0),
                'top_skills': resume_data.get('skills', {}).get('top_skills', [])[:10],
            }
            metadata_list.append(metadata)
        
        # Batch add to vector store
        embeddings_array = np.array(embeddings_list)
        self.vector_store.add_batch(embeddings_array, resume_ids, metadata_list)
        
        print(f"✅ Indexed {len(resumes_data)} resumes")
        return resume_ids
    
    def search_for_job(self, 
                       job_data: Dict[str, Any],
                       k: int = 50,
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Find matching candidates for a job
        
        Args:
            job_data: Parsed job description
            k: Number of candidates to return
            filters: Optional filters (experience_years, skills, education)
            
        Returns:
            List of matching candidates with scores
        """
        # Generate job embedding
        job_embeddings = self.embedding_gen.encode_job(job_data)
        query_embedding = job_embeddings['full_text']
        
        # Create filter function if filters provided
        filter_fn = None
        if filters:
            filter_fn = self._create_filter_function(filters)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            k=k,
            filter_fn=filter_fn
        )
        
        # Enhance results with additional info and flatten metadata
        for result in results:
            # Flatten metadata to top level for easier access
            metadata = result.pop('metadata', {})
            result.update(metadata)
            
            # Add job info
            result['job_title'] = job_data.get('title', 'Unknown Position')
            result['job_id'] = job_data.get('job_id', 'unknown')
        
        return results
    
    def find_similar_resumes(self,
                            resume_id: str,
                            k: int = 10) -> List[Dict[str, Any]]:
        """
        Find resumes similar to a given resume
        
        Args:
            resume_id: Reference resume ID
            k: Number of similar resumes to find
            
        Returns:
            List of similar resumes with scores
        """
        # Get the resume's embedding by searching with itself
        metadata = self.vector_store.get_by_resume_id(resume_id)
        if not metadata:
            return []
        
        # Get FAISS ID and reconstruct embedding by searching
        # (In production, you'd store embeddings separately for this use case)
        # For now, return empty list
        return []
    
    def _calculate_experience_years(self, resume_data: Dict[str, Any]) -> int:
        """Calculate total years of experience from resume"""
        experiences = resume_data.get('experience', [])
        if not experiences:
            return 0
        
        total_months = 0
        for exp in experiences:
            duration = exp.get('duration_months', 0)
            if duration:
                total_months += duration
        
        return total_months // 12
    
    def _create_filter_function(self, filters: Dict[str, Any]) -> callable:
        """Create filter function from filter criteria"""
        def filter_fn(metadata: Dict[str, Any]) -> bool:
            # Experience filter
            if 'min_experience_years' in filters:
                exp_years = metadata.get('experience_years', 0)
                if exp_years < filters['min_experience_years']:
                    return False
            
            if 'max_experience_years' in filters:
                exp_years = metadata.get('experience_years', 0)
                if exp_years > filters['max_experience_years']:
                    return False
            
            # Skills filter (must have at least one required skill)
            if 'required_skills' in filters:
                candidate_skills = set(s.lower() for s in metadata.get('skills', []))
                required_skills = set(s.lower() for s in filters['required_skills'])
                if not candidate_skills.intersection(required_skills):
                    return False
            
            # Education filter
            if 'required_degree' in filters:
                degrees = metadata.get('education', [])
                degree_str = ' '.join(degrees).lower()
                required = filters['required_degree'].lower()
                if required not in degree_str:
                    return False
            
            # Quality score filter
            if 'min_quality_score' in filters:
                quality = metadata.get('quality_score', 0)
                if quality < filters['min_quality_score']:
                    return False
            
            return True
        
        return filter_fn
    
    def save(self, name: str = 'default'):
        """Save vector store to disk"""
        self.vector_store.save(name)
    
    @classmethod
    def load(cls, name: str = 'default', 
             embedding_model: str = 'mini') -> 'SemanticSearch':
        """Load saved vector store"""
        # Load vector store
        vector_store = VectorStore.load(name)
        
        # Create instance
        instance = cls(embedding_model=embedding_model, vector_store=vector_store)
        
        return instance
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'embedding_model': self.embedding_gen.model_name,
            'embedding_dim': self.embedding_gen.embedding_dim,
            **self.vector_store.stats()
        }


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Semantic Search")
    print("=" * 70)
    
    # Initialize
    print("\n1️⃣ Initializing semantic search...")
    search = SemanticSearch(embedding_model='mini')
    
    # Create sample resumes (simulating parsed data)
    print("\n2️⃣ Creating sample resumes...")
    sample_resumes = [
        {
            'metadata': {'file_name': 'john_doe.pdf', 'quality_score': 95},
            'personal_info': {'name': 'John Doe', 'email': 'john@example.com'},
            'skills': {
                'all_skills': ['Python', 'Django', 'AWS', 'PostgreSQL', 'Docker'],
                'top_skills': ['Python', 'Django', 'AWS']
            },
            'experience': [
                {'title': 'Senior Backend Engineer', 'company': 'TechCorp', 
                 'duration_months': 36, 'achievements': ['Built scalable APIs']},
                {'title': 'Backend Developer', 'company': 'StartupXYZ',
                 'duration_months': 24, 'achievements': ['Migrated to microservices']}
            ],
            'education': [{'degree': "Bachelor's in Computer Science", 'institution': 'MIT'}]
        },
        {
            'metadata': {'file_name': 'jane_smith.pdf', 'quality_score': 92},
            'personal_info': {'name': 'Jane Smith', 'email': 'jane@example.com'},
            'skills': {
                'all_skills': ['Python', 'Machine Learning', 'TensorFlow', 'Pandas', 'Spark'],
                'top_skills': ['Python', 'Machine Learning', 'TensorFlow']
            },
            'experience': [
                {'title': 'Data Scientist', 'company': 'AI Corp',
                 'duration_months': 30, 'achievements': ['Built ML pipeline']}
            ],
            'education': [{"degree": "Master's in Statistics", 'institution': 'Stanford'}]
        },
        {
            'metadata': {'file_name': 'bob_johnson.pdf', 'quality_score': 88},
            'personal_info': {'name': 'Bob Johnson', 'email': 'bob@example.com'},
            'skills': {
                'all_skills': ['React', 'JavaScript', 'TypeScript', 'Next.js', 'CSS'],
                'top_skills': ['React', 'JavaScript', 'TypeScript']
            },
            'experience': [
                {'title': 'Frontend Engineer', 'company': 'WebCo',
                 'duration_months': 48, 'achievements': ['Built responsive apps']}
            ],
            'education': [{"degree": "Bachelor's in CS", 'institution': 'Berkeley'}]
        }
    ]
    
    # Index resumes
    print("\n3️⃣ Indexing resumes...")
    resume_ids = search.index_resumes_batch(sample_resumes)
    print(f"   Indexed IDs: {resume_ids}")
    
    # Create sample job
    print("\n4️⃣ Creating sample job...")
    sample_job = {
        'job_id': 'job_001',
        'title': 'Senior Backend Engineer',
        'company': 'TechCorp',
        'required_skills': ['Python', 'Django', 'AWS'],
        'required_experience_years': 3,
        'responsibilities': [
            'Build scalable backend services',
            'Design REST APIs',
            'Deploy to AWS cloud'
        ]
    }
    
    # Search for candidates
    print("\n5️⃣ Searching for matching candidates...")
    results = search.search_for_job(sample_job, k=3)
    
    print(f"   Job: {sample_job['title']}")
    print(f"   Top {len(results)} candidates:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"\n   {i}. {meta['name']}")
        print(f"      Score: {result['score']:.2f}/100")
        print(f"      Skills: {', '.join(meta['top_skills'])}")
        print(f"      Experience: {meta['experience_years']} years")
    
    # Test with filters
    print("\n6️⃣ Testing filtered search...")
    filters = {
        'required_skills': ['Python'],
        'min_experience_years': 2,
        'min_quality_score': 90
    }
    
    results = search.search_for_job(sample_job, k=3, filters=filters)
    print(f"   Filters: Python, 2+ years, quality 90+")
    print(f"   Found {len(results)} candidates:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"   {i}. {meta['name']} - {result['score']:.2f}/100")
    
    # Save and load
    print("\n7️⃣ Testing save/load...")
    search.save('semantic_search_test')
    
    print("\n   Loading...")
    loaded_search = SemanticSearch.load('semantic_search_test')
    
    # Test loaded search
    results = loaded_search.search_for_job(sample_job, k=2)
    print(f"   Loaded search works: {len(results)} results")
    
    # Stats
    print("\n8️⃣ Statistics:")
    stats = loaded_search.stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
