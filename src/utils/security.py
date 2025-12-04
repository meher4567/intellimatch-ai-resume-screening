"""
Security utilities for input validation and sanitization
"""
import re
from typing import Optional

def sanitize_sql_input(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent SQL injection
    Note: SQLAlchemy ORM already handles this, but useful for raw queries
    """
    if not value:
        return ""
    
    # Remove SQL keywords and special characters
    dangerous_patterns = [
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=|\bAND\b.*=)",
    ]
    
    cleaned = value
    for pattern in dangerous_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    # Trim to max length
    return cleaned[:max_length].strip()


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags and dangerous characters from text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove javascript: and data: URIs
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
    
    # Remove event handlers
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_search_query(query: str, max_length: int = 200) -> str:
    """
    Sanitize search query to prevent injection attacks
    """
    if not query:
        return ""
    
    # Remove special regex characters that could cause ReDoS
    query = re.sub(r'[(){}[\]\\^$*+?.|]', '', query)
    
    # Remove SQL special characters
    query = re.sub(r'[;\'"`]', '', query)
    
    # Trim and limit length
    return query[:max_length].strip()


def validate_json_field(data: dict, required_keys: list) -> tuple[bool, Optional[str]]:
    """
    Validate JSON field has required keys
    Returns (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    return True, None


def sanitize_url(url: str) -> Optional[str]:
    """
    Validate and sanitize URL
    """
    if not url:
        return None
    
    # Only allow http and https
    if not url.startswith(('http://', 'https://')):
        return None
    
    # Remove dangerous characters
    url = re.sub(r'[<>"\']', '', url)
    
    return url if len(url) < 2048 else None


def validate_positive_int(value: any, min_val: int = 0, max_val: int = 1000000) -> tuple[bool, int]:
    """
    Validate and convert to positive integer
    Returns (is_valid, value)
    """
    try:
        num = int(value)
        if min_val <= num <= max_val:
            return True, num
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validate_float_range(value: any, min_val: float = 0.0, max_val: float = 100.0) -> tuple[bool, float]:
    """
    Validate float is within range
    Returns (is_valid, value)
    """
    try:
        num = float(value)
        if min_val <= num <= max_val:
            return True, num
        return False, 0.0
    except (ValueError, TypeError):
        return False, 0.0
