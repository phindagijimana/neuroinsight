"""
Example unit tests demonstrating fixture usage.

This file shows how to use the fixtures defined in conftest.py.
These are example tests - adapt them to your actual test cases.
"""

import pytest
from uuid import UUID
from datetime import datetime

from backend.models.job import JobStatus
from backend.services import JobService
from backend.models import Job


class TestJobServiceWithFixtures:
    """
    Example test class showing fixture usage.
    
    All fixtures from conftest.py are automatically available
    as method parameters.
    """
    
    def test_get_job_found(self, db_session, job_factory):
        """
        Test getting an existing job.
        
        Fixtures used:
        - db_session: Database session
        - job_factory: Creates a test job
        """
        # Arrange: Create a job using factory
        job = job_factory(
            filename="test_scan.nii.gz",
            status=JobStatus.PENDING
        )
        
        # Act: Get the job
        result = JobService.get_job(db_session, job.id)
        
        # Assert: Job was found
        assert result is not None
        assert result.id == job.id
        assert result.filename == "test_scan.nii.gz"
        assert result.status == JobStatus.PENDING
    
    def test_get_job_not_found(self, db_session):
        """
        Test getting a non-existent job.
        
        Fixtures used:
        - db_session: Database session
        """
        from uuid import uuid4
        
        # Arrange: Don't create a job
        
        # Act: Try to get a non-existent job
        result = JobService.get_job(db_session, uuid4())
        
        # Assert: Job not found
        assert result is None
    
    def test_create_job(self, db_session, sample_job_data):
        """
        Test creating a new job.
        
        Fixtures used:
        - db_session: Database session
        - sample_job_data: Sample job data dictionary
        """
        from backend.schemas import JobCreate
        
        # Arrange: Prepare job creation data
        job_data = JobCreate(**sample_job_data)
        
        # Act: Create job
        job = JobService.create_job(db_session, job_data)
        
        # Assert: Job was created
        assert job.id is not None
        assert job.filename == sample_job_data["filename"]
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None
    
    def test_delete_job(self, db_session, job_factory, mock_task_management_service):
        """
        Test deleting a job.
        
        Fixtures used:
        - db_session: Database session
        - job_factory: Creates a test job
        - mock_task_management_service: Mocks task cancellation
        """
        # Arrange: Create a job
        job = job_factory(status=JobStatus.RUNNING)
        job_id = job.id
        
        # Act: Delete the job
        result = JobService.delete_job(db_session, job_id)
        
        # Assert: Job was deleted
        assert result is True
        
        # Verify job no longer exists
        deleted_job = db_session.query(Job).filter(Job.id == job_id).first()
        assert deleted_job is None
    
    def test_delete_job_not_found(self, db_session):
        """
        Test deleting a non-existent job.
        
        Fixtures used:
        - db_session: Database session
        """
        from uuid import uuid4
        
        # Act: Try to delete non-existent job
        result = JobService.delete_job(db_session, uuid4())
        
        # Assert: Returns False (not found)
        assert result is False
    
    def test_get_jobs_with_filter(self, db_session, job_factory):
        """
        Test getting jobs with status filter.
        
        Fixtures used:
        - db_session: Database session
        - job_factory: Creates test jobs
        """
        # Arrange: Create jobs with different statuses
        pending_job = job_factory(status=JobStatus.PENDING)
        running_job = job_factory(status=JobStatus.RUNNING)
        completed_job = job_factory(status=JobStatus.COMPLETED)
        
        # Act: Get only pending jobs
        pending_jobs = JobService.get_jobs(
            db_session,
            skip=0,
            limit=100,
            status=JobStatus.PENDING
        )
        
        # Assert: Only pending job returned
        assert len(pending_jobs) == 1
        assert pending_jobs[0].id == pending_job.id
    
    def test_complete_job(self, db_session, job_factory, temp_output_dir):
        """
        Test completing a job.
        
        Fixtures used:
        - db_session: Database session
        - job_factory: Creates a test job
        - temp_output_dir: Temporary output directory
        """
        # Arrange: Create a running job
        job = job_factory(status=JobStatus.RUNNING)
        result_path = str(temp_output_dir / str(job.id))
        
        # Act: Mark job as completed
        JobService.complete_job(db_session, job.id, result_path)
        
        # Assert: Job status updated
        db_session.refresh(job)
        assert job.status == JobStatus.COMPLETED
        assert job.result_path == result_path
        assert job.completed_at is not None


class TestJobFactories:
    """Test the factory fixtures themselves."""
    
    def test_job_factory_defaults(self, job_factory):
        """Test job factory with default values."""
        job = job_factory()
        
        assert job.id is not None
        assert job.filename == "test_scan.nii.gz"
        assert job.status == JobStatus.PENDING
    
    def test_job_factory_custom_values(self, job_factory):
        """Test job factory with custom values."""
        custom_id = UUID('12345678-1234-5678-1234-567812345678')
        job = job_factory(
            id=custom_id,
            filename="custom.nii.gz",
            status=JobStatus.RUNNING
        )
        
        assert job.id == custom_id
        assert job.filename == "custom.nii.gz"
        assert job.status == JobStatus.RUNNING
    
    def test_completed_job_factory(self, completed_job_factory):
        """Test completed job factory."""
        job = completed_job_factory()
        
        assert job.status == JobStatus.COMPLETED
        assert job.result_path is not None
        assert job.completed_at is not None
    
    def test_job_with_metrics(self, job_with_metrics):
        """Test job with metrics factory."""
        job = job_with_metrics()
        
        assert job.id is not None
        # Check that metrics are loaded (if relationship is configured)
        # This depends on your model configuration
        # assert len(job.metrics) > 0


class TestFixtureCleanup:
    """Test that fixtures properly clean up."""
    
    def test_database_isolation(self, db_session, job_factory):
        """
        Test that database changes are isolated between tests.
        
        Each test should start with a clean database.
        """
        # Create a job
        job1 = job_factory()
        
        # Verify it exists
        assert JobService.get_job(db_session, job1.id) is not None
    
    def test_another_isolation_test(self, db_session):
        """
        This test should run after the previous one.
        
        The database should be clean (previous test's job should be gone).
        This demonstrates fixture cleanup between tests.
        """
        # Count jobs - should be 0 (clean state)
        jobs = JobService.get_jobs(db_session, skip=0, limit=100)
        assert len(jobs) == 0


# ============================================================================
# Usage Examples
# ============================================================================

def example_using_multiple_fixtures(db_session, job_factory, metric_factory):
    """Example showing how to use multiple fixtures together."""
    # Create a job
    job = job_factory(status=JobStatus.COMPLETED)
    
    # Create metrics for the job
    metric1 = metric_factory(job_id=job.id, region="whole_hippocampus")
    metric2 = metric_factory(job_id=job.id, region="CA1")
    
    # Now test something that uses both
    # ...



