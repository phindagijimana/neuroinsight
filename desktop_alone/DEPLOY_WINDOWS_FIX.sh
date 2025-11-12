#!/bin/bash
# Quick deployment script for Windows build fix v1.3.8

echo "=========================================="
echo "  Windows Build Fix Deployment - v1.3.8"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "desktop_alone/electron-app/package.json" ]; then
    echo "❌ Error: Please run this from the repository root"
    echo "   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo"
    exit 1
fi

echo "📝 Committing changes..."
git add .github/workflows/desktop-build-v15.yml
git add desktop_alone/build.spec
git add desktop_alone/electron-app/package.json
git add desktop_alone/WINDOWS_BUILD_FIX_v1.3.8.md
git add desktop_alone/DEPLOY_WINDOWS_FIX.sh

git commit -m "Fix Windows build - v1.3.8

- Enhanced error detection and reporting in GitHub workflow
- Added PyInstaller verbose logging and verification
- Added electron-builder prerequisites check
- Improved checksums generation with better error handling
- Enabled console output for debugging Windows builds
- Bumped version to 1.3.8"

echo ""
echo "🚀 Pushing to main..."
git push origin main

echo ""
echo "🏷️  Creating tag desktop-v1.3.8..."
git tag -a desktop-v1.3.8 -m "Desktop v1.3.8 - Windows Build Fix

Fixes:
- Windows installer generation (was only creating checksums)
- Enhanced build error detection and reporting
- Added verbose PyInstaller logging for debugging
- Improved workflow error handling

Testing:
- This build has enhanced debugging enabled
- Console output enabled for Windows backend
- Detailed logs will show exact failure point if any"

echo ""
echo "🚀 Pushing tag to trigger build..."
git push origin desktop-v1.3.8

echo ""
echo "=========================================="
echo "✅ Deployment complete!"
echo "=========================================="
echo ""
echo "🔍 Monitor the build at:"
echo "   https://github.com/phindagijimana/neuroinsight/actions"
echo ""
echo "📦 Focus on: 'Build Windows Installer' job"
echo ""
echo "Expected to see:"
echo "  ✅ Backend directory exists"
echo "  ✅ Windows backend executable found"
echo "  ✅ Prerequisites verified"
echo "  ✅ Found Windows installer"
echo ""
echo "If build fails, logs will now show EXACTLY where and why!"
echo ""



