import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/intellimatch"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "supersecret"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
