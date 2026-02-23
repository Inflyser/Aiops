from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Todo Startup"
    
    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "todo"
    POSTGRES_PASSWORD: str = "todo123"
    POSTGRES_DB: str = "tododb"
    # Используем DATABASE_URL если установлена, иначе собираем из компонентов
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('POSTGRES_USER', 'todo')}:{os.getenv('POSTGRES_PASSWORD', 'todo123')}@{os.getenv('POSTGRES_SERVER', 'postgres')}:5432/{os.getenv('POSTGRES_DB', 'tododb')}"
    )
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://localhost:3000",
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
