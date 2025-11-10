#!/bin/bash

echo "================================================================================"
echo "🧹 NeuroInsight macOS Complete Cleanup Script"
echo "================================================================================"
echo ""
echo "This will remove ALL NeuroInsight data from your Mac"
echo "The app will recreate everything on next launch"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 1
fi

echo ""
echo "Starting cleanup..."
echo ""

# 1. Kill running processes
echo "1. Stopping NeuroInsight processes..."
killall NeuroInsight 2>/dev/null && echo "   ✅ Stopped NeuroInsight" || echo "   ℹ️  NeuroInsight not running"
killall "Electron Helper" 2>/dev/null && echo "   ✅ Stopped Electron Helper" || echo "   ℹ️  No Electron Helper"

# Check for backend
BACKEND_PID=$(ps aux | grep "neuroinsight-backend" | grep -v grep | awk '{print $2}')
if [ -n "$BACKEND_PID" ]; then
    echo "   Killing backend process (PID: $BACKEND_PID)..."
    kill -9 $BACKEND_PID 2>/dev/null && echo "   ✅ Backend stopped"
else
    echo "   ℹ️  No backend running"
fi

sleep 1

# 2. Remove application bundle
echo ""
echo "2. Removing application bundle..."
if [ -d "/Applications/NeuroInsight.app" ]; then
    rm -rf /Applications/NeuroInsight.app && echo "   ✅ Removed /Applications/NeuroInsight.app"
else
    echo "   ℹ️  No app found in /Applications"
fi

# 3. Remove logs
echo ""
echo "3. Removing logs..."
if [ -d ~/Library/Logs/NeuroInsight ]; then
    rm -rf ~/Library/Logs/NeuroInsight/ && echo "   ✅ Removed logs"
else
    echo "   ℹ️  No logs found"
fi

# 4. Remove application support
echo ""
echo "4. Removing application support data..."
if [ -d ~/Library/Application\ Support/NeuroInsight ]; then
    rm -rf ~/Library/Application\ Support/NeuroInsight/ && echo "   ✅ Removed app support data"
else
    echo "   ℹ️  No app support data found"
fi

# 5. Remove preferences
echo ""
echo "5. Removing preferences..."
PREFS_REMOVED=0
for pref in ~/Library/Preferences/com.neuroinsight.* ~/Library/Preferences/com.electron.neuroinsight-standalone.*; do
    if [ -e "$pref" ]; then
        rm -rf "$pref"
        PREFS_REMOVED=$((PREFS_REMOVED + 1))
    fi
done
if [ $PREFS_REMOVED -gt 0 ]; then
    echo "   ✅ Removed $PREFS_REMOVED preference file(s)"
else
    echo "   ℹ️  No preferences found"
fi

# 6. Remove caches
echo ""
echo "6. Removing caches..."
CACHES_REMOVED=0
for cache in ~/Library/Caches/com.neuroinsight.* ~/Library/Caches/neuroinsight-standalone ~/Library/Caches/NeuroInsight; do
    if [ -d "$cache" ]; then
        rm -rf "$cache"
        CACHES_REMOVED=$((CACHES_REMOVED + 1))
    fi
done
if [ $CACHES_REMOVED -gt 0 ]; then
    echo "   ✅ Removed $CACHES_REMOVED cache director(ies)"
else
    echo "   ℹ️  No caches found"
fi

# 7. Remove saved state
echo ""
echo "7. Removing saved application state..."
for state in ~/Library/Saved\ Application\ State/com.neuroinsight.*; do
    if [ -d "$state" ]; then
        rm -rf "$state" && echo "   ✅ Removed saved state"
    fi
done

# 8. Remove user documents
echo ""
echo "8. Removing user documents..."
if [ -d ~/Documents/NeuroInsight ]; then
    echo "   ⚠️  Found ~/Documents/NeuroInsight with user data"
    read -p "   Delete user documents? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf ~/Documents/NeuroInsight/ && echo "   ✅ Removed user documents"
    else
        echo "   ℹ️  Kept user documents"
    fi
else
    echo "   ℹ️  No user documents found"
fi

# 9. Remove test/debug logs
echo ""
echo "9. Removing test logs..."
LOG_COUNT=$(ls ~/*.log 2>/dev/null | wc -l)
if [ $LOG_COUNT -gt 0 ]; then
    rm -f ~/neuroinsight*.log ~/app*.log ~/v*.log ~/debug*.log ~/test*.log ~/fresh*.log
    echo "   ✅ Removed test logs"
else
    echo "   ℹ️  No test logs found"
fi

# 10. Refresh Launch Services (optional but recommended)
echo ""
echo "10. Refreshing macOS Launch Services..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user >/dev/null 2>&1
echo "   ✅ Launch Services refreshed"

echo ""
echo "================================================================================"
echo "✅ CLEANUP COMPLETE!"
echo "================================================================================"
echo ""
echo "Your Mac is now clean. Ready for fresh v1.1.4 install!"
echo ""
echo "Next steps:"
echo "1. Download v1.1.4 from GitHub Actions"
echo "2. sudo xattr -cr ~/Downloads/NeuroInsight-1.0.0-arm64.dmg"
echo "3. Install to Applications"
echo "4. sudo xattr -cr /Applications/NeuroInsight.app"
echo "5. Test!"
echo ""
echo "================================================================================"

