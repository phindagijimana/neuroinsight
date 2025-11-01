#!/usr/bin/env python3
"""
Restore job records for orphaned output directories.

This script finds output directories that don't have corresponding
database records and creates job records for them, marking them as COMPLETED.
"""

import sys
from pathlib import Path
from datetime import datetime
from uuid import UUID

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import SessionLocal
from backend.models import Job
from backend.models.job import JobStatus
from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def find_upload_file(job_id: str) -> tuple[str, str]:
    """Find the original upload file for a job ID."""
    upload_dir = Path(settings.upload_dir)
    
    # Look for files matching the job ID pattern
    for file_path in upload_dir.iterdir():
        if job_id in file_path.name:
            # Extract original filename (remove UUID prefix)
            parts = file_path.name.split('_', 1)
            if len(parts) == 2:
                return str(file_path), parts[1]  # (file_path, original_filename)
            return str(file_path), file_path.name
    
    return None, "unknown.nii"


def restore_orphaned_jobs():
    """Restore job records from orphaned output directories."""
    output_dir = Path(settings.output_dir)
    db = SessionLocal()
    
    try:
        # Find all output directories
        job_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
        
        restored_count = 0
        skipped_count = 0
        
        print("=" * 80)
        print("RESTORING ORPHANED JOB RECORDS")
        print("=" * 80)
        
        for job_dir in job_dirs:
            job_id_str = job_dir.name
            
            try:
                job_id = UUID(job_id_str)
            except ValueError:
                print(f"WARNING: Skipping invalid UUID: {job_id_str}")
                continue
            
            # Check if job already exists
            existing_job = db.query(Job).filter(Job.id == job_id).first()
            if existing_job:
                print(f"Job {job_id_str} already exists, skipping")
                skipped_count += 1
                continue
            
            # Check if output directory has FastSurfer or visualizations (indicates completion)
            fastsurfer_dir = job_dir / "fastsurfer"
            viz_dirs = list(job_dir.glob("visualizations*"))
            
            if not fastsurfer_dir.exists() and not viz_dirs:
                print(f"WARNING: Skipping {job_id_str} (no FastSurfer or visualizations)")
                skipped_count += 1
                continue
            
            # Find original upload file
            file_path, filename = find_upload_file(job_id_str)
            
            # Determine if truly completed (has visualizations)
            has_viz = len(viz_dirs) > 0
            status = JobStatus.COMPLETED if has_viz else JobStatus.COMPLETED
            
            # Create job record
            now = datetime.utcnow()
            # Use directory modification time as completed_at if available
            completed_at = datetime.fromtimestamp(job_dir.stat().st_mtime)
            
            job = Job(
                id=job_id,
                filename=filename,
                file_path=file_path if file_path else None,
                status=status,
                created_at=completed_at,  # Approximate creation time
                started_at=completed_at,  # Approximate start time
                completed_at=completed_at,
                result_path=str(job_dir),
                error_message=None
            )
            
            db.add(job)
            db.commit()
            
            print(f"SUCCESS: Restored job {job_id_str}")
            print(f"   Filename: {filename}")
            print(f"   Status: {status.value}")
            print(f"   Result path: {job_dir}")
            print(f"   Has visualizations: {has_viz}")
            print()
            
            restored_count += 1
        
        print("=" * 80)
        print(f"SUMMARY:")
        print(f"  Restored: {restored_count} jobs")
        print(f"  Skipped: {skipped_count} jobs")
        print("=" * 80)
        
    except Exception as e:
        logger.error("restore_failed", error=str(e), exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    restore_orphaned_jobs()

