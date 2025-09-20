#!/usr/bin/env python3
"""
PDF2PNG/PDF2PPTX Converter v3.0 - GUI Main Entry Point

PySide6-based GUI application without TCL/Tkinter dependencies.
Provides modern, native look and feel with improved stability.

Usage:
    python main_gui.py              # Launch Qt GUI application
    python main_gui.py --version    # Show version information
    python main_gui.py --test-mode  # Test mode (for build validation)

Features:
- Modern Qt6 interface
- TCL/Tkinter independent
- Native Windows look and feel
- Stable PyInstaller packaging
- Asynchronous conversion processing
- Comprehensive error handling

Requirements:
    - Python 3.8+
    - PySide6 - Modern Qt6 bindings
    - PyMuPDF (fitz) - PDF processing
    - python-pptx - PowerPoint generation
    - Pillow (PIL) - Image processing

Author: PDF2PNG Project
Version: 3.0.0 (Qt Edition)
Date: 2025-09-20
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Add src directory to Python path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Version information
__version__ = "3.0.0"
__app_name__ = "PDF2PNG/PDF2PPTX Converter (GUI)"


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="PDF2PNG GUI Converter",
        description="Convert PDF files to PNG images or PowerPoint presentations (GUI Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_gui.py                   # Launch GUI application
  python main_gui.py --version         # Show version
  python main_gui.py --test-mode       # Test mode (for build validation)

Qt Edition Features:
  - Modern PySide6 interface
  - TCL/Tkinter independent
  - Native Windows appearance
  - Stable packaging with PyInstaller
  - Enhanced error handling
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

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )

    parser.add_argument(
        "--config-dir",
        type=Path,
        help="Custom configuration directory"
    )

    return parser.parse_args()


def setup_application_environment(args: argparse.Namespace) -> None:
    """Set up the application environment."""
    # Set up logging level
    import logging
    logging.basicConfig(level=getattr(logging, args.log_level))

    # Set environment variables if needed
    if args.config_dir:
        os.environ["PDF2PNG_CONFIG_DIR"] = str(args.config_dir)

    # Windows-specific optimizations
    if sys.platform == "win32":
        try:
            import ctypes
            # Enable DPI awareness for sharp display on high-DPI screens
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass  # Ignore if not available


def test_mode() -> int:
    """Run in test mode for build validation."""
    print(f"{__app_name__} v{__version__}")
    print("Test mode: Qt Edition functionality check")

    try:
        # Test PySide6 imports
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        print("[OK] PySide6 imports successful")

        # Test core application imports
        from src.config import get_app_config
        from src.core.pdf_processor import PDFProcessor
        from src.utils.path_utils import PathManager
        from src.ui.qt_main_window import QtMainWindow

        print("[OK] All core modules imported successfully")

        # Test configuration system
        config = get_app_config()
        print(f"[OK] Configuration loaded: {config.window_title}")

        # Test path manager
        path_manager = PathManager()
        print(f"[OK] Path manager initialized: {path_manager.base_path}")

        # Test PDF processor
        pdf_processor = PDFProcessor()
        print("[OK] PDF processor initialized")

        # ConversionService removed - skip test

        # Test Qt application creation (without showing window)
        app = QApplication([])
        app.setApplicationName("PDF2PPTX Test")
        print("[OK] Qt application created successfully")

        # Test main window creation
        window = QtMainWindow()
        print("[OK] Qt main window created successfully")

        print("")
        print("[SUCCESS] All Qt Edition tests passed successfully!")
        print("Build validation completed.")

        return 0

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    """Main application entry point."""
    args = parse_arguments()

    # Handle test mode
    if args.test_mode:
        return test_mode()

    # Set up application environment
    setup_application_environment(args)

    try:
        # Import Qt GUI components
        from src.ui.qt_main_window import main as qt_main
        from src.utils.error_handling import setup_logging

        # Set up logging
        log_file = PROJECT_ROOT / "logs" / "qt_application.log"
        logger = setup_logging(log_file, level=args.log_level)
        logger.info(f"Starting {__app_name__} v{__version__}")

        # Run Qt application
        logger.info("Launching Qt GUI application")
        return qt_main()

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("\nPossible solutions:")
        print("1. Install required dependencies:")
        print("   pip install PySide6")
        print("   pip install -r requirements.txt")
        print("\n2. Ensure you're running from the project root directory")
        print("\n3. Check that the src/ directory structure is intact")
        return 1

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        print("\nThis appears to be a bug. Please check:")
        print("1. All dependencies are properly installed")
        print("2. No files are missing from the src/ directory")
        print("3. You have proper permissions to read/write project files")

        # Log detailed error information
        if args.log_level == "DEBUG":
            import traceback
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    # Enable high DPI support on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            # Per-monitor DPI awareness v2
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            pass

    # Exit with proper code
    sys.exit(main())