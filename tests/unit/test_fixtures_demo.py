"""
Simple demo tests showing how to use fixtures.

Run this file to see fixtures in action:
    pytest tests/unit/test_fixtures_demo.py -v
"""

import pytest
from uuid import uuid4

from backend.services import JobService
from backend.models import Job
from backend.models.job import JobStatus


# ============================================================================
# Demo 1: Basic Fixture Usage
# ============================================================================

def test_demo_basic_fixtures(db_session, job_factory):
    """
    Demo: Using basic fixtures.
    
    This test shows the simplest way to use fixtures:
    - db_session: Provides a database connection
    - job_factory: Creates a test job
    
    Fixtures are automatically injected as function parameters.
    """
    # Create a job using the factory
    job = job_factory()
    
    # Use the database session
    result = JobService.get_job(db_session, job.id)
    
    # Assertions
    assert result is not None
    assert result.id == job.id
    print(f"Created job: {job.id}, status: {job.status}")
    
    # Note: Cleanup happens automatically - you don't need to delete the job!


# ============================================================================
# Demo 2: Customizing Factory Values
# ============================================================================

def test_demo_custom_factory_values(db_session, job_factory):
    """
    Demo: Customizing factory values.
    
    You can override default values when using factories.
    """
    # Create a job with custom values
    job = job_factory(
        filename="custom_scan.nii.gz",
        status=JobStatus.RUNNING
    )
    
    # Verify custom values
    assert job.filename == "custom_scan.nii.gz"
    assert job.status == JobStatus.RUNNING
    print(f"Custom job: {job.filename}, status: {job.status}")


# ============================================================================
# Demo 3: Multiple Fixtures
# ============================================================================

def test_demo_multiple_fixtures(db_session, job_factory, metric_factory):
    """
    Demo: Using multiple fixtures together.
    
    You can use as many fixtures as you need - just add them as parameters.
    """
    # Create a job
    job = job_factory()
    
    # Create metrics for the job
    metric1 = metric_factory(
        job_id=job.id,
        region="whole_hippocampus",
        left_volume=2000.0,
        right_volume=2100.0
    )
    
    metric2 = metric_factory(
        job_id=job.id,
        region="CA1"
    )
    
    # Verify metrics were created
    assert metric1.job_id == job.id
    assert metric2.job_id == job.id
    print(f"Job {job.id} has {2} metrics")


# ============================================================================
# Demo 4: Pre-built Composite Fixtures
# ============================================================================

def test_demo_completed_job_fixture(completed_job_factory):
    """
    Demo: Using pre-built composite fixtures.
    
    Some fixtures combine multiple things for convenience.
    """
    # This fixture creates a completed job with result_path and completed_at
    job = completed_job_factory()
    
    assert job.status == JobStatus.COMPLETED
    assert job.result_path is not None
    assert job.completed_at is not None
    print(f"Completed job: {job.id}, result_path: {job.result_path}")


def test_demo_job_with_metrics(job_with_metrics):
    """
    Demo: Using a fixture that creates a job with metrics.
    """
    # This fixture creates a job and automatically adds metrics
    job = job_with_metrics()
    
    assert job.id is not None
    # The job has metrics attached (depending on your model relationships)
    print(f"Job with metrics: {job.id}")


# ============================================================================
# Demo 5: Testing Different Scenarios
# ============================================================================

def test_demo_get_job_found(db_session, job_factory):
    """Test getting an existing job."""
    job = job_factory()
    result = JobService.get_job(db_session, job.id)
    
    assert result is not None
    assert result.id == job.id


def test_demo_get_job_not_found(db_session):
    """Test getting a non-existent job."""
    # No fixture needed - just use a random UUID
    fake_id = uuid4()
    result = JobService.get_job(db_session, fake_id)
    
    assert result is None


def test_demo_get_jobs_filtered(db_session, job_factory):
    """Test filtering jobs by status."""
    # Create jobs with different statuses
    pending_job = job_factory(status=JobStatus.PENDING, filename="pending.nii.gz")
    running_job = job_factory(status=JobStatus.RUNNING, filename="running.nii.gz")
    completed_job = job_factory(status=JobStatus.COMPLETED, filename="completed.nii.gz")
    
    # Get only pending jobs
    pending_jobs = JobService.get_jobs(
        db_session,
        skip=0,
        limit=100,
        status=JobStatus.PENDING
    )
    
    # Verify only pending job returned
    assert len(pending_jobs) == 1
    assert pending_jobs[0].id == pending_job.id
    assert pending_jobs[0].status == JobStatus.PENDING


# ============================================================================
# Demo 6: Fixture Isolation (Each test gets fresh state)
# ============================================================================

def test_demo_isolation_first(db_session, job_factory):
    """First test - creates a job."""
    job = job_factory(filename="test1.nii.gz")
    jobs = JobService.get_jobs(db_session, skip=0, limit=100)
    print(f"Test 1: Found {len(jobs)} jobs")


def test_demo_isolation_second(db_session):
    """Second test - should have clean database."""
    # This test runs after the previous one, but the database is clean
    # because each test gets a fresh db_session
    jobs = JobService.get_jobs(db_session, skip=0, limit=100)
    assert len(jobs) == 0  # Clean state!
    print(f"Test 2: Found {len(jobs)} jobs (clean state)")


# ============================================================================
# How to Run These Tests
# ============================================================================

"""
To run these demo tests:

1. Run all demo tests:
   pytest tests/unit/test_fixtures_demo.py -v

2. Run a specific test:
   pytest tests/unit/test_fixtures_demo.py::test_demo_basic_fixtures -v

3. Run with output showing what fixtures do:
   pytest tests/unit/test_fixtures_demo.py -v --setup-show

4. See available fixtures:
   pytest --fixtures
"""



