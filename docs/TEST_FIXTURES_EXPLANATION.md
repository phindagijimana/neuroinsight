# Test Fixtures - Explanation

## What are Test Fixtures?

**Test fixtures** are reusable pieces of code that set up the testing environment and provide test data. Think of them as "preparation helpers" that run before your tests execute.

## Real-World Analogy

Imagine you're testing a recipe:
- **Without fixtures**: You manually buy ingredients, prep the kitchen, and clean up after each test
- **With fixtures**: You have a setup that automatically provides a clean kitchen, prepared ingredients, and handles cleanup

## Why Use Fixtures?

### 1. **Eliminate Repetition (DRY Principle)**
Instead of repeating setup code in every test:

```python
# ❌ WITHOUT FIXTURES - Repetitive code
def test_get_job():
    # Setup: Create database session
    db = SessionLocal()
    # Setup: Create test job
    job = Job(id=uuid4(), filename="test.nii.gz", status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    
    # Test code
    result = JobService.get_job(db, job.id)
    assert result is not None
    
    # Cleanup
    db.delete(job)
    db.commit()
    db.close()

def test_delete_job():
    # Setup: Create database session (REPEATED!)
    db = SessionLocal()
    # Setup: Create test job (REPEATED!)
    job = Job(id=uuid4(), filename="test.nii.gz", status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    
    # Test code
    JobService.delete_job(db, job.id)
    # ... cleanup
```

```python
# ✅ WITH FIXTURES - Write once, use everywhere
@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db  # Provide db to test
    db.close()  # Cleanup after test

@pytest.fixture
def test_job(db_session):
    job = Job(id=uuid4(), filename="test.nii.gz", status=JobStatus.PENDING)
    db_session.add(job)
    db_session.commit()
    return job

def test_get_job(db_session, test_job):
    # db_session and test_job are automatically provided!
    result = JobService.get_job(db_session, test_job.id)
    assert result is not None
    # Cleanup happens automatically!

def test_delete_job(db_session, test_job):
    # Same fixtures automatically available!
    JobService.delete_job(db_session, test_job.id)
    # Cleanup happens automatically!
```

### 2. **Automatic Cleanup**
Fixtures handle cleanup automatically, preventing test pollution:

```python
@pytest.fixture
def db_session():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)  # Setup
    
    yield db  # Provide to test
    
    # Cleanup runs AFTER test, even if test fails
    Base.metadata.drop_all(bind=engine)
    db.close()
```

### 3. **Dependency Injection**
Fixtures can depend on other fixtures, creating reusable chains:

```python
@pytest.fixture
def db_session():
    """Database session fixture."""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def test_job(db_session):  # Depends on db_session
    """Creates a test job in the database."""
    job = Job(filename="test.nii.gz", status=JobStatus.PENDING)
    db_session.add(job)
    db_session.commit()
    return job

@pytest.fixture
def test_job_with_metrics(test_job, db_session):  # Depends on test_job
    """Creates a job with associated metrics."""
    metric = Metric(job_id=test_job.id, region="whole_hippocampus", ...)
    db_session.add(metric)
    db_session.commit()
    return test_job  # Returns job with metrics attached
```

### 4. **Flexible Scopes**
Fixtures can be reused at different levels:

```python
@pytest.fixture(scope="function")  # Default: new for each test
def db_session():
    """Fresh database for each test."""
    return SessionLocal()

@pytest.fixture(scope="class")
def db_session():
    """Shared database for all tests in a class."""
    return SessionLocal()

@pytest.fixture(scope="module")
def db_session():
    """Shared database for all tests in a file."""
    return SessionLocal()

@pytest.fixture(scope="session")
def db_session():
    """Shared database for entire test run."""
    return SessionLocal()
```

## Common Fixture Patterns

### 1. **Database Fixture**
Provides a clean database session for each test:

```python
@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create test database
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    yield session  # Provide session to test
    
    # Cleanup: Remove all data after test
    session.rollback()
    Base.metadata.drop_all(bind=engine)
    session.close()
```

### 2. **Factory Fixture**
Creates test data with customizable parameters:

```python
@pytest.fixture
def job_factory(db_session):
    """Factory for creating test jobs."""
    def _create_job(**kwargs):
        defaults = {
            "filename": "test.nii.gz",
            "status": JobStatus.PENDING,
            "file_path": "/test/path.nii.gz",
        }
        defaults.update(kwargs)  # Override with provided values
        
        job = Job(**defaults)
        db_session.add(job)
        db_session.commit()
        return job
    
    return _create_job

# Usage:
def test_job_creation(job_factory):
    # Create with defaults
    job1 = job_factory()
    
    # Create with custom values
    job2 = job_factory(filename="custom.nii.gz", status=JobStatus.RUNNING)
```

### 3. **Mock Fixture**
Provides mocked dependencies:

```python
@pytest.fixture
def mock_storage_service():
    """Mock storage service for tests."""
    with patch('backend.services.StorageService') as mock:
        mock_instance = mock.return_value
        mock_instance.get_file_path.return_value = "/test/path.nii.gz"
        yield mock_instance
```

### 4. **Configuration Fixture**
Provides test-specific configuration:

```python
@pytest.fixture
def test_settings(monkeypatch):
    """Override settings for tests."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test/test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    return get_settings()
```

## How Pytest Fixtures Work

### 1. **Fixture Discovery**
Pytest automatically discovers fixtures in:
- `conftest.py` files (shared across tests)
- Test files themselves

### 2. **Fixture Execution Flow**

```
Test Run Starts
    ↓
Find fixtures needed by test
    ↓
Execute fixture dependencies first
    ↓
Execute fixture setup code (before yield)
    ↓
Yield value to test
    ↓
Test executes
    ↓
Fixture cleanup code (after yield)
    ↓
Test completes
```

### 3. **Example Execution**

```python
@pytest.fixture
def setup_database():
    print("1. Setting up database...")
    db = SessionLocal()
    yield db
    print("3. Cleaning up database...")
    db.close()

def test_example(setup_database):
    print("2. Test is running...")
    # Use setup_database here
    
# Output:
# 1. Setting up database...
# 2. Test is running...
# 3. Cleaning up database...
```

## Benefits for Your Codebase

### Before Fixtures (Current State):
```python
def test_get_job():
    # Manual setup in every test
    db = SessionLocal()
    job = Job(...)
    db.add(job)
    db.commit()
    
    result = JobService.get_job(db, job.id)
    
    # Manual cleanup in every test
    db.delete(job)
    db.commit()
    db.close()
```

**Problems:**
- ❌ Repeated code in every test
- ❌ Easy to forget cleanup
- ❌ Tests can interfere with each other
- ❌ Hard to maintain

### After Fixtures:
```python
def test_get_job(db_session, job_factory):
    job = job_factory()
    result = JobService.get_job(db_session, job.id)
    assert result is not None
    # Cleanup happens automatically!
```

**Benefits:**
- ✅ Write setup code once
- ✅ Automatic cleanup
- ✅ Tests are isolated
- ✅ Easy to maintain
- ✅ Reusable across test files

## Real Example from Your Codebase

### Testing JobService.get_job()

**Without fixtures:**
```python
def test_get_job_found():
    # Setup
    db = SessionLocal()
    job_id = uuid4()
    job = Job(
        id=job_id,
        filename="test.nii.gz",
        status=JobStatus.PENDING,
        created_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    
    # Test
    result = JobService.get_job(db, job_id)
    
    # Assertions
    assert result is not None
    assert result.id == job_id
    assert result.filename == "test.nii.gz"
    
    # Cleanup
    db.delete(job)
    db.commit()
    db.close()
```

**With fixtures:**
```python
# In conftest.py
@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = SessionLocal(bind=test_engine)
    yield session
    session.rollback()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def job_factory(db_session):
    def _create_job(**kwargs):
        job = Job(
            filename="test.nii.gz",
            status=JobStatus.PENDING,
            **kwargs
        )
        db_session.add(job)
        db_session.commit()
        return job
    return _create_job

# In test_job_service.py
def test_get_job_found(db_session, job_factory):
    job = job_factory()
    result = JobService.get_job(db_session, job.id)
    
    assert result is not None
    assert result.id == job.id
    assert result.filename == "test.nii.gz"
    # Cleanup automatic!
```

## Summary

**Test fixtures are:**
- ✅ Reusable setup/teardown code
- ✅ Dependency injection mechanism
- ✅ Automatic cleanup handlers
- ✅ Shared test utilities

**They help you:**
- ✅ Write DRY (Don't Repeat Yourself) tests
- ✅ Ensure consistent test environment
- ✅ Prevent test pollution
- ✅ Make tests easier to write and maintain

**Next:** We'll implement fixtures specifically for your codebase!



