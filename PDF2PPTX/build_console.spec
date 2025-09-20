# -*- mode: python ; coding: utf-8 -*-
"""
Console-only PyInstaller spec for PDF2PNG/PDF2PPTX Converter v3.0
Bypasses Tkinter issues by building console-only version.
"""

import sys
import os
from pathlib import Path

# Project configuration
PROJECT_ROOT = Path(os.getcwd())
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

a = Analysis(
    ['main_console.py'],
    pathex=[str(PROJECT_ROOT), str(SRC_PATH)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "README.md"), "."),
        (str(PROJECT_ROOT / "PDF2PPTX_統合仕様書.md"), "."),
    ],
    hiddenimports=[
        # Core modules without Tkinter
        'fitz',
        'PIL',
        'PIL.Image',
        'pptx',
        'src.config',
        'src.core.pdf_processor',
        'src.utils.error_handling',
        'src.utils.path_utils',
        'socket',  # Required for multiprocessing
        'json',
        'pathlib',
        'logging',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude GUI and problematic modules
        'tkinter',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.ttk',
        '_tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'unittest',
        'test',
        'tests',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF2PNG_Console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x64',
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    uac_admin=False,
    uac_uiaccess=False,
)