"""
MRI processing - Desktop mode compatible.

This module contains the core processing logic that works both with
Celery (server mode) and threading (desktop mode).
"""

from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.services import JobService, MetricService
from pipeline.processors import MRIProcessor

logger = get_logger(__name__)


def process_mri(job_id: str) -> dict:
    """
    Process MRI scan through the analysis pipeline.
    
    Core processing function that works without Celery.
    Can be called directly or wrapped in Celery task.
    
    Args:
        job_id: Job identifier (UUID as string)
    
    Returns:
        Dictionary with processing results
    """
    db: Session = SessionLocal()
    
    try:
        logger.info("processing_started", job_id=job_id)
        
        # Get job
        job = JobService.get_job(db, job_id)
        if not job:
            logger.error("job_not_found", job_id=job_id)
            return {"status": "error", "message": "Job not found"}
        
        # Check if already cancelled
        if hasattr(job, 'status') and job.status.value == 'CANCELLED':
            logger.info("job_cancelled_before_processing", job_id=job_id)
            return {"status": "cancelled", "job_id": job_id}
        
        # Update job status to running
        job = JobService.update_job_status(db, job_id, "RUNNING")
        logger.info("job_started", job_id=job_id)
        
        # Initialize processor
        processor = MRIProcessor(job_id=job_id)
        logger.info("processor_initialized", job_id=job_id, gpu_available=processor.use_gpu)
        
        # Process the MRI scan
        try:
            file_path = job.file_path
            logger.info("processing_pipeline_started", job_id=job_id)
            
            results = processor.process(file_path)
            
            logger.info("processing_pipeline_completed", job_id=job_id, metrics_count=len(results.get("metrics", [])))
            
        except Exception as proc_error:
            logger.error(
                "processing_failed",
                job_id=job_id,
                error=str(proc_error),
                exc_info=True,
            )
            # Update job status to failed
            JobService.update_job_status(
                db, job_id, "FAILED", error_message=str(proc_error)
            )
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(proc_error),
            }
        
        # Save metrics to database
        metrics = results.get("metrics", [])
        if metrics:
            for metric_data in metrics:
                MetricService.create_metric(db, job_id, metric_data)
        
        # Update job status to completed
        output_dir = results.get("output_dir")
        JobService.update_job_status(
            db, job_id, "COMPLETED", result_path=output_dir
        )
        
        logger.info("processing_completed", job_id=job_id, metrics_count=len(metrics))
        
        return {
            "status": "completed",
            "job_id": job_id,
            "metrics_count": len(metrics),
            "output_dir": output_dir,
        }
    
    except Exception as e:
        logger.error(
            "task_failed",
            job_id=job_id,
            error=str(e),
            exc_info=True,
        )
        # Try to mark job as failed
        try:
            JobService.update_job_status(
                db, job_id, "FAILED", error_message=str(e)
            )
        except:
            pass
        
        return {
            "status": "error",
            "job_id": job_id,
            "error": str(e),
        }
    
    finally:
        db.close()


# Celery wrapper (only used in server mode)
try:
    from workers.celery_app import celery_app
    
    @celery_app.task(
        name="workers.tasks.processing.process_mri_task",
        bind=True,
        max_retries=5,
        default_retry_delay=2,
    )
    def process_mri_task(self, job_id: str):
        """
        Celery task wrapper for MRI processing.
        
        Only used in server mode with Celery.
        Desktop mode calls process_mri() directly via threading.
        """
        return process_mri(job_id)

except ImportError:
    # Celery not available (desktop mode) - that's OK
    logger.info("celery_not_available_using_threading_mode")
    pass
