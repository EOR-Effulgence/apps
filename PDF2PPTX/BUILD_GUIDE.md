# PDF2PNG/PDF2PPTX Build & Deployment Guide

**Version**: 3.0.0
**Last Updated**: 2025年9月20日

## 🚀 Quick Start Build

### **Option 1: Ready-to-Use Executable (推奨)**
```bash
# Download and run directly
dist\PDF2PNG_Console.exe --test-mode
dist\PDF2PNG_Console.exe --help
```

### **Option 2: Build from Source**
```bash
# 1. Setup environment
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Build executable
pyinstaller build_console.spec --clean --noconfirm

# 3. Test
dist\PDF2PNG_Console.exe --test-mode
```

## 🔧 Environment Setup

### **Requirements**
- **Python**: 3.8+ (3.11 recommended)
- **Operating System**: Windows 10/11 (x64)
- **Memory**: 4GB RAM minimum
- **Disk Space**: 500MB for development environment

### **Verified Working Environments**
1. **Python.org Standard Installation** ✅ (Recommended)
   - Download from python.org
   - Full feature support including GUI

2. **System Python** ✅ (Alternative)
   - Windows Store Python or system-installed Python
   - Compatible with all features

### **Dependencies Installation**
```bash
# Core dependencies
pip install PyMuPDF>=1.26.0 python-pptx>=1.0.0 Pillow>=11.0.0

# Build tools
pip install pyinstaller>=6.0.0

# Development tools (optional)
pip install pytest mypy black
```

## 🏗️ Build Process

### **Console Version Build (Recommended)**
```bash
# Use console-specific build configuration
pyinstaller build_console.spec --clean --noconfirm

# Output: dist/PDF2PNG_Console.exe (38.9MB)
```

**Features**:
- ✅ Full PDF conversion functionality
- ✅ Command-line interface
- ✅ No GUI dependencies
- ✅ Resolves Tkinter issues

### **GUI Version Build (Standard Python Only)**
```bash
# Requires standard Python environment
pyinstaller build_windows.spec --clean --noconfirm

# Output: dist/PDF2PNG_Converter.exe (40.7MB)
```

**Features**:
- ✅ Graphical user interface
- ⚠️ Requires properly configured Tkinter
- ❌ May have issues in some Python environments

### **UV High-Performance Build**
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.ps1 | powershell

# Build with UV (10-100x faster dependency resolution)
.\scripts\build_with_uv.ps1 -Version "3.0.0" -Clean -Test
```

## 🧪 Testing & Validation

### **Basic Functionality Test**
```bash
# Test executable creation
dist\PDF2PNG_Console.exe --version
# Expected: PDF2PNG/PDF2PPTX Converter (Console) v3.0.0

# Test dependencies
dist\PDF2PNG_Console.exe --test-mode
# Expected: All dependencies verified, All tests passed!

# Test command help
dist\PDF2PNG_Console.exe convert --help
```

### **Build Validation Checklist**
- [ ] Executable file created in `dist/` directory
- [ ] File size reasonable (30-50MB range)
- [ ] Version command returns correct version
- [ ] Test mode passes all dependency checks
- [ ] Help commands work properly
- [ ] No import errors on startup

### **Performance Validation**
```bash
# Startup time test (should be < 5 seconds)
Measure-Command { dist\PDF2PNG_Console.exe --version }

# Memory usage test
# Task Manager: Check memory usage during --test-mode
```

## ⚠️ Known Issues & Solutions

### **Issue 1: Tkinter Runtime Error**
```
FileNotFoundError: Tcl data directory not found
```

**Solution**: Use console version build
```bash
# Use build_console.spec instead of build_windows.spec
pyinstaller build_console.spec --clean --noconfirm
```

**Root Cause**: Some Python environments may have incomplete Tkinter installation

### **Issue 2: Multiprocessing Import Error**
```
ModuleNotFoundError: No module named 'socket'
```

**Solution**: Ensure `socket` in hidden imports
```python
# In .spec file
hiddenimports=[
    'socket',  # Required for multiprocessing
    # ... other imports
]
```

**Status**: ✅ Fixed in current build configurations

### **Issue 3: Unicode Encoding Error**
```
UnicodeEncodeError: 'cp932' codec can't encode character
```

**Solution**: Avoid Unicode symbols in console output
```python
# Replace emoji characters with ASCII
print("PDF2PNG Test Mode")  # Instead of print("🧪 PDF2PNG Test Mode")
```

**Status**: ✅ Fixed in main_console.py

## 📊 Build Configurations Comparison

| Configuration | Output | Size | GUI | Status | Use Case |
|---------------|--------|------|-----|--------|----------|
| `build_console.spec` | PDF2PNG_Console.exe | 38.9MB | ❌ | ✅ Working | **Production** |
| `build_windows.spec` | PDF2PNG_Converter.exe | 40.7MB | ✅ | ⚠️ Limited | Standard Python |
| `build_simple.spec` | PDF2PNG_Converter.exe | 40.7MB | ✅ | ⚠️ Limited | Debugging |

## 🔍 Troubleshooting

### **Build Fails**
1. **Check Python Environment**
   ```bash
   python --version
   pip list | grep -E "(PyMuPDF|python-pptx|Pillow|pyinstaller)"
   ```

2. **Clear Cache and Retry**
   ```bash
   rm -rf build/ dist/ __pycache__/
   pyinstaller build_console.spec --clean --noconfirm
   ```

3. **Verbose Output for Debugging**
   ```bash
   pyinstaller build_console.spec --clean --noconfirm --debug all
   ```

### **Runtime Errors**
1. **Test in Isolation**
   ```bash
   # Run from different directory to test dependencies
   cd /tmp
   /path/to/PDF2PNG_Console.exe --test-mode
   ```

2. **Check System Requirements**
   - Windows 10/11 (64-bit)
   - Visual C++ Redistributable installed
   - No antivirus blocking execution

### **Performance Issues**
1. **Disable Antivirus Scanning**
   - Add `dist/` directory to antivirus exclusions
   - Add PyInstaller cache directory to exclusions

2. **SSD vs HDD**
   - Build on SSD for faster compilation
   - Run from SSD for better startup performance

## 📦 Distribution Packaging

### **Release Package Structure**
```
PDF2PNG_Windows_v3.0.0/
├── PDF2PNG_Console.exe        # Main executable
├── README.md                   # Quick start guide
├── BUILD_GUIDE.md             # This file
├── PDF2PNG_仕様書.md          # Detailed specifications
└── examples/                   # Sample files (optional)
```

### **Automated Packaging**
```bash
# Create release package
mkdir release/PDF2PNG_Windows_v3.0.0
cp dist/PDF2PNG_Console.exe release/PDF2PNG_Windows_v3.0.0/
cp README.md release/PDF2PNG_Windows_v3.0.0/
cp BUILD_GUIDE.md release/PDF2PNG_Windows_v3.0.0/

# Create ZIP archive
Compress-Archive -Path release/PDF2PNG_Windows_v3.0.0/* -DestinationPath release/PDF2PNG_Windows_v3.0.0.zip
```

## 🎯 Build Success Criteria

### **Technical Validation**
- ✅ Executable size: 30-50MB
- ✅ Startup time: < 5 seconds
- ✅ Memory usage: < 100MB (idle)
- ✅ All dependencies embedded
- ✅ No external file dependencies

### **Functional Validation**
- ✅ Version command works
- ✅ Help system functional
- ✅ Test mode passes
- ✅ Core conversion functionality available
- ✅ Error handling graceful

## 🚀 Next Steps

### **Production Deployment**
1. **Security Scanning**: Virus scan executable
2. **User Testing**: Test on clean Windows systems
3. **Documentation**: Update user guides
4. **Distribution**: Upload to release channels

### **Future Improvements**
1. **GUI Version**: Resolve Tkinter issues in standard Python
2. **Cross-Platform**: Linux/macOS builds
3. **Installer**: MSI package for Windows
4. **Auto-Update**: Implement update mechanism

---

**Build Status**: ✅ **Production Ready**
**Recommended Version**: PDF2PNG_Console.exe (38.9MB)
**Last Successful Build**: 2025年9月20日