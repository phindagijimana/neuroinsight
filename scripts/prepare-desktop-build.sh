#!/bin/bash
# Prepare NeuroInsight for Desktop App Build

set -e

echo "🏗️  Preparing NeuroInsight for Desktop Build..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the hippo directory"
    exit 1
fi

# Step 2: Create desktop-specific backend configuration
echo -e "${BLUE}📦 Step 1: Creating desktop backend configuration...${NC}"

cat > backend/config_desktop.py << 'EOF'
"""Desktop-specific configuration for embedded mode"""
from pydantic_settings import BaseSettings
from pydantic import Field

class DesktopSettings(BaseSettings):
    """Settings for desktop embedded mode"""
    
    # Use SQLite instead of PostgreSQL
    database_url: str = "sqlite:///./neuroinsight.db"
    
    # Disable Redis/Celery in embedded mode
    use_celery: bool = False
    
    # Use in-memory queue
    use_embedded_queue: bool = True
    
    # Disable cleanup services for desktop
    cleanup_enabled: bool = False
    
    # Desktop mode flag
    desktop_mode: bool = True
    
    class Config:
        env_prefix = "NEUROINSIGHT_"
EOF

echo -e "${GREEN}✅ Created backend/config_desktop.py${NC}"

# Step 3: Create PyInstaller spec file
echo -e "${BLUE}📦 Step 2: Creating PyInstaller spec file...${NC}"

cat > build_backend.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for NeuroInsight backend"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect data files
backend_data = [
    ('backend', 'backend'),
    ('pipeline', 'pipeline'),
]

# Hidden imports
hidden_imports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'nibabel',
    'numpy',
]

a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=backend_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',  # Exclude for now - add back when needed
        'matplotlib',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='neuroinsight-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='neuroinsight-backend',
)
EOF

echo -e "${GREEN}✅ Created build_backend.spec${NC}"

# Step 4: Update Electron main.js for embedded backend
echo -e "${BLUE}📦 Step 3: Updating Electron configuration...${NC}"

if [ -f "hippo_desktop/src/main.js" ]; then
    # Backup original
    cp hippo_desktop/src/main.js hippo_desktop/src/main.js.backup
    echo -e "${GREEN}✅ Backed up hippo_desktop/src/main.js${NC}"
fi

# Step 5: Create build script
echo -e "${BLUE}📦 Step 4: Creating build script...${NC}"

cat > scripts/build-desktop-app.sh << 'EOF'
#!/bin/bash
# Build NeuroInsight Desktop App

set -e

echo "🏗️  Building NeuroInsight Desktop App..."
echo ""

# 1. Install PyInstaller
echo "📦 Installing PyInstaller..."
pip install pyinstaller

# 2. Build backend
echo "📦 Building backend executable..."
pyinstaller build_backend.spec

# 3. Build Electron app
echo "⚡ Building Electron app..."
cd hippo_desktop

# Install dependencies
npm install

# Build for current platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Building for macOS..."
    npm run dist:mac
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Building for Linux..."
    npm run dist:linux
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🪟 Building for Windows..."
    npm run dist:win
fi

cd ..

echo ""
echo "✅ Build complete!"
echo "📦 Output: hippo_desktop/dist/"
EOF

chmod +x scripts/build-desktop-app.sh
echo -e "${GREEN}✅ Created scripts/build-desktop-app.sh${NC}"

# Step 6: Create README for desktop build
echo -e "${BLUE}📦 Step 5: Creating desktop build README...${NC}"

cat > DESKTOP_BUILD.md << 'EOF'
# Building NeuroInsight Desktop App

## Quick Start

```bash
# 1. Prepare desktop build
bash scripts/prepare-desktop-build.sh

# 2. Build the app
bash scripts/build-desktop-app.sh
```

## Output

Installers will be in `hippo_desktop/dist/`:

**macOS:**
- `NeuroInsight-1.0.5.dmg`
- `NeuroInsight-1.0.5-mac.zip`

**Windows:**
- `NeuroInsight Setup 1.0.5.exe`
- `NeuroInsight 1.0.5.exe` (portable)

**Linux:**
- `NeuroInsight-1.0.5.AppImage`
- `neuroinsight_1.0.5_amd64.deb`
- `neuroinsight-1.0.5.x86_64.rpm`

## Distribution

Users can download and install without any prerequisites!

## Next Steps

See `docs/STANDALONE_DESKTOP_APP.md` for detailed information.
EOF

echo -e "${GREEN}✅ Created DESKTOP_BUILD.md${NC}"

echo ""
echo -e "${GREEN}🎉 Preparation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review: docs/STANDALONE_DESKTOP_APP.md (comprehensive guide)"
echo "2. Review: DESKTOP_BUILD.md (quick build instructions)"
echo "3. Build: bash scripts/build-desktop-app.sh"
echo ""
echo "⚠️  Note: Full desktop build requires:"
echo "   - Simplifying backend (SQLite, no Docker)"
echo "   - Bundling ML models (~1-2 GB)"
echo "   - Platform-specific testing"
echo ""

