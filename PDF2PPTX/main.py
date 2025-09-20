#!/usr/bin/env python3
"""
PDF2PNG/PDF2PPTX Converter v3.0 - Main Entry Point

Refactored application with MVP architecture, enhanced UX, and optimized performance.

Key improvements in v3.0:
- MVP (Model-View-Presenter) architecture pattern
- Asynchronous conversion processing
- Enhanced error handling and user feedback
- Modular design with dependency injection
- Windows-optimized build configuration

Usage:
    python main_v3.py              # Launch GUI application
    python main_v3.py --version    # Show version information
    python main_v3.py --help       # Show help information

Features:
- PDF to PNG image conversion with customizable scaling
- PDF to PowerPoint (PPTX) conversion with A3 landscape layout
- Configurable PowerPoint label styling (colors, fonts, position)
- Real-time progress tracking with cancellation support
- Asynchronous processing for responsive UI
- Comprehensive error handling with user-friendly messages

Requirements:
    - Python 3.8+
    - PyMuPDF (fitz) - PDF processing
    - python-pptx - PowerPoint generation
    - Pillow (PIL) - Image processing
    - tkinter - GUI framework (usually included with Python)

Author: PDF2PNG Project
Version: 3.0.0
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
__app_name__ = "PDF2PNG/PDF2PPTX Converter"


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="PDF2PNG Converter",
        description="Convert PDF files to PNG images or PowerPoint presentations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_v3.py                    # Launch GUI application
  python main_v3.py --version          # Show version
  python main_v3.py --test-mode        # Test mode (for build validation)

For detailed usage instructions, see README.md or PDF2PNG_仕様書.md
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

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (planned for future CLI mode)"
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
        # Improve GUI performance on Windows
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Enable DPI awareness
        except (AttributeError, OSError):
            pass  # Ignore if not available


def test_mode() -> int:
    """Run in test mode for build validation."""
    print(f"{__app_name__} v{__version__}")
    print("Test mode: Basic functionality check")

    try:
        # Test basic imports
        from src.config import get_app_config
        from src.core.pdf_processor import PDFProcessor
        from src.utils.path_utils import PathManager

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

        print("")
        print("[SUCCESS] All tests passed successfully!")
        print("Build validation completed.")

        return 0

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main_sync() -> int:
    """Main application entry point (async version)."""
    args = parse_arguments()

    # Handle test mode
    if args.test_mode:
        return test_mode()

    # Handle no-GUI mode - redirect to console version
    if args.no_gui:
        print("Redirecting to console mode...")
        print("Please use: python main_console.py")
        return 1

    # Set up application environment
    setup_application_environment(args)

    try:
        # For GUI mode, redirect to Qt version
        print("GUI mode requires Qt interface.")
        print("Please use: python main_gui.py")
        print("")
        print("For console mode, use: python main_console.py")
        return 1

        logger.info("Application initialized successfully")

        # Run the application
        app.run()

        logger.info("Application shut down normally")
        return 0

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("\nPossible solutions:")
        print("1. Install required dependencies:")
        print("   pip install -r requirements.txt")
        print("\n2. Ensure you're running from the project root directory")
        print("\n3. Check that the src/ directory structure is intact")
        return 1

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0

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


def main() -> int:
    """Main application entry point."""
    try:
        return main_sync()
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    # Enable high DPI support on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI awareness
        except (AttributeError, OSError):
            pass

    # Exit with proper code
    sys.exit(main())