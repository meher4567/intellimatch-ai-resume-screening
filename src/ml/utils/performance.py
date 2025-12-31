"""
Performance Utilities for ML Components
Provides profiling, batch processing optimization, and memory management
"""

import time
import functools
import logging
import gc
import sys
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generator
from dataclasses import dataclass, field
from contextlib import contextmanager
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Track performance metrics for operations"""
    operation_name: str
    total_calls: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    last_time_ms: float = 0.0
    errors: int = 0
    
    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.total_calls if self.total_calls > 0 else 0
    
    def record(self, time_ms: float, is_error: bool = False):
        self.total_calls += 1
        self.total_time_ms += time_ms
        self.last_time_ms = time_ms
        self.min_time_ms = min(self.min_time_ms, time_ms)
        self.max_time_ms = max(self.max_time_ms, time_ms)
        if is_error:
            self.errors += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation_name,
            'calls': self.total_calls,
            'avg_ms': round(self.avg_time_ms, 2),
            'min_ms': round(self.min_time_ms, 2) if self.min_time_ms != float('inf') else 0,
            'max_ms': round(self.max_time_ms, 2),
            'total_ms': round(self.total_time_ms, 2),
            'errors': self.errors
        }


class PerformanceTracker:
    """Global performance tracking for ML operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics = {}
            cls._instance._enabled = True
        return cls._instance
    
    def get_metrics(self, operation: str) -> PerformanceMetrics:
        if operation not in self._metrics:
            self._metrics[operation] = PerformanceMetrics(operation)
        return self._metrics[operation]
    
    def record(self, operation: str, time_ms: float, is_error: bool = False):
        if self._enabled:
            self.get_metrics(operation).record(time_ms, is_error)
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        return {name: m.to_dict() for name, m in self._metrics.items()}
    
    def clear(self):
        self._metrics.clear()
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False


def get_tracker() -> PerformanceTracker:
    """Get the global performance tracker"""
    return PerformanceTracker()


T = TypeVar('T')


def profile(operation_name: str = None) -> Callable:
    """
    Decorator to profile function execution time
    
    Usage:
        @profile("embedding_generation")
        def generate_embeddings(texts):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = operation_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            tracker = get_tracker()
            start = time.perf_counter()
            is_error = False
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                is_error = True
                raise
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                tracker.record(name, elapsed_ms, is_error)
        
        return wrapper
    return decorator


@contextmanager
def timed_operation(operation_name: str, log_threshold_ms: float = 1000.0):
    """
    Context manager for timing operations
    
    Usage:
        with timed_operation("search"):
            results = vector_store.search(query)
    """
    start = time.perf_counter()
    tracker = get_tracker()
    is_error = False
    
    try:
        yield
    except Exception:
        is_error = True
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        tracker.record(operation_name, elapsed_ms, is_error)
        
        if elapsed_ms > log_threshold_ms:
            logger.warning(f"{operation_name} took {elapsed_ms:.2f}ms (threshold: {log_threshold_ms}ms)")


def optimal_batch_size(
    total_items: int,
    min_batch: int = 8,
    max_batch: int = 128,
    target_batches: int = 10
) -> int:
    """
    Calculate optimal batch size based on total items
    
    Args:
        total_items: Total number of items to process
        min_batch: Minimum batch size
        max_batch: Maximum batch size
        target_batches: Target number of batches for large datasets
        
    Returns:
        Optimal batch size
    """
    if total_items <= min_batch:
        return total_items
    
    # For small datasets, use minimum batch size
    if total_items <= min_batch * target_batches:
        return min_batch
    
    # Calculate batch size for target number of batches
    optimal = total_items // target_batches
    
    # Clamp to range
    return max(min_batch, min(max_batch, optimal))


def batch_generator(
    items: List[T], 
    batch_size: int = 32,
    progress_callback: Callable[[int, int], None] = None
) -> Generator[List[T], None, None]:
    """
    Generate batches from a list of items
    
    Args:
        items: List of items to batch
        batch_size: Size of each batch
        progress_callback: Optional callback(current, total) for progress
        
    Yields:
        Batches of items
    """
    total = len(items)
    processed = 0
    
    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        yield batch
        processed += len(batch)
        
        if progress_callback:
            progress_callback(processed, total)


class MemoryManager:
    """Utilities for memory management"""
    
    @staticmethod
    def get_memory_usage_mb() -> float:
        """Get current memory usage in MB"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    
    @staticmethod
    def force_gc():
        """Force garbage collection"""
        gc.collect()
    
    @staticmethod
    @contextmanager
    def memory_limit(max_mb: float = 1024.0, action: str = 'warn'):
        """
        Context manager to monitor memory usage
        
        Args:
            max_mb: Maximum allowed memory in MB
            action: 'warn', 'gc', or 'raise'
        """
        try:
            import psutil
            process = psutil.Process()
            start_mb = process.memory_info().rss / (1024 * 1024)
        except ImportError:
            yield
            return
        
        try:
            yield
        finally:
            end_mb = process.memory_info().rss / (1024 * 1024)
            
            if end_mb > max_mb:
                msg = f"Memory usage ({end_mb:.1f}MB) exceeds limit ({max_mb}MB)"
                
                if action == 'raise':
                    raise MemoryError(msg)
                elif action == 'gc':
                    logger.warning(f"{msg}. Running garbage collection.")
                    gc.collect()
                else:
                    logger.warning(msg)
    
    @staticmethod
    def estimate_embedding_memory_mb(
        num_embeddings: int, 
        embedding_dim: int = 384,
        dtype_bytes: int = 4
    ) -> float:
        """Estimate memory needed for embeddings"""
        return (num_embeddings * embedding_dim * dtype_bytes) / (1024 * 1024)


def estimate_processing_time(
    num_items: int,
    samples_per_second: float = 100.0
) -> str:
    """
    Estimate processing time
    
    Returns:
        Human-readable time estimate
    """
    seconds = num_items / samples_per_second
    
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    else:
        return f"{seconds / 3600:.1f} hours"


class LazyLoader:
    """
    Lazy loader for expensive objects (models, large data)
    
    Usage:
        model = LazyLoader(lambda: load_heavy_model())
        # Model is only loaded when accessed:
        result = model.value.predict(data)
    """
    
    def __init__(self, loader: Callable[[], T]):
        self._loader = loader
        self._value = None
        self._loaded = False
        self._load_time_ms = None
    
    @property
    def value(self) -> T:
        if not self._loaded:
            start = time.perf_counter()
            self._value = self._loader()
            self._load_time_ms = (time.perf_counter() - start) * 1000
            self._loaded = True
            logger.debug(f"Lazy loaded object in {self._load_time_ms:.2f}ms")
        return self._value
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    def unload(self):
        """Unload the object to free memory"""
        if self._loaded:
            self._value = None
            self._loaded = False
            gc.collect()


def memoize(maxsize: int = 128):
    """
    Memoization decorator with size limit
    
    Similar to functools.lru_cache but with better error handling
    and optional size configuration.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = {}
        access_order = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            try:
                key = (args, tuple(sorted(kwargs.items())))
                # Handle unhashable types
                key = str(key)
            except:
                # If we can't create a key, just call the function
                return func(*args, **kwargs)
            
            if key in cache:
                # Move to end (most recently used)
                access_order.remove(key)
                access_order.append(key)
                return cache[key]
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            access_order.append(key)
            
            # Evict oldest if over limit
            while len(cache) > maxsize:
                oldest = access_order.pop(0)
                del cache[oldest]
            
            return result
        
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'maxsize': maxsize
        }
        wrapper.cache_clear = lambda: (cache.clear(), access_order.clear())
        
        return wrapper
    return decorator


# Numpy optimization utilities
def normalize_embeddings_batch(embeddings: np.ndarray, inplace: bool = False) -> np.ndarray:
    """
    Efficiently normalize a batch of embeddings to unit length
    
    Args:
        embeddings: 2D array of shape (n_samples, embedding_dim)
        inplace: Whether to modify the input array
        
    Returns:
        Normalized embeddings
    """
    if not inplace:
        embeddings = embeddings.copy()
    
    # Calculate norms
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Avoid division by zero
    norms = np.where(norms < 1e-10, 1.0, norms)
    
    embeddings /= norms
    return embeddings


def cosine_similarity_batch(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """
    Efficiently compute cosine similarity between query and candidates
    
    Args:
        query: 1D query embedding
        candidates: 2D array of candidate embeddings
        
    Returns:
        1D array of similarities
    """
    # Normalize
    query_norm = query / (np.linalg.norm(query) + 1e-10)
    cand_norms = np.linalg.norm(candidates, axis=1, keepdims=True)
    cand_norms = np.where(cand_norms < 1e-10, 1.0, cand_norms)
    candidates_norm = candidates / cand_norms
    
    # Dot product
    return np.dot(candidates_norm, query_norm)
