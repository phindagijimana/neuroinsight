#!/bin/bash
# Test NeuroInsight Desktop App Locally

echo "🧠 Testing NeuroInsight Desktop App Locally"
echo "==========================================="

# Check if we have a display
if [ -z "$DISPLAY" ]; then
    echo "❌ No display detected. Options:"
    echo "   1. Use X11 forwarding: ssh -X username@hostname"
    echo "   2. Install Xvfb: sudo yum install xorg-x11-server-Xvfb"
    echo "   3. Test on a GUI Linux machine"
    exit 1
fi

echo "✅ Display detected: $DISPLAY"

# Check if Docker/Podman is available
if command -v docker &> /dev/null || [ -f "$HOME/bin/docker" ]; then
    echo "✅ Container runtime available"
else
    echo "⚠️  No container runtime found. Install Docker or Podman first:"
    echo "   sudo yum install podman"
fi

# Test with AppImage
echo ""
echo "Testing with AppImage..."
chmod +x hippo_desktop/installers/NeuroInsight-1.0.5.AppImage

echo "🚀 Starting NeuroInsight Desktop App..."
echo "   (App will check system requirements and start Docker services)"
echo "   Close the app window when done testing"
echo ""

# Set up environment
export PATH="$HOME/bin:$PATH"

# Run the app (this will open the GUI)
hippo_desktop/installers/NeuroInsight-1.0.5.AppImage

echo ""
echo "✅ Desktop app test completed!"
