"""
Rate limiting configuration and decorators
Protects endpoints from abuse and ensures fair resource usage
"""

from functools import wraps
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import asyncio

# In-memory storage for rate limits (use Redis in production)
_rate_limit_storage: Dict[str, Dict[str, Tuple[int, datetime]]] = defaultdict(dict)
_lock = asyncio.Lock()

# Rate limit configurations by endpoint category
RATE_LIMITS = {
    # Authentication endpoints - strict limits to prevent brute force
    "auth_register": (5, 3600),      # 5 requests per hour
    "auth_login": (10, 60),           # 10 requests per minute
    "auth_protected": (100, 60),      # 100 requests per minute
    
    # File upload endpoints - moderate limits
    "upload_single": (20, 3600),      # 20 uploads per hour
    "upload_batch": (5, 3600),        # 5 batch uploads per hour
    
    # Search and matching endpoints - higher limits
    "search": (100, 60),              # 100 searches per minute
    "matching": (50, 60),             # 50 matches per minute
    
    # CRUD operations - standard limits
    "read": (200, 60),                # 200 reads per minute
    "write": (50, 60),                # 50 writes per minute
    "delete": (20, 60),               # 20 deletes per minute
    
    # Analytics endpoints - higher limits
    "analytics": (100, 60),           # 100 requests per minute
    
    # Default fallback
    "default": (60, 60),              # 60 requests per minute
}


def get_client_id(request: Request) -> str:
    """
    Get unique identifier for client (IP address or API key)
    In production, prioritize API key over IP
    """
    # Try to get API key from header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key}"
    
    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


async def check_rate_limit(
    client_id: str,
    limit_key: str,
    max_requests: int,
    window_seconds: int
) -> Tuple[bool, Dict[str, any]]:
    """
    Check if client has exceeded rate limit
    
    Returns:
        Tuple of (is_allowed, rate_limit_info)
    """
    async with _lock:
        now = datetime.utcnow()
        
        # Get or initialize client's rate limit data
        if limit_key not in _rate_limit_storage[client_id]:
            _rate_limit_storage[client_id][limit_key] = (1, now)
            return True, {
                "limit": max_requests,
                "remaining": max_requests - 1,
                "reset": (now + timedelta(seconds=window_seconds)).isoformat()
            }
        
        count, window_start = _rate_limit_storage[client_id][limit_key]
        
        # Check if window has expired
        if (now - window_start).total_seconds() > window_seconds:
            # Reset window
            _rate_limit_storage[client_id][limit_key] = (1, now)
            return True, {
                "limit": max_requests,
                "remaining": max_requests - 1,
                "reset": (now + timedelta(seconds=window_seconds)).isoformat()
            }
        
        # Check if limit exceeded
        if count >= max_requests:
            reset_time = window_start + timedelta(seconds=window_seconds)
            return False, {
                "limit": max_requests,
                "remaining": 0,
                "reset": reset_time.isoformat(),
                "retry_after": int((reset_time - now).total_seconds())
            }
        
        # Increment counter
        _rate_limit_storage[client_id][limit_key] = (count + 1, window_start)
        
        return True, {
            "limit": max_requests,
            "remaining": max_requests - count - 1,
            "reset": (window_start + timedelta(seconds=window_seconds)).isoformat()
        }


def rate_limit(limit_type: str = "default"):
    """
    Decorator to add rate limiting to endpoints
    
    Usage:
        @router.post("/upload")
        @rate_limit("upload_single")
        async def upload_file(request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            
            if not request:
                # No request found, skip rate limiting
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Get rate limit config
            max_requests, window_seconds = RATE_LIMITS.get(limit_type, RATE_LIMITS["default"])
            
            # Check rate limit
            client_id = get_client_id(request)
            is_allowed, limit_info = await check_rate_limit(
                client_id, limit_type, max_requests, window_seconds
            )
            
            # Add rate limit headers to response
            if hasattr(request.state, '_rate_limit_info'):
                request.state._rate_limit_info.update(limit_info)
            else:
                request.state._rate_limit_info = limit_info
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {limit_info.get('retry_after', 0)} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(limit_info['limit']),
                        "X-RateLimit-Remaining": str(limit_info['remaining']),
                        "X-RateLimit-Reset": limit_info['reset'],
                        "Retry-After": str(limit_info.get('retry_after', 60))
                    }
                )
            
            # Call the actual endpoint
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


async def add_rate_limit_headers(request: Request, response):
    """
    Middleware to add rate limit headers to all responses
    """
    if hasattr(request.state, '_rate_limit_info'):
        limit_info = request.state._rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(limit_info['limit'])
        response.headers["X-RateLimit-Remaining"] = str(limit_info['remaining'])
        response.headers["X-RateLimit-Reset"] = limit_info['reset']
    return response


def clear_expired_limits():
    """
    Cleanup function to remove expired rate limit entries
    Call this periodically (e.g., via background task)
    """
    now = datetime.utcnow()
    clients_to_remove = []
    
    for client_id, limits in _rate_limit_storage.items():
        keys_to_remove = []
        for limit_key, (count, window_start) in limits.items():
            limit_config = RATE_LIMITS.get(limit_key, RATE_LIMITS["default"])
            window_seconds = limit_config[1]
            if (now - window_start).total_seconds() > window_seconds * 2:
                keys_to_remove.append(limit_key)
        
        for key in keys_to_remove:
            del limits[key]
        
        if not limits:
            clients_to_remove.append(client_id)
    
    for client_id in clients_to_remove:
        del _rate_limit_storage[client_id]
