# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NeuroInsight standalone backend.

This bundles the entire Python backend with all dependencies into a single executable.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Increase recursion limit for PyInstaller analysis (needed for PyTorch)
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None

# Collect all backend modules and data files
backend_data = [
    ('backend', 'backend'),
    ('pipeline', 'pipeline'),
    ('frontend', 'frontend'),
]

# Hidden imports - packages PyInstaller might not detect automatically
hidden_imports = [
    # FastAPI and Uvicorn
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    
    # SQLAlchemy
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.ext.asyncio',
    'sqlalchemy.sql.default_comparator',
    
    # Pydantic
    'pydantic.deprecated.decorator',
    'pydantic_settings',
    
    # FastSurfer and deep learning
    'torch',
    'torchvision',
    'nibabel',
    'nibabel.loadsave',
    'nibabel.nifti1',
    'nibabel.freesurfer',
    
    # Utilities
    'platformdirs',
    'structlog',
    'aiofiles',
    
    # Image processing
    'PIL._imaging',
]

# Exclude packages not needed for standalone
excludes = [
    # Development tools
    'pytest',
    'black',
    'flake8',
    'mypy',
    
    # Docker/Celery (not used in desktop mode)
    'celery',
    'redis',
    'docker',
    
    # Optional large packages
    'matplotlib',  # If not used
    'pandas',  # If not used for core functionality
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
    excludes=excludes,
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
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='electron-app/build/icon.ico' if sys.platform == 'win32' else None,
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

