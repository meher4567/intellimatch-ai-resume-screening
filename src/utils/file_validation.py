"""
File upload validation utilities
"""
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    
from fastapi import HTTPException, UploadFile, status
import logging

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/msword',  # .doc
]
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx']


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file for security and compatibility
    
    Args:
        file: Uploaded file from FastAPI
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate filename exists
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    # Sanitize filename
    filename = file.filename.lower()
    
    # Check file extension
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (read first to get size)
    try:
        contents = file.file.read()
        file_size = len(contents)
        file.file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
            
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error reading uploaded file"
        )
    
    logger.info(f"File validation passed: {filename} ({file_size / 1024:.1f}KB)")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import os
    import re
    
    # Remove directory paths
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except dots, hyphens, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:200] + ext
    
    return filename


def validate_file_content(file_content: bytes, expected_type: str = 'pdf') -> bool:
    """
    Validate file content matches expected type using magic numbers
    
    Args:
        file_content: File bytes
        expected_type: Expected file type ('pdf', 'doc', 'docx')
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check magic number (first few bytes)
        if expected_type == 'pdf' and file_content[:4] == b'%PDF':
            return True
        elif expected_type == 'docx' and file_content[:2] == b'PK':  # ZIP format
            return True
        elif expected_type == 'doc' and file_content[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
            return True
    except:
        pass
    
    return False
