#!/usr/bin/env python3
"""
PDF2PNG/PDF2PPTX Converter v3.0 - Console Mode Entry Point

Standalone console version that bypasses Tkinter issues in FreeCAD environment.
This version provides basic PDF conversion functionality through command line.

Usage:
    python main_console.py --help
    python main_console.py convert --input input.pdf --output output_dir --format png

Author: PDF2PNG Project
Version: 3.0.0
Date: 2025-09-20
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Version information
__version__ = "3.0.0"
__app_name__ = "PDF2PNG/PDF2PPTX Converter (Console)"


def test_mode():
    """Test mode for build validation."""
    print("PDF2PNG Converter v3.0 - Test Mode")
    print("Console application initialized successfully")
    print("Python environment: OK")
    print("Dependencies check:")

    try:
        import fitz
        print(f"   PyMuPDF: {fitz.__version__}")
    except ImportError as e:
        print(f"   PyMuPDF: {e}")
        return False

    try:
        import pptx
        print(f"   python-pptx: {pptx.__version__}")
    except ImportError as e:
        print(f"   python-pptx: {e}")
        return False

    try:
        from PIL import Image
        print(f"   Pillow: {Image.__version__}")
    except ImportError as e:
        print(f"   Pillow: {e}")
        return False

    print("All dependencies verified")
    print("Build validation completed successfully")
    print("\nAll tests passed!")
    return True


def convert_pdf(input_path: str, output_dir: str, format_type: str):
    """Convert PDF using core functionality."""
    try:
        from src.core.pdf_processor import PDFProcessor
        from src.config import AppConfig

        config = AppConfig()
        processor = PDFProcessor(config)

        input_file = Path(input_path)
        output_path = Path(output_dir)

        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            return False

        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Converting {input_file.name} to {format_type.upper()}...")

        if format_type.lower() == "png":
            success = processor.convert_to_images(input_file, output_path)
        elif format_type.lower() == "pptx":
            success = processor.convert_to_powerpoint(input_file, output_path)
        else:
            print(f"Unsupported format: {format_type}")
            return False

        if success:
            print(f"Conversion completed successfully")
            print(f"   Output directory: {output_path}")
            return True
        else:
            print(f"Conversion failed")
            return False

    except Exception as e:
        print(f"Conversion error: {e}")
        return False


def main():
    """Main entry point for console application."""
    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description="PDF to PNG/PPTX conversion tool (Console Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_console.py --version
  python main_console.py --test-mode
  python main_console.py convert --input document.pdf --output ./output --format png
  python main_console.py convert --input document.pdf --output ./output --format pptx
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{__app_name__} v{__version__}"
    )

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode (for build validation)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert PDF files")
    convert_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input PDF file path"
    )
    convert_parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory path"
    )
    convert_parser.add_argument(
        "--format", "-f",
        choices=["png", "pptx"],
        default="png",
        help="Output format (default: png)"
    )

    args = parser.parse_args()

    if args.test_mode:
        success = test_mode()
        sys.exit(0 if success else 1)

    if args.command == "convert":
        success = convert_pdf(args.input, args.output, args.format)
        sys.exit(0 if success else 1)

    if not args.command:
        print(f"{__app_name__} v{__version__}")
        print("Console mode - Tkinter GUI not available in this build")
        print("Use --help for available commands")
        print("\nFor GUI version, use regular Python environment:")
        print("  python main.py")
        sys.exit(0)


if __name__ == "__main__":
    main()