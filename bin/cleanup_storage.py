#!/usr/bin/env python3
"""
CLI tool for manual storage cleanup.

Usage:
    python bin/cleanup_storage.py [--dry-run] [--orphaned-only] [--old-completed] [--old-failed]

Options:
    --dry-run          Show what would be deleted without actually deleting
    --orphaned-only    Only clean up orphaned files (no database records)
    --old-completed    Only clean up old completed jobs
    --old-failed       Only clean up old failed jobs
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal
from backend.core.config import get_settings
from backend.services import CleanupService
from backend.core.logging import setup_logging

def main():
    parser = argparse.ArgumentParser(description="Clean up storage for NeuroInsight")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--orphaned-only", action="store_true", help="Only clean up orphaned files")
    parser.add_argument("--old-completed", action="store_true", help="Only clean up old completed jobs")
    parser.add_argument("--old-failed", action="store_true", help="Only clean up old failed jobs")
    parser.add_argument("--completed-days", type=int, default=None, help="Days to retain completed jobs (default: from config)")
    parser.add_argument("--failed-days", type=int, default=None, help="Days to retain failed jobs (default: from config)")
    
    args = parser.parse_args()
    
    # Initialize logging
    settings = get_settings()
    setup_logging(settings.log_level, settings.environment)
    
    cleanup_service = CleanupService()
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("Storage Cleanup Tool")
        print("=" * 80)
        
        if args.dry_run:
            print("\nDRY RUN MODE - No files will be deleted\n")
        
        # Show current storage stats
        stats = cleanup_service.get_storage_stats()
        print(f"\nCurrent Storage:")
        print(f"  Uploads: {stats['uploads']['count']} files ({stats['uploads']['size_gb']:.2f} GB)")
        print(f"  Outputs: {stats['outputs']['count']} directories ({stats['outputs']['size_gb']:.2f} GB)")
        print(f"  Total: {stats['total_size_gb']:.2f} GB")
        
        total_deleted = {
            "jobs": 0,
            "uploads": 0,
            "outputs": 0
        }
        
        # Clean up orphaned files
        if args.orphaned_only or not (args.old_completed or args.old_failed):
            print(f"\n{'='*80}")
            print("Cleaning up orphaned files...")
            print(f"{'='*80}")
            orphaned_uploads, orphaned_outputs = cleanup_service.cleanup_orphaned_files(
                db=db,
                dry_run=args.dry_run
            )
            total_deleted["uploads"] += orphaned_uploads
            total_deleted["outputs"] += orphaned_outputs
            print(f"  Orphaned uploads: {orphaned_uploads}")
            print(f"  Orphaned outputs: {orphaned_outputs}")
        
        # Clean up old completed jobs
        if args.old_completed or (not args.orphaned_only and not args.old_failed):
            print(f"\n{'='*80}")
            print("Cleaning up old completed jobs...")
            print(f"{'='*80}")
            completed_days = args.completed_days or settings.retention_completed_days
            completed_jobs, completed_uploads, completed_outputs = cleanup_service.cleanup_old_completed_jobs(
                db=db,
                days_old=completed_days,
                dry_run=args.dry_run
            )
            total_deleted["jobs"] += completed_jobs
            total_deleted["uploads"] += completed_uploads
            total_deleted["outputs"] += completed_outputs
            print(f"  Jobs deleted: {completed_jobs}")
            print(f"  Upload files deleted: {completed_uploads}")
            print(f"  Output directories deleted: {completed_outputs}")
            print(f"  Retention: {completed_days} days")
        
        # Clean up old failed jobs
        if args.old_failed or (not args.orphaned_only and not args.old_completed):
            print(f"\n{'='*80}")
            print("Cleaning up old failed jobs...")
            print(f"{'='*80}")
            failed_days = args.failed_days or settings.retention_failed_days
            failed_jobs, failed_uploads, failed_outputs = cleanup_service.cleanup_failed_jobs(
                db=db,
                days_old=failed_days,
                dry_run=args.dry_run
            )
            total_deleted["jobs"] += failed_jobs
            total_deleted["uploads"] += failed_uploads
            total_deleted["outputs"] += failed_outputs
            print(f"  Jobs deleted: {failed_jobs}")
            print(f"  Upload files deleted: {failed_uploads}")
            print(f"  Output directories deleted: {failed_outputs}")
            print(f"  Retention: {failed_days} days")
        
        # Show final stats
        if not args.dry_run:
            final_stats = cleanup_service.get_storage_stats()
            print(f"\n{'='*80}")
            print("Cleanup Summary")
            print(f"{'='*80}")
            print(f"  Jobs deleted: {total_deleted['jobs']}")
            print(f"  Upload files deleted: {total_deleted['uploads']}")
            print(f"  Output directories deleted: {total_deleted['outputs']}")
            print(f"\nFinal Storage:")
            print(f"  Uploads: {final_stats['uploads']['count']} files ({final_stats['uploads']['size_gb']:.2f} GB)")
            print(f"  Outputs: {final_stats['outputs']['count']} directories ({final_stats['outputs']['size_gb']:.2f} GB)")
            print(f"  Total: {final_stats['total_size_gb']:.2f} GB")
            print(f"  Space freed: {stats['total_size_gb'] - final_stats['total_size_gb']:.2f} GB")
        else:
            print(f"\n{'='*80}")
            print("Dry Run Summary")
            print(f"{'='*80}")
            print(f"  Would delete {total_deleted['jobs']} jobs")
            print(f"  Would delete {total_deleted['uploads']} upload files")
            print(f"  Would delete {total_deleted['outputs']} output directories")
        
        print(f"\n{'='*80}")
        print("Cleanup completed successfully")
        print(f"{'='*80}")
    
    except Exception as e:
        print(f"\nERROR: Error during cleanup: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()


