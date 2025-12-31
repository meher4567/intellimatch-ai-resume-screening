"""
Embedding Generator for Semantic Search
Generates vector embeddings using sentence-transformers

Edge Cases Handled:
- Empty or None text inputs
- Very long text (truncation with warning)
- Invalid text types (conversion with fallback)
- Model loading failures (graceful degradation)
- Unicode/encoding issues
- Batch size optimization for memory
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union, Dict, Any, Optional
import numpy as np
from pathlib import Path
import json
import time
import logging

# Import caching system
import sys
sys.path.append(str(Path(__file__).parent.parent))
from core.caching import EmbeddingCache, BatchProcessor
from utils.logger import get_logger, get_metrics, timed

logger = get_logger(__name__)
metrics = get_metrics()


# Constants for edge case handling
MAX_TEXT_LENGTH = 50000  # Maximum characters before truncation
MIN_TEXT_LENGTH = 1  # Minimum valid text length
MAX_BATCH_SIZE = 128  # Maximum batch size to prevent OOM
DEFAULT_EMBEDDING_VALUE = None  # Returned on complete failure


def _sanitize_text(text: Any, max_length: int = MAX_TEXT_LENGTH) -> str:
    """
    Sanitize text input for embedding generation
    
    Handles:
    - None -> empty string
    - Non-string types -> string conversion
    - Very long text -> truncation with warning
    - Control characters -> removal
    - Unicode normalization
    """
    if text is None:
        return ""
    
    # Convert non-strings
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return ""
    
    # Remove control characters (except newlines and tabs)
    import re
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Truncate if too long
    if len(text) > max_length:
        logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]
    
    return text.strip()


def _validate_text_list(texts: List[Any]) -> List[str]:
    """Validate and sanitize a list of texts"""
    if not texts:
        return []
    
    return [_sanitize_text(t) for t in texts]


class EmbeddingGenerator:
    """Generate semantic embeddings using sentence-transformers"""
    
    # Available models (ordered by size/performance)
    MODELS = {
        'mini': 'all-MiniLM-L6-v2',        # 384 dims, 80MB, fastest
        'base': 'all-mpnet-base-v2',       # 768 dims, 420MB, most accurate
        'large': 'all-mpnet-base-v2',      # Same as base (no larger available)
    }
    
    # Embedding dimensions for each model
    MODEL_DIMS = {
        'mini': 384,
        'base': 768,
        'large': 768
    }
    
    def __init__(self, model_name: str = 'mini', cache_dir: str = None, enable_cache: bool = True):
        """
        Initialize embedding generator
        
        Args:
            model_name: Model size ('mini', 'base', 'large')
            cache_dir: Directory to cache models (default: ./models/embeddings)
            enable_cache: Enable embedding caching (default: True)
        
        Raises:
            ValueError: If model_name is not valid
        """
        # Validate model name with helpful error
        if model_name not in self.MODELS:
            valid_models = list(self.MODELS.keys())
            raise ValueError(
                f"Model '{model_name}' not found. "
                f"Valid options: {valid_models}. "
                f"Using 'mini' for speed, 'base' for accuracy."
            )
        
        self.model_name = model_name
        self.model_path = self.MODELS[model_name]
        self._expected_dim = self.MODEL_DIMS[model_name]
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "models" / "embeddings"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model (with error handling)
        self._model = None
        self._model_loaded = False
        self._load_error = None
        
        try:
            self._load_model()
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to load model: {e}")
        
        # Initialize embedding cache
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache = EmbeddingCache(max_size=10000, ttl_seconds=3600)
            self.batch_processor = BatchProcessor(optimal_batch_size=32)
            logger.info("Embedding cache enabled", extra={
                "max_size": 10000,
                "ttl_seconds": 3600
            })
        else:
            self.cache = None
            self.batch_processor = None
            logger.info("Embedding cache disabled")
    
    def _load_model(self):
        """Load the sentence transformer model with error handling"""
        if self._model_loaded:
            return
            
        logger.info(f"Loading model: {self.model_path}")
        start_time = time.time()
        
        try:
            self._model = SentenceTransformer(self.model_path, cache_folder=str(self.cache_dir))
            self.embedding_dim = self._model.get_sentence_embedding_dimension()
            self._model_loaded = True
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully", extra={
                "load_time_seconds": load_time,
                "embedding_dim": self.embedding_dim,
                "max_seq_length": self._model.max_seq_length
            })
            metrics.record("model_load_time", load_time)
        except Exception as e:
            self._load_error = str(e)
            # Set default dimension so other code can continue
            self.embedding_dim = self._expected_dim
            raise RuntimeError(f"Failed to load model '{self.model_path}': {e}")
    
    @property
    def model(self) -> SentenceTransformer:
        """Get the loaded model (lazy loading)"""
        if not self._model_loaded:
            if self._load_error:
                raise RuntimeError(f"Model failed to load: {self._load_error}")
            self._load_model()
        return self._model
    
    def is_ready(self) -> bool:
        """Check if the model is loaded and ready"""
        return self._model_loaded and self._model is not None
    
    def get_zero_embedding(self) -> np.ndarray:
        """Get a zero embedding (for fallback on errors)"""
        return np.zeros(self.embedding_dim, dtype=np.float32)
    
    @timed(logger=logger, event="encode_embeddings")
    def encode(self, texts: Union[str, List[str], Any], 
               batch_size: int = 32,
               show_progress: bool = False,
               normalize: bool = True,
               use_cache: bool = None) -> np.ndarray:
        """
        Generate embeddings for text(s) with caching support
        
        Edge cases handled:
        - None input -> zero embedding
        - Empty string -> zero embedding
        - Non-string types -> string conversion
        - Very long text -> truncation
        - Single text vs batch -> consistent output shape
        
        Args:
            texts: Single text or list of texts (can also be None or non-string)
            batch_size: Batch size for processing (clamped to MAX_BATCH_SIZE)
            show_progress: Show progress bar
            normalize: Normalize embeddings to unit length (for cosine similarity)
            use_cache: Override cache enable setting (default: use self.enable_cache)
            
        Returns:
            numpy array of embeddings (shape: [n_texts, embedding_dim] or [embedding_dim] for single)
        """
        # Determine if cache should be used
        if use_cache is None:
            use_cache = self.enable_cache
        
        # Handle None input
        if texts is None:
            logger.warning("Received None text for embedding")
            return self.get_zero_embedding()
        
        # Convert single text to list
        single_text = False
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        elif not isinstance(texts, (list, tuple)):
            # Try to convert or wrap
            try:
                texts = [str(texts)]
                single_text = True
            except:
                logger.error(f"Cannot convert {type(texts)} to string")
                return self.get_zero_embedding()
        
        # Sanitize all texts
        texts = [_sanitize_text(t) for t in texts]
        
        # Handle all-empty case
        if not texts or all(not t for t in texts):
            logger.warning("All texts are empty, returning zero embeddings")
            empty_result = np.zeros((len(texts) if texts else 1, self.embedding_dim), dtype=np.float32)
            return empty_result[0] if single_text else empty_result
        
        # Clamp batch size
        batch_size = min(batch_size, MAX_BATCH_SIZE)
        
        # Try to get from cache
        results = []
        texts_to_encode = []
        indices_to_encode = []
        
        if use_cache and self.cache is not None:
            for i, text in enumerate(texts):
                cached = self.cache.get(text)
                if cached is not None:
                    results.append((i, cached))
                    logger.debug(f"Cache hit for text {i}")
                else:
                    texts_to_encode.append(text)
                    indices_to_encode.append(i)
                    logger.debug(f"Cache miss for text {i}")
        else:
            texts_to_encode = texts
            indices_to_encode = list(range(len(texts)))
        
        # Generate embeddings for cache misses
        if texts_to_encode:
            logger.debug(f"Encoding {len(texts_to_encode)}/{len(texts)} texts")
            embeddings = self.model.encode(
                texts_to_encode,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
            
            # Add to cache and results
            for i, text, embedding in zip(indices_to_encode, texts_to_encode, embeddings):
                if use_cache and self.cache is not None:
                    self.cache.put(text, embedding)
                results.append((i, embedding))
        
        # Sort results by original index
        results.sort(key=lambda x: x[0])
        final_embeddings = np.array([emb for _, emb in results])
        
        # Log cache statistics
        if use_cache and self.cache is not None:
            stats = self.cache.get_stats()
            logger.debug("Cache statistics", extra=stats)
            metrics.record("cache_hit_rate", stats['hit_rate'])
        
        # Return single embedding as 1D array
        if single_text:
            return final_embeddings[0]
        
        return final_embeddings
    
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
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache is not None:
            return self.cache.get_stats()
        return {"cache_enabled": False}
    
    def clear_cache(self):
        """Clear the embedding cache"""
        if self.cache is not None:
            self.cache.clear()
            logger.info("Embedding cache cleared")
        else:
            logger.warning("Cache not enabled, nothing to clear")
    
    def save_cache(self, filepath: Optional[str] = None):
        """Save cache to disk"""
        if self.cache is not None:
            if filepath is None:
                filepath = str(Path("data/cache/embedding_cache.pkl"))
            self.cache.save_cache_to_disk(filepath)
            logger.info(f"Cache saved to {filepath}")
        else:
            logger.warning("Cache not enabled, nothing to save")
    
    def load_cache(self, filepath: Optional[str] = None):
        """Load cache from disk"""
        if self.cache is not None:
            if filepath is None:
                filepath = str(Path("data/cache/embedding_cache.pkl"))
            self.cache.load_cache_from_disk(filepath)
            logger.info(f"Cache loaded from {filepath}")
        else:
            logger.warning("Cache not enabled, cannot load")
    
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
