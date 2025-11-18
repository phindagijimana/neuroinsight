"""Core configuration and utilities for NeuroInsight application."""

# Use desktop-specific configuration
from .config_desktop import DesktopSettings as Settings, get_desktop_settings as get_settings
from .database import Base, get_db, init_db
from .logging import setup_logging

__all__ = ["Settings", "get_settings", "Base", "get_db", "init_db", "setup_logging"]

