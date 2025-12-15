"""
Configuration settings for FastAPI application
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import os


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # Application
    APP_NAME: str = "RFID Attendance System"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, validation_alias='APP_DEBUG')
    
    # Security
    SECRET_KEY: str = Field(..., validation_alias='APP_KEY')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://karty:karty@localhost/karty",
        validation_alias='DATABASE_URL'
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # Email
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USERNAME: Optional[str] = Field(default=None, validation_alias='APP_MAIL_USERNAME')
    MAIL_PASSWORD: Optional[str] = Field(default=None, validation_alias='APP_MAIL_PASSWORD')
    MAIL_FROM: Optional[str] = Field(default=None, validation_alias='APP_MAIL_INFO_ACCOUNT')
    
    # MQTT
    MQTT_BROKER: str = Field(default="192.168.1.110", validation_alias='MQTT_BROKER')
    MQTT_PORT: int = Field(default=1883, validation_alias='MQTT_PORT')
    MQTT_KEEPALIVE: int = 60
    
    # File uploads
    UPLOAD_FOLDER: str = "uploads/"
    ALLOWED_EXTENSIONS: List[str] = ["xml"]
    
    # Bcrypt
    BCRYPT_LOG_ROUNDS: int = 12


# Create settings instance
settings = Settings()
