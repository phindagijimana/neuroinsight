# Production-Ready Codebase Organization Principles

This document outlines industry-standard codebase organization patterns used by senior engineers for production-ready applications.

## Table of Contents

1. [Directory Structure Patterns](#1-directory-structure-patterns)
2. [Separation of Concerns](#2-separation-of-concerns)
3. [Module Organization](#3-module-organization)
4. [Configuration Management](#4-configuration-management)
5. [Error Handling Patterns](#5-error-handling-patterns)
6. [Testing Organization](#6-testing-organization)
7. [Documentation Standards](#7-documentation-standards)
8. [Dependency Management](#8-dependency-management)
9. [Code Quality Tools](#9-code-quality-tools)
10. [API Design Patterns](#10-api-design-patterns)

---

## 1. Directory Structure Patterns

### Standard Python Project Structure

```
project_root/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration management
│   │
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── v1/                   # API versioning
│   │   │   ├── __init__.py
│   │   │   ├── routes/           # Route handlers
│   │   │   └── schemas/          # Request/response models
│   │   └── middleware.py          # API middleware
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── database.py           # DB connection/session
│   │   ├── security.py           # Auth, encryption
│   │   ├── logging.py            # Logging setup
│   │   └── exceptions.py         # Custom exceptions
│   │
│   ├── domain/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── models/               # Domain models (SQLAlchemy)
│   │   ├── services/             # Business logic
│   │   ├── repositories/        # Data access layer
│   │   └── use_cases/            # Use case handlers
│   │
│   ├── infrastructure/           # External integrations
│   │   ├── storage/              # File storage (S3, local)
│   │   ├── messaging/            # Queue, pub/sub
│   │   └── external_apis/       # Third-party integrations
│   │
│   ├── utils/                    # Utility functions
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── decorators.py
│   │
│   └── workers/                  # Background tasks
│       ├── celery_app.py
│       └── tasks/
│
├── tests/                        # Test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
│
├── migrations/                   # Database migrations
│   └── versions/
│
├── scripts/                      # Utility scripts
│   ├── setup.sh
│   └── deploy.sh
│
├── docs/                         # Documentation
│   ├── api/
│   └── architecture/
│
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── pyproject.toml                # Modern Python config
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Key Principles:
- **Feature-based vs Layer-based**: Choose based on team size
  - Small teams: Layer-based (api/, services/, models/)
  - Large teams: Feature-based (users/, orders/, payments/)
- **Flat is better than nested**: Avoid deeply nested directories (>3 levels)
- **Clear naming**: Use descriptive, consistent names

---

## 2. Separation of Concerns

### Three-Layer Architecture (Recommended)

```
┌─────────────────────────────────────┐
│   Presentation Layer (API)          │
│   - Route handlers                  │
│   - Request/response validation     │
│   - HTTP concerns only              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Business Logic Layer (Services)   │
│   - Domain logic                    │
│   - Use cases                      │
│   - Business rules                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Data Access Layer (Repository)    │
│   - Database queries               │
│   - External API calls              │
│   - File operations                 │
└─────────────────────────────────────┘
```

### Responsibilities by Layer:

**API Layer (routes/**):
- HTTP request/response handling
- Parameter validation
- Authentication/authorization
- Error formatting
- **NOT**: Business logic, database queries

**Service Layer (services/**):
- Business rules and workflows
- Domain logic
- Orchestration of multiple operations
- Transaction management
- **NOT**: HTTP concerns, direct DB access

**Repository Layer (repositories/**):
- Database queries
- Data persistence
- Query optimization
- **NOT**: Business logic, HTTP handling

---

## 3. Module Organization

### Single Responsibility Principle (SRP)

Each module should have one reason to change:

```python
# ❌ BAD: Multiple responsibilities
class UserManager:
    def create_user(self, data):      # User creation
        pass
    def send_email(self, email):      # Email sending
        pass
    def validate_password(self, pwd):  # Password validation
        pass

# ✅ GOOD: Single responsibility
class UserService:
    def create_user(self, data): pass

class EmailService:
    def send_email(self, email): pass

class PasswordValidator:
    def validate(self, password): pass
```

### Module Size Guidelines:
- **50-200 lines**: Ideal module size
- **>500 lines**: Consider splitting
- **<20 lines**: May be too granular

### Import Organization:
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import sqlalchemy
from fastapi import APIRouter

# Local application
from app.core.database import Session
from app.services import UserService
```

---

## 4. Configuration Management

### Environment-Based Configuration

```python
# config/base.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# config/development.py
class DevelopmentSettings(Settings):
    debug: bool = True
    database_url: str = "postgresql://localhost/dev_db"

# config/production.py
class ProductionSettings(Settings):
    debug: bool = False
    database_url: str = Field(..., env="DATABASE_URL")
```

### Configuration Best Practices:
- ✅ Use `.env` files for local development
- ✅ Never commit secrets to version control
- ✅ Use environment variables in production
- ✅ Provide `.env.example` template
- ✅ Validate configuration at startup
- ❌ Hard-code configuration values
- ❌ Mix configuration with business logic

---

## 5. Error Handling Patterns

### Custom Exception Hierarchy

```python
# core/exceptions.py
class AppException(Exception):
    """Base application exception"""
    pass

class ValidationError(AppException):
    """Input validation error"""
    pass

class NotFoundError(AppException):
    """Resource not found"""
    pass

class BusinessLogicError(AppException):
    """Business rule violation"""
    pass
```

### Error Handling Strategy:

```python
# ✅ GOOD: Consistent error handling
@router.post("/users")
async def create_user(user_data: UserCreate):
    try:
        user = user_service.create(user_data)
        return UserResponse.from_orm(user)
    except ValidationError as e:
        raise HTTPException(400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(422, detail=str(e))
    except Exception as e:
        logger.error("unexpected_error", error=str(e), exc_info=True)
        raise HTTPException(500, detail="Internal server error")
```

### Error Handling Principles:
- **Fail fast**: Validate inputs early
- **Be specific**: Use specific exception types
- **Log everything**: Log errors with context
- **User-friendly messages**: Don't expose internals
- **Graceful degradation**: Handle errors without crashing

---

## 6. Testing Organization

### Test Structure

```
tests/
├── unit/                          # Fast, isolated tests
│   ├── test_user_service.py
│   └── test_validators.py
│
├── integration/                   # Test component interactions
│   ├── test_api_endpoints.py
│   └── test_database.py
│
├── e2e/                          # End-to-end tests
│   └── test_full_workflow.py
│
├── fixtures/                     # Test data
│   ├── users.json
│   └── conftest.py
│
└── helpers/                      # Test utilities
    └── factories.py
```

### Testing Best Practices:
- **AAA Pattern**: Arrange, Act, Assert
- **One assertion per test**: Focus on one behavior
- **Descriptive names**: `test_create_user_with_invalid_email_raises_error`
- **Isolation**: Tests should not depend on each other
- **Fast unit tests**: <100ms each
- **Coverage target**: 80%+ for critical paths

---

## 7. Documentation Standards

### Code Documentation

```python
def process_mri_scan(
    job_id: UUID,
    file_path: Path,
    options: Optional[ProcessingOptions] = None
) -> ProcessingResult:
    """
    Process an MRI scan through the analysis pipeline.
    
    This function orchestrates the complete MRI processing workflow,
    including segmentation, metric calculation, and result storage.
    
    Args:
        job_id: Unique identifier for the processing job
        file_path: Path to the MRI scan file (NIfTI format)
        options: Optional processing configuration options
        
    Returns:
        ProcessingResult containing metrics and output paths
        
    Raises:
        ValidationError: If input file is invalid
        ProcessingError: If processing fails
        
    Example:
        >>> result = process_mri_scan(
        ...     job_id=uuid4(),
        ...     file_path=Path("scan.nii.gz")
        ... )
        >>> print(result.metrics)
    """
    pass
```

### Documentation Requirements:
- **Docstrings**: All public functions/classes
- **Type hints**: For function signatures
- **README.md**: Setup and usage instructions
- **API docs**: Auto-generated from docstrings
- **Architecture docs**: System design decisions

---

## 8. Dependency Management

### Requirements Organization

```python
# requirements/base.txt
# Core dependencies
fastapi==0.104.1
sqlalchemy==2.0.23

# requirements/dev.txt
# Development tools
-r base.txt
pytest==7.4.3
black==23.11.0
mypy==1.7.1

# requirements/prod.txt
# Production-only
-r base.txt
gunicorn==21.2.0
```

### Dependency Best Practices:
- **Pin versions**: Use exact versions (`==`) in production
- **Separate dev/prod**: Different requirements files
- **Regular updates**: Review and update quarterly
- **Security scanning**: Use `safety` or `pip-audit`
- **Virtual environments**: Always use venv/conda

---

## 9. Code Quality Tools

### Essential Tools

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true

[tool.pylint]
max-line-length = 100
```

### Tool Stack:
1. **Black**: Code formatting (automatic)
2. **isort**: Import sorting
3. **mypy**: Type checking
4. **pylint/flake8**: Linting
5. **pytest**: Testing
6. **pre-commit**: Git hooks

### Pre-commit Hooks:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

---

## 10. API Design Patterns

### RESTful API Structure

```
/api/v1/
  ├── /jobs                  # Collection resource
  │   ├── GET               # List jobs
  │   └── POST              # Create job
  │
  ├── /jobs/{id}            # Item resource
  │   ├── GET               # Get job
  │   ├── PUT/PATCH        # Update job
  │   └── DELETE            # Delete job
  │
  └── /jobs/{id}/metrics    # Sub-resource
      └── GET               # Get job metrics
```

### API Best Practices:
- **Versioning**: `/api/v1/`, `/api/v2/`
- **Consistent naming**: Use nouns, plural for collections
- **HTTP methods**: GET, POST, PUT, PATCH, DELETE
- **Status codes**: 200, 201, 400, 404, 500
- **Pagination**: For list endpoints
- **Filtering**: Query parameters for filtering
- **Error format**: Consistent error response structure

---

## Additional Best Practices

### 1. Logging Standards

```python
# Structured logging
logger.info(
    "user_created",
    user_id=str(user.id),
    email=user.email,
    timestamp=datetime.utcnow().isoformat()
)
```

### 2. Environment Variables

```bash
# .env.example
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
API_SECRET_KEY=your-secret-key-here
DEBUG=false
```

### 3. Database Migrations

- Use Alembic or similar
- Never modify migrations in production
- Test migrations on staging first

### 4. CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
- Run linters
- Run type checkers
- Run tests
- Build Docker image
- Deploy to staging
```

---

## Summary Checklist

### Production-Ready Codebase Should Have:

- ✅ Clear directory structure
- ✅ Separation of concerns (layers)
- ✅ Consistent naming conventions
- ✅ Comprehensive error handling
- ✅ Logging and monitoring
- ✅ Configuration management
- ✅ Test coverage (>80%)
- ✅ Documentation (code + README)
- ✅ Code quality tools (black, mypy, etc.)
- ✅ CI/CD pipeline
- ✅ Security best practices
- ✅ Performance considerations
- ✅ Database migrations
- ✅ Dependency management

---

## References

- Python Packaging User Guide
- FastAPI Best Practices
- Clean Architecture (Robert C. Martin)
- The Twelve-Factor App
- Google Python Style Guide
- PEP 8 (Python Style Guide)
