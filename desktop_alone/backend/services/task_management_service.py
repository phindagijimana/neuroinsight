"""
Task management service for canceling/revoking Celery tasks and stopping processes.

This service handles graceful cancellation of running or pending jobs.
"""

import os
import signal
import subprocess
from typing import Optional
from uuid import UUID

from backend.core.logging import get_logger
# Celery only available in server mode
try:
    from workers.celery_app import celery_app
except ImportError:
    celery_app = None

logger = get_logger(__name__)


class TaskManagementService:
    """Service for managing task cancellation and process termination."""
    
    @staticmethod
    def revoke_celery_task(task_id: str, terminate: bool = False) -> bool:
        """
        Revoke a Celery task.
        
        Args:
            task_id: Celery task ID
            terminate: If True, terminate running task; if False, only revoke pending tasks
            
        Returns:
            True if revocation was successful
        """
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            logger.info("celery_task_revoked", task_id=task_id, terminate=terminate)
            return True
        except Exception as e:
            logger.warning("celery_task_revoke_failed", task_id=task_id, error=str(e))
            return False
    
    @staticmethod
    def find_celery_task_id(job_id: UUID) -> Optional[str]:
        """
        Find the Celery task ID for a given job.
        
        This searches active and scheduled tasks to find the task ID.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Celery task ID if found, None otherwise
        """
        try:
            inspect = celery_app.control.inspect()
            
            # Check active tasks
            active = inspect.active()
            if active:
                for worker, tasks in active.items():
                    for task in tasks:
                        args = task.get('args', [])
                        if args and len(args) > 0 and str(args[0]) == str(job_id):
                            task_id = task.get('id')
                            logger.info("celery_task_found_active", job_id=str(job_id), task_id=task_id)
                            return task_id
            
            # Check scheduled/reserved tasks
            scheduled = inspect.scheduled()
            if scheduled:
                for worker, tasks in scheduled.items():
                    for task in tasks:
                        request = task.get('request', {})
                        args = request.get('args', [])
                        if args and len(args) > 0 and str(args[0]) == str(job_id):
                            task_id = request.get('id')
                            logger.info("celery_task_found_scheduled", job_id=str(job_id), task_id=task_id)
                            return task_id
            
            logger.warning("celery_task_not_found", job_id=str(job_id))
            return None
            
        except Exception as e:
            logger.warning("celery_task_search_failed", job_id=str(job_id), error=str(e))
            return None
    
    @staticmethod
    def terminate_fastsurfer_process(job_id: UUID) -> bool:
        """
        Find and terminate FastSurfer processes for a given job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            True if processes were found and terminated
        """
        try:
            import psutil
            
            job_id_str = str(job_id)
            terminated_count = 0
            
            # Find processes related to this job
            for proc in psutil.process_iter(['pid', 'cmdline', 'name']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    cmdline_str = ' '.join(cmdline) if cmdline else ''
                    
                    # Check if this process is related to our job
                    if job_id_str in cmdline_str or (job_id_str.split('-')[0] in cmdline_str and 'fastsurfer' in cmdline_str.lower()):
                        logger.info(
                            "fastsurfer_process_found",
                            job_id=job_id_str,
                            pid=proc.info['pid'],
                            cmdline=cmdline_str[:200]
                        )
                        
                        # Terminate the process
                        try:
                            proc.terminate()
                            terminated_count += 1
                        except psutil.NoSuchProcess:
                            pass
                        except Exception as e:
                            logger.warning("fastsurfer_terminate_failed", pid=proc.info['pid'], error=str(e))
                    
                    # Also check for parent-child relationships
                    try:
                        parent = proc.parent()
                        if parent:
                            parent_cmdline = ' '.join(parent.info.get('cmdline', [])) if parent.info.get('cmdline') else ''
                            if job_id_str in parent_cmdline or 'fastsurfer' in parent_cmdline.lower():
                                proc.terminate()
                                terminated_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if terminated_count > 0:
                logger.info("fastsurfer_processes_terminated", job_id=job_id_str, count=terminated_count)
                
                # Give processes a moment to terminate gracefully
                import time
                time.sleep(2)
                
                # Force kill if still running
                for proc in psutil.process_iter(['pid', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info.get('cmdline', [])) if proc.info.get('cmdline') else ''
                        if job_id_str in cmdline and 'fastsurfer' in cmdline.lower():
                            proc.kill()
                            logger.info("fastsurfer_process_killed", pid=proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                return True
            else:
                logger.info("no_fastsurfer_processes_found", job_id=job_id_str)
                return False
                
        except ImportError:
            logger.warning("psutil_not_available", note="Cannot terminate FastSurfer processes without psutil")
            # Fallback: try using pgrep and pkill
            try:
                job_id_str = str(job_id)
                result = subprocess.run(
                    ['pgrep', '-f', job_id_str],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            logger.info("fastsurfer_process_terminated_fallback", pid=pid)
                        except (ProcessLookupError, ValueError):
                            pass
                    
                    return len(pids) > 0
                
                return False
            except Exception as e:
                logger.warning("fastsurfer_termination_fallback_failed", error=str(e))
                return False
        except Exception as e:
            logger.error("fastsurfer_termination_failed", job_id=str(job_id), error=str(e))
            return False
    
    @staticmethod
    def cancel_job_task(job_id: UUID, job_status: str) -> bool:
        """
        Cancel a job's Celery task and terminate associated processes.
        
        Args:
            job_id: Job UUID
            job_status: Current job status (to determine cancellation strategy)
            
        Returns:
            True if cancellation was attempted
        """
        from backend.models.job import JobStatus
        
        cancelled = False
        
        # Find and revoke Celery task
        task_id = TaskManagementService.find_celery_task_id(job_id)
        if task_id:
            # Terminate if running, just revoke if pending
            terminate = (job_status == JobStatus.RUNNING.value)
            cancelled = TaskManagementService.revoke_celery_task(task_id, terminate=terminate)
        
        # Terminate FastSurfer processes if job is running
        if job_status == JobStatus.RUNNING.value:
            TaskManagementService.terminate_fastsurfer_process(job_id)
        
        return cancelled




