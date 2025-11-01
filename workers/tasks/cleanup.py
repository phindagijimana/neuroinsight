"""
Scheduled cleanup tasks for storage management.

This module contains Celery tasks for automatic cleanup of old jobs
and orphaned files based on retention policies.
"""

from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.services import CleanupService
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="workers.tasks.cleanup.run_cleanup")
def run_cleanup():
    """
    Scheduled cleanup task - runs retention policy cleanup.
    
    This task:
    - Deletes old completed jobs (based on retention_completed_days)
    - Deletes old failed jobs (based on retention_failed_days)
    - Removes orphaned files with no database records
    
    Should be scheduled to run periodically (e.g., daily).
    """
    from backend.core.config import get_settings
    
    settings = get_settings()
    
    if not settings.cleanup_enabled:
        logger.info("cleanup_disabled", note="Cleanup is disabled in configuration")
        return
    
    db = SessionLocal()
    cleanup_service = CleanupService()
    
    try:
        logger.info("cleanup_started")
        
        # Clean up old completed jobs
        completed_jobs, completed_uploads, completed_outputs = cleanup_service.cleanup_old_completed_jobs(
            db=db,
            days_old=settings.retention_completed_days,
            dry_run=False
        )
        
        # Clean up old failed jobs
        failed_jobs, failed_uploads, failed_outputs = cleanup_service.cleanup_failed_jobs(
            db=db,
            days_old=settings.retention_failed_days,
            dry_run=False
        )
        
        # Clean up orphaned files
        orphaned_uploads, orphaned_outputs = cleanup_service.cleanup_orphaned_files(
            db=db,
            dry_run=False
        )
        
        # Get final storage stats
        stats = cleanup_service.get_storage_stats()
        
        logger.info(
            "cleanup_completed",
            completed_jobs_deleted=completed_jobs,
            failed_jobs_deleted=failed_jobs,
            orphaned_uploads_deleted=orphaned_uploads,
            orphaned_outputs_deleted=orphaned_outputs,
            total_storage_mb=stats["total_size_mb"],
        )
        
        return {
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "orphaned_uploads": orphaned_uploads,
            "orphaned_outputs": orphaned_outputs,
            "storage_stats": stats,
        }
    
    except Exception as e:
        logger.error("cleanup_failed", error=str(e), exc_info=True)
        raise
    
    finally:
        db.close()




