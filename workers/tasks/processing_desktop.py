"""
MRI processing task for desktop mode.

This module contains direct execution functions for the MRI processing pipeline
in desktop mode (no Celery).
"""

from uuid import UUID

from sqlalchemy import update
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.models.job import Job
from backend.services import JobService, MetricService, StorageService
from pipeline.processors import MRIProcessor

logger = get_logger(__name__)


def update_job_progress(db: Session, job_id: UUID, progress: int, current_step: str):
    """
    Update job progress and current step description.

    Args:
        db: Database session
        job_id: Job identifier
        progress: Progress percentage (0-100)
        current_step: Description of current processing step
    """
    try:
        db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(progress=progress, current_step=current_step)
        )
        db.commit()
        logger.info("progress_updated", job_id=str(job_id), progress=progress, step=current_step)
    except Exception as e:
        logger.warning("progress_update_failed", job_id=str(job_id), error=str(e))
        db.rollback()


def process_mri_direct(job_id: str):
    """
    Process MRI scan directly through the analysis pipeline (desktop mode).

    This function orchestrates the complete processing workflow:
    1. Convert DICOM to NIfTI (if needed)
    2. Run FastSurfer segmentation
    3. Extract hippocampal subfields
    4. Calculate asymmetry indices
    5. Store results in database

    Args:
        job_id: Job identifier (UUID as string)

    Returns:
        Dictionary with processing results
    """
    logger.info("DESKTOP_PROCESSING_STARTED", job_id=job_id, function="process_mri_direct")
    db: Session = SessionLocal()
    logger.info("Database session created", job_id=job_id)

    try:
        logger.info("desktop_processing_started", job_id=job_id)

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

        # Update progress: Job started
        update_job_progress(db, job_uuid, 5, "Job started - preparing file...")

        # Get file path from storage
        storage_service = StorageService()
        file_path = storage_service.get_file_path(job.file_path)

        logger.info("processing_started", job_id=job_id, file_path=file_path)

        # Update progress: File retrieved
        update_job_progress(db, job_uuid, 10, "File retrieved - initializing processor...")

        # Define progress callback for detailed tracking inside processor
        def progress_callback(progress: int, step: str):
            """Callback for processor to update job progress."""
            update_job_progress(db, job_uuid, progress, step)

        # Initialize processor with progress callback
        processor = MRIProcessor(job_uuid, progress_callback=progress_callback)

        # Update progress: Starting brain segmentation
        update_job_progress(db, job_uuid, 15, "Starting brain segmentation (FastSurfer)...")

        # Run processing pipeline
        try:
            # Periodic check for cancellation during long-running operations
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

            # Check cancellation before starting
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

            # Update progress: Processing complete, saving results
            update_job_progress(db, job_uuid, 85, "Processing complete - saving metrics...")

            logger.info(
                "processing_completed",
                job_id=job_id,
                metrics_count=len(results["metrics"]),
            )

            # Store metrics in database
            from backend.schemas import MetricCreate
            from backend.models.metric import Metric

            # Delete existing metrics for this job (in case of reprocessing)
            existing_metrics_count = db.query(Metric).filter(Metric.job_id == job_uuid).count()
            if existing_metrics_count > 0:
                logger.info(
                    "clearing_existing_metrics",
                    job_id=job_id,
                    count=existing_metrics_count,
                    reason="Job is being reprocessed"
                )
                db.query(Metric).filter(Metric.job_id == job_uuid).delete()
                db.commit()

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

            # Update progress: Finalizing
            update_job_progress(db, job_uuid, 95, "Finalizing results...")

            # Mark job as completed (this will set progress to 100)
            JobService.complete_job(db, job_uuid, results["output_dir"])

            # Update progress: Complete
            update_job_progress(db, job_uuid, 100, "Complete")

            logger.info("desktop_processing_completed", job_id=job_id)

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
                "DESKTOP_PROCESSING_FAILED",
                job_id=job_id,
                error=error_message,
                error_type=type(e).__name__,
                exc_info=True,
            )

            raise  # Re-raise so the task fails
    finally:
        db.close()
