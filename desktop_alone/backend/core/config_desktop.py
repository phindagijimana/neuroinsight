"""
Desktop-specific configuration for NeuroInsight standalone application.

This configuration is used when running in desktop mode (no Docker, no external services).
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
import platformdirs


class DesktopSettings(BaseSettings):
    """Settings for standalone desktop application"""
    
    # Mode detection
    desktop_mode: bool = Field(default=True, env="DESKTOP_MODE")
    
    # Application info
    app_name: str = "NeuroInsight"
    app_version: str = "1.0.0"
    environment: str = "desktop"
    
    # Database - SQLite for desktop
    @property
    def database_url(self) -> str:
        """Use SQLite in user data directory"""
        data_dir = Path(platformdirs.user_data_dir(self.app_name, "NeuroInsight"))
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "neuroinsight.db"
        return f"sqlite:///{db_path}"
    
    # Storage directories
    @property
    def user_data_dir(self) -> Path:
        """User data directory for database and config"""
        return Path(platformdirs.user_data_dir(self.app_name, "NeuroInsight"))
    
    @property
    def upload_dir(self) -> Path:
        """Upload directory in user documents"""
        docs = Path(platformdirs.user_documents_dir())
        upload_dir = docs / self.app_name / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    @property
    def output_dir(self) -> Path:
        """Output directory in user documents"""
        docs = Path(platformdirs.user_documents_dir())
        output_dir = docs / self.app_name / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    # Task processing - No Celery in desktop mode
    use_celery: bool = False
    task_mode: str = "threading"
    max_concurrent_jobs: int = 1  # Desktop: one job at a time
    
    # Server settings
    host: str = Field(default="127.0.0.1", env="HOST")  # Desktop: localhost only
    port: int = Field(default=8000, env="PORT")

    # API Configuration (aliases for compatibility)
    api_host: str = Field(default="127.0.0.1", env="API_HOST")  # Desktop: localhost only
    api_port: int = Field(default=8000, env="API_PORT")
    
    # CORS - Desktop mode allows localhost
    cors_origins: str = Field(default="http://localhost:8000,http://127.0.0.1:8000", env="CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(self.cors_origins, str):
            # Handle wildcard - if set to "*", return ["*"] for FastAPI
            if self.cors_origins.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins if isinstance(self.cors_origins, list) else []

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Processing
    enable_gpu: bool = Field(default=True, env="ENABLE_GPU")  # Auto-detect GPU
    processing_timeout: int = Field(default=10800, env="PROCESSING_TIMEOUT")  # 3 hours for desktop
    
    # Cleanup - Desktop mode uses less aggressive cleanup
    cleanup_enabled: bool = Field(default=True, env="CLEANUP_ENABLED")
    retention_completed_days: int = Field(default=90, env="RETENTION_COMPLETED_DAYS")  # Keep longer
    retention_failed_days: int = Field(default=30, env="RETENTION_FAILED_DAYS")
    
    class Config:
        env_prefix = "NEUROINSIGHT_"
        case_sensitive = False


# Singleton instance
_settings: Optional[DesktopSettings] = None


def get_desktop_settings() -> DesktopSettings:
    """Get desktop settings singleton"""
    global _settings
    if _settings is None:
        _settings = DesktopSettings()
    return _settings

