"""
Error Handling Utilities for ML Components
Provides centralized error handling, recovery strategies, and graceful degradation
"""

import logging
import traceback
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    LOW = "low"          # Recoverable, continue with defaults
    MEDIUM = "medium"    # Partially recoverable, some data loss
    HIGH = "high"        # Significant impact, needs attention
    CRITICAL = "critical"  # System cannot function properly


class ErrorCategory(Enum):
    """Categories of errors"""
    INPUT_VALIDATION = "input_validation"
    EMBEDDING_GENERATION = "embedding_generation"
    MATCHING = "matching"
    SCORING = "scoring"
    PARSING = "parsing"
    STORAGE = "storage"
    MODEL_LOADING = "model_loading"
    NETWORK = "network"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class MLError:
    """Structured ML error with context"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    original_exception: Optional[Exception] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    traceback_str: Optional[str] = None
    recovery_action: Optional[str] = None
    
    def __str__(self):
        return f"[{self.severity.value}] {self.category.value}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "recovery_action": self.recovery_action
        }


class ErrorHandler:
    """Centralized error handling for ML operations"""
    
    # Default fallback values for different operations
    FALLBACKS = {
        "embedding": None,  # Will be set based on dimension
        "score": 50.0,  # Neutral score
        "skills": [],
        "match_result": {
            "score": 0,
            "matches": [],
            "missing": [],
            "error": True
        },
        "experience_level": "mid",
        "quality_score": 50.0
    }
    
    def __init__(self, 
                 max_retries: int = 3,
                 retry_delay: float = 0.5,
                 log_all_errors: bool = True):
        """
        Initialize error handler
        
        Args:
            max_retries: Maximum retry attempts for recoverable errors
            retry_delay: Delay between retries in seconds
            log_all_errors: Whether to log all errors
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.log_all_errors = log_all_errors
        self.error_history: list[MLError] = []
        self.error_counts: Dict[ErrorCategory, int] = {}
    
    def handle(self, 
               exception: Exception,
               category: ErrorCategory = ErrorCategory.UNKNOWN,
               context: Dict[str, Any] = None,
               fallback_key: str = None,
               custom_fallback: Any = None) -> tuple[MLError, Any]:
        """
        Handle an exception and return appropriate error + fallback
        
        Args:
            exception: The caught exception
            category: Category of the error
            context: Additional context
            fallback_key: Key for default fallback value
            custom_fallback: Custom fallback value to use
            
        Returns:
            Tuple of (MLError, fallback_value)
        """
        # Determine severity
        severity = self._classify_severity(exception, category)
        
        # Build error object
        error = MLError(
            category=category,
            severity=severity,
            message=str(exception),
            original_exception=exception,
            context=context or {},
            traceback_str=traceback.format_exc(),
            recovery_action=self._suggest_recovery(category, exception)
        )
        
        # Track error
        self.error_history.append(error)
        self.error_counts[category] = self.error_counts.get(category, 0) + 1
        
        # Log
        if self.log_all_errors:
            self._log_error(error)
        
        # Get fallback
        if custom_fallback is not None:
            fallback = custom_fallback
        elif fallback_key and fallback_key in self.FALLBACKS:
            fallback = self.FALLBACKS[fallback_key]
        else:
            fallback = None
        
        return error, fallback
    
    def _classify_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Classify error severity based on exception type and category"""
        # Critical errors
        if isinstance(exception, (MemoryError, SystemError)):
            return ErrorSeverity.CRITICAL
        
        if category == ErrorCategory.MODEL_LOADING:
            return ErrorSeverity.CRITICAL
        
        # High severity
        if isinstance(exception, (RuntimeError, OSError)):
            return ErrorSeverity.HIGH
        
        if category in (ErrorCategory.STORAGE, ErrorCategory.EMBEDDING_GENERATION):
            return ErrorSeverity.HIGH
        
        # Medium severity
        if isinstance(exception, (TypeError, KeyError)):
            return ErrorSeverity.MEDIUM
        
        if category in (ErrorCategory.SCORING, ErrorCategory.MATCHING):
            return ErrorSeverity.MEDIUM
        
        # Low severity (validation, etc.)
        return ErrorSeverity.LOW
    
    def _suggest_recovery(self, category: ErrorCategory, exception: Exception) -> str:
        """Suggest recovery action based on error type"""
        suggestions = {
            ErrorCategory.INPUT_VALIDATION: "Check input data format and content",
            ErrorCategory.EMBEDDING_GENERATION: "Retry with smaller batch size or simplified text",
            ErrorCategory.MATCHING: "Check skill data format and retry with exact matching only",
            ErrorCategory.SCORING: "Using default neutral score",
            ErrorCategory.PARSING: "Verify file format and content structure",
            ErrorCategory.STORAGE: "Check disk space and file permissions",
            ErrorCategory.MODEL_LOADING: "Verify model files exist and are not corrupted",
            ErrorCategory.NETWORK: "Check network connectivity and retry",
            ErrorCategory.TIMEOUT: "Increase timeout or reduce data size"
        }
        return suggestions.get(category, "Check logs for details")
    
    def _log_error(self, error: MLError):
        """Log error with appropriate level"""
        log_msg = f"{error.category.value}: {error.message}"
        
        if error.context:
            log_msg += f" | Context: {error.context}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_msg)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_msg)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": len(self.error_history),
            "by_category": {k.value: v for k, v in self.error_counts.items()},
            "by_severity": {
                s.value: sum(1 for e in self.error_history if e.severity == s)
                for s in ErrorSeverity
            },
            "recent_errors": [e.to_dict() for e in self.error_history[-10:]]
        }
    
    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_counts.clear()


# Global error handler instance
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return _error_handler


T = TypeVar('T')


def with_fallback(fallback_value: T = None,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 log_error: bool = True) -> Callable:
    """
    Decorator that provides fallback values on exceptions
    
    Args:
        fallback_value: Value to return on error
        category: Error category for logging
        log_error: Whether to log the error
        
    Usage:
        @with_fallback(fallback_value=[], category=ErrorCategory.MATCHING)
        def match_skills(skills1, skills2):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                error, _ = handler.handle(
                    exception=e,
                    category=category,
                    context={
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    }
                )
                
                if log_error:
                    logger.warning(f"{func.__name__} failed, using fallback: {error.message}")
                
                return fallback_value
        return wrapper
    return decorator


def with_retry(max_retries: int = 3,
              delay: float = 0.5,
              backoff: float = 2.0,
              exceptions: tuple = (Exception,),
              category: ErrorCategory = ErrorCategory.UNKNOWN) -> Callable:
    """
    Decorator that retries function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
        category: Error category for logging
        
    Usage:
        @with_retry(max_retries=3, delay=1.0)
        def fetch_embeddings(text):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
            
            # All retries failed
            handler = get_error_handler()
            handler.handle(
                exception=last_exception,
                category=category,
                context={"function": func.__name__, "attempts": max_retries + 1}
            )
            raise last_exception
        return wrapper
    return decorator


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default on zero/invalid"""
    try:
        if denominator == 0 or denominator is None:
            return default
        result = numerator / denominator
        if not isinstance(result, (int, float)) or result != result:  # NaN check
            return default
        return result
    except (TypeError, ValueError):
        return default


def safe_get(data: Dict, *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary values
    
    Usage:
        value = safe_get(data, 'level1', 'level2', 'key', default='fallback')
    """
    try:
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            elif isinstance(result, (list, tuple)) and isinstance(key, int):
                result = result[key] if 0 <= key < len(result) else default
            else:
                return default
        return result if result is not None else default
    except (KeyError, IndexError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float"""
    try:
        if value is None:
            return default
        result = float(value)
        if result != result:  # NaN check
            return default
        return result
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert to int"""
    try:
        if value is None:
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_list(value: Any, default: list = None) -> list:
    """Ensure value is a list"""
    if default is None:
        default = []
    
    if value is None:
        return default
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, (tuple, set)):
        return list(value)
    
    if isinstance(value, dict):
        # Common pattern: dict with 'all_skills' or similar key
        for key in ['all_skills', 'items', 'values', 'data']:
            if key in value and isinstance(value[key], list):
                return value[key]
    
    # Single value to list
    return [value]


class GracefulDegradation:
    """
    Context manager for graceful degradation
    
    Usage:
        with GracefulDegradation(fallback={'score': 50}, category=ErrorCategory.SCORING) as ctx:
            result = compute_complex_score()
            ctx.set_result(result)
        
        final_result = ctx.get_result()  # Returns computed result or fallback
    """
    
    def __init__(self, 
                 fallback: Any = None,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 log_degradation: bool = True):
        self.fallback = fallback
        self.category = category
        self.log_degradation = log_degradation
        self._result = None
        self._degraded = False
        self._error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._degraded = True
            self._error = exc_val
            
            if self.log_degradation:
                logger.warning(
                    f"Graceful degradation triggered ({self.category.value}): {exc_val}. "
                    f"Using fallback value."
                )
            
            # Suppress the exception
            return True
        return False
    
    def set_result(self, result: Any):
        """Set the successful result"""
        self._result = result
    
    def get_result(self) -> Any:
        """Get result or fallback"""
        if self._degraded:
            return self.fallback
        return self._result if self._result is not None else self.fallback
    
    @property
    def degraded(self) -> bool:
        """Check if degradation occurred"""
        return self._degraded
    
    @property
    def error(self) -> Optional[Exception]:
        """Get the error that caused degradation"""
        return self._error
