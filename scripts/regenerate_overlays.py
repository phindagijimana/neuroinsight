#!/usr/bin/env python3
"""
Regenerate Overlays for Completed Jobs

This script regenerates visualization overlays for all completed jobs
with the updated 180-degree flipped orientation (view from below).

Usage:
    python scripts/regenerate_overlays.py [--job-id JOB_ID] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import get_settings
from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.models.job import Job, JobStatus
from pipeline.utils import visualization

logger = get_logger(__name__)
settings = get_settings()


def regenerate_job_overlays(job_id: str, dry_run: bool = False) -> bool:
    """
    Regenerate overlays for a single job.
    
    Args:
        job_id: Job ID to regenerate
        dry_run: If True, don't actually regenerate, just check
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_dir = Path(settings.output_dir) / job_id
        fastsurfer_dir = output_dir / "fastsurfer"
        viz_dir = output_dir / "visualizations"
        
        # Check if job output exists
        if not output_dir.exists():
            logger.warning("job_output_not_found", job_id=job_id, path=str(output_dir))
            return False
        
        # Check for required files
        orig_mgz = fastsurfer_dir / job_id / "mri" / "orig.mgz"
        if not orig_mgz.exists():
            logger.warning("orig_mgz_not_found", job_id=job_id, path=str(orig_mgz))
            return False
        
        aseg_path = fastsurfer_dir / job_id / "mri" / "aparc.DKTatlas+aseg.deep.mgz"
        if not aseg_path.exists():
            aseg_path = fastsurfer_dir / job_id / "mri" / "aparc+aseg.mgz"
        
        if not aseg_path.exists():
            logger.warning("aseg_not_found", job_id=job_id)
            return False
        
        if dry_run:
            logger.info("dry_run_would_regenerate", 
                       job_id=job_id,
                       orig_mgz=str(orig_mgz),
                       aseg=str(aseg_path))
            return True
        
        logger.info("regenerating_overlays", job_id=job_id)
        
        # Extract segmentation
        aseg_nii, _ = visualization.extract_hippocampus_segmentation(
            fastsurfer_dir,
            job_id
        )
        
        # Convert T1 to NIfTI
        t1_nifti = visualization.convert_t1_to_nifti(
            orig_mgz,
            viz_dir / "whole_hippocampus"
        )
        
        if not aseg_nii or not aseg_nii.exists():
            logger.error("segmentation_extraction_failed", job_id=job_id)
            return False
        
        # Remove old overlays
        overlay_dir = viz_dir / "overlays"
        if overlay_dir.exists():
            import shutil
            shutil.rmtree(overlay_dir)
            logger.info("removed_old_overlays", job_id=job_id, path=str(overlay_dir))
        
        # Generate new overlays for ALL 3 orientations
        all_overlays = visualization.generate_all_orientation_overlays(
            t1_nifti,
            aseg_nii,
            viz_dir / "overlays",
            prefix="hippocampus",
            specific_labels=[17, 53]  # Hippocampus labels
        )
        
        if all_overlays:
            # Count total overlays across all orientations
            total_count = sum(len(overlays) for overlays in all_overlays.values())
            logger.info("overlays_regenerated", 
                       job_id=job_id,
                       total_count=total_count,
                       orientations=list(all_overlays.keys()),
                       axial_count=len(all_overlays.get('axial', {})),
                       coronal_count=len(all_overlays.get('coronal', {})),
                       sagittal_count=len(all_overlays.get('sagittal', {})))
            return True
        else:
            logger.error("overlay_generation_failed", job_id=job_id)
            return False
            
    except Exception as e:
        logger.error("regeneration_failed", job_id=job_id, error=str(e), exc_info=True)
        return False


def regenerate_all_completed_jobs(dry_run: bool = False) -> tuple:
    """
    Regenerate overlays for all completed jobs.
    
    Args:
        dry_run: If True, don't actually regenerate, just check
        
    Returns:
        Tuple of (success_count, total_count)
    """
    db = SessionLocal()
    
    try:
        # Get all completed jobs
        completed_jobs = db.query(Job).filter(
            Job.status == JobStatus.COMPLETED
        ).all()
        
        total = len(completed_jobs)
        logger.info("found_completed_jobs", count=total, dry_run=dry_run)
        
        if total == 0:
            logger.info("no_completed_jobs_found")
            return 0, 0
        
        success_count = 0
        
        for job in completed_jobs:
            job_id = str(job.id)
            logger.info("processing_job", 
                       job_id=job_id,
                       filename=job.filename,
                       completed_at=job.completed_at)
            
            if regenerate_job_overlays(job_id, dry_run):
                success_count += 1
                logger.info("job_processed_successfully", job_id=job_id)
            else:
                logger.warning("job_processing_failed", job_id=job_id)
        
        return success_count, total
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate overlays for completed jobs with new 180° flipped orientation"
    )
    parser.add_argument(
        "--job-id",
        type=str,
        help="Regenerate overlays for specific job ID only"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check what would be regenerated without actually doing it"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 Overlay Regeneration (180° Flipped View)")
    print("=" * 60)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()
    
    if args.job_id:
        # Regenerate single job
        print(f"Regenerating overlays for job: {args.job_id}")
        print()
        
        success = regenerate_job_overlays(args.job_id, args.dry_run)
        
        print()
        print("=" * 60)
        if success:
            if args.dry_run:
                print("✅ Job can be regenerated successfully")
            else:
                print("✅ Overlays regenerated successfully!")
        else:
            print("❌ Failed to regenerate overlays")
        print("=" * 60)
        
        sys.exit(0 if success else 1)
    
    else:
        # Regenerate all completed jobs
        print("Regenerating overlays for ALL completed jobs...")
        print()
        
        success_count, total_count = regenerate_all_completed_jobs(args.dry_run)
        
        print()
        print("=" * 60)
        print("📊 REGENERATION SUMMARY")
        print("=" * 60)
        print(f"Total completed jobs: {total_count}")
        print(f"Successfully regenerated: {success_count}")
        print(f"Failed: {total_count - success_count}")
        
        if args.dry_run:
            print()
            print("This was a DRY RUN. Run without --dry-run to actually regenerate.")
        
        print("=" * 60)
        
        sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()

