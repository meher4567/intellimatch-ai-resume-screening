"""
Production-grade structured logging configuration for IntelliMatch AI
Provides request tracing, performance metrics, and structured JSON logs
"""
import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
from pathlib import Path
from functools import wraps
import sys

class StructuredLogger:
    """Structured JSON logger with request tracing and metrics"""
    
    def __init__(self, name: str = "intellimatch", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler - JSON format
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.json"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        
        # Console handler - Human readable
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(HumanFormatter())
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Context storage for request tracing
        self._context = {}
    
    def set_context(self, **kwargs):
        """Set context for all subsequent logs (e.g., request_id)"""
        self._context.update(kwargs)
    
    def clear_context(self):
        """Clear context"""
        self._context.clear()
    
    def _build_log(self, level: str, event: str, **kwargs) -> Dict[str, Any]:
        """Build structured log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.name,
            "event": event,
            **self._context,
            **kwargs
        }
        return log_entry
    
    def info(self, event: str, **kwargs):
        """Log info level"""
        log_entry = self._build_log("INFO", event, **kwargs)
        self.logger.info(json.dumps(log_entry))
    
    def warning(self, event: str, **kwargs):
        """Log warning level"""
        log_entry = self._build_log("WARNING", event, **kwargs)
        self.logger.warning(json.dumps(log_entry))
    
    def error(self, event: str, **kwargs):
        """Log error level"""
        log_entry = self._build_log("ERROR", event, **kwargs)
        self.logger.error(json.dumps(log_entry))
    
    def debug(self, event: str, **kwargs):
        """Log debug level"""
        log_entry = self._build_log("DEBUG", event, **kwargs)
        self.logger.debug(json.dumps(log_entry))


class JSONFormatter(logging.Formatter):
    """Formatter for JSON log output"""
    def format(self, record):
        return record.getMessage()


class HumanFormatter(logging.Formatter):
    """Formatter for human-readable console output"""
    
    COLORS = {
        'INFO': '\033[92m',      # Green
        'WARNING': '\033[93m',   # Yellow
        'ERROR': '\033[91m',     # Red
        'DEBUG': '\033[94m',     # Blue
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        try:
            log_data = json.loads(record.getMessage())
            level = log_data.get('level', 'INFO')
            event = log_data.get('event', 'unknown')
            timestamp = log_data.get('timestamp', '')
            
            # Build human-readable message
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            
            msg = f"{color}[{level}]{reset} {timestamp[:19]} | {event}"
            
            # Add important fields
            if 'request_id' in log_data:
                msg += f" | req_id={log_data['request_id'][:8]}"
            if 'duration_ms' in log_data:
                msg += f" | {log_data['duration_ms']:.1f}ms"
            if 'error' in log_data:
                msg += f" | error={log_data['error']}"
            
            return msg
        except:
            return record.getMessage()


def timed(logger: StructuredLogger, event: str):
    """Decorator to time function execution and log"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                logger.info(
                    event,
                    duration_ms=duration_ms,
                    status="success",
                    function=func.__name__
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                logger.error(
                    event,
                    duration_ms=duration_ms,
                    status="error",
                    error=str(e),
                    function=func.__name__
                )
                raise
        return wrapper
    return decorator


# Global logger instance
_logger = None

def get_logger(name: str = "intellimatch") -> StructuredLogger:
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name)
    return _logger


# Performance metrics collector
class MetricsCollector:
    """Collect and aggregate performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'embedding_generation': [],
            'vector_search': [],
            'matching': [],
            'skill_extraction': []
        }
    
    def record(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        values = [m['value'] for m in self.metrics.get(metric_name, [])]
        if not values:
            return {}
        
        values.sort()
        n = len(values)
        return {
            'count': n,
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / n,
            'p50': values[n // 2],
            'p95': values[int(n * 0.95)] if n > 1 else values[0],
            'p99': values[int(n * 0.99)] if n > 1 else values[0]
        }
    
    def reset(self):
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key] = []
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics"""
        return {name: self.get_stats(name) for name in self.metrics.keys()}


# Global metrics collector
_metrics = MetricsCollector()

def get_metrics() -> MetricsCollector:
    """Get global metrics collector"""
    return _metrics


if __name__ == "__main__":
    # Test logging
    logger = get_logger()
    logger.set_context(request_id=str(uuid4()))
    
    logger.info("test_event", component="embedding_generator", model="mini")
    logger.warning("slow_operation", duration_ms=1500, threshold=1000)
    
    # Test timed decorator
    @timed(logger, "test_function")
    def slow_function():
        time.sleep(0.1)
        return "done"
    
    result = slow_function()
    
    # Test metrics
    metrics = get_metrics()
    metrics.record('embedding_generation', 45.3)
    metrics.record('embedding_generation', 52.1)
    metrics.record('embedding_generation', 48.7)
    
    print("\nMetrics Stats:")
    print(json.dumps(metrics.get_stats('embedding_generation'), indent=2))
