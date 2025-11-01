"""
MRI processing task definitions.

This module contains Celery tasks for orchestrating the
MRI processing pipeline.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.services import JobService, MetricService, StorageService
from pipeline.processors import MRIProcessor
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="workers.tasks.processing.process_mri_task",
    bind=True,
    max_retries=5,
    default_retry_delay=2,  # seconds; per-call retry can override countdown
)
def process_mri_task(self, job_id: str):
    """
    Process MRI scan through the analysis pipeline.
    
    This task orchestrates the complete processing workflow:
    1. Convert DICOM to NIfTI (if needed)
    2. Run FastSurfer segmentation
    3. Extract hippocampal subfields
    4. Calculate asymmetry indices
    5. Store results in database
    
    Args:
        self: Task instance (bound task)
        job_id: Job identifier (UUID as string)
    
    Returns:
        Dictionary with processing results
    """
    db: Session = SessionLocal()
    
    try:
        logger.info("task_started", job_id=job_id, task_id=self.request.id)
        
        # Parse job ID
        job_uuid = UUID(job_id)
        
        # Check if job exists and is not cancelled
        job = JobService.get_job(db, job_uuid)
        if not job:
            logger.error("job_not_found", job_id=job_id)
            raise ValueError(f"Job {job_id} not found")
        
        # Check if job was cancelled
        from backend.models.job import JobStatus
        if job.status == JobStatus.CANCELLED:
            logger.info("job_cancelled_aborting", job_id=job_id)
            return {
                "status": "cancelled",
                "job_id": job_id,
                "message": "Job was cancelled before processing started"
            }
        
        # Mark job as started
        job = JobService.start_job(db, job_uuid)
        if not job:
            logger.error("job_not_found_after_check", job_id=job_id)
            raise ValueError(f"Job {job_id} not found")
        
        # Get file path from storage (with Celery auto-retry on transient S3 delays)
        storage_service = StorageService()
        try:
            file_path = storage_service.get_file_path(job.file_path)
        except Exception as e:
            logger.warning(
                "file_fetch_retry",
                job_id=job_id,
                error=str(e),
                note="Retrying shortly due to transient storage read error",
            )
            # Requeue the task briefly to allow object propagation
            raise self.retry(exc=e, countdown=2, max_retries=5)
        
        logger.info("processing_started", job_id=job_id, file_path=file_path)
        
        # Initialize processor
        processor = MRIProcessor(job_uuid)
        
        # Run processing pipeline
        try:
            # Periodic check for cancellation during long-running operations
            # This allows graceful cancellation even during FastSurfer execution
            def check_cancellation():
                """Check if job was cancelled during processing."""
                db_check = SessionLocal()
                try:
                    current_job = JobService.get_job(db_check, job_uuid)
                    if current_job and current_job.status == JobStatus.CANCELLED:
                        logger.info("job_cancelled_during_processing", job_id=job_id)
                        return True
                    return False
                finally:
                    db_check.close()
            
            # Note: FastSurfer doesn't support cancellation mid-execution,
            # but we check before and after the processing step
            if check_cancellation():
                logger.info("processing_aborted_cancelled", job_id=job_id)
                return {
                    "status": "cancelled",
                    "job_id": job_id,
                    "message": "Job was cancelled during processing"
                }
            
            results = processor.process(file_path)
            
            # Check again after processing completes
            if check_cancellation():
                logger.info("processing_completed_but_cancelled", job_id=job_id)
                # Don't save results if job was cancelled
                return {
                    "status": "cancelled",
                    "job_id": job_id,
                    "message": "Job was cancelled after processing completed"
                }
            
            logger.info(
                "processing_completed",
                job_id=job_id,
                metrics_count=len(results["metrics"]),
            )
            
            # Store metrics in database
            from backend.schemas import MetricCreate
            
            metrics_data = [
                MetricCreate(
                    job_id=job_uuid,
                    region=metric["region"],
                    left_volume=metric["left_volume"],
                    right_volume=metric["right_volume"],
                    asymmetry_index=metric["asymmetry_index"],
                )
                for metric in results["metrics"]
            ]
            
            MetricService.create_metrics_bulk(db, metrics_data)
            
            # Mark job as completed
            JobService.complete_job(db, job_uuid, results["output_dir"])
            
            logger.info("task_completed", job_id=job_id)
            
            return {
                "status": "completed",
                "job_id": job_id,
                "metrics_count": len(results["metrics"]),
                "output_dir": results["output_dir"],
            }
        
        except Exception as e:
            # Mark job as failed
            error_message = f"Processing failed: {str(e)}"
            JobService.fail_job(db, job_uuid, error_message)
            
            logger.error(
                "processing_failed",
                job_id=job_id,
                error=error_message,
                exc_info=True,
            )
            
            # Retry task if not at max retries
            if self.request.retries < self.max_retries:
                logger.info(
                    "task_retrying",
                    job_id=job_id,
                    retry=self.request.retries + 1,
                )
                raise self.retry(exc=e)
            
            raise
    
    finally:
        db.close()

