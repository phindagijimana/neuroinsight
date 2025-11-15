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
    - Strict pre-validation: size, readability, voxel/header sanity, and T1 markers
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
    
    logger.info(
        "upload_received",
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=file_size,
    )
    
    # Generate unique filename early for cleanup on failure
    unique_filename = None
    try:
        # Read file content once for validation and saving
        file_data = await file.read()
        
        # Optional strict validation for NIfTI files before saving to long-term storage
        if file.filename.endswith((".nii", ".nii.gz")):
            import tempfile
            import nibabel as nib
            import numpy as np
            import platform

            # Alternative: Multi-library validation (nibabel + SimpleITK fallback)
            current_platform = platform.system()
            logger.info("nifti_validation_platform_check", platform=current_platform, filename=file.filename)

            # Use BytesIO for cross-platform compatibility
            from io import BytesIO
            file_obj = BytesIO(file_data)

            img = None
            validation_success = False

            # Try nibabel first (works on Linux/macOS)
            try:
                img = nib.load(file_obj)
                file_obj.seek(0)  # Reset for potential reuse
                logger.info("nifti_validation_nibabel_success", filename=file.filename)
                validation_success = True
            except Exception as nibabel_error:
                logger.warning(
                    "nifti_validation_nibabel_failed",
                    filename=file.filename,
                    file_size=len(file_data),
                    error=str(nibabel_error),
                    error_type=type(nibabel_error).__name__
                )

                # Try SimpleITK as fallback (better Windows compatibility)
                try:
                    import SimpleITK as sitk
                    file_obj.seek(0)  # Reset to beginning
                    img = sitk.ReadImage(file_obj)
                    logger.info("nifti_validation_simpleitk_success", filename=file.filename)
                    validation_success = True
                except ImportError:
                    logger.warning("simpleitk_not_available", filename=file.filename)
                except Exception as sitk_error:
                    logger.warning(
                        "nifti_validation_simpleitk_failed",
                        filename=file.filename,
                        error=str(sitk_error),
                        error_type=type(sitk_error).__name__
                    )

            # If neither library worked, skip validation
            if not validation_success:
                logger.info("nifti_validation_skipped_both_failed", filename=file.filename)
                # Continue without validation rather than failing
            elif img is not None:
                # Basic header/shape sanity (works with both nibabel and SimpleITK)
                try:
                    # Get shape - different APIs for different libraries
                    if hasattr(img, 'shape'):  # nibabel
                        shape = img.shape
                        spacing = img.header.get_zooms()[:3] if hasattr(img, 'header') else [1.0, 1.0, 1.0]
                        # Get data array
                        data_array = img.get_fdata(dtype=np.float32)
                    else:  # SimpleITK
                        shape = tuple(reversed(img.GetSize()))  # SimpleITK size is reversed
                        spacing = list(img.GetSpacing())
                        # Convert SimpleITK image to numpy array
                        import SimpleITK as sitk
                        data_array = sitk.GetArrayFromImage(img).astype(np.float32)

                    # Validate shape
                    if len(shape) < 3:
                        raise HTTPException(status_code=400, detail=f"Expected 3D/4D NIfTI, got shape {shape}")

                    # Validate dimensions (minimum 32x32x32)
                    if len(shape) >= 3:
                        if any(dim < 32 for dim in shape[:3]):
                            raise HTTPException(status_code=400, detail=f"Image dimensions too small {shape[:3]} (min 32x32x32)")

                        # Voxel size sanity: 0.2mm to 5mm typical
                        if any(z <= 0 for z in spacing) or any(z > 5.0 for z in spacing) or any(z < 0.2 for z in spacing):
                            raise HTTPException(status_code=400, detail=f"Unusual voxel spacing {spacing} (expected 0.2–5.0 mm)")

                    # Data sanity: not all zeros/NaN
                    if not np.isfinite(data_array).any():
                        raise HTTPException(status_code=400, detail="Image contains no finite values")
                    if np.allclose(data_array, 0.0):
                        raise HTTPException(status_code=400, detail="Image appears to be all zeros")

                    logger.info("nifti_validation_checks_passed", filename=file.filename, shape=shape, spacing=spacing)

                except Exception as validation_error:
                    logger.warning(
                        "nifti_validation_checks_failed",
                        filename=file.filename,
                        error=str(validation_error),
                        error_type=type(validation_error).__name__
                    )
                    # Continue without failing - validation is optional
        elif file.filename.endswith((".dcm", ".dicom")):
            # Quick DICOM check for T1 using SeriesDescription/ProtocolName if pydicom present
            try:
                import pydicom
                import tempfile
                # For DICOM files, use the original suffix
                file_suffix = Path(file.filename).suffix
                with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=True) as tmp:
                    tmp.write(file_data)
                    tmp.flush()
                    ds = pydicom.dcmread(tmp.name, stop_before_pixels=True, force=True)
                    series_desc = str(getattr(ds, "SeriesDescription", "")).lower()
                    protocol = str(getattr(ds, "ProtocolName", "")).lower()
                    seq_name = str(getattr(ds, "SequenceName", "")).lower()
                    # Previously enforced T1 markers for DICOM. Per request, allow all DICOM uploads.
            except ModuleNotFoundError:
                # Fallback: filename check only
                nm = file.filename.lower()
                if not any(k in nm for k in ["t1", "mprage", "spgr", "tfl", "tfe"]):
                    raise HTTPException(status_code=400, detail="DICOM appears not to be T1-weighted (install pydicom for better detection)")

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
        # Desktop mode: Use background thread
        # Server mode: Use Celery
        from backend.core.config import get_settings
        settings = get_settings()
        
        if settings.desktop_mode:
            # Desktop mode: Process in background thread
            try:
                from workers.tasks.processing_desktop import process_mri_direct
                from backend.services.task_service import submit_task
                
                # Submit task to thread pool executor
                task_result = submit_task(process_mri_direct, str(job.id))
                
                logger.info(
                    "desktop_task_submitted",
                    job_id=str(job.id),
                    task_id=task_result.id,
                    mode="threading"
                )
            except Exception as task_error:
                logger.error(
                    "desktop_task_submit_failed",
                    job_id=str(job.id),
                    error=str(task_error),
                    error_type=type(task_error).__name__,
                )
                # Don't raise - job is created successfully, just needs manual trigger
        else:
            # Server mode: Use Celery
            try:
                from workers.tasks.processing import process_mri_task
                process_mri_task.delay(str(job.id))
                
                logger.info(
                    "celery_task_submitted",
                    job_id=str(job.id),
                    mode="celery"
                )
            except Exception as celery_error:
                # If Celery task enqueueing fails, log but don't fail the upload
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
    
    except HTTPException:
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

