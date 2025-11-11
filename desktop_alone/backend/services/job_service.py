"""
Job service for managing MRI processing jobs.

This service provides business logic for creating, retrieving,
and updating jobs in the system.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from datetime import datetime

from backend.core.logging import get_logger
from backend.models import Job, Metric
from backend.models.job import JobStatus
from backend.schemas import JobCreate, JobUpdate

logger = get_logger(__name__)


class JobService:
    """
    Service class for job-related operations.
    
    Handles CRUD operations and business logic for MRI processing jobs.
    """
    
    @staticmethod
    def create_job(db: Session, job_data: JobCreate) -> Job:
        """
        Create a new processing job.
        
        Args:
            db: Database session
            job_data: Job creation data
        
        Returns:
            Created job instance
        """
        job = Job(
            filename=job_data.filename,
            file_path=job_data.file_path,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(
            "job_created",
            job_id=str(job.id),
            filename=job.filename,
            status=job.status.value,
        )
        
        return job
    
    @staticmethod
    def get_job(db: Session, job_id) -> Optional[Job]:
        """
        Retrieve a job by ID.
        
        Args:
            db: Database session
            job_id: Job identifier (UUID or string - will be converted to string for SQLite)
        
        Returns:
            Job instance if found, None otherwise
        """
        # Convert to string for SQLite compatibility (VARCHAR(36) with dashes)
        job_id_str = str(job_id)
        return db.query(Job).filter(Job.id == job_id_str).first()
    
    @staticmethod
    def get_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[JobStatus] = None
    ) -> List[Job]:
        """
        Retrieve multiple jobs with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status: Filter by job status (optional)
        
        Returns:
            List of job instances
        """
        query = db.query(Job)
        
        if status:
            query = query.filter(Job.status == status)
        
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_job(db: Session, job_id, job_update: JobUpdate) -> Optional[Job]:
        """
        Update an existing job.
        
        Args:
            db: Database session
            job_id: Job identifier (UUID or string - will be converted to string for SQLite)
            job_update: Updated job data
        
        Returns:
            Updated job instance if found, None otherwise
        """
        # Convert to string for SQLite compatibility
        job_id_str = str(job_id)
        job = db.query(Job).filter(Job.id == job_id_str).first()
        
        if not job:
            logger.warning("job_not_found", job_id=str(job_id))
            return None
        
        # Update fields if provided
        update_data = job_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        
        db.commit()
        db.refresh(job)
        
        logger.info(
            "job_updated",
            job_id=str(job.id),
            updates=list(update_data.keys()),
            status=job.status.value,
        )
        
        return job
    
    @staticmethod
    def delete_job(db: Session, job_id) -> bool:
        """
        Delete a job and its associated metrics and files.
        
        For RUNNING or PENDING jobs, this will:
        1. Cancel/revoke the Celery task
        2. Terminate FastSurfer processes (if running)
        3. Mark job as CANCELLED (if active)
        4. Delete files after a brief delay
        
        For COMPLETED or FAILED jobs, this will:
        1. Immediately delete files and database records
        
        Args:
            db: Database session
            job_id: Job identifier (UUID or string - will be converted to string for SQLite)
        
        Returns:
            True if deleted, False if not found
        """
        # Convert to string for SQLite compatibility
        job_id_str = str(job_id)
        job = db.query(Job).filter(Job.id == job_id_str).first()
        
        if not job:
            logger.warning("job_not_found", job_id=str(job_id))
            return False
        
        job_status = job.status
        is_active = job.is_active
        
        # Handle active jobs (PENDING or RUNNING)
        if is_active:
            logger.info("cancelling_active_job", job_id=str(job_id), status=job_status.value)
            
            # Cancel Celery task and terminate FastSurfer
            try:
                from backend.services import TaskManagementService
                TaskManagementService.cancel_job_task(job_id, job_status.value)
            except Exception as e:
                logger.warning("task_cancellation_failed", job_id=str(job_id), error=str(e))
                # Continue with deletion even if cancellation fails
            
            # Mark job as CANCELLED instead of deleting immediately
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            job.error_message = "Job cancelled by user"
            db.commit()
            
            # Wait a moment for processes to terminate gracefully
            import time
            time.sleep(2)
            
            logger.info("job_marked_cancelled", job_id=str(job_id))
        
        # Delete associated metrics (use string format for SQLite)
        db.query(Metric).filter(Metric.job_id == job_id_str).delete()
        
        # Delete associated files (upload and output directory)
        try:
            from backend.services import CleanupService
            cleanup_service = CleanupService()
            cleanup_service.delete_job_files(job)
        except Exception as e:
            logger.warning("file_cleanup_failed_during_job_delete", job_id=str(job_id), error=str(e))
            # Continue with database deletion even if file deletion fails
        
        # Delete job record
        db.delete(job)
        db.commit()
        
        logger.info(
            "job_deleted_with_files",
            job_id=str(job_id),
            previous_status=job_status.value,
            was_active=is_active
        )
        
        return True
    
    @staticmethod
    def start_job(db: Session, job_id) -> Optional[Job]:
        """
        Mark a job as started.
        
        Args:
            db: Database session
            job_id: Job identifier (UUID or string - will be converted to string for SQLite)
        
        Returns:
            Updated job instance if found, None otherwise
        """
        # Convert to string for SQLite compatibility
        job_id_str = str(job_id)
        job = db.query(Job).filter(Job.id == job_id_str).first()
        
        if not job:
            return None
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        
        logger.info("job_started", job_id=str(job.id))
        
        return job
    
    @staticmethod
    def complete_job(
        db: Session,
        job_id,
        result_path: str
    ) -> Optional[Job]:
        """
        Mark a job as completed.
        
        Args:
            db: Database session
            job_id: Job identifier (UUID or string - will be converted to string for SQLite)
            result_path: Path to processing results
        
        Returns:
            Updated job instance if found, None otherwise
        """
        # Convert to string for SQLite compatibility
        job_id_str = str(job_id)
        job = db.query(Job).filter(Job.id == job_id_str).first()
        
        if not job:
            return None
        
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result_path = result_path
        
        db.commit()
        db.refresh(job)
        
        logger.info(
            "job_completed",
            job_id=str(job.id),
            duration_seconds=job.duration_seconds,
        )
        
        return job
    
    @staticmethod
    def fail_job(db: Session, job_id, error_message: str) -> Optional[Job]:
        """
        Mark a job as failed.
        
        Args:
            db: Database session
            job_id: Job identifier (UUID or string - will be converted to string for SQLite)
            error_message: Error description
        
        Returns:
            Updated job instance if found, None otherwise
        """
        # Convert to string for SQLite compatibility
        job_id_str = str(job_id)
        job = db.query(Job).filter(Job.id == job_id_str).first()
        
        if not job:
            return None
        
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.error_message = error_message
        
        db.commit()
        db.refresh(job)
        
        logger.error(
            "job_failed",
            job_id=str(job.id),
            error=error_message,
        )
        
        return job

