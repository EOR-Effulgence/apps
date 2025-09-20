# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## natural-language
 日本語で回答して

## Project Overview

PDF2PPTX is a Windows desktop application for converting PDF documents into PNG images or PowerPoint presentations. It supports both GUI and command-line interfaces, with features like batch processing, automatic rotation, and customizable PowerPoint labels.

## ⚠️ IMPORTANT: Virtual Environment Usage

**このプロジェクトでは、プロジェクト内の仮想環境 (`venv/`) を必須で使用してください。FreeCADや他の外部Pythonインストールは使用しないでください。**

**Virtual environment must be used for this project. Do not use FreeCAD or other external Python installations.**

All development, building, and testing must be done within the project's virtual environment to ensure consistent dependencies and avoid Tkinter runtime errors.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment (Windows) - REQUIRED
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Install PyInstaller for building executables
pip install pyinstaller
```

### Running the Application
```bash
# ⚠️ ALWAYS activate virtual environment first
venv\Scripts\activate

# Standalone executable (recommended)
dist\PDF2PNG_Converter.exe

# Python GUI version (development)
python main.py

# Console version
dist\PDF2PNG_Console.exe

# Development mode
python -m src.ui.main_window
```

### Testing
```bash
# ⚠️ ALWAYS activate virtual environment first
venv\Scripts\activate

# Run all tests
pytest

# Run specific test files
pytest tests/test_pdf_processor.py
pytest tests/test_basic_functionality.py

# Run tests with coverage
pytest --cov=src tests/
```

### Code Quality
```bash
# ⚠️ ALWAYS activate virtual environment first
venv\Scripts\activate

# Format code
black src tests

# Type checking
mypy src

# Code compilation check
python -m py_compile main.py
```

### Building Executables
```bash
# ⚠️ ALWAYS activate virtual environment first
venv\Scripts\activate

# Manual build with PyInstaller (Windows GUI version)
pyinstaller build_windows.spec --clean --noconfirm

# Manual build with PyInstaller (Console version)
pyinstaller build_console.spec --clean --noconfirm

# Check if virtual environment Python is being used
where python
# Should show: G:\works\apps\PDF2PPTX\venv\Scripts\python.exe
```

## Architecture

### Core Components
- **main.py**: Main GUI application entry point
- **main_console.py**: Console version entry point
- **src/core/pdf_processor.py**: Core PDF processing logic
- **src/ui/main_window.py**: Main GUI window implementation
- **src/ui/converters.py**: UI conversion handlers
- **src/config.py**: Application configuration management

### Key Features
- **PDF to PNG Conversion**: High-quality PNG image extraction from PDFs
- **PDF to PowerPoint**: A3 landscape PowerPoint presentations from PDFs
- **Automatic Rotation**: Portrait pages automatically rotated to landscape
- **Batch Processing**: Process entire folders of PDF files at once
- **Progress Tracking**: Real-time progress updates with user feedback
- **Error Handling**: Comprehensive error reporting and recovery

### File Structure
```
PDF2PPTX/
├── main.py                    # Main GUI entry point
├── main_console.py            # Console version entry point
├── requirements.txt           # Python dependencies
├── build_windows.spec         # PyInstaller Windows config
├── build_console.spec         # PyInstaller console config
├── venv/                      # Virtual environment (REQUIRED)
│   ├── Scripts/
│   │   ├── activate.bat       # Activation script
│   │   ├── python.exe         # Virtual environment Python
│   │   └── pyinstaller.exe    # PyInstaller in venv
│   └── Lib/                   # Installed packages
├── dist/                      # Built executables
│   ├── PDF2PNG_Converter.exe  # Windows GUI version
│   └── PDF2PNG_Console.exe    # Console version
├── src/                       # Source code
│   ├── core/
│   │   └── pdf_processor.py   # Core PDF processing
│   ├── ui/
│   │   ├── main_window.py     # GUI implementation
│   │   └── converters.py      # UI conversion handlers
│   ├── utils/
│   │   ├── error_handling.py  # Error management
│   │   └── path_utils.py      # Path operations
│   └── config.py              # Configuration
└── tests/                     # Unit tests
    ├── test_pdf_processor.py
    └── test_basic_functionality.py
```

### GUI Framework
- **Tkinter**: Built-in Python GUI framework (requires proper virtual environment setup)
- **Features**: File dialog, progress bars, real-time status updates
- **Virtual Environment**: Essential for proper Tkinter library linking and DLL resolution

### Dependencies
- **Core**: PyMuPDF (fitz), python-pptx, Pillow for PDF/image processing
- **GUI**: tkinter (built-in) for user interface
- **Build**: PyInstaller for executable creation
- **Development**: pytest, black, mypy for code quality

## Development Guidelines

### Code Style
- Use Black for formatting (line length: 88)
- Follow PEP 8 naming conventions
- Add type hints to all functions
- Use docstrings for public functions and classes

### Error Handling
- Handle encoding detection failures gracefully
- Provide user-friendly error messages in GUI
- Log detailed error information for debugging
- Validate file paths and permissions before processing

### Performance Considerations
- Use pandas chunking for large files (>100MB)
- Implement progress callbacks for long operations
- Avoid loading entire datasets into memory when possible
- Optimize UI responsiveness with threading

### Testing Strategy
- Unit tests for core conversion logic
- Integration tests for file operations
- UI tests for critical user workflows
- Performance tests for large file handling

### Build Process
The build.py script handles:
1. Environment cleanup
2. PyInstaller spec file generation
3. GUI and CLI executable creation
4. Distribution package assembly
5. ZIP archive creation for distribution

### Windows-Specific Considerations
- Handle Japanese file paths and names correctly
- Use virtual environment to avoid Tkinter DLL conflicts
- Ensure proper Tcl/Tk library inclusion in PyInstaller builds
- Virtual environment prevents issues with system Python or FreeCAD Python
- Executables must include all Tkinter dependencies from virtual environment