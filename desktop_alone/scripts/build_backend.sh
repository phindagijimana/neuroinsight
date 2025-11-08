#!/bin/bash
# Build standalone backend with PyInstaller

set -e

echo "======================================"
echo "Building NeuroInsight Backend Bundle"
echo "======================================"
echo ""

cd "$(dirname "$0")/.."

# Check if in desktop_alone directory
if [ ! -f "build.spec" ]; then
    echo "Error: Must run from desktop_alone directory"
    exit 1
fi

# Install requirements
echo "[1/3] Installing Python dependencies..."
pip install -r backend/requirements.txt
pip install pyinstaller
echo "✓ Dependencies installed"
echo ""

# Build with PyInstaller
echo "[2/3] Building backend executable with PyInstaller..."
echo "This may take 5-10 minutes..."
pyinstaller build.spec --clean

if [ $? -eq 0 ]; then
    echo "✓ Backend built successfully"
else
    echo "✗ Build failed"
    exit 1
fi
echo ""

# Test the build
echo "[3/3] Testing backend..."
export DESKTOP_MODE=true

# Start backend in background
dist/neuroinsight-backend/neuroinsight-backend &
BACKEND_PID=$!

# Wait for startup
echo "Waiting for backend to start..."
sleep 5

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is responding"
else
    echo "✗ Backend not responding"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Stop backend
kill $BACKEND_PID
sleep 2

echo ""
echo "======================================"
echo "✓ Build Complete!"
echo "======================================"
echo ""
echo "Backend executable: dist/neuroinsight-backend/"
echo "Size: $(du -sh dist/neuroinsight-backend | cut -f1)"
echo ""
echo "To test manually:"
echo "  cd dist/neuroinsight-backend"
echo "  export DESKTOP_MODE=true"
echo "  ./neuroinsight-backend"
echo ""

