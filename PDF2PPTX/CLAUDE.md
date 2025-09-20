# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## natural-language
 日本語で回答して

## Project Overview

CSV2XLSX_IC is a Windows desktop application for converting between CSV and Excel (XLSX) files. It supports both GUI (classic and modern) and CLI interfaces, with features like drag-and-drop, automatic encoding detection, and batch processing.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install modern UI dependencies (optional)
pip install -r requirements_modern.txt
```

### Running the Application
```bash
# Unified GUI version (recommended)
uv run python src\app.py
# Or use batch file
csv2xlsx_app.bat

# CLI version
python src\cli.py --help
# Or use batch file
csv2xlsx_cli.bat csv2xlsx file1.csv file2.csv --output result.xlsx
```

### Testing
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_converter.py
pytest tests/test_integration.py

# Run tests with coverage
pytest --cov=src tests/
```

### Code Quality
```bash
# Format code
black src tests

# Lint code
ruff src tests

# Type checking
mypy src

# Security check
bandit -r src
```

### Building Executables
```bash
# Automated build (recommended)
python build.py

# Quick build (minimal setup)
quick_build.bat

# Manual build with PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed --name CSV2XLSX_GUI src\main.py
pyinstaller --onefile --console --name CSV2XLSX_CLI src\cli.py
```

## Architecture

### Core Components
- **src/converter.py**: Core conversion logic for CSV ↔ XLSX operations
- **src/main.py**: Classic GUI implementation using tkinter
- **src/modern_gui.py**: Modern GUI using CustomTkinter with animations
- **src/cli.py**: Command-line interface
- **src/animations.py**: Animation utilities for modern GUI

### Key Features
- **Encoding Detection**: Automatic detection of CSV encoding (UTF-8/Shift_JIS)
- **Batch Processing**: Multiple CSV files to single XLSX workbook
- **Multi-sheet Export**: XLSX to multiple CSV files (one per sheet)
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Handling**: Comprehensive error handling for file operations

### File Structure
```
src/
├── __init__.py
├── app.py           # Unified GUI entry point (recommended)
├── cli.py           # CLI entry point
└── converter.py     # Core conversion logic

tests/
├── test_converter.py     # Unit tests
├── test_integration.py   # Integration tests
└── test_data_*.csv      # Test data files

docs/
├── BUILD_CHECKLIST.md
└── WINDOWS_BUILD_GUIDE.md
```

### GUI Framework
- **Unified GUI**: CustomTkinter with tkinterdnd2 for modern styling and drag-and-drop
- **Features**: Dark mode support, animations, toast notifications, progress visualization
- **Shared Logic**: Common conversion logic in converter.py

### Dependencies
- **Core**: pandas, openpyxl for data processing
- **GUI**: tkinter (built-in), tkinterdnd2, customtkinter
- **CLI**: click for command-line interface
- **Build**: PyInstaller for executable creation
- **Development**: pytest, black, ruff, mypy, bandit

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
- Support Shift_JIS encoding for legacy CSV files
- Create Windows-specific batch files for easy launching
- Ensure executables work without Python installation