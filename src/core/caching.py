"""
Phase 2: Performance Optimization - Implementation
Focuses on caching, fast loading, and performance improvements
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import pickle
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np


class EmbeddingCache:
    """
    In-memory cache for embeddings with LRU eviction
    Dramatically reduces redundant embedding generation
    """
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        """
        Initialize embedding cache
        
        Args:
            max_size: Maximum number of cached embeddings
            ttl_seconds: Time-to-live for cache entries (default: 1 hour)
        """
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, text: str, model_name: Optional[str] = None) -> str:
        """Generate cache key from text and model"""
        if model_name:
            content = f"{model_name}:{text}"
        else:
            content = text
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, text: str, model_name: Optional[str] = None) -> Optional[np.ndarray]:
        """Get cached embedding if available and not expired"""
        key = self._generate_key(text, model_name)
        
        if key in self.cache:
            # Check if expired
            access_time = self.access_times.get(key, datetime.min)
            if datetime.now() - access_time < timedelta(seconds=self.ttl_seconds):
                self.hits += 1
                self.access_times[key] = datetime.now()
                return self.cache[key]
            else:
                # Expired - remove
                del self.cache[key]
                del self.access_times[key]
        
        self.misses += 1
        return None
    
    def put(self, text: str, embedding: np.ndarray, model_name: Optional[str] = None):
        """Cache an embedding"""
        key = self._generate_key(text, model_name)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = embedding
        self.access_times[key] = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests) if total_requests > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.access_times.clear()
        self.hits = 0
        self.misses = 0


class MatchResultCache:
    """
    Cache for match results to avoid redundant matching
    Uses job hash as key
    """
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """
        Initialize match result cache
        
        Args:
            ttl_seconds: Time-to-live (default: 1 hour)
            max_size: Maximum cached results
        """
        self.cache = {}
        self.timestamps = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, job_data: Dict[str, Any], top_k: int, filters: Optional[Dict] = None) -> str:
        """Generate cache key from job data"""
        # Create deterministic string from job data
        key_parts = [
            job_data.get('title', ''),
            job_data.get('description', ''),
            ','.join(sorted(job_data.get('required_skills', []))),
            str(job_data.get('experience_years', '')),
            job_data.get('experience_level', ''),
            str(top_k),
            str(filters) if filters else ''
        ]
        content = '|'.join(key_parts)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, job_data: Dict[str, Any], top_k: int = 50, filters: Optional[Dict] = None) -> Optional[List[Dict]]:
        """Get cached match results"""
        key = self._generate_key(job_data, top_k, filters)
        
        if key in self.cache:
            # Check expiration
            timestamp = self.timestamps.get(key, datetime.min)
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                self.hits += 1
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
        
        self.misses += 1
        return None
    
    def put(self, job_data: Dict[str, Any], results: List[Dict], top_k: int = 50, filters: Optional[Dict] = None):
        """Cache match results"""
        key = self._generate_key(job_data, top_k, filters)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = results
        self.timestamps[key] = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0


class BatchProcessor:
    """
    Optimized batch processing for embeddings
    Groups requests and processes in optimal batches
    """
    
    def __init__(self, optimal_batch_size: int = 32):
        self.optimal_batch_size = optimal_batch_size
        self.pending_requests = []
        self.last_flush = time.time()
        self.flush_interval = 0.1  # 100ms
    
    def should_flush(self) -> bool:
        """Check if batch should be flushed"""
        return (
            len(self.pending_requests) >= self.optimal_batch_size or
            (len(self.pending_requests) > 0 and 
             time.time() - self.last_flush > self.flush_interval)
        )
    
    def add_request(self, text: str, callback):
        """Add request to batch"""
        self.pending_requests.append((text, callback))
    
    def flush(self, process_fn):
        """Process all pending requests"""
        if not self.pending_requests:
            return
        
        texts = [req[0] for req in self.pending_requests]
        callbacks = [req[1] for req in self.pending_requests]
        
        # Process batch
        results = process_fn(texts)
        
        # Distribute results
        for callback, result in zip(callbacks, results):
            callback(result)
        
        self.pending_requests.clear()
        self.last_flush = time.time()


def save_cache_to_disk(cache: EmbeddingCache, filename: str = "data/cache/embedding_cache.pkl"):
    """Persist embedding cache to disk"""
    cache_path = Path(filename)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    cache_data = {
        'cache': cache.cache,
        'access_times': cache.access_times,
        'hits': cache.hits,
        'misses': cache.misses
    }
    
    with open(cache_path, 'wb') as f:
        pickle.dump(cache_data, f)
    
    print(f"✅ Cache saved: {len(cache.cache)} embeddings")


def load_cache_from_disk(filename: str = "data/cache/embedding_cache.pkl") -> Optional[EmbeddingCache]:
    """Load embedding cache from disk"""
    cache_path = Path(filename)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'rb') as f:
            cache_data = pickle.load(f)
        
        cache = EmbeddingCache()
        cache.cache = cache_data.get('cache', {})
        cache.access_times = cache_data.get('access_times', {})
        cache.hits = cache_data.get('hits', 0)
        cache.misses = cache_data.get('misses', 0)
        
        print(f"✅ Cache loaded: {len(cache.cache)} embeddings")
        return cache
    except Exception as e:
        print(f"⚠️  Failed to load cache: {e}")
        return None


if __name__ == "__main__":
    # Test caching system
    print("="*70)
    print("  PHASE 2: Testing Caching System")
    print("="*70)
    
    # Test 1: Embedding Cache
    print("\n[Test 1] Embedding Cache")
    cache = EmbeddingCache(max_size=100, ttl_seconds=60)
    
    # Simulate embeddings
    test_embedding = np.random.rand(384)
    
    # Cache miss
    result = cache.get("test text", "mini")
    assert result is None, "Should be cache miss"
    
    # Cache put
    cache.put("test text", "mini", test_embedding)
    
    # Cache hit
    result = cache.get("test text", "mini")
    assert result is not None, "Should be cache hit"
    assert np.array_equal(result, test_embedding), "Embedding should match"
    
    stats = cache.get_stats()
    print(f"   Hits: {stats['hits']}, Misses: {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate']:.1f}%")
    print("   ✅ Embedding cache working")
    
    # Test 2: Match Result Cache
    print("\n[Test 2] Match Result Cache")
    match_cache = MatchResultCache(ttl_seconds=3600, max_size=100)
    
    job = {
        "title": "Software Engineer",
        "required_skills": ["Python", "Django"],
        "experience_years": 3
    }
    
    matches = [{"id": "1", "score": 85}, {"id": "2", "score": 75}]
    
    # Cache miss
    result = match_cache.get(job, top_k=5)
    assert result is None, "Should be cache miss"
    
    # Cache put
    match_cache.put(job, top_k=5, results=matches)
    
    # Cache hit
    result = match_cache.get(job, top_k=5)
    assert result is not None, "Should be cache hit"
    assert len(result) == 2, "Should return 2 matches"
    
    stats = match_cache.get_stats()
    print(f"   Hits: {stats['hits']}, Misses: {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate']:.1f}%")
    print("   ✅ Match result cache working")
    
    # Test 3: Persistence
    print("\n[Test 3] Cache Persistence")
    save_cache_to_disk(cache, "data/cache/test_cache.pkl")
    loaded_cache = load_cache_from_disk("data/cache/test_cache.pkl")
    assert loaded_cache is not None, "Should load cache"
    assert len(loaded_cache.cache) == len(cache.cache), "Cache size should match"
    print("   ✅ Cache persistence working")
    
    print("\n" + "="*70)
    print("✅ ALL CACHING TESTS PASSED")
    print("="*70)
