#!/bin/bash
# Quick update script to apply platform compatibility fixes
# Run this if you already have NeuroInsight installed

set -e

echo "======================================================================"
echo "  NeuroInsight Platform Compatibility Update"
echo "======================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📦 Applying platform compatibility updates..."
echo ""

# 1. Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found"
    echo "Please run this script from the neuroinsight root directory"
    exit 1
fi

# 2. Stop current services
echo "🛑 Stopping current services..."
docker-compose down
echo "✓ Services stopped"
echo ""

# 3. Pull latest changes (if git repo)
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes from GitHub..."
    git pull || echo "⚠️  Git pull failed (continuing anyway)"
    echo ""
fi

# 4. Rebuild worker with new platform config
echo "🔨 Rebuilding worker container with platform support..."
docker-compose build --no-cache worker
echo "✓ Worker rebuilt"
echo ""

# 5. Pull FastSurfer image for current platform
echo "📥 Pulling FastSurfer image (x86_64 for compatibility)..."
docker pull --platform linux/amd64 deepmi/fastsurfer:latest || echo "⚠️  Pull skipped (will use cached)"
echo ""

# 6. Start services
echo "🚀 Starting all services..."
docker-compose up -d
echo ""

# 7. Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# 8. Check status
echo "📊 Service Status:"
echo "------------------------------"
docker-compose ps
echo ""

# 9. Show platform info
ARCH=$(uname -m)
echo "======================================================================"
echo "  Update Complete!"
echo "======================================================================"
echo ""
echo "Platform: $ARCH"

case "$ARCH" in
    arm64|aarch64)
        echo "Status: ✅ ARM64 compatibility enabled"
        echo ""
        echo "ℹ️  Note: You're on ARM architecture (Apple Silicon or ARM Linux)"
        echo "   FastSurfer will run via emulation (slower but functional)"
        echo ""
        echo "   Expected processing time:"
        echo "   • ~80-120 minutes per scan (vs ~40-60 on x86_64)"
        echo ""
        ;;
    x86_64|amd64)
        echo "Status: ✅ Native x86_64 execution"
        echo ""
        echo "   Expected processing time:"
        echo "   • ~40-60 minutes per scan (CPU)"
        echo "   • ~2-5 minutes per scan (with GPU)"
        echo ""
        ;;
esac

echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""

echo "🔍 To verify everything works:"
echo "   ./bin/test_platform_compatibility.sh"
echo ""

echo "📋 To view logs:"
echo "   docker-compose logs -f worker"
echo ""

echo "✅ Platform compatibility update applied successfully!"

