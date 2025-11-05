#!/bin/bash
# Platform Compatibility Test Script
# Tests if NeuroInsight works correctly on the current platform

set -e

echo "======================================================================"
echo "  NeuroInsight Platform Compatibility Test"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 1. Detect Platform
echo "📋 Step 1: Platform Detection"
echo "------------------------------"

PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo "OS: $PLATFORM"
echo "Architecture: $ARCH"

case "$ARCH" in
    x86_64|amd64)
        echo -e "${GREEN}✓${NC} x86_64 detected - Native performance expected"
        EXPECTED_PERF="100%"
        ;;
    arm64|aarch64)
        echo -e "${YELLOW}⚠${NC} ARM64 detected - Emulation will be used"
        EXPECTED_PERF="50-60% (emulation overhead)"
        ;;
    *)
        echo -e "${RED}✗${NC} Unknown architecture: $ARCH"
        echo "This platform may not be supported"
        ;;
esac

echo "Expected performance: $EXPECTED_PERF"
echo ""

# 2. Check Docker
echo "📋 Step 2: Docker Availability"
echo "------------------------------"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker not found"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}✗${NC} Docker daemon not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓${NC} Docker installed: $DOCKER_VERSION"
echo ""

# 3. Check Multi-Platform Support
echo "📋 Step 3: Multi-Platform Support"
echo "------------------------------"

# Test if Docker can run x86_64 images
if docker run --rm --platform linux/amd64 alpine uname -m 2>&1 | grep -q "x86_64"; then
    echo -e "${GREEN}✓${NC} Docker can run x86_64 images (via emulation if needed)"
else
    echo -e "${RED}✗${NC} Docker cannot run x86_64 images"
    echo "Please ensure Docker Desktop is updated to version 4.6+"
    if [[ "$PLATFORM" == "Darwin" ]] && [[ "$ARCH" == "arm64" ]]; then
        echo "You may need to install Rosetta 2:"
        echo "  softwareupdate --install-rosetta"
    fi
    exit 1
fi
echo ""

# 4. Check Configuration Files
echo "📋 Step 4: Configuration Files"
echo "------------------------------"

# Check if platform flag is in docker-compose.yml
if grep -q "platform:.*linux/amd64" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} docker-compose.yml has platform specification"
else
    echo -e "${YELLOW}⚠${NC} docker-compose.yml missing platform flag"
    echo "Run: git pull to get the latest changes"
fi

# Check if platform flag is in mri_processor.py
if grep -q '"--platform".*"linux/amd64"' pipeline/processors/mri_processor.py; then
    echo -e "${GREEN}✓${NC} mri_processor.py has platform flag"
else
    echo -e "${YELLOW}⚠${NC} mri_processor.py missing platform flag"
    echo "Run: git pull to get the latest changes"
fi
echo ""

# 5. Check Services
echo "📋 Step 5: Service Status"
echo "------------------------------"

if docker-compose ps | grep -q "neuroinsight-worker.*Up"; then
    echo -e "${GREEN}✓${NC} Worker service is running"
    
    # Check worker logs for platform warnings
    if docker-compose logs worker 2>&1 | grep -q "platform.*does not match"; then
        echo -e "${YELLOW}⚠${NC} Platform mismatch warning detected (this is normal on ARM)"
    else
        echo -e "${GREEN}✓${NC} No platform warnings (native execution)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Worker service not running"
    echo "Start services with: docker-compose up -d"
fi

if docker-compose ps | grep -q "neuroinsight-backend.*Up"; then
    echo -e "${GREEN}✓${NC} Backend service is running"
else
    echo -e "${YELLOW}⚠${NC} Backend service not running"
fi
echo ""

# 6. Test Docker Platform Override
echo "📋 Step 6: Testing Platform Override"
echo "------------------------------"

echo "Running FastSurfer image test..."
if timeout 30 docker run --rm --platform linux/amd64 \
    --entrypoint /bin/sh \
    deepmi/fastsurfer:latest \
    -c "echo 'Platform test successful' && uname -m" 2>&1 | grep -q "x86_64"; then
    echo -e "${GREEN}✓${NC} FastSurfer image can run with platform override"
else
    echo -e "${RED}✗${NC} FastSurfer image test failed"
    echo "This may indicate a Docker configuration issue"
fi
echo ""

# 7. Performance Estimate
echo "📋 Step 7: Performance Estimate"
echo "------------------------------"

case "$ARCH" in
    x86_64|amd64)
        echo "Estimated processing time per scan:"
        echo "  • CPU only: 40-60 minutes"
        echo "  • With GPU: 2-5 minutes (if NVIDIA GPU available)"
        ;;
    arm64|aarch64)
        echo "Estimated processing time per scan:"
        echo "  • CPU only: 80-120 minutes (due to emulation)"
        echo "  • GPU: Not supported on ARM (NVIDIA only)"
        echo ""
        echo "💡 Tip: For faster processing, consider:"
        echo "  - Using an HPC server (if available)"
        echo "  - Cloud processing option (coming soon)"
        ;;
esac
echo ""

# 8. Summary
echo "======================================================================"
echo "  Test Summary"
echo "======================================================================"
echo ""

# Count successes
TOTAL=0
PASSED=0

# Rerun checks and count
[ "$ARCH" != "unknown" ] && ((PASSED++))
((TOTAL++))

command -v docker &> /dev/null && ((PASSED++))
((TOTAL++))

docker info &> /dev/null && ((PASSED++))
((TOTAL++))

docker run --rm --platform linux/amd64 alpine uname -m 2>&1 | grep -q "x86_64" && ((PASSED++))
((TOTAL++))

grep -q "platform:.*linux/amd64" docker-compose.yml && ((PASSED++))
((TOTAL++))

grep -q '"--platform".*"linux/amd64"' pipeline/processors/mri_processor.py && ((PASSED++))
((TOTAL++))

echo "Results: $PASSED/$TOTAL checks passed"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Your system is ready to run NeuroInsight."
    echo "Platform compatibility is correctly configured."
    echo ""
    if [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "aarch64" ]]; then
        echo "ℹ️  Note: You're on ARM architecture."
        echo "   Processing will work but may be slower due to emulation."
    fi
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed${NC}"
    echo ""
    echo "Please review the output above and:"
    echo "1. Ensure Docker Desktop is installed and running"
    echo "2. Pull latest changes: git pull"
    echo "3. Rebuild services: docker-compose down && docker-compose up -d --build"
    echo ""
    exit 1
fi

