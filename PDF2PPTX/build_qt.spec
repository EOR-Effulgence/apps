# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF2PNG/PDF2PPTX Converter Qt Edition
PySide6-based GUI without TCL/Tkinter dependencies.

Key advantages:
- No TCL/Tkinter dependencies
- Native Qt6 widgets
- Stable PyInstaller packaging
- Modern Windows appearance
- Reduced file size

Usage:
    venv\Scripts\activate
    pyinstaller build_qt.spec --clean --noconfirm

Output:
    dist/PDF2PNG_Qt.exe - Qt6-based Windows executable
"""

import sys
import os
from pathlib import Path

# Project configuration
PROJECT_ROOT = Path(os.getcwd())
SRC_PATH = PROJECT_ROOT / "src"
VERSION = "3.0.0"
APP_NAME = "PDF2PNG_Qt"

# Add src to Python path
sys.path.insert(0, str(SRC_PATH))

# Security settings
block_cipher = None

# Hidden imports for Qt edition
HIDDEN_IMPORTS = [
    # PySide6 Qt framework
    'PySide6.QtWidgets',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtOpenGL',

    # PDF processing core
    'fitz',  # PyMuPDF
    'fitz._fitz',

    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',

    # PowerPoint generation
    'pptx',
    'pptx.util',
    'pptx.dml.color',
    'pptx.enum.shapes',
    'pptx.enum.text',
    'pptx.enum.dml',

    # Application modules
    'src.config',
    'src.core.pdf_processor',
    'src.core.image_converter',
    'src.core.powerpoint_converter',
    'src.ui.qt_main_window',
    'src.application.services.conversion_service',
    'src.utils.error_handling',
    'src.utils.path_utils',

    # Async support
    'asyncio',
    'concurrent.futures',
    'threading',
    'queue',

    # Standard libraries
    'json',
    'pathlib',
    'contextlib',
    'dataclasses',
    'typing',
    'functools',
    'io',
    'tempfile',
    'shutil',
    'logging',
    'logging.handlers',
    'enum',
    'weakref',
    'socket',
    'subprocess',
    'os',
    'sys',
]

# Data files to include
DATA_FILES = [
    (str(PROJECT_ROOT / "README.md"), "."),
    (str(PROJECT_ROOT / "PDF2PPTX_統合仕様書.md"), "."),
]

# Check for optional assets
assets_dir = PROJECT_ROOT / "assets"
if assets_dir.exists():
    DATA_FILES.append((str(assets_dir), "assets"))

# Modules to exclude (reduce size)
EXCLUDES = [
    # Tkinter and TCL (Qt replaces these)
    'tkinter',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.ttk',
    'tkinter.font',
    'tkinter.colorchooser',
    '_tkinter',
    'customtkinter',
    'tkinterdnd2',

    # Development and testing
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'test',
    'tests',

    # Large scientific packages
    'matplotlib',
    'numpy',
    'numpy.distutils',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',

    # Development tools
    'black',
    'mypy',
    'flake8',
    'pylint',
    'autopep8',
    'isort',

    # Web frameworks
    'flask',
    'django',
    'tornado',
    'fastapi',
    'requests',
    'urllib3',

    # Database drivers
    'sqlite3',
    'psycopg2',
    'pymongo',

    # Other GUI frameworks
    'wx',
    'PyQt5',
    'PyQt6',
    'PySide2',  # Keep only PySide6

    # Unused modules (commented out modules required by dependencies)
    # 'email',  # Required by python-pptx/urllib
    # 'html',  # Required by PyMuPDF
    # 'xml.etree.ElementTree',  # Required by python-pptx
    # 'xml.dom',  # Required by python-pptx
    # 'xml.sax',  # Required by python-pptx
    'curses',
    'readline',
    'rlcompleter',
    'distutils',
    'setuptools',
    'pkg_resources',
]

# Analysis configuration
a = Analysis(
    ['main_qt.py'],
    pathex=[str(PROJECT_ROOT), str(SRC_PATH)],
    binaries=[],
    datas=DATA_FILES,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=2,  # Maximum bytecode optimization
    cipher=block_cipher,
)

# Remove duplicate binaries and unnecessary Windows DLLs
a.binaries = a.binaries - TOC([
    # Windows system DLLs that should come from system
    ('api-ms-win-core-console-l1-1-0.dll', None, None),
    ('api-ms-win-core-datetime-l1-1-0.dll', None, None),
    ('api-ms-win-core-debug-l1-1-0.dll', None, None),
    ('api-ms-win-core-errorhandling-l1-1-0.dll', None, None),
    ('api-ms-win-core-file-l1-1-0.dll', None, None),
    ('api-ms-win-core-file-l1-2-0.dll', None, None),
    ('api-ms-win-core-file-l2-1-0.dll', None, None),
    ('api-ms-win-core-handle-l1-1-0.dll', None, None),
    ('api-ms-win-core-heap-l1-1-0.dll', None, None),
    ('api-ms-win-core-interlocked-l1-1-0.dll', None, None),
    ('api-ms-win-core-libraryloader-l1-1-0.dll', None, None),
    ('api-ms-win-core-localization-l1-2-0.dll', None, None),
    ('api-ms-win-core-memory-l1-1-0.dll', None, None),
    ('api-ms-win-core-namedpipe-l1-1-0.dll', None, None),
    ('api-ms-win-core-processenvironment-l1-1-0.dll', None, None),
    ('api-ms-win-core-processthreads-l1-1-0.dll', None, None),
    ('api-ms-win-core-processthreads-l1-1-1.dll', None, None),
    ('api-ms-win-core-profile-l1-1-0.dll', None, None),
    ('api-ms-win-core-rtlsupport-l1-1-0.dll', None, None),
    ('api-ms-win-core-string-l1-1-0.dll', None, None),
    ('api-ms-win-core-synch-l1-1-0.dll', None, None),
    ('api-ms-win-core-synch-l1-2-0.dll', None, None),
    ('api-ms-win-core-sysinfo-l1-1-0.dll', None, None),
    ('api-ms-win-core-timezone-l1-1-0.dll', None, None),
    ('api-ms-win-core-util-l1-1-0.dll', None, None),
])

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,       # Don't strip - Qt may need symbols
    upx=False,         # Disable UPX - Qt can have issues
    runtime_tmpdir=None,
    console=False,     # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x64',
    codesign_identity=None,
    entitlements_file=None,

    # Windows-specific settings
    icon=str(PROJECT_ROOT / "assets" / "app_icon.ico") if (PROJECT_ROOT / "assets" / "app_icon.ico").exists() else None,

    # Security and compatibility
    uac_admin=False,
    uac_uiaccess=False,
    exclude_binaries=False,
    manifest=None,
)

# Windows executable properties
if sys.platform == 'win32':
    exe.version_info = {
        'version': tuple(map(int, VERSION.split('.')[:4])),
        'file_version': tuple(map(int, VERSION.split('.')[:4])),
        'product_version': tuple(map(int, VERSION.split('.')[:4])),
        'file_description': 'PDF to PNG/PPTX Converter - Qt Edition',
        'product_name': 'PDF2PNG/PDF2PPTX Converter Qt',
        'company_name': 'PDF2PNG Project',
        'legal_copyright': '© 2025 PDF2PNG Project. All rights reserved.',
        'original_filename': f'{APP_NAME}.exe',
        'internal_name': APP_NAME,
        'comments': 'High-performance PDF conversion tool with Qt6 interface',
    }