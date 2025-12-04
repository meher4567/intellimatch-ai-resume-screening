"""
Simplified Authentication API endpoints
Basic login and register only
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.core.dependencies import get_db
from src.core.auth import verify_password, get_password_hash, create_access_token
from src.core.auth_dependencies import get_current_active_user
from src.models.user import User
from src.schemas.auth import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    Creates a new user with the specified role and generates credentials.
    
    **Password Requirements:**
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 digit
    
    **Available Roles:**
    - `candidate`: Job seekers (default)
    - `recruiter`: Can view and match candidates
    - `admin`: Full system access
    
    **Example Request:**
    ```json
    {
        "email": "john@example.com",
        "password": "SecurePass123",
        "full_name": "John Doe",
        "role": "candidate"
    }
    ```
    
    **Response:** User details (without password)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(request: Request, user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and receive JWT access token
    
    Use this endpoint to log in and receive an access token for protected endpoints.
    
    **Example Request:**
    ```json
    {
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    ```
    
    **Response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
    
    **Using the token:**
    ```
    curl -H "Authorization: Bearer YOUR_TOKEN" \\
         http://localhost:8000/api/v1/auth/me
    ```
    
    **Token expires in:** 30 minutes
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_login.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's profile
    
    Requires: Valid access token
    """
    return current_user
