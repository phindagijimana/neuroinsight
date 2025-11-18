"""
Task execution service - abstraction layer for desktop vs server mode.

Desktop mode: Uses direct threading (not ThreadPoolExecutor due to PyInstaller issues)
Server mode: Uses Celery (if needed in future)
"""

import os
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Dict
import logging

logger = logging.getLogger(__name__)

# ThreadPoolExecutor doesn't work reliably in PyInstaller frozen apps
# Desktop mode uses direct threading instead
executor = None  # Not used in desktop mode


class TaskResult:
    """Wrapper for task results compatible with both threading and Celery"""
    
    def __init__(self, future: Future, task_id: str):
        self.future = future
        self.task_id = task_id
    
    @property
    def id(self) -> str:
        """Task ID"""
        return self.task_id
    
    def ready(self) -> bool:
        """Check if task is complete"""
        return self.future.done()
    
    def get(self, timeout: float = None) -> Any:
        """Get task result (blocks until complete)"""
        try:
            return self.future.result(timeout=timeout)
        except Exception as e:
            logger.error(f"Task {self.task_id} failed: {e}")
            raise
    
    def cancel(self) -> bool:
        """Attempt to cancel task"""
        return self.future.cancel()


class TaskService:
    """Service for submitting and managing background tasks"""
    
    @staticmethod
    def submit_task(func: Callable, *args, **kwargs) -> TaskResult:
        """
        Submit a task for background execution.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            TaskResult: Object to track task status
        """
        # Generate task ID
        import uuid
        task_id = str(uuid.uuid4())

        logger.warning(f"TaskService.submit_task called but ThreadPoolExecutor disabled for desktop mode. Use direct threading instead.")

        # This should not be called in desktop mode - raise error
        raise RuntimeError("TaskService.submit_task should not be used in desktop mode. Use direct threading.")
    
    @staticmethod
    def get_executor_stats() -> Dict[str, Any]:
        """Get statistics about the task executor"""
        if executor is None:
            return {
                "mode": "direct_threading",
                "note": "ThreadPoolExecutor disabled for desktop mode",
            }
        return {
            "max_workers": executor._max_workers,
            "queue_size": executor._work_queue.qsize(),
            "mode": "threading",
        }
    
    @staticmethod
    def shutdown(wait: bool = True):
        """Shutdown the task executor"""
        if executor is not None:
            logger.info("Shutting down task executor")
            executor.shutdown(wait=wait)
        else:
            logger.info("No task executor to shutdown (desktop mode)")


# Convenience function - disabled in desktop mode
def submit_task(func: Callable, *args, **kwargs) -> TaskResult:
    """Submit a background task - disabled in desktop mode"""
    raise RuntimeError("submit_task() should not be used in desktop mode. Use direct threading.")

