# PDF2PNG/PDF2PPTX Converter - Getting Started

**Version**: 3.0.0
**Quick Start Guide for New Users**

## 🎯 What is PDF2PNG?

PDF2PNG/PDF2PPTX Converter is a powerful tool that transforms PDF documents into:
- **PNG Images** - High-quality image files for each PDF page
- **PowerPoint Presentations** - A3 landscape slides with customizable labels

## 🚀 Quick Start (3 Steps)

### **Step 1: Download & Run**
```bash
# Option A: Use ready-made executable (Recommended)
dist\PDF2PNG_Console.exe --help

# Option B: Run from source code
python main.py
```

### **Step 2: Test Installation**
```bash
# Verify everything works
dist\PDF2PNG_Console.exe --test-mode

# Expected output:
# PDF2PNG Converter v3.0 - Test Mode
# All dependencies verified
# All tests passed!
```

### **Step 3: Convert Your First PDF**
```bash
# Convert PDF to PNG images
dist\PDF2PNG_Console.exe convert --input document.pdf --output ./images --format png

# Convert PDF to PowerPoint
dist\PDF2PNG_Console.exe convert --input document.pdf --output ./slides --format pptx
```

## 📋 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB
- **Storage**: 500MB free space
- **No Python installation required** (for executable version)

### **For Source Code Usage**
- **Python**: 3.8 or higher (3.11 recommended)
- **Dependencies**: PyMuPDF, python-pptx, Pillow
- **Development**: Git (for cloning repository)

## 🛠️ Installation Options

### **Option 1: Executable Version (Easiest)**
1. Download `PDF2PNG_Console.exe` from releases
2. Run directly - no installation needed
3. Works without Python environment

**Pros**:
- ✅ No setup required
- ✅ Single file execution
- ✅ No dependency conflicts

**Cons**:
- ❌ Console interface only
- ❌ Larger file size (38.9MB)

### **Option 2: Python Source Code**
```bash
# 1. Clone repository
git clone <repository-url>
cd PDF2PNG

# 2. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python main.py  # GUI version
python main_console.py  # Console version
```

**Pros**:
- ✅ Full GUI interface
- ✅ Modifiable source code
- ✅ Latest features

**Cons**:
- ❌ Requires Python setup
- ❌ More complex installation

## 📖 Basic Usage

### **Command Line Interface**
```bash
# Show help
dist\PDF2PNG_Console.exe --help

# Show version
dist\PDF2PNG_Console.exe --version

# Convert to PNG (default)
dist\PDF2PNG_Console.exe convert -i input.pdf -o output_directory

# Convert to PowerPoint
dist\PDF2PNG_Console.exe convert -i input.pdf -o output_directory -f pptx

# Detailed conversion help
dist\PDF2PNG_Console.exe convert --help
```

### **GUI Interface (Source Code)**
```bash
# Activate environment
venv\Scripts\Activate.ps1

# Launch GUI
python main.py

# GUI Steps:
# 1. Click "フォルダ選択" to choose folder with PDFs
# 2. Configure settings (scale, rotation, PowerPoint styling)
# 3. Click conversion button
# 4. Wait for completion
```

## 🎨 Configuration Options

### **PowerPoint Customization**
- **Label Position**: Top-left, top-right, bottom-left, bottom-right
- **Font Settings**: 游ゴシック, size 18, bold
- **Colors**:
  - Text: White (#FFFFFF)
  - Background: Orange (#FF6600)
  - Border: Red (#FF0000) ← Customizable red borders!
- **Label Size**: 30% width, 6% height of slide

### **PNG Conversion Settings**
- **Scale Factor**: 1.0-3.0 (higher = better quality, larger files)
- **Rotation**: Auto-rotate portrait pages to landscape
- **Output Format**: PNG with transparency support

## 🔍 Troubleshooting

### **Common Issues**

#### **1. "Command not found" Error**
```bash
# Solution: Use full path
"C:\path\to\PDF2PNG_Console.exe" --version
```

#### **2. "Permission Denied" Error**
```bash
# Solution: Run as administrator or check antivirus
# Add PDF2PNG_Console.exe to antivirus exceptions
```

#### **3. "No module named X" Error (Source Code)**
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### **4. Slow Performance**
```bash
# Solution: Add to antivirus exclusions
# Exclude: dist/PDF2PNG_Console.exe and temp directories
```

### **Getting Help**
1. **Check Documentation**: See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed setup
2. **Run Test Mode**: `dist\PDF2PNG_Console.exe --test-mode`
3. **Check System Requirements**: Windows 10/11, 64-bit required
4. **File Issues**: Check GitHub issues or create new issue

## 📁 File Organization

### **Input Files**
- Place PDF files in any directory
- Support for multiple PDFs in same folder
- Japanese filenames supported

### **Output Structure**
```
output_directory/
├── document_page_001.png    # PNG conversion
├── document_page_002.png
├── ...
└── Slides_from_PDF.pptx     # PowerPoint conversion
```

### **File Naming**
- **PNG**: `{filename}_page_{page_number}.png`
- **PowerPoint**: `Slides_from_{filename}.pptx`
- **Labels**: Filename displayed on each slide

## 🎯 Next Steps

### **For End Users**
1. **Try the Examples**: Start with simple PDFs
2. **Customize Settings**: Experiment with PowerPoint styling
3. **Batch Processing**: Process entire folders
4. **Explore Features**: Check all available options

### **For Developers**
1. **Read Specifications**: See [PDF2PNG_仕様書.md](PDF2PNG_仕様書.md)
2. **Setup Development**: Follow [DEVELOPMENT.md](DEVELOPMENT.md)
3. **Build Process**: Check [BUILD_GUIDE.md](BUILD_GUIDE.md)
4. **Contribute**: Submit issues and pull requests

## 🎉 Success!

You're now ready to convert PDFs to images and PowerPoint presentations!

**Quick Test Command**:
```bash
dist\PDF2PNG_Console.exe --test-mode
```

If you see "All tests passed!", everything is working correctly.

---

**Need More Help?**
- 📖 **Detailed Guide**: [README.md](README.md)
- 🔧 **Technical Details**: [BUILD_GUIDE.md](BUILD_GUIDE.md)
- 🎨 **Feature Specs**: [PDF2PNG_仕様書.md](PDF2PNG_仕様書.md)