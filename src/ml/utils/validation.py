"""
Validation Utilities for ML Components
Provides robust input validation, sanitization, and error handling
for all ML/DL operations
"""

import re
import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(f"{field}: {message}" if field else message)


class DataType(Enum):
    """Supported data types for validation"""
    TEXT = "text"
    EMBEDDING = "embedding"
    SKILLS = "skills"
    RESUME = "resume"
    JOB = "job"
    SCORE = "score"


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    sanitized_value: Any
    warnings: List[str]
    errors: List[str]


class TextValidator:
    """Validates and sanitizes text inputs for ML processing"""
    
    # Maximum text lengths
    MAX_TEXT_LENGTH = 100_000  # 100KB of text
    MAX_SKILL_LENGTH = 100
    MAX_SKILL_COUNT = 500
    MIN_TEXT_LENGTH = 10
    
    # Patterns to clean
    CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
    EXCESSIVE_WHITESPACE = re.compile(r'\s{5,}')
    URL_PATTERN = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    @classmethod
    def validate_text(cls, text: Any, field_name: str = "text", 
                     min_length: int = 0, max_length: int = None,
                     allow_empty: bool = False) -> ValidationResult:
        """
        Validate and sanitize text input
        
        Args:
            text: Input text to validate
            field_name: Name of the field for error messages
            min_length: Minimum required length
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are acceptable
            
        Returns:
            ValidationResult with sanitized text
        """
        warnings = []
        errors = []
        
        # Handle None
        if text is None:
            if allow_empty:
                return ValidationResult(True, "", [], [])
            errors.append(f"{field_name} cannot be None")
            return ValidationResult(False, "", warnings, errors)
        
        # Convert to string
        if not isinstance(text, str):
            try:
                text = str(text)
                warnings.append(f"{field_name} was converted from {type(text).__name__} to str")
            except Exception as e:
                errors.append(f"{field_name} could not be converted to string: {e}")
                return ValidationResult(False, "", warnings, errors)
        
        # Remove control characters
        sanitized = cls.CONTROL_CHARS.sub('', text)
        if sanitized != text:
            warnings.append(f"{field_name} contained control characters (removed)")
        
        # Clean excessive whitespace
        sanitized = cls.EXCESSIVE_WHITESPACE.sub(' ', sanitized)
        
        # Trim
        sanitized = sanitized.strip()
        
        # Check empty
        if not sanitized and not allow_empty:
            errors.append(f"{field_name} cannot be empty")
            return ValidationResult(False, sanitized, warnings, errors)
        
        # Check length
        if max_length is None:
            max_length = cls.MAX_TEXT_LENGTH
            
        if len(sanitized) > max_length:
            warnings.append(f"{field_name} truncated from {len(sanitized)} to {max_length} characters")
            sanitized = sanitized[:max_length]
        
        if len(sanitized) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters (got {len(sanitized)})")
            return ValidationResult(False, sanitized, warnings, errors)
        
        return ValidationResult(True, sanitized, warnings, errors)
    
    @classmethod
    def validate_skill(cls, skill: Any, normalize: bool = True) -> ValidationResult:
        """Validate a single skill string"""
        result = cls.validate_text(skill, "skill", max_length=cls.MAX_SKILL_LENGTH, allow_empty=True)
        
        if not result.is_valid:
            return result
        
        sanitized = result.sanitized_value
        
        # Skip empty
        if not sanitized:
            return ValidationResult(True, "", result.warnings, result.errors)
        
        # Normalize if requested
        if normalize:
            sanitized = sanitized.lower().strip()
            
        # Remove non-printable characters but keep special chars common in skills
        sanitized = re.sub(r'[^\w\s\+\#\.\-\/\(\)]', '', sanitized)
        
        return ValidationResult(True, sanitized, result.warnings, result.errors)
    
    @classmethod
    def validate_skills_list(cls, skills: Any, normalize: bool = True) -> ValidationResult:
        """
        Validate and sanitize a list of skills
        
        Args:
            skills: List of skills (or dict with 'all_skills' key)
            normalize: Whether to normalize skills
            
        Returns:
            ValidationResult with cleaned skills list
        """
        warnings = []
        errors = []
        
        # Handle dict format (new format with 'all_skills')
        if isinstance(skills, dict):
            skills = skills.get('all_skills', skills.get('top_skills', []))
            warnings.append("Skills extracted from dict format")
        
        # Handle None or non-list
        if skills is None:
            return ValidationResult(True, [], [], [])
        
        if not isinstance(skills, (list, tuple, set)):
            try:
                skills = [str(skills)]
                warnings.append("Skills converted from single value to list")
            except:
                errors.append("Skills must be a list")
                return ValidationResult(False, [], warnings, errors)
        
        # Validate each skill
        sanitized_skills = []
        seen = set()
        
        for i, skill in enumerate(skills):
            if len(sanitized_skills) >= cls.MAX_SKILL_COUNT:
                warnings.append(f"Skills list truncated at {cls.MAX_SKILL_COUNT}")
                break
                
            result = cls.validate_skill(skill, normalize=normalize)
            
            if result.is_valid and result.sanitized_value:
                # Deduplicate
                skill_key = result.sanitized_value.lower()
                if skill_key not in seen:
                    seen.add(skill_key)
                    sanitized_skills.append(result.sanitized_value)
                else:
                    warnings.append(f"Duplicate skill removed: {result.sanitized_value}")
            
            warnings.extend(result.warnings)
        
        return ValidationResult(True, sanitized_skills, warnings, errors)


class EmbeddingValidator:
    """Validates embeddings and numerical arrays"""
    
    SUPPORTED_DIMS = [384, 768, 1024]  # Common embedding dimensions
    
    @classmethod
    def validate_embedding(cls, embedding: Any, 
                          expected_dim: int = None,
                          allow_none: bool = False) -> ValidationResult:
        """
        Validate an embedding vector
        
        Args:
            embedding: Numpy array or list of floats
            expected_dim: Expected dimension (if None, any supported dim is OK)
            allow_none: Whether None is acceptable
            
        Returns:
            ValidationResult with validated numpy array
        """
        warnings = []
        errors = []
        
        # Handle None
        if embedding is None:
            if allow_none:
                return ValidationResult(True, None, [], [])
            errors.append("Embedding cannot be None")
            return ValidationResult(False, None, warnings, errors)
        
        # Convert to numpy array if needed
        if not isinstance(embedding, np.ndarray):
            try:
                embedding = np.array(embedding, dtype=np.float32)
                warnings.append("Embedding converted to numpy array")
            except Exception as e:
                errors.append(f"Could not convert embedding to numpy array: {e}")
                return ValidationResult(False, None, warnings, errors)
        
        # Ensure float32 dtype
        if embedding.dtype != np.float32:
            embedding = embedding.astype(np.float32)
        
        # Flatten if needed
        if embedding.ndim > 1:
            if embedding.shape[0] == 1:
                embedding = embedding.flatten()
                warnings.append("Embedding reshaped from 2D to 1D")
            else:
                errors.append(f"Expected 1D embedding, got shape {embedding.shape}")
                return ValidationResult(False, embedding, warnings, errors)
        
        # Check dimension
        dim = embedding.shape[0]
        if expected_dim is not None and dim != expected_dim:
            errors.append(f"Expected embedding dimension {expected_dim}, got {dim}")
            return ValidationResult(False, embedding, warnings, errors)
        
        if expected_dim is None and dim not in cls.SUPPORTED_DIMS:
            warnings.append(f"Unusual embedding dimension: {dim} (expected one of {cls.SUPPORTED_DIMS})")
        
        # Check for NaN/Inf
        if np.any(np.isnan(embedding)):
            errors.append("Embedding contains NaN values")
            return ValidationResult(False, embedding, warnings, errors)
        
        if np.any(np.isinf(embedding)):
            errors.append("Embedding contains infinite values")
            return ValidationResult(False, embedding, warnings, errors)
        
        # Check for zero vector
        norm = np.linalg.norm(embedding)
        if norm < 1e-8:
            warnings.append("Embedding is a near-zero vector (may affect similarity calculations)")
        
        return ValidationResult(True, embedding, warnings, errors)
    
    @classmethod
    def validate_embedding_batch(cls, embeddings: Any,
                                 expected_dim: int = None,
                                 expected_count: int = None) -> ValidationResult:
        """Validate a batch of embeddings"""
        warnings = []
        errors = []
        
        if embeddings is None:
            errors.append("Embeddings batch cannot be None")
            return ValidationResult(False, None, warnings, errors)
        
        # Convert to numpy if needed
        if not isinstance(embeddings, np.ndarray):
            try:
                embeddings = np.array(embeddings, dtype=np.float32)
            except Exception as e:
                errors.append(f"Could not convert embeddings to numpy array: {e}")
                return ValidationResult(False, None, warnings, errors)
        
        # Ensure 2D
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
            warnings.append("Single embedding reshaped to batch of 1")
        elif embeddings.ndim != 2:
            errors.append(f"Expected 2D embeddings array, got shape {embeddings.shape}")
            return ValidationResult(False, embeddings, warnings, errors)
        
        n_samples, dim = embeddings.shape
        
        # Check dimension
        if expected_dim is not None and dim != expected_dim:
            errors.append(f"Expected embedding dimension {expected_dim}, got {dim}")
            return ValidationResult(False, embeddings, warnings, errors)
        
        # Check count
        if expected_count is not None and n_samples != expected_count:
            errors.append(f"Expected {expected_count} embeddings, got {n_samples}")
            return ValidationResult(False, embeddings, warnings, errors)
        
        # Check for NaN/Inf
        nan_count = np.sum(np.any(np.isnan(embeddings), axis=1))
        if nan_count > 0:
            errors.append(f"{nan_count}/{n_samples} embeddings contain NaN values")
            return ValidationResult(False, embeddings, warnings, errors)
        
        inf_count = np.sum(np.any(np.isinf(embeddings), axis=1))
        if inf_count > 0:
            errors.append(f"{inf_count}/{n_samples} embeddings contain infinite values")
            return ValidationResult(False, embeddings, warnings, errors)
        
        return ValidationResult(True, embeddings.astype(np.float32), warnings, errors)


class ScoreValidator:
    """Validates match scores and percentages"""
    
    @classmethod
    def validate_score(cls, score: Any, 
                      min_val: float = 0, 
                      max_val: float = 100,
                      field_name: str = "score") -> ValidationResult:
        """Validate a numeric score"""
        warnings = []
        errors = []
        
        if score is None:
            errors.append(f"{field_name} cannot be None")
            return ValidationResult(False, None, warnings, errors)
        
        # Convert to float
        try:
            score = float(score)
        except (TypeError, ValueError) as e:
            errors.append(f"{field_name} must be numeric: {e}")
            return ValidationResult(False, None, warnings, errors)
        
        # Check NaN/Inf
        if np.isnan(score):
            errors.append(f"{field_name} is NaN")
            return ValidationResult(False, None, warnings, errors)
        
        if np.isinf(score):
            errors.append(f"{field_name} is infinite")
            return ValidationResult(False, None, warnings, errors)
        
        # Clamp to range
        if score < min_val:
            warnings.append(f"{field_name} {score} clamped to minimum {min_val}")
            score = min_val
        elif score > max_val:
            warnings.append(f"{field_name} {score} clamped to maximum {max_val}")
            score = max_val
        
        return ValidationResult(True, round(score, 2), warnings, errors)
    
    @classmethod
    def validate_weights(cls, weights: Dict[str, float]) -> ValidationResult:
        """Validate that weights sum to 1.0"""
        warnings = []
        errors = []
        
        if not weights:
            errors.append("Weights dict cannot be empty")
            return ValidationResult(False, weights, warnings, errors)
        
        # Validate each weight
        validated = {}
        for key, value in weights.items():
            result = cls.validate_score(value, min_val=0, max_val=1, field_name=f"weight.{key}")
            if not result.is_valid:
                errors.extend(result.errors)
                return ValidationResult(False, weights, warnings, errors)
            validated[key] = result.sanitized_value
            warnings.extend(result.warnings)
        
        # Check sum
        total = sum(validated.values())
        if abs(total - 1.0) > 0.01:
            errors.append(f"Weights must sum to 1.0, got {total:.4f}")
            return ValidationResult(False, validated, warnings, errors)
        
        return ValidationResult(True, validated, warnings, errors)


class ResumeDataValidator:
    """Validates resume data structures"""
    
    REQUIRED_FIELDS = ['skills']
    RECOMMENDED_FIELDS = ['experience', 'education', 'personal_info', 'summary']
    
    @classmethod
    def validate(cls, resume_data: Any) -> ValidationResult:
        """
        Validate resume data structure
        
        Args:
            resume_data: Dict containing resume data
            
        Returns:
            ValidationResult with sanitized resume data
        """
        warnings = []
        errors = []
        
        if resume_data is None:
            errors.append("Resume data cannot be None")
            return ValidationResult(False, None, warnings, errors)
        
        if not isinstance(resume_data, dict):
            errors.append("Resume data must be a dictionary")
            return ValidationResult(False, None, warnings, errors)
        
        sanitized = dict(resume_data)
        
        # Validate skills
        skills_result = TextValidator.validate_skills_list(
            resume_data.get('skills', [])
        )
        sanitized['skills'] = skills_result.sanitized_value
        warnings.extend(skills_result.warnings)
        
        # Check recommended fields
        for field in cls.RECOMMENDED_FIELDS:
            if field not in resume_data or not resume_data[field]:
                warnings.append(f"Missing recommended field: {field}")
        
        # Validate experience entries
        if 'experience' in resume_data:
            validated_exp = []
            for i, exp in enumerate(resume_data.get('experience', [])):
                if isinstance(exp, dict):
                    validated_exp.append(exp)
                else:
                    warnings.append(f"Experience entry {i} is not a dict, skipping")
            sanitized['experience'] = validated_exp
        
        # Validate education entries
        if 'education' in resume_data:
            validated_edu = []
            for i, edu in enumerate(resume_data.get('education', [])):
                if isinstance(edu, dict):
                    validated_edu.append(edu)
                else:
                    warnings.append(f"Education entry {i} is not a dict, skipping")
            sanitized['education'] = validated_edu
        
        return ValidationResult(True, sanitized, warnings, errors)


class JobDataValidator:
    """Validates job description data structures"""
    
    @classmethod
    def validate(cls, job_data: Any) -> ValidationResult:
        """
        Validate job data structure
        
        Args:
            job_data: Dict containing job requirements
            
        Returns:
            ValidationResult with sanitized job data
        """
        warnings = []
        errors = []
        
        if job_data is None:
            errors.append("Job data cannot be None")
            return ValidationResult(False, None, warnings, errors)
        
        if not isinstance(job_data, dict):
            errors.append("Job data must be a dictionary")
            return ValidationResult(False, None, warnings, errors)
        
        sanitized = dict(job_data)
        
        # Validate required skills
        req_result = TextValidator.validate_skills_list(
            job_data.get('required_skills', [])
        )
        sanitized['required_skills'] = req_result.sanitized_value
        warnings.extend(req_result.warnings)
        
        # Validate optional skills
        opt_result = TextValidator.validate_skills_list(
            job_data.get('optional_skills', [])
        )
        sanitized['optional_skills'] = opt_result.sanitized_value
        warnings.extend(opt_result.warnings)
        
        # Validate experience requirements
        if 'experience_years' in job_data:
            try:
                years = int(job_data['experience_years'])
                if years < 0:
                    warnings.append("Negative experience years set to 0")
                    years = 0
                elif years > 50:
                    warnings.append(f"Experience years {years} seems unusually high")
                sanitized['experience_years'] = years
            except (TypeError, ValueError):
                warnings.append("Could not parse experience_years, setting to None")
                sanitized['experience_years'] = None
        
        return ValidationResult(True, sanitized, warnings, errors)


def validate_and_log(validator_result: ValidationResult, 
                    context: str = "",
                    raise_on_error: bool = False) -> ValidationResult:
    """
    Log validation results and optionally raise on errors
    
    Args:
        validator_result: Result from a validation method
        context: Additional context for logging
        raise_on_error: Whether to raise exception on validation errors
        
    Returns:
        The same ValidationResult
    """
    if validator_result.warnings:
        for warning in validator_result.warnings:
            logger.warning(f"[{context}] {warning}")
    
    if validator_result.errors:
        for error in validator_result.errors:
            logger.error(f"[{context}] {error}")
        
        if raise_on_error:
            raise ValidationError(
                message="; ".join(validator_result.errors),
                field=context
            )
    
    return validator_result
