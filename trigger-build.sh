#!/bin/bash
# Quick script to trigger NeuroInsight desktop builds on GitHub Actions
# Usage: ./trigger-build.sh [tag-version]

set -e

echo "🚀 NeuroInsight Desktop Build Trigger"
echo "======================================"

# Check if we have a version argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <version-tag>"
    echo "Example: $0 v1.3.15"
    echo ""
    echo "This will:"
    echo "1. Create a git tag 'desktop-v1.3.15'"
    echo "2. Push the tag to trigger GitHub Actions"
    echo "3. Build Windows & Linux installers automatically"
    echo ""
    echo "Monitor progress at:"
    echo "https://github.com/phindagijimana/neuroinsight/actions"
    exit 1
fi

VERSION=$1
TAG="desktop-$VERSION"

echo "Version: $VERSION"
echo "Tag: $TAG"
echo ""

# Confirm
read -p "This will create tag '$TAG' and trigger GitHub Actions builds. Continue? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "Creating and pushing tag..."
git tag "$TAG"
git push origin "$TAG"

echo ""
echo "✅ Tag pushed! Build started."
echo ""
echo "Monitor progress:"
echo "https://github.com/phindagijimana/neuroinsight/actions"
echo ""
echo "Download installers from Actions artifacts after completion."
echo ""
echo "Expected build time: ~25-35 minutes"
echo "Outputs:"
echo "- neuroinsight-linux (AppImage)"
echo "- neuroinsight-windows (Setup.exe)"
