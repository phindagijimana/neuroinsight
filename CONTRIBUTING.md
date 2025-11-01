# Contributing to NeuroInsight

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git

### Clone and Setup

```bash
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight

# Start all services
./RUN_ALL.sh
```

## Making Changes

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Follow standard ESLint rules
- **TypeScript**: Use strict mode

### Testing
```bash
# Backend tests
cd backend && pytest

# Run specific test
pytest tests/unit/test_specific.py
```

### Commit Messages
```
Format: <type>: <description>

Types: feat, fix, docs, style, refactor, test, chore

Example:
feat: add GPU acceleration support
fix: correct asymmetry formula calculation
docs: update installation guide
```

## Creating a Release

### 1. Update Version
```bash
cd hippo_desktop
# Edit package.json version field
```

### 2. Create Release Tag
```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

### 3. Automatic Builds
GitHub Actions will automatically:
- Build macOS installer
- Build Windows installer  
- Build Linux packages
- Create GitHub Release
- Upload all installers

Monitor at: https://github.com/phindagijimana/neuroinsight/actions

### 4. Verify Release
Check: https://github.com/phindagijimana/neuroinsight/releases

## Project Structure

```
neuroinsight/
├── backend/          # FastAPI application
├── frontend/         # React UI
├── workers/          # Celery workers
├── pipeline/         # MRI processing
├── hippo_desktop/    # Desktop application
├── docs/             # Technical documentation
└── tests/            # Test suite
```

## Questions?

Open an issue: https://github.com/phindagijimana/neuroinsight/issues

