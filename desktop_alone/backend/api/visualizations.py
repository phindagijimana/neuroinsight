"""
API routes for serving segmentation visualizations.

Provides endpoints to retrieve NIfTI files and images for web viewers.
"""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.models.job import JobStatus
from backend.services import JobService

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/visualizations", tags=["visualizations"])


@router.get("/{job_id}/whole-hippocampus/anatomical")
def get_anatomical_t1(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get anatomical T1-weighted NIfTI file.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        NIfTI file (.nii.gz)
    
    Raises:
        HTTPException: If job not found or file missing
    """
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not yet completed")
    
    # Construct path to T1 file
    viz_dir = Path(settings.output_dir) / str(job_id) / "visualizations" / "whole_hippocampus"
    t1_path = viz_dir / "anatomical.nii.gz"
    
    if not t1_path.exists():
        raise HTTPException(status_code=404, detail="Anatomical image not found")
    
    logger.info("serving_anatomical_t1", job_id=str(job_id))
    
    return FileResponse(
        path=t1_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'inline; filename="{job_id}_anatomical.nii.gz"',
            "Accept-Ranges": "bytes"
        }
    )


@router.get("/{job_id}/whole-hippocampus/nifti")
def get_whole_hippocampus_nifti(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get NIfTI file for whole hippocampus segmentation.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        NIfTI file (.nii.gz)
    
    Raises:
        HTTPException: If job not found or file missing
    """
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not yet completed")
    
    # Construct path to visualization files
    viz_dir = Path(settings.output_dir) / str(job_id) / "visualizations" / "whole_hippocampus"
    nifti_path = viz_dir / "segmentation.nii.gz"
    
    if not nifti_path.exists():
        raise HTTPException(status_code=404, detail="Segmentation file not found")
    
    logger.info("serving_whole_hippocampus_nifti", job_id=str(job_id))
    
    return FileResponse(
        path=nifti_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'inline; filename="{job_id}_whole_hippocampus.nii.gz"',
            "Accept-Ranges": "bytes"
        }
    )


@router.get("/{job_id}/whole-hippocampus/metadata")
def get_whole_hippocampus_metadata(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get metadata for whole hippocampus segmentation.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        JSON with label information and colormap
    
    Raises:
        HTTPException: If job not found or file missing
    """
    import json
    
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    viz_dir = Path(settings.output_dir) / str(job_id) / "visualizations" / "whole_hippocampus"
    metadata_path = viz_dir / "segmentation_metadata.json"
    
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata not found")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return metadata


@router.get("/{job_id}/subfields/nifti")
def get_subfields_nifti(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get NIfTI file for hippocampal subfields segmentation.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        NIfTI file (.nii.gz)
    
    Raises:
        HTTPException: If job not found or file missing
    """
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not yet completed")
    
    viz_dir = Path(settings.output_dir) / str(job_id) / "visualizations" / "subfields"
    nifti_path = viz_dir / "segmentation.nii.gz"
    
    if not nifti_path.exists():
        raise HTTPException(status_code=404, detail="Subfields segmentation not found")
    
    logger.info("serving_subfields_nifti", job_id=str(job_id))
    
    return FileResponse(
        path=nifti_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'inline; filename="{job_id}_subfields.nii.gz"',
            "Accept-Ranges": "bytes"
        }
    )


@router.get("/{job_id}/subfields/metadata")
def get_subfields_metadata(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get metadata for hippocampal subfields segmentation.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        JSON with label information and colormap
    
    Raises:
        HTTPException: If job not found or file missing
    """
    import json
    
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    viz_dir = Path(settings.output_dir) / str(job_id) / "visualizations" / "subfields"
    metadata_path = viz_dir / "segmentation_metadata.json"
    
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata not found")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return metadata


@router.get("/{job_id}/overlay/{slice_id}")
def get_overlay_image(
    job_id: UUID,
    slice_id: str,  # "slice_00", "slice_01", etc.
    seg_type: str = "whole",  # "whole" or "subfields"
    db: Session = Depends(get_db),
):
    """
    Get PNG overlay image for a specific slice.
    
    Args:
        job_id: Job identifier
        slice_id: Slice identifier (e.g., "slice_00", "slice_01")
        seg_type: Segmentation type (whole or subfields)
        db: Database session dependency
    
    Returns:
        PNG image file
    
    Raises:
        HTTPException: If job not found or file missing
    """
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    viz_dir = Path(settings.output_dir) / str(job_id) / "visualizations" / "overlays"
    
    if seg_type == "whole":
        image_path = viz_dir / f"hippocampus_{slice_id}.png"
    else:
        image_path = viz_dir / f"subfields_{slice_id}.png"
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Overlay image not found")
    
    logger.info("serving_overlay_image", job_id=str(job_id), slice=slice_id, type=seg_type)
    
    return FileResponse(
        path=image_path,
        media_type="image/png",
        filename=f"{job_id}_{seg_type}_{slice_id}.png"
    )

