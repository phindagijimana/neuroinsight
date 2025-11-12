"""
API routes for file upload.

Handles MRI file uploads (DICOM/NIfTI) and triggers
processing pipeline.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.schemas import JobCreate, JobResponse
from backend.services import JobService, StorageService

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=JobResponse, status_code=201)
async def upload_mri(
    file: UploadFile = File(..., description="MRI file (DICOM or NIfTI)"),
    db: Session = Depends(get_db),
):
    """Upload an MRI scan for processing (T1-only).

    - Accepts DICOM series or NIfTI files (.nii, .nii.gz)
    - Simple validation: file size, extension, and "T1" in filename
    - Creates a new job and enqueues background processing task
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file size (soft limit)
    # Use underlying file object for portable seek/tell
    import os
    try:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0, os.SEEK_SET)
    except Exception as e:
        logger.warning("file_size_check_failed", error=str(e))
        file_size = 1  # fallback to allow processing to continue

    MAX_UPLOAD_BYTES = 1024 * 1024 * 1024  # 1 GB
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if file_size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File is too large (limit 1 GB)")
    
    # Validate file extension
    valid_extensions = [".nii", ".nii.gz", ".dcm", ".dicom"]
    file_path = Path(file.filename)
    
    if not any(file.filename.endswith(ext) for ext in valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(valid_extensions)}"
        )
    
    # Simple T1 validation: require "T1" in filename (case-insensitive)
    filename_lower = file.filename.lower()
    if "t1" not in filename_lower:
        raise HTTPException(
            status_code=400,
            detail='Filename must contain "T1" (case-insensitive). Example: patient_001_T1w.nii.gz'
        )
    
    logger.info(
        "upload_received",
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=file_size,
    )
    
    # Generate unique filename early for cleanup on failure
    unique_filename = None
    try:
        # Read file content once for saving (no complex validation)
        file_data = await file.read()

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        
        # Save file using storage service: persist locally first, mirror to S3
        # Use BytesIO to create a file-like object from the cached file data
        from io import BytesIO
        file_obj = BytesIO(file_data)
        storage_service = StorageService()
        storage_path = storage_service.save_upload_local_then_s3(file_obj, unique_filename)
        
        # Create job record
        job_data = JobCreate(
            filename=file.filename,
            file_path=storage_path,
        )
        job = JobService.create_job(db, job_data)
        
        # Trigger processing asynchronously
        try:
            from workers.tasks.processing import process_mri_task
            process_mri_task.delay(str(job.id))
        except Exception as celery_error:
            # If Celery task enqueueing fails, log but don't fail the upload
            # The job is already created, so it can be manually triggered later
            logger.error(
                "celery_task_enqueue_failed",
                job_id=str(job.id),
                error=str(celery_error),
                error_type=type(celery_error).__name__,
            )
            # Don't raise - job is created successfully, just needs manual trigger
        
        logger.info(
            "upload_successful",
            job_id=str(job.id),
            filename=file.filename,
            storage_path=storage_path,
        )
        
        return job
    
    except HTTPException as http_exc:
        # Log validation error details before re-raising
        logger.error(
            "upload_validation_failed",
            filename=file.filename,
            status_code=http_exc.status_code,
            detail=http_exc.detail,
            file_size=file_size if 'file_size' in locals() else 'unknown',
        )
        # Re-raise HTTP exceptions (validation errors)
        # No cleanup needed - file wasn't saved yet
        raise
    except Exception as e:
        logger.error(
            "upload_failed",
            error=str(e),
            filename=file.filename,
            error_type=type(e).__name__,
            exc_info=True,
        )
        
        # Cleanup: Delete uploaded file if it was saved but job creation failed
        if unique_filename:
            try:
                # Path is already imported at the top of the file
                from backend.core.config import get_settings
                settings = get_settings()
                upload_path = Path(settings.upload_dir) / unique_filename
                if upload_path.exists():
                    upload_path.unlink()
                    logger.info("cleanup_failed_upload_file", filename=unique_filename)
            except Exception as cleanup_error:
                logger.warning("cleanup_failed_upload_file_error", error=str(cleanup_error))
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

