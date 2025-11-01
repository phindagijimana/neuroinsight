"""Celery task definitions."""

from .processing import process_mri_task

__all__ = ["process_mri_task"]

