"""
Core configuration module for NeuroInsight application.

This module handles all application settings using Pydantic Settings,
enabling type-safe configuration from environment variables.

Supports both server mode (PostgreSQL, Celery) and desktop mode (SQLite, threading).
"""

import os
from functools import lru_cache
from typing import List

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables.
    See .env.example for a complete list of configuration options.
    """
    
    # Mode Detection
    desktop_mode: bool = Field(default=False, env="DESKTOP_MODE")
    
    # Application Metadata
    app_name: str = "NeuroInsight Dev"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://localhost:56052,http://127.0.0.1:56052",
        env="CORS_ORIGINS"
    )
    
    # Database Configuration
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="neuroinsight", env="POSTGRES_USER")
    postgres_password: str = Field(default="dev_password", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="neuroinsight", env="POSTGRES_DB")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # MinIO/S3 Configuration
    minio_endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="neuroinsight-data", env="MINIO_BUCKET")
    minio_use_ssl: bool = Field(default=False, env="MINIO_USE_SSL")
    
    # File Storage - Desktop mode uses user directories
    upload_dir: str = Field(default="", env="UPLOAD_DIR")
    output_dir: str = Field(default="", env="OUTPUT_DIR")

    def __init__(self, **data):
        super().__init__(**data)
        # Set desktop directories if not explicitly provided and in desktop mode
        if self.desktop_mode and not self.upload_dir:
            from backend.core.config_desktop import get_desktop_settings
            desktop_settings = get_desktop_settings()
            self.upload_dir = str(desktop_settings.upload_dir)
        if self.desktop_mode and not self.output_dir:
            from backend.core.config_desktop import get_desktop_settings
            desktop_settings = get_desktop_settings()
            self.output_dir = str(desktop_settings.output_dir)

        # Set defaults for server mode
        if not self.desktop_mode and not self.upload_dir:
            self.upload_dir = "/data/uploads"
        if not self.desktop_mode and not self.output_dir:
            self.output_dir = "/data/outputs"
    
    max_upload_size: int = Field(default=524288000, env="MAX_UPLOAD_SIZE")  # 500MB
    
    # Cleanup & Retention Policies
    cleanup_enabled: bool = Field(default=True, env="CLEANUP_ENABLED")
    cleanup_interval_hours: int = Field(default=24, env="CLEANUP_INTERVAL_HOURS")  # Run daily
    retention_completed_days: int = Field(default=30, env="RETENTION_COMPLETED_DAYS")  # Keep completed jobs 30 days
    retention_failed_days: int = Field(default=7, env="RETENTION_FAILED_DAYS")  # Keep failed jobs 7 days
    
    # Processing Configuration (SegmentHA removed; FastSurfer-only)
    fastsurfer_container: str = Field(
        default="fastsurfer/fastsurfer:latest",
        env="FASTSURFER_CONTAINER"
    )
    processing_timeout: int = Field(default=36000, env="PROCESSING_TIMEOUT")  # 10 hours
    max_concurrent_jobs: int = Field(default=2, env="MAX_CONCURRENT_JOBS")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-me", env="SECRET_KEY")
    api_key_enabled: bool = Field(default=False, env="API_KEY_ENABLED")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(self.cors_origins, str):
            # Handle wildcard - if set to "*", return ["*"] for FastAPI
            if self.cors_origins.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins if isinstance(self.cors_origins, list) else []
    
    @property
    def database_url(self) -> str:
        """Construct database URL - SQLite for desktop, PostgreSQL for server."""
        if self.desktop_mode:
            # Desktop mode: Use SQLite in user data directory
            from backend.core.config_desktop import get_desktop_settings
            desktop_settings = get_desktop_settings()
            return desktop_settings.database_url
        else:
            # Server mode: Use PostgreSQL
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
    
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def celery_broker_url(self) -> str:
        """Construct Celery broker URL."""
        return self.redis_url
    
    @property
    def celery_result_backend(self) -> str:
        """Construct Celery result backend URL."""
        return self.redis_url
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are loaded once and reused.
    This is particularly useful for dependency injection in FastAPI.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()

