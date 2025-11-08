#!/usr/bin/env python3
"""
Zombie Process Cleanup Script

This script detects and kills orphaned FastSurfer processes that are still running
despite their jobs being marked as completed or failed.

Usage:
    python scripts/cleanup_zombie_processes.py [--dry-run] [--kill-all]
"""

import argparse
import os
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import get_settings
from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.models.job import Job, JobStatus

logger = get_logger(__name__)
settings = get_settings()


def get_running_fastsurfer_processes():
    """
    Get list of running FastSurfer processes.
    
    Returns:
        List of (pid, command) tuples
    """
    import subprocess
    
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            check=True
        )
        
        processes = []
        for line in result.stdout.split('\n'):
            if 'FastSurferCNN/run_prediction' in line or 'fastsurfer/run_fastsurfer' in line:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])
                        cmd = ' '.join(parts[10:])
                        processes.append((pid, cmd))
                    except (ValueError, IndexError):
                        continue
        
        return processes
    except Exception as e:
        logger.error("failed_to_get_processes", error=str(e))
        return []


def extract_job_id_from_command(cmd):
    """
    Extract job ID from FastSurfer command line.
    
    Args:
        cmd: Command line string
        
    Returns:
        Job ID string or None
    """
    import re
    
    # Look for --sid argument
    match = re.search(r'--sid\s+([0-9a-f-]+)', cmd)
    if match:
        return match.group(1)
    
    # Look for job ID in output path
    match = re.search(r'/([0-9a-f-]{36})/', cmd)
    if match:
        return match.group(1)
    
    return None


def get_job_status(db, job_id):
    """
    Get the status of a job from the database.
    
    Args:
        db: Database session
        job_id: Job ID string
        
    Returns:
        JobStatus or None
    """
    from uuid import UUID
    
    try:
        job_uuid = UUID(job_id)
        job = db.query(Job).filter(Job.id == job_uuid).first()
        return job.status if job else None
    except Exception as e:
        logger.warning("failed_to_get_job_status", job_id=job_id, error=str(e))
        return None


def kill_process_group(pid, dry_run=False):
    """
    Kill a process and its entire process group.
    
    Args:
        pid: Process ID
        dry_run: If True, don't actually kill the process
        
    Returns:
        True if killed successfully, False otherwise
    """
    try:
        pgid = os.getpgid(pid)
        
        if dry_run:
            logger.info("would_kill_process_group", pid=pid, pgid=pgid)
            return True
        
        logger.info("killing_process_group", pid=pid, pgid=pgid)
        
        # Try SIGTERM first (graceful)
        try:
            os.killpg(pgid, signal.SIGTERM)
            import time
            time.sleep(2)
            
            # Check if still alive
            try:
                os.kill(pid, 0)
                # Still alive, use SIGKILL
                logger.warning("process_still_alive_using_sigkill", pid=pid)
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                # Already dead
                pass
        except ProcessLookupError:
            logger.info("process_already_dead", pid=pid)
        
        logger.info("process_killed", pid=pid)
        return True
        
    except Exception as e:
        logger.error("failed_to_kill_process", pid=pid, error=str(e))
        return False


def cleanup_zombie_processes(dry_run=False, kill_all=False):
    """
    Find and kill zombie FastSurfer processes.
    
    Args:
        dry_run: If True, don't actually kill processes
        kill_all: If True, kill all FastSurfer processes regardless of job status
        
    Returns:
        Number of processes killed
    """
    logger.info("starting_zombie_cleanup", dry_run=dry_run, kill_all=kill_all)
    
    # Get running processes
    processes = get_running_fastsurfer_processes()
    logger.info("found_processes", count=len(processes))
    
    if not processes:
        logger.info("no_processes_found")
        return 0
    
    # Get database session
    db = SessionLocal()
    killed_count = 0
    
    try:
        for pid, cmd in processes:
            job_id = extract_job_id_from_command(cmd)
            
            if not job_id:
                logger.warning("could_not_extract_job_id", pid=pid, cmd=cmd[:100])
                continue
            
            # Get job status
            job_status = get_job_status(db, job_id)
            
            if kill_all:
                logger.info("killing_process_kill_all_mode", pid=pid, job_id=job_id)
                if kill_process_group(pid, dry_run):
                    killed_count += 1
            elif job_status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                logger.warning(
                    "zombie_process_detected",
                    pid=pid,
                    job_id=job_id,
                    job_status=job_status.value if job_status else "unknown"
                )
                if kill_process_group(pid, dry_run):
                    killed_count += 1
            elif job_status == JobStatus.RUNNING:
                logger.info("process_ok_job_still_running", pid=pid, job_id=job_id)
            else:
                logger.warning("unknown_job_status", pid=pid, job_id=job_id, status=job_status)
    
    finally:
        db.close()
    
    logger.info("cleanup_complete", killed=killed_count, dry_run=dry_run)
    return killed_count


def main():
    parser = argparse.ArgumentParser(description="Cleanup zombie FastSurfer processes")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be killed without actually killing"
    )
    parser.add_argument(
        "--kill-all",
        action="store_true",
        help="Kill all FastSurfer processes regardless of job status"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧹 Zombie Process Cleanup")
    print("=" * 60)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No processes will be killed")
    if args.kill_all:
        print("⚠️  KILL ALL MODE - All FastSurfer processes will be killed")
    
    print()
    
    killed_count = cleanup_zombie_processes(
        dry_run=args.dry_run,
        kill_all=args.kill_all
    )
    
    print()
    print("=" * 60)
    if args.dry_run:
        print(f"✅ Would have killed {killed_count} zombie processes")
    else:
        print(f"✅ Killed {killed_count} zombie processes")
    print("=" * 60)


if __name__ == "__main__":
    main()


