# PDF2PNG/PDF2PPTX Converter

**Version 3.0 - MVP Architecture with Compiled Executable**

A robust PDF conversion tool that transforms PDF documents into PNG images or PowerPoint presentations with a user-friendly GUI interface. Now includes a standalone Windows executable.

## 🚀 Quick Start

### **⚠️ 重要: Virtual Environment の使用が必須です**

**このプロジェクトでは、Tkinterの安定動作のためにプロジェクト内の仮想環境 (`venv/`) を必須で使用してください。**

### **Option 1: Console版実行ファイル (推奨・完全動作)**
```bash
# すぐに使える - TCL依存問題なし
dist\PDF2PNG_Console.exe --help
dist\PDF2PNG_Console.exe --test-mode

# PDF変換実行例
dist\PDF2PNG_Console.exe convert --input document.pdf --format png
```

### **Option 2: 仮想環境GUI版 (完全動作)**
```bash
# 1. Activate virtual environment (REQUIRED)
venv\Scripts\activate

# 2. Run GUI version (works perfectly in venv)
python main.py
```

### **Option 2: Virtual Environment Development**
```bash
# 1. Create virtual environment (if not exists)
python -m venv venv

# 2. Activate virtual environment (REQUIRED)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 4. Run the application
python main.py
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
# ALWAYS activate virtual environment first
venv\Scripts\activate

# Then run the application
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
# ALWAYS activate virtual environment first
venv\Scripts\activate

# Direct module execution
python -m src.ui.main_window

# Console version
python main_console.py

# Or import in Python scripts
from src.core.pdf_processor import PDFProcessor
from src.config import AppConfig
```

## 🏗️ Building Executable

### **Virtual Environment + PyInstaller Build (必須)**
```bash
# 1. Activate virtual environment (REQUIRED)
venv\Scripts\activate

# 2. Ensure PyInstaller is installed in venv
pip install pyinstaller

# 3. Build Windows executable
pyinstaller build_windows.spec --clean --noconfirm

# 4. Build Console version
pyinstaller build_console.spec --clean --noconfirm

# 5. Find executables in dist/ directory
./dist/PDF2PNG_Converter.exe   # Windows GUI (37.4MB)
./dist/PDF2PNG_Console.exe      # Console version
```

### **Manual Development Setup (推奨セットアップ)**
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment (REQUIRED)
venv\Scripts\activate

# 3. Verify virtual environment is active
where python
# Should show: G:\works\apps\PDF2PPTX\venv\Scripts\python.exe

# 4. Install all dependencies
pip install -r requirements.txt
pip install pyinstaller

# 5. Build executable
pyinstaller build_windows.spec --clean --noconfirm
```

## 🧪 Testing

Run the test suite:

```bash
# ALWAYS activate virtual environment first
venv\Scripts\activate

# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 🔄 Version History

### Version 3.0 (Current - 2025-09-20 開発状況)

#### ✅ **完了した開発**
- **Compiled Executable**: Standalone Windows EXE (40.5MB) - GUI版とConsole版
- **MVP Architecture**: Model-View-Presenter design pattern
- **Virtual Environment**: 仮想環境での安定動作確認済み
- **Console版**: 完全動作確認済み (`dist\PDF2PNG_Console.exe`)
- **Core機能**: PDF→PNG/PPTX変換エンジン完成
- **Configuration System**: JSON設定保存・読み込み機能
- **Error Handling**: 包括的エラーハンドリングシステム
- **Path Management**: セキュアなパス管理とバリデーション
- **Build System**: PyInstaller設定とビルドプロセス

#### 🚧 **現在の課題**
- **GUI版 Tkinter問題**: TCL/Tkライブラリ依存によるexe実行時エラー
  ```
  FileNotFoundError: Tcl data directory "_tcl_data" not found
  ```

#### 🔄 **進行中の解決策**
- **PySide6への移行**: TCL非依存のQt GUIフレームワーク採用
  - ✅ PySide6インストール完了
  - 🚧 QtMainWindow実装中 (`src/ui/qt_main_window.py`)
  - ⏳ main_qt.py エントリーポイント作成予定
  - ⏳ PyInstaller Qt仕様書作成予定
  - ⏳ Qt版exe生成・テスト予定

#### 📋 **技術仕様**
- **動作確認済み**: Console版 (`dist\PDF2PNG_Console.exe`)
- **依存関係**: PyMuPDF 1.26.4, python-pptx 1.0.2, Pillow 11.3.0
- **開発環境**: Python 3.11.10 (仮想環境)
- **ビルド**: PyInstaller 6.16.0
- **新フレームワーク**: PySide6 6.9.2 (Qt6ベース)

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

### Current Status (2025-09-20)

#### ✅ **動作確認済み**
- **Console版**: `dist\PDF2PNG_Console.exe` - 完全動作
- **仮想環境**: GUI版 `python main.py` - 正常動作
- **Core機能**: PDF変換エンジン - テスト通過

#### ❌ **既知の問題**
- **GUI版exe**: Tkinter TCL依存問題でクラッシュ
- **解決策**: PySide6への移行作業中

### Common Issues

1. **Tkinter Runtime Errors** (現在の主要課題)
   ```bash
   # 問題: GUI版exeが起動しない
   # Error: FileNotFoundError: Tcl data directory "_tcl_data" not found

   # 解決策1: Console版を使用 (完全動作)
   dist\PDF2PNG_Console.exe --help

   # 解決策2: 仮想環境でPython実行 (GUI完全動作)
   venv\Scripts\activate
   python main.py

   # 解決策3: Qt版開発中 (次バージョン予定)
   # PySide6ベースでTCL非依存
   ```

2. **Missing Dependencies**
   ```bash
   # Activate virtual environment first
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Import Errors**
   - Ensure virtual environment is activated
   - Ensure you're running from the project root directory
   - Check that `src/` directory structure is intact

4. **Build Errors**
   - Always build from within the virtual environment
   - Do not use FreeCAD Python or system Python for building

5. **Permission Errors**
   - Ensure write permissions for output folders
   - Run as administrator if necessary on Windows

6. **Memory Issues**
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