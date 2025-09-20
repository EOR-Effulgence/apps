# PDF2PNG/PDF2PPTX Converter

**Version 3.0 - MVP Architecture with Compiled Executable**

A robust PDF conversion tool that transforms PDF documents into PNG images or PowerPoint presentations with a user-friendly GUI interface. Now includes a standalone Windows executable.

## 🚀 Quick Start

### **Option 1: Standalone Executable (推奨)**
```bash
# Download and run directly (no Python installation required)
dist\PDF2PNG_Converter.exe
```

### **Option 2: Python Development Environment**
```bash
# 1. Activate virtual environment
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

### **Option 3: UV High-Performance Build**
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.ps1 | powershell

# Build with UV (10-100x faster)
.\scripts\build_with_uv.ps1 -Version "3.0.0" -Clean -Test
```

## ✨ Features

- **PDF to PNG Conversion**: Convert PDF pages to high-quality PNG images
- **PDF to PowerPoint**: Create A3 landscape PowerPoint presentations from PDFs
- **Automatic Rotation**: Portrait pages automatically rotated to landscape
- **Customizable Labels**: Configurable fonts, colors, and positioning for PowerPoint labels
- **Batch Processing**: Process entire folders of PDF files at once
- **Progress Tracking**: Real-time progress updates with user feedback
- **Error Handling**: Comprehensive error reporting and recovery

## 📁 Project Structure

```
PDF2PNG/
├── main.py                    # Main entry point for the application
├── requirements.txt           # Python dependencies
├── build_windows.spec        # PyInstaller configuration (v3.0 optimized)
├── venv/                      # Python virtual environment
├── dist/                      # Compiled executable output
│   └── PDF2PNG_Converter.exe  # Standalone Windows executable (37.4MB)
├── PDF2PNG_仕様書.md         # Japanese specification document
├── REFACTORING_REPORT.md     # Detailed refactoring analysis
├──
├── src/                      # Refactored source code
│   ├── __init__.py
│   ├── config.py             # Application configuration management
│   ├── core/                 # Core PDF processing logic
│   │   ├── __init__.py
│   │   └── pdf_processor.py  # Unified PDF conversion engine
│   ├── ui/                   # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main GUI application
│   │   └── converters.py     # UI conversion handlers
│   └── utils/                # Utility modules
│       ├── __init__.py
│       ├── error_handling.py # Error management system
│       └── path_utils.py     # Secure path operations
├──
├── tests/                    # Unit tests
│   ├── __init__.py
│   └── test_pdf_processor.py # Core functionality tests
├──
├── legacy_original/          # Original files (archived)
│   ├── PDF2PPTX.py          # Original main application
│   ├── 1_image_PDF2IMG.py   # Original PNG converter
│   ├── 2_ppt_PAF2PPT.py     # Original PPTX converter
│   ├── reset.py             # Original folder reset utility
│   ├── *.spec               # Original PyInstaller configurations
│   └── migrate_to_refactored.py # Migration helper script
└──
└── sample_outputs/           # Example output files
    ├── Slides_from_Images.pptx
    └── Slides_from_PDF_direct.pptx
```

## 🔧 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: See `requirements.txt`
  - PyMuPDF (fitz) - PDF processing
  - python-pptx - PowerPoint generation
  - Pillow (PIL) - Image processing
  - tkinter - GUI framework (usually included with Python)

## 🖥️ Usage

### GUI Application
```bash
python main.py
```

1. Click "📁 フォルダ選択" to choose a folder containing PDF files
2. Adjust conversion settings (scale, rotation, PowerPoint styling)
3. Click the desired conversion button:
   - "📄 PDF → PNG 変換" for image conversion
   - "📈 PDF → PPTX 変換 (A3 横)" for PowerPoint conversion
4. Wait for processing to complete
5. Output files will be saved in the same folder as the input PDFs

### Command Line (Advanced)
```bash
# Direct module execution
python -m src.ui.main_window

# Or import in Python scripts
from src.core.pdf_processor import PDFProcessor
from src.config import AppConfig
```

## 🏗️ Building Executable

### **Standard PyInstaller Build**
```bash
# Install PyInstaller
pip install pyinstaller

# Build Windows executable
pyinstaller build_windows.spec --clean --noconfirm

# Build using system Python
pyinstaller build_windows.spec --clean --noconfirm

# Find executable in dist/ directory
./dist/PDF2PNG_Converter.exe   # Windows (37.4MB)
```

### **UV High-Performance Build (推奨)**
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.ps1 | powershell

# Run UV-powered build script (10-100x faster)
.\scripts\build_with_uv.ps1 -Version "3.0.0" -Clean -Test -Verbose
```

### **Manual Development Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies
pip install PyMuPDF python-pptx Pillow pyinstaller

# Build executable
pyinstaller build_windows.spec --clean --noconfirm
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 🔄 Version History

### Version 3.0 (Current - MVP Architecture with Compiled Executable)
- ✅ **Compiled Executable**: Standalone Windows EXE (37.4MB)
- ✅ **MVP Architecture**: Model-View-Presenter design pattern
- ✅ **Virtual Environment**: Integrated venv setup for development
- ✅ **Asynchronous Processing**: Non-blocking UI operations
- ✅ **UV Support**: High-performance package management (10-100x faster)
- ✅ **Customizable PowerPoint**: Configurable labels with red borders
- ✅ **Windows Optimization**: DPI awareness and modern theming
- ✅ **Build Automation**: Comprehensive build and test scripts

### Version 1.0 (Legacy - Archived in `legacy_original/`)
- Basic PDF to PNG/PPTX conversion functionality
- Monolithic architecture with code duplication
- Limited error handling and validation

## 📋 Key Improvements in v2.0

| Aspect | v1.0 (Legacy) | v2.0 (Refactored) |
|--------|---------------|-------------------|
| **Architecture** | Monolithic scripts | Modular, testable components |
| **Code Duplication** | ~60% overlap | Unified core logic |
| **Error Handling** | Basic try/catch | Comprehensive error system |
| **Path Security** | Hardcoded paths | Validated, configurable paths |
| **Resource Management** | Manual cleanup | Automatic context managers |
| **Type Safety** | No type hints | Full type annotations |
| **Testing** | No tests | Unit test coverage |
| **Documentation** | Minimal comments | Comprehensive documentation |

## 🐛 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Import Errors**
   - Ensure you're running from the project root directory
   - Check that `src/` directory structure is intact

3. **Permission Errors**
   - Ensure write permissions for output folders
   - Run as administrator if necessary on Windows

4. **Memory Issues**
   - Reduce scale factor for large PDFs
   - Process files in smaller batches

## 🤝 Contributing

1. Follow the established architecture patterns in `src/`
2. Add tests for new functionality in `tests/`
3. Update documentation for any API changes
4. Run type checking: `mypy src/`
5. Format code: `black src/ tests/`

## 📄 License

This project is available under the terms specified in the project repository.

## 📞 Support

For issues, questions, or contributions, please refer to:
- `PDF2PNG_仕様書.md` - Japanese specification document
- `REFACTORING_REPORT.md` - Detailed technical analysis
- Test files in `tests/` directory for usage examples

---

**Note**: The original version files are preserved in `legacy_original/` for reference and compatibility, but the refactored architecture in `src/` is recommended for all new development and usage.