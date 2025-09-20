# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF2PNG/PDF2PPTX Converter v3.0 - Virtual Environment Optimized
Refactored architecture with MVP pattern and enhanced performance.

Key improvements in v3.0:
- MVP architecture with separation of concerns
- Virtual environment dependency management
- Enhanced error handling and user experience
- Optimized build configuration for Tkinter compatibility
- Windows-native look and feel

Usage:
    venv\Scripts\activate
    pyinstaller build_windows.spec --clean

Output:
    dist/PDF2PNG_Converter.exe - Virtual Environment Compatible Windows executable

Build optimizations:
- Virtual environment Tkinter libraries
- Reduced dependency conflicts
- UPX compression for smaller file size
- Windows-specific theming and integration
- No FreeCAD dependencies required
"""

import sys
import os
from pathlib import Path

# Project configuration
PROJECT_ROOT = Path(os.getcwd())
SRC_PATH = PROJECT_ROOT / "src"
VERSION = "3.0.0"
APP_NAME = "PDF2PNG_Converter"

# Add src to Python path
sys.path.insert(0, str(SRC_PATH))

# Security settings
block_cipher = None

# Virtual Environment Python configuration
# Automatically detects Python installation and Tkinter libraries
# from the current virtual environment

# Hidden imports for refactored architecture
HIDDEN_IMPORTS = [
    # Modern GUI framework
    'customtkinter',
    'tkinterdnd2',
    'darkdetect',

    # Core GUI framework (fallback)
    'tkinter',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.ttk',
    'tkinter.font',
    'tkinter.colorchooser',
    '_tkinter',  # Low-level tkinter support

    # PDF processing core
    'fitz',  # PyMuPDF
    'fitz._fitz',

    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL._tkinter_finder',

    # PowerPoint generation
    'pptx',
    'pptx.util',
    'pptx.dml.color',
    'pptx.enum.shapes',
    'pptx.enum.text',
    'pptx.enum.dml',

    # Refactored modules (v3.0)
    'src.application.services.conversion_service',
    'src.presentation.presenters.main_presenter',
    'src.config',
    'src.core.pdf_processor',
    'src.ui.main_window',
    'src.ui.converters',
    'src.utils.error_handling',
    'src.utils.path_utils',

    # Async support
    'asyncio',
    'concurrent.futures',
    'threading',
    'queue',

    # Standard libraries (explicit)
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
    'socket',  # Required for multiprocessing

    # Windows integration
    'subprocess',
    'os',
    'sys',
]

# Data files to include
DATA_FILES = [
    # Configuration files
    (str(PROJECT_ROOT / "README.md"), "."),
    (str(PROJECT_ROOT / "PDF2PNG_仕様書.md"), "."),
]

# Virtual environment will provide Tkinter libraries automatically

# Check for optional assets
assets_dir = PROJECT_ROOT / "assets"
if assets_dir.exists():
    DATA_FILES.append((str(assets_dir), "assets"))

# Add Tcl/Tk data files - FreeCAD Compatibility Mode
# Since virtual environment uses FreeCAD's Tkinter, we need FreeCAD's Tcl/Tk libraries
try:
    import sys
    import os

    # Get Python installation directory from virtual environment
    python_dir = os.path.dirname(sys.executable)
    print(f"Using Python from: {python_dir}")

    # FreeCAD Tcl/Tk paths that are actually needed
    freecad_bin = r"C:\Program Files\FreeCAD 1.0\bin"
    freecad_lib = r"C:\Program Files\FreeCAD 1.0\lib"

    # Critical Tcl/Tk DLLs from FreeCAD
    freecad_dlls = [
        (os.path.join(freecad_bin, "tcl86t.dll"), "."),
        (os.path.join(freecad_bin, "tk86t.dll"), "."),
        (os.path.join(freecad_bin, "DLLs", "_tkinter.pyd"), "."),
    ]

    for dll_path, dest in freecad_dlls:
        if os.path.exists(dll_path):
            DATA_FILES.append((dll_path, dest))
            print(f"Added FreeCAD Tkinter DLL: {dll_path}")

    # Try to find and include Tcl library directories
    # Common locations where FreeCAD might have Tcl libraries
    tcl_search_paths = [
        os.path.join(freecad_lib, "tcl8.6"),
        os.path.join(freecad_bin, "tcl8.6"),
        os.path.join(freecad_bin, "lib", "tcl8.6"),
        os.path.join(freecad_lib, "tk8.6"),
        os.path.join(freecad_bin, "tk8.6"),
        os.path.join(freecad_bin, "lib", "tk8.6"),
    ]

    for tcl_path in tcl_search_paths:
        if os.path.exists(tcl_path):
            if "tcl8.6" in tcl_path:
                DATA_FILES.append((tcl_path, "tcl8.6"))
                print(f"Added Tcl library: {tcl_path}")
            elif "tk8.6" in tcl_path:
                DATA_FILES.append((tcl_path, "tk8.6"))
                print(f"Added Tk library: {tcl_path}")

except Exception as e:
    print(f"Warning: Could not locate FreeCAD Tcl/Tk libraries: {e}")

# Also add virtual environment Python DLLs if they exist
python_dir = os.path.dirname(sys.executable)
venv_dll_files = [
    os.path.join(python_dir, "DLLs", "_tkinter.pyd"),
]

for dll_file in venv_dll_files:
    if os.path.exists(dll_file):
        DATA_FILES.append((dll_file, "."))
        print(f"Added virtual environment DLL: {dll_file}")

# Modules to exclude (reduce size)
EXCLUDES = [
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

    # Network libraries (excluding socket - needed for multiprocessing)
    'http.server',
    'http.client',
    'xmlrpc',
    'ftplib',
    'smtplib',

    # Unused GUI frameworks
    'wx',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',

    # Unused tkinter modules
    'tkinter.test',
    'tkinter.dnd',
    'tkinter.tix',

    # Other unnecessary modules
    'email',
    'html',
    'xml.etree.ElementTree',
    'xml.dom',
    'xml.sax',
    'curses',
    'readline',
    'rlcompleter',
    'distutils',
    'setuptools',
    'pkg_resources',
]

# Analysis configuration
a = Analysis(
    ['main.py'],
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

# Remove duplicate and unnecessary binaries
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
    ('api-ms-win-crt-conio-l1-1-0.dll', None, None),
    ('api-ms-win-crt-convert-l1-1-0.dll', None, None),
    ('api-ms-win-crt-environment-l1-1-0.dll', None, None),
    ('api-ms-win-crt-filesystem-l1-1-0.dll', None, None),
    ('api-ms-win-crt-heap-l1-1-0.dll', None, None),
    ('api-ms-win-crt-locale-l1-1-0.dll', None, None),
    ('api-ms-win-crt-math-l1-1-0.dll', None, None),
    ('api-ms-win-crt-multibyte-l1-1-0.dll', None, None),
    ('api-ms-win-crt-private-l1-1-0.dll', None, None),
    ('api-ms-win-crt-process-l1-1-0.dll', None, None),
    ('api-ms-win-crt-runtime-l1-1-0.dll', None, None),
    ('api-ms-win-crt-stdio-l1-1-0.dll', None, None),
    ('api-ms-win-crt-string-l1-1-0.dll', None, None),
    ('api-ms-win-crt-time-l1-1-0.dll', None, None),
    ('api-ms-win-crt-utility-l1-1-0.dll', None, None),
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
    strip=True,        # Strip debug symbols
    upx=True,          # Enable UPX compression
    upx_exclude=[
        # Exclude problematic files from UPX compression
        'vcruntime140.dll',
        'msvcp140.dll',
        'python38.dll',
        'python39.dll',
        'python310.dll',
        'python311.dll',
        'python312.dll',
        'python313.dll',
        '_tkinter.pyd',
        'tk86t.dll',
        'tcl86t.dll',
    ],
    runtime_tmpdir=None,
    console=False,     # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x64',  # 64-bit Windows
    codesign_identity=None,
    entitlements_file=None,

    # Windows-specific settings
    icon=str(PROJECT_ROOT / "assets" / "app_icon.ico") if (PROJECT_ROOT / "assets" / "app_icon.ico").exists() else None,
    version='version_info.txt' if (PROJECT_ROOT / "version_info.txt").exists() else None,

    # Security and compatibility
    uac_admin=False,
    uac_uiaccess=False,
    exclude_binaries=False,
    manifest=None,
)

# Post-build optimizations for Windows
if sys.platform == 'win32':
    # Set executable properties
    exe.strip_binaries = True

    # Version information (if version_info.txt doesn't exist)
    if not (PROJECT_ROOT / "version_info.txt").exists():
        exe.version_info = {
            'version': tuple(map(int, VERSION.split('.')[:4])),
            'file_version': tuple(map(int, VERSION.split('.')[:4])),
            'product_version': tuple(map(int, VERSION.split('.')[:4])),
            'file_description': 'PDF to PNG/PPTX Converter - Refactored Edition',
            'product_name': 'PDF2PNG/PDF2PPTX Converter',
            'company_name': 'PDF2PNG Project',
            'legal_copyright': '© 2025 PDF2PNG Project. All rights reserved.',
            'original_filename': f'{APP_NAME}.exe',
            'internal_name': APP_NAME,
            'comments': 'High-performance PDF conversion tool with modern architecture',
        }