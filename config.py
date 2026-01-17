from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    APP_NAME: str = "DPDP Compliance Demo"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    RELOAD: bool = False
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    
    # DPDP
    DPO_EMAIL: str
    DPO_NAME: str = "Data Protection Officer"
    ORGANIZATION_NAME: str = "DPDP Demo Organization"
    
    # SIEM
    SIEM_WEBHOOK_URL: Optional[str] = None
    SIEM_API_KEY: Optional[str] = None
    
    # Data Retention
    RETENTION_ACTIVE_USER: int = 365
    RETENTION_CONSENT: int = 1095
    RETENTION_GRIEVANCE: int = 1825
    
    # Security
    BCRYPT_ROUNDS: int = 12
    SESSION_LIFETIME_HOURS: int = 24
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()


# Database configuration
def get_database_url() -> str:
    """Get database URL with proper formatting"""
    return settings.DATABASE_URL.replace('postgres://', 'postgresql://')


# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)