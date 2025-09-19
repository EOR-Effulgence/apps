# -*- mode: python ; coding: utf-8 -*-
"""
Simple PyInstaller spec file for PDF2PNG/PDF2PPTX Converter v3.0
Minimal configuration to avoid Tkinter issues with FreeCAD Python environment.
"""

import sys
import os
from pathlib import Path

# Project configuration
PROJECT_ROOT = Path(os.getcwd())
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

a = Analysis(
    ['main.py'],
    pathex=[str(PROJECT_ROOT), str(SRC_PATH)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "README.md"), "."),
        (str(PROJECT_ROOT / "PDF2PNG_仕様書.md"), "."),
    ],
    hiddenimports=[
        # Essential modules only
        'tkinter',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.ttk',
        'fitz',
        'PIL',
        'PIL.Image',
        'pptx',
        'src.config',
        'src.core.pdf_processor',
        'src.ui.main_window',
        'src.ui.converters',
        'src.utils.error_handling',
        'src.utils.path_utils',
        'socket',  # Required for multiprocessing
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Minimal excludes
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
    optimize=0,  # Disable optimization to avoid issues
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF2PNG_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,   # Disable strip to avoid issues
    upx=False,     # Disable UPX to avoid issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x64',
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    uac_admin=False,
    uac_uiaccess=False,
)