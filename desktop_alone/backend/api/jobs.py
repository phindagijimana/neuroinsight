"""
API routes for job management.

Provides endpoints for retrieving, updating, and deleting
MRI processing jobs.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.schemas import JobResponse, JobStatus
from backend.services import JobService

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of processing jobs.
    
    Supports pagination and filtering by status.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Optional status filter
        db: Database session dependency
    
    Returns:
        List of job records
    """
    jobs = JobService.get_jobs(db, skip=skip, limit=limit, status=status)
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific job by ID.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        Job record with associated metrics
    
    Raises:
        HTTPException: If job not found
    """
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a job and its associated data.
    
    For RUNNING or PENDING jobs:
    - Cancels Celery task and terminates FastSurfer processes
    - Marks job as CANCELLED before deletion
    - Waits briefly for graceful termination
    
    For COMPLETED or FAILED jobs:
    - Immediately deletes files and database records
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Raises:
        HTTPException: If job not found
    """
    deleted = JobService.delete_job(db, job_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")


@router.get("/{job_id}/status", response_model=dict)
def get_job_status(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get the current status of a job.
    
    Lightweight endpoint for polling job progress.
    
    Args:
        job_id: Job identifier
        db: Database session dependency
    
    Returns:
        Dictionary with job status information
    
    Raises:
        HTTPException: If job not found
    """
    job = JobService.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
    }

