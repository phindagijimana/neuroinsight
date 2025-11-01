# How to Use Test Fixtures - Practical Guide

This guide shows you exactly how to use the fixtures we created in real tests.

---

## Quick Start: Your First Test with Fixtures

### Step 1: Create a Test File

Create a new file: `tests/unit/test_my_feature.py`

### Step 2: Import What You Need

```python
import pytest
from backend.services import JobService
from backend.models.job import JobStatus
```

### Step 3: Use Fixtures as Parameters

Fixtures are automatically available - just add them as function parameters:

```python
def test_get_job(db_session, job_factory):
    """Simple test using fixtures."""
    # job_factory automatically creates a job
    job = job_factory()
    
    # db_session provides a database connection
    result = JobService.get_job(db_session, job.id)
    
    # Assertions
    assert result is not None
    assert result.id == job.id
    # Cleanup happens automatically!
```

That's it! The fixtures handle all setup and cleanup automatically.

---

## Common Usage Patterns

### Pattern 1: Basic Test with One Fixture

```python
def test_create_job(db_session):
    """Test creating a job."""
    from backend.schemas import JobCreate
    
    job_data = JobCreate(
        filename="test.nii.gz",
        file_path="/test/path.nii.gz"
    )
    
    job = JobService.create_job(db_session, job_data)
    
    assert job.id is not None
    assert job.status == JobStatus.PENDING
```

**What happens:**
- `db_session` provides a fresh database session
- Test runs
- Database is automatically cleaned up

---

### Pattern 2: Using Factory Fixtures

Factory fixtures create test data with sensible defaults:

```python
def test_get_job_found(db_session, job_factory):
    """Test getting an existing job."""
    # Create a job using factory (uses defaults)
    job = job_factory()
    
    # Use the job
    result = JobService.get_job(db_session, job.id)
    
    assert result is not None
    assert result.id == job.id
```

**Customizing the factory:**

```python
def test_get_running_job(db_session, job_factory):
    """Test getting a running job."""
    # Override defaults with custom values
    job = job_factory(
        filename="custom_scan.nii.gz",
        status=JobStatus.RUNNING
    )
    
    result = JobService.get_job(db_session, job.id)
    
    assert result.status == JobStatus.RUNNING
```

---

### Pattern 3: Using Multiple Fixtures

You can use as many fixtures as you need:

```python
def test_job_with_metrics(db_session, job_factory, metric_factory):
    """Test a job with associated metrics."""
    # Create a job
    job = job_factory(status=JobStatus.COMPLETED)
    
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
    
    # Test something that uses both job and metrics
    metrics = JobService.get_job_metrics(db_session, job.id)
    assert len(metrics) == 2
```

---

### Pattern 4: Using Pre-built Composite Fixtures

Some fixtures combine multiple things:

```python
def test_completed_job(completed_job_factory):
    """Test with a completed job."""
    # This creates a job with result_path and completed_at set
    job = completed_job_factory()
    
    assert job.status == JobStatus.COMPLETED
    assert job.result_path is not None
    assert job.completed_at is not None
```

```python
def test_job_with_metrics(job_with_metrics):
    """Test with a job that has metrics."""
    # This creates a job + 3 default metrics
    job = job_with_metrics()
    
    # Job already has metrics attached
    # (depending on your model relationships)
```

---

### Pattern 5: Using Mock Fixtures

Mock fixtures replace real services with fake ones:

```python
def test_delete_job_cancels_task(mock_task_management_service, db_session, job_factory):
    """Test that deleting a running job cancels the task."""
    job = job_factory(status=JobStatus.RUNNING)
    
    # Delete the job
    JobService.delete_job(db_session, job.id)
    
    # Verify mock was called
    mock_task_management_service.cancel_job_task.assert_called_once()
```

```python
def test_upload_uses_storage(mock_storage_service):
    """Test file upload."""
    # Configure mock
    mock_storage_service.save_upload.return_value = "/saved/path.nii.gz"
    
    # Your upload code here
    result = storage_service.save_upload(file, "test.nii.gz")
    
    assert result == "/saved/path.nii.gz"
    mock_storage_service.save_upload.assert_called_once()
```

---

### Pattern 6: Using Configuration Fixtures

```python
def test_with_temp_directories(temp_upload_dir, temp_output_dir):
    """Test using temporary directories."""
    # temp_upload_dir and temp_output_dir are Path objects
    test_file = temp_upload_dir / "test.nii.gz"
    test_file.write_bytes(b"test content")
    
    assert test_file.exists()
    # Directories automatically cleaned up after test
```

---

## Complete Real-World Examples

### Example 1: Testing JobService.get_job()

```python
# tests/unit/test_job_service.py
import pytest
from backend.services import JobService
from backend.models.job import JobStatus

class TestJobServiceGetJob:
    """Tests for JobService.get_job() method."""
    
    def test_get_job_found(self, db_session, job_factory):
        """Test getting an existing job."""
        # Arrange: Create a job
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
        """Test getting a non-existent job."""
        from uuid import uuid4
        
        # Act: Try to get non-existent job
        result = JobService.get_job(db_session, uuid4())
        
        # Assert: Returns None
        assert result is None
```

---

### Example 2: Testing JobService.delete_job()

```python
def test_delete_job_completed(self, db_session, completed_job_factory):
    """Test deleting a completed job."""
    # Arrange: Create a completed job
    job = completed_job_factory()
    job_id = job.id
    
    # Act: Delete the job
    result = JobService.delete_job(db_session, job_id)
    
    # Assert: Job was deleted
    assert result is True
    
    # Verify job no longer exists
    deleted_job = db_session.query(Job).filter(Job.id == job_id).first()
    assert deleted_job is None

def test_delete_job_running(self, db_session, job_factory, mock_task_management_service):
    """Test deleting a running job cancels task."""
    # Arrange: Create a running job
    job = job_factory(status=JobStatus.RUNNING)
    
    # Act: Delete the job
    JobService.delete_job(db_session, job.id)
    
    # Assert: Task cancellation was called
    mock_task_management_service.cancel_job_task.assert_called_once()
```

---

### Example 3: Testing with Multiple Jobs

```python
def test_get_jobs_with_filter(self, db_session, job_factory):
    """Test getting jobs filtered by status."""
    # Arrange: Create multiple jobs with different statuses
    pending_job = job_factory(status=JobStatus.PENDING, filename="pending.nii.gz")
    running_job = job_factory(status=JobStatus.RUNNING, filename="running.nii.gz")
    completed_job = job_factory(status=JobStatus.COMPLETED, filename="completed.nii.gz")
    
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
    assert pending_jobs[0].status == JobStatus.PENDING
```

---

### Example 4: Testing with Files

```python
def test_file_upload(temp_upload_dir, sample_nifti_file):
    """Test file upload functionality."""
    # Arrange: sample_nifti_file fixture creates a test file
    assert sample_nifti_file.exists()
    
    # Act: Process the file
    # ... your code here ...
    
    # Assert: File was processed
    # ... assertions here ...
```

---

## Available Fixtures Reference

### Database Fixtures

```python
def test_with_database(db_session):
    """db_session provides a database connection."""
    # Use db_session for database operations
    jobs = db_session.query(Job).all()
```

### Model Factory Fixtures

```python
# Job factories
job = job_factory()                    # Default job
job = job_factory(status=JobStatus.RUNNING)  # Custom status
job = completed_job_factory()          # Completed job with result_path
job = job_with_metrics()              # Job with metrics attached

# Metric factory
metric = metric_factory(job_id=job.id)  # Requires job_id
metric = metric_factory(job_id=job.id, region="CA1")  # Custom region
```

### Mock Fixtures

```python
def test_with_mocks(mock_storage_service, mock_task_management_service):
    """Use mocks to isolate tests."""
    # Configure mocks
    mock_storage_service.get_file_path.return_value = "/test/path"
    
    # Use in tests
    # ... test code ...
```

### Configuration Fixtures

```python
def test_with_temp_dirs(temp_upload_dir, temp_output_dir):
    """Use temporary directories."""
    # temp_upload_dir and temp_output_dir are Path objects
    test_file = temp_upload_dir / "test.txt"
    test_file.write_text("test")
```

---

## Common Pitfalls and Solutions

### ❌ Problem: Forgetting to Use Fixtures

```python
# WRONG: Manual setup without fixtures
def test_bad():
    db = SessionLocal()  # Not using fixture
    job = Job(...)       # Manual creation
    db.add(job)
    # Forgot cleanup!
```

```python
# ✅ CORRECT: Using fixtures
def test_good(db_session, job_factory):
    job = job_factory()  # Automatic setup
    # Automatic cleanup!
```

### ❌ Problem: Modifying Shared Fixtures

```python
# WRONG: Modifying fixture return value
def test_bad(db_session, job_factory):
    job = job_factory()
    job.status = JobStatus.RUNNING  # This persists if not careful
    db_session.commit()
```

```python
# ✅ CORRECT: Create new data for modifications
def test_good(db_session, job_factory):
    job = job_factory()  # Don't modify this
    # Create another job if needed
    modified_job = job_factory(status=JobStatus.RUNNING)
```

### ✅ Solution: Understanding Fixture Scope

Fixtures have different scopes:
- `scope="function"` (default): New for each test (most common)
- `scope="class"`: Shared within a test class
- `scope="module"`: Shared within a test file
- `scope="session"`: Shared for entire test run

Most fixtures are `function` scope, so each test gets a fresh copy.

---

## Running Tests with Fixtures

### Run a specific test:
```bash
pytest tests/unit/test_job_service.py::test_get_job_found -v
```

### Run all tests in a file:
```bash
pytest tests/unit/test_job_service.py -v
```

### Run with output showing fixture usage:
```bash
pytest tests/unit/test_job_service.py -v --setup-show
```

### Run with fixture debugging:
```bash
pytest tests/unit/test_job_service.py -v --fixtures
```

---

## Step-by-Step: Writing Your First Test

### 1. Create Test File

Create: `tests/unit/test_my_first_test.py`

### 2. Write Test Function

```python
import pytest
from backend.services import JobService
from backend.models.job import JobStatus

def test_my_first_fixture_test(db_session, job_factory):
    """My first test using fixtures!"""
    # Step 1: Create test data using factory
    job = job_factory(
        filename="my_test.nii.gz",
        status=JobStatus.PENDING
    )
    
    # Step 2: Use the data in your test
    result = JobService.get_job(db_session, job.id)
    
    # Step 3: Make assertions
    assert result is not None
    assert result.filename == "my_test.nii.gz"
    # That's it! Cleanup happens automatically.
```

### 3. Run the Test

```bash
pytest tests/unit/test_my_first_test.py -v
```

### Output:
```
test_my_first_test.py::test_my_first_fixture_test PASSED
```

---

## Tips and Best Practices

1. **Name fixtures clearly**: Use descriptive fixture names like `db_session`, `job_factory`

2. **Use factories for test data**: Don't manually create models - use factories:
   ```python
   # ✅ Good
   job = job_factory(status=JobStatus.RUNNING)
   
   # ❌ Avoid
   job = Job(status=JobStatus.RUNNING, ...)
   db_session.add(job)
   ```

3. **Keep tests focused**: One fixture = one responsibility
   ```python
   # ✅ Good: Each fixture does one thing
   def test_job(db_session, job_factory):
   
   # ❌ Avoid: Too many fixtures for simple test
   def test_job(db_session, job_factory, metric_factory, mock_storage, ...):
   ```

4. **Use mocks for external dependencies**: Isolate your tests
   ```python
   def test_upload(mock_storage_service):
       # Test doesn't need real storage
   ```

5. **Read fixture source**: Check `tests/conftest.py` to understand what fixtures do

---

## Next Steps

1. **Try the examples**: Run `pytest tests/unit/test_job_service_example.py -v`

2. **Write your own test**: Create a test file and use fixtures

3. **Read fixture code**: Look at `tests/conftest.py` to see fixture implementations

4. **Experiment**: Try different fixture combinations

Remember: **Just add fixture names as parameters** - pytest does the rest!



