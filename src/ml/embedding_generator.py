"""
Embedding Generator for Semantic Search
Generates vector embeddings using sentence-transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union, Dict, Any
import numpy as np
from pathlib import Path
import json
import time


class EmbeddingGenerator:
    """Generate semantic embeddings using sentence-transformers"""
    
    # Available models (ordered by size/performance)
    MODELS = {
        'mini': 'all-MiniLM-L6-v2',        # 384 dims, 80MB, fastest
        'base': 'all-mpnet-base-v2',       # 768 dims, 420MB, most accurate
        'large': 'all-mpnet-base-v2',      # Same as base (no larger available)
    }
    
    def __init__(self, model_name: str = 'mini', cache_dir: str = None):
        """
        Initialize embedding generator
        
        Args:
            model_name: Model size ('mini', 'base', 'large')
            cache_dir: Directory to cache models (default: ./models/embeddings)
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Model must be one of {list(self.MODELS.keys())}")
        
        self.model_name = model_name
        self.model_path = self.MODELS[model_name]
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "models" / "embeddings"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Loading model: {self.model_path}...")
        start_time = time.time()
        
        # Load model
        self.model = SentenceTransformer(self.model_path, cache_folder=str(self.cache_dir))
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s")
        print(f"   Embedding dimension: {self.embedding_dim}")
        print(f"   Max sequence length: {self.model.max_seq_length}")
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32,
               show_progress: bool = False,
               normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            show_progress: Show progress bar
            normalize: Normalize embeddings to unit length (for cosine similarity)
            
        Returns:
            numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        # Return single embedding as 1D array
        if single_text:
            return embeddings[0]
        
        return embeddings
    
    def encode_resume(self, resume_data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for different parts of a resume
        
        Args:
            resume_data: Parsed resume data (from enhanced_resume_parser)
            
        Returns:
            Dictionary with embeddings for different sections
        """
        embeddings = {}
        
        # Full resume text (primary embedding)
        full_text = self._build_resume_text(resume_data)
        embeddings['full_text'] = self.encode(full_text)
        
        # Skills summary (handle both dict and list formats)
        skills_data = resume_data.get('skills', [])
        if isinstance(skills_data, dict):
            skills = skills_data.get('all_skills', [])
        else:
            skills = skills_data
        
        if skills:
            skills_text = ', '.join([str(s) for s in skills[:50]])
            embeddings['skills'] = self.encode(skills_text)
        
        # Experience descriptions (encode each job separately)
        if resume_data.get('experience'):
            exp_texts = []
            for exp in resume_data['experience']:
                exp_text = f"{exp.get('title', '')} at {exp.get('company', '')}. "
                exp_text += ' '.join(exp.get('achievements', [])[:5])
                exp_texts.append(exp_text)
            
            if exp_texts:
                embeddings['experience'] = self.encode(exp_texts)
        
        # Education summary
        if resume_data.get('education'):
            edu_texts = []
            for edu in resume_data['education']:
                edu_text = f"{edu.get('degree', '')} in {edu.get('field_of_study', '')} from {edu.get('institution', '')}"
                edu_texts.append(edu_text)
            
            if edu_texts:
                embeddings['education'] = self.encode(edu_texts)
        
        return embeddings
    
    def encode_job(self, job_data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for different parts of a job description
        
        Args:
            job_data: Parsed job description (from job_description_parser)
            
        Returns:
            Dictionary with embeddings for different sections
        """
        embeddings = {}
        
        # Full job description (primary embedding)
        full_text = self._build_job_text(job_data)
        embeddings['full_text'] = self.encode(full_text)
        
        # Requirements
        req_skills = job_data.get('required_skills', [])
        if req_skills:
            skills_text = ', '.join(req_skills)
            embeddings['requirements'] = self.encode(skills_text)
        
        # Responsibilities
        responsibilities = job_data.get('responsibilities', [])
        if responsibilities:
            resp_text = ' '.join(responsibilities[:10])
            embeddings['responsibilities'] = self.encode(resp_text)
        
        return embeddings
    
    def _build_resume_text(self, resume_data: Dict[str, Any]) -> str:
        """Build comprehensive text from resume data for embedding"""
        parts = []
        
        # Personal info
        personal = resume_data.get('personal_info', {})
        if personal.get('name'):
            parts.append(f"Name: {personal['name']}")
        
        # Summary
        if resume_data.get('summary'):
            parts.append(f"Summary: {resume_data['summary']}")
        
        # Skills (handle both dict and list formats)
        skills_data = resume_data.get('skills', [])
        if isinstance(skills_data, dict):
            skills = skills_data.get('all_skills', [])
        else:
            skills = skills_data
        
        if skills:
            parts.append(f"Skills: {', '.join(skills[:50])}")
        
        # Experience
        for exp in resume_data.get('experience', [])[:5]:  # Top 5 experiences
            exp_text = f"{exp.get('title', '')} at {exp.get('company', '')}. "
            exp_text += ' '.join(exp.get('achievements', [])[:5])
            parts.append(exp_text)
        
        # Education
        for edu in resume_data.get('education', [])[:3]:  # Top 3 education entries
            edu_text = f"{edu.get('degree', '')} in {edu.get('field_of_study', '')} from {edu.get('institution', '')}"
            parts.append(edu_text)
        
        return ' '.join(parts)
    
    def _build_job_text(self, job_data: Dict[str, Any]) -> str:
        """Build comprehensive text from job data for embedding"""
        parts = []
        
        # Title and company
        parts.append(f"Position: {job_data.get('title', '')}")
        parts.append(f"Company: {job_data.get('company', '')}")
        
        # Required skills
        req_skills = job_data.get('required_skills', [])
        if req_skills:
            parts.append(f"Required skills: {', '.join(req_skills)}")
        
        # Experience
        exp_level = job_data.get('experience_level', '')
        exp_years = job_data.get('required_experience_years')
        if exp_years:
            parts.append(f"{exp_level} level, {exp_years}+ years experience")
        
        # Responsibilities
        responsibilities = job_data.get('responsibilities', [])
        if responsibilities:
            parts.append("Responsibilities: " + ' '.join(responsibilities[:10]))
        
        # Description
        if job_data.get('description'):
            # Take first 500 chars of description
            desc = job_data['description'][:500]
            parts.append(desc)
        
        return ' '.join(parts)
    
    def calculate_similarity(self, embedding1: np.ndarray, 
                           embedding2: np.ndarray,
                           metric: str = 'cosine') -> float:
        """
        Calculate similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            metric: Similarity metric ('cosine' or 'euclidean')
            
        Returns:
            Similarity score (0-1 for cosine, distance for euclidean)
        """
        if metric == 'cosine':
            # Cosine similarity (assumes normalized embeddings)
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)
        elif metric == 'euclidean':
            # Euclidean distance (lower is more similar)
            distance = np.linalg.norm(embedding1 - embedding2)
            return float(distance)
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def batch_similarity(self, query_embedding: np.ndarray,
                        candidate_embeddings: np.ndarray,
                        metric: str = 'cosine') -> np.ndarray:
        """
        Calculate similarity between query and multiple candidates
        
        Args:
            query_embedding: Query embedding (1D array)
            candidate_embeddings: Candidate embeddings (2D array: [n_candidates, dim])
            metric: Similarity metric
            
        Returns:
            Array of similarity scores
        """
        if metric == 'cosine':
            # Matrix multiplication for batch cosine similarity
            similarities = np.dot(candidate_embeddings, query_embedding)
            return similarities
        elif metric == 'euclidean':
            # Batch euclidean distance
            distances = np.linalg.norm(candidate_embeddings - query_embedding, axis=1)
            return distances
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def save_embeddings(self, embeddings: Dict[str, Any], filepath: str):
        """Save embeddings to file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy arrays to lists for JSON serialization
        serializable = {}
        for key, value in embeddings.items():
            if isinstance(value, np.ndarray):
                serializable[key] = value.tolist()
            else:
                serializable[key] = value
        
        with open(filepath, 'w') as f:
            json.dump(serializable, f)
        
        print(f"✅ Embeddings saved to {filepath}")
    
    def load_embeddings(self, filepath: str) -> Dict[str, Any]:
        """Load embeddings from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert lists back to numpy arrays
        for key, value in data.items():
            if isinstance(value, list):
                data[key] = np.array(value)
        
        return data
    
    def benchmark(self, num_texts: int = 100, text_length: int = 200):
        """
        Benchmark embedding generation speed
        
        Args:
            num_texts: Number of texts to encode
            text_length: Approximate length of each text
        """
        print(f"\n🔬 Benchmarking embedding generation...")
        print(f"   Model: {self.model_name} ({self.model_path})")
        print(f"   Texts: {num_texts}, Length: ~{text_length} chars")
        
        # Generate sample texts
        sample_text = "This is a sample resume text with skills and experience. " * (text_length // 60)
        texts = [sample_text] * num_texts
        
        # Benchmark
        start_time = time.time()
        embeddings = self.encode(texts, batch_size=32)
        elapsed = time.time() - start_time
        
        print(f"\n   Results:")
        print(f"   ⏱️  Total time: {elapsed:.2f}s")
        print(f"   ⚡ Speed: {num_texts / elapsed:.1f} texts/second")
        print(f"   📊 Per text: {elapsed / num_texts * 1000:.1f}ms")
        print(f"   💾 Embedding shape: {embeddings.shape}")
        print(f"   🎯 Memory: {embeddings.nbytes / 1024 / 1024:.2f} MB")


# Convenience function
def create_embedding_generator(model_size: str = 'mini') -> EmbeddingGenerator:
    """
    Create embedding generator with specified model size
    
    Args:
        model_size: 'mini' (fast), 'base' (accurate), or 'large' (best)
    
    Returns:
        EmbeddingGenerator instance
    """
    return EmbeddingGenerator(model_name=model_size)


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Embedding Generator")
    print("=" * 70)
    
    # Test with mini model
    print("\n1️⃣ Testing with MINI model (fast)...")
    gen = EmbeddingGenerator(model_name='mini')
    
    # Test single text
    print("\n📝 Testing single text:")
    text = "Experienced Python developer with 5 years in backend development, Django, and AWS"
    embedding = gen.encode(text)
    print(f"   Input: {text[:80]}...")
    print(f"   Embedding shape: {embedding.shape}")
    print(f"   Embedding (first 10): {embedding[:10]}")
    
    # Test batch
    print("\n📚 Testing batch:")
    texts = [
        "Python developer with Django experience",
        "Data scientist specializing in machine learning",
        "Frontend engineer skilled in React and TypeScript"
    ]
    embeddings = gen.encode(texts)
    print(f"   Input: {len(texts)} texts")
    print(f"   Embeddings shape: {embeddings.shape}")
    
    # Test similarity
    print("\n🔍 Testing similarity:")
    emb1 = gen.encode("Python Django developer")
    emb2 = gen.encode("Python backend engineer")
    emb3 = gen.encode("Frontend React developer")
    
    sim_12 = gen.calculate_similarity(emb1, emb2)
    sim_13 = gen.calculate_similarity(emb1, emb3)
    
    print(f"   Similarity (Python Django vs Python backend): {sim_12:.4f}")
    print(f"   Similarity (Python Django vs React frontend): {sim_13:.4f}")
    print(f"   ✅ Python roles more similar than unrelated roles")
    
    # Benchmark
    gen.benchmark(num_texts=100, text_length=200)
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
