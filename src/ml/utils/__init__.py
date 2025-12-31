"""
ML Utilities Package
Provides validation, error handling, performance utilities, and helper functions for ML components
"""

from .validation import (
    ValidationError,
    ValidationResult,
    TextValidator,
    EmbeddingValidator,
    ScoreValidator,
    ResumeDataValidator,
    JobDataValidator,
    validate_and_log
)

from .error_handling import (
    ErrorSeverity,
    ErrorCategory,
    MLError,
    ErrorHandler,
    get_error_handler,
    with_fallback,
    with_retry,
    safe_divide,
    safe_get,
    safe_float,
    safe_int,
    safe_list,
    GracefulDegradation
)

from .performance import (
    PerformanceMetrics,
    PerformanceTracker,
    get_tracker,
    profile,
    timed_operation,
    optimal_batch_size,
    batch_generator,
    MemoryManager,
    estimate_processing_time,
    LazyLoader,
    memoize,
    normalize_embeddings_batch,
    cosine_similarity_batch
)

__all__ = [
    # Validation
    'ValidationError',
    'ValidationResult',
    'TextValidator',
    'EmbeddingValidator',
    'ScoreValidator',
    'ResumeDataValidator',
    'JobDataValidator',
    'validate_and_log',
    
    # Error Handling
    'ErrorSeverity',
    'ErrorCategory',
    'MLError',
    'ErrorHandler',
    'get_error_handler',
    'with_fallback',
    'with_retry',
    'safe_divide',
    'safe_get',
    'safe_float',
    'safe_int',
    'safe_list',
    'GracefulDegradation',
    
    # Performance
    'PerformanceMetrics',
    'PerformanceTracker',
    'get_tracker',
    'profile',
    'timed_operation',
    'optimal_batch_size',
    'batch_generator',
    'MemoryManager',
    'estimate_processing_time',
    'LazyLoader',
    'memoize',
    'normalize_embeddings_batch',
    'cosine_similarity_batch'
]
