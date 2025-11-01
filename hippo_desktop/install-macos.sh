#!/bin/bash
#
# NeuroInsight macOS Installation Script
# Handles Gatekeeper bypass automatically
#

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         NeuroInsight macOS Installer                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then 
   echo "ERROR: Do NOT run with sudo. Run as normal user."
   exit 1
fi

# Find the app
APP_PATH=""
if [ -f "NeuroInsight.app/Contents/Info.plist" ]; then
    APP_PATH="$(pwd)/NeuroInsight.app"
elif [ -f "../../NeuroInsight.app/Contents/Info.plist" ]; then
    APP_PATH="$(cd ../.. && pwd)/NeuroInsight.app"
else
    echo "ERROR: Cannot find NeuroInsight.app"
    echo "Please run this script from the extracted ZIP folder."
    exit 1
fi

echo "Found app: $APP_PATH"
echo ""

# Step 1: Remove quarantine
echo "Step 1/4: Removing quarantine attributes..."
xattr -cr "$APP_PATH" 2>/dev/null || true
echo "  ✓ Done"
echo ""

# Step 2: Allow execution
echo "Step 2/4: Setting executable permissions..."
chmod -R +x "$APP_PATH/Contents/MacOS" 2>/dev/null || true
echo "  ✓ Done"
echo ""

# Step 3: Add to Gatekeeper whitelist
echo "Step 3/4: Adding to Gatekeeper whitelist..."
echo "  (This may ask for your password)"
sudo spctl --add "$APP_PATH" 2>/dev/null || true
sudo xattr -r -d com.apple.quarantine "$APP_PATH" 2>/dev/null || true
echo "  ✓ Done"
echo ""

# Step 4: Move to Applications
echo "Step 4/4: Installing to Applications folder..."
if [ -d "/Applications/NeuroInsight.app" ]; then
    echo "  Removing old version..."
    rm -rf "/Applications/NeuroInsight.app"
fi
cp -R "$APP_PATH" "/Applications/"
echo "  ✓ Done"
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         Installation Complete!                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "NeuroInsight has been installed to /Applications"
echo ""
echo "To launch:"
echo "  1. Open Applications folder"
echo "  2. Double-click NeuroInsight"
echo "  3. If still blocked, RIGHT-CLICK → Open → Click 'Open'"
echo ""
echo "First run will check system requirements and help install Docker."
echo ""

# Offer to launch
read -p "Launch NeuroInsight now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "/Applications/NeuroInsight.app"
fi

