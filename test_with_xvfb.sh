#!/bin/bash
# Test NeuroInsight with Virtual Display (Xvfb)

echo "🧠 Testing NeuroInsight with Virtual Display"
echo "============================================"

# Check if Xvfb is installed
if ! command -v Xvfb &> /dev/null; then
    echo "Installing Xvfb..."
    sudo yum install -y xorg-x11-server-Xvfb
fi

# Start virtual display
echo "Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!
export DISPLAY=:99

# Wait for Xvfb to start
sleep 2

echo "✅ Virtual display ready on $DISPLAY"

# Set up environment
export PATH="$HOME/bin:$PATH"
chmod +x hippo_desktop/installers/NeuroInsight-1.0.5.AppImage

echo "🚀 Starting NeuroInsight Desktop App..."
echo "   (Testing in virtual display - no visible window)"

# Run app in background for testing
timeout 30 hippo_desktop/installers/NeuroInsight-1.0.5.AppImage &
APP_PID=$!

# Wait a bit for app to start
sleep 10

echo "Checking if app started..."
if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ App started successfully!"
    
    # Could add more automated tests here
    # For example, check if API endpoints are responding
    
    # Kill the app
    kill $APP_PID
    wait $APP_PID 2>/dev/null
else
    echo "❌ App failed to start"
fi

# Clean up
kill $XVFB_PID 2>/dev/null
wait $XVFB_PID 2>/dev/null

echo "✅ Virtual display test completed!"
