"""
Pytest configuration and shared fixtures.

This file contains fixtures that are automatically available to all tests
in the test suite. Fixtures defined here can be used by any test without
explicit import.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import before creating test database to ensure all models are registered
from backend.core.database import Base, get_db
from backend.core.config import get_settings
from backend.models import Job, Metric
from backend.models.job import JobStatus


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_database_url() -> str:
    """
    Provide a test database URL.
    
    Uses TEST_DATABASE_URL environment variable if set.
    
    ⚠️  WARNING: If TEST_DATABASE_URL is not set, tests will use the
    production database. Always set TEST_DATABASE_URL in your environment
    or .env file to use a separate test database.
    """
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if test_db_url:
        return test_db_url
    
    # WARNING: Using production database - this is dangerous!
    # Tests should use a separate test database
    settings = get_settings()
    db_url = settings.database_url
    print(f"\n⚠️  WARNING: Using production database for tests: {db_url}")
    print("   Set TEST_DATABASE_URL environment variable to use a test database.\n")
    return db_url


@pytest.fixture(scope="function")
def test_engine(test_database_url: str):
    """
    Create a test database engine.
    
    Creates all tables before tests and drops them after.
    Uses PostgreSQL (recommended for UUID support).
    """
    engine = create_engine(
        test_database_url,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # ⚠️  IMPORTANT: Only drop tables if using a dedicated test database
    # Do NOT drop tables if using the production database!
    # Instead, use transactions that roll back (handled by db_session fixture)
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if test_db_url and "test" in test_db_url.lower():
        # Safe to drop - we're using a test database
        Base.metadata.drop_all(bind=engine)
    else:
        # Using production database - DO NOT DROP TABLES!
        # Tests should use transactions that roll back
        pass
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Provide a test database session.
    
    Creates a new session for each test and rolls back changes after.
    This ensures tests are isolated and don't affect each other.
    """
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    session = TestSessionLocal()
    
    yield session
    
    # Cleanup: rollback any uncommitted transactions
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def db_session_factory(test_engine):
    """
    Provide a factory for creating database sessions.
    
    Useful when you need multiple sessions in a test.
    """
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    return TestSessionLocal


# ============================================================================
# Model Factory Fixtures
# ============================================================================

@pytest.fixture
def job_factory(db_session: Session):
    """
    Factory for creating test Job instances.
    
    Usage:
        job = job_factory()  # Uses defaults
        job = job_factory(status=JobStatus.RUNNING)  # Custom status
        job = job_factory(filename="custom.nii.gz")  # Custom filename
    """
    def _create_job(**kwargs):
        """Create a job with default or custom values."""
        defaults = {
            "id": uuid4(),
            "filename": "test_scan.nii.gz",
            "status": JobStatus.PENDING,
            "file_path": "/test/uploads/test_scan.nii.gz",
        }
        defaults.update(kwargs)
        
        job = Job(**defaults)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        return job
    
    return _create_job


@pytest.fixture
def metric_factory(db_session: Session):
    """
    Factory for creating test Metric instances.
    
    Usage:
        metric = metric_factory(job_id=job.id)  # Requires job_id
        metric = metric_factory(job_id=job.id, region="subiculum")
    """
    def _create_metric(job_id, **kwargs):
        """Create a metric with default or custom values."""
        defaults = {
            "region": "whole_hippocampus",
            "left_volume": 2000.0,
            "right_volume": 2100.0,
            "asymmetry_index": -0.024390243902439025,  # (L-R)/(L+R)
        }
        defaults.update(kwargs)
        
        metric = Metric(job_id=job_id, **defaults)
        db_session.add(metric)
        db_session.commit()
        db_session.refresh(metric)
        return metric
    
    return _create_metric


@pytest.fixture
def completed_job_factory(db_session: Session, job_factory):
    """
    Factory for creating completed jobs with result paths.
    
    Usage:
        job = completed_job_factory()
    """
    def _create_completed_job(**kwargs):
        """Create a completed job."""
        from datetime import datetime
        
        defaults = {
            "status": JobStatus.COMPLETED,
            "result_path": f"/test/outputs/{uuid4()}",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        
        return job_factory(**defaults)
    
    return _create_completed_job


@pytest.fixture
def job_with_metrics(db_session: Session, job_factory, metric_factory):
    """
    Create a job with associated metrics.
    
    Usage:
        job = job_with_metrics()  # Job with default metrics
    """
    def _create_job_with_metrics(**job_kwargs):
        """Create a job with default metrics."""
        job = job_factory(**job_kwargs)
        
        # Create a few default metrics
        metric_factory(job_id=job.id, region="whole_hippocampus")
        metric_factory(job_id=job.id, region="CA1")
        metric_factory(job_id=job.id, region="CA3")
        
        db_session.refresh(job)
        return job
    
    return _create_job_with_metrics


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_settings(monkeypatch):
    """
    Provide test-specific settings.
    
    Overrides environment variables for testing.
    """
    # Use temporary directories for tests
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("UPLOAD_DIR", str(Path(tmpdir) / "uploads"))
        monkeypatch.setenv("OUTPUT_DIR", str(Path(tmpdir) / "outputs"))
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ENVIRONMENT", "test")
        
        settings = get_settings()
        yield settings


@pytest.fixture
def temp_upload_dir(test_settings) -> Path:
    """
    Provide a temporary directory for test uploads.
    
    Automatically cleaned up after test.
    """
    upload_dir = Path(test_settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    yield upload_dir
    # Cleanup handled by TemporaryDirectory context manager


@pytest.fixture
def temp_output_dir(test_settings) -> Path:
    """
    Provide a temporary directory for test outputs.
    
    Automatically cleaned up after test.
    """
    output_dir = Path(test_settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    yield output_dir
    # Cleanup handled by TemporaryDirectory context manager


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_storage_service(monkeypatch):
    """
    Mock StorageService for tests that don't need real file operations.
    
    Usage:
        def test_something(mock_storage_service):
            mock_storage_service.get_file_path.return_value = "/test/path.nii.gz"
    """
    from unittest.mock import MagicMock
    from backend.services import StorageService
    
    mock_service = MagicMock(spec=StorageService)
    mock_service.get_file_path.return_value = "/test/path.nii.gz"
    mock_service.save_upload.return_value = "/test/saved.nii.gz"
    mock_service.delete_file.return_value = True
    
    monkeypatch.setattr("backend.services.StorageService", lambda: mock_service)
    return mock_service


@pytest.fixture
def mock_task_management_service(monkeypatch):
    """
    Mock TaskManagementService for tests.
    """
    from unittest.mock import MagicMock
    from backend.services import TaskManagementService
    
    mock_service = MagicMock(spec=TaskManagementService)
    mock_service.revoke_celery_task.return_value = True
    mock_service.terminate_fastsurfer_process.return_value = True
    mock_service.cancel_job_task.return_value = True
    
    monkeypatch.setattr("backend.services.TaskManagementService", lambda: mock_service)
    return mock_service


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_nifti_file(temp_upload_dir: Path) -> Path:
    """
    Create a sample NIfTI file for testing.
    
    Creates a minimal valid NIfTI file that can be used for upload tests.
    Note: This is a placeholder - you may want to use a real test file.
    """
    # Create a dummy file (not a real NIfTI, but sufficient for path-based tests)
    test_file = temp_upload_dir / "test_scan.nii.gz"
    test_file.write_bytes(b"dummy nifti content")
    return test_file


@pytest.fixture
def sample_job_data():
    """
    Provide sample job creation data.
    
    Returns a dictionary suitable for JobCreate schema.
    """
    return {
        "filename": "sample_scan.nii.gz",
        "file_path": "/test/uploads/sample_scan.nii.gz",
    }


# ============================================================================
# Integration Test Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def test_client():
    """
    Provide a FastAPI test client.
    
    For integration tests that need to hit the actual API endpoints.
    """
    from fastapi.testclient import TestClient
    from backend.main import app
    
    # Override database dependency for testing
    from backend.core.database import get_db
    
    def override_get_db():
        # This will be provided by individual tests
        yield
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def clean_db(db_session: Session):
    """
    Ensure database is clean before test.
    
    Deletes all records from all tables.
    Useful for tests that require a completely clean state.
    """
    # Delete in reverse order of dependencies
    db_session.query(Metric).delete()
    db_session.query(Job).delete()
    db_session.commit()
    yield
    # Cleanup handled by db_session fixture


@pytest.fixture
def uuid_generator():
    """
    Provide a UUID generator for tests.
    
    Usage:
        job_id = uuid_generator()
    """
    return uuid4

