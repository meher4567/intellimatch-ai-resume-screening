import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "IntelliMatch AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/intellimatch"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "data/uploads"
    
    # ML Models
    ML_MODEL_NAME: str = "mini"
    ML_STORAGE_PATH: str = "data/production"
    EMBEDDINGS_DIR: str = "data/embeddings"
    
    # Redis (Optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security (Optional)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
