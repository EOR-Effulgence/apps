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
import asyncio
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
        from src.application.services.conversion_service import ConversionService
        from src.utils.path_utils import PathManager

        print("✅ All core modules imported successfully")

        # Test configuration system
        config = get_app_config()
        print(f"✅ Configuration loaded: {config.window_title}")

        # Test path manager
        path_manager = PathManager()
        print(f"✅ Path manager initialized: {path_manager.base_path}")

        # Test PDF processor
        pdf_processor = PDFProcessor()
        print("✅ PDF processor initialized")

        # Test conversion service
        conversion_service = ConversionService(path_manager)
        print("✅ Conversion service initialized")

        print("")
        print("🎉 All tests passed successfully!")
        print("Build validation completed.")

        return 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


async def main_async() -> int:
    """Main application entry point (async version)."""
    args = parse_arguments()

    # Handle test mode
    if args.test_mode:
        return test_mode()

    # Handle no-GUI mode (placeholder for future CLI implementation)
    if args.no_gui:
        print("CLI mode is not yet implemented.")
        print("Please run without --no-gui flag to use the GUI interface.")
        return 1

    # Set up application environment
    setup_application_environment(args)

    try:
        # Import GUI components
        from src.ui.main_window import MainWindow
        from src.application.services.conversion_service import ConversionService
        from src.presentation.presenters.main_presenter import MainPresenter
        from src.utils.path_utils import PathManager
        from src.utils.error_handling import setup_logging

        # Set up logging
        log_file = PROJECT_ROOT / "logs" / "application.log"
        logger = setup_logging(log_file, level=args.log_level)
        logger.info(f"Starting {__app_name__} v{__version__}")

        # Initialize core components
        path_manager = PathManager()
        conversion_service = ConversionService(path_manager)

        # Create and run GUI application
        app = MainWindow()
        presenter = MainPresenter(app, conversion_service)

        # Initialize presenter
        await presenter.initialize()

        # Bind presenter to view
        app.set_presenter(presenter)

        logger.info("Application initialized successfully")

        # Run the application
        app.run()

        logger.info("Application shut down normally")
        return 0

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Install required dependencies:")
        print("   pip install -r requirements.txt")
        print("\n2. Ensure you're running from the project root directory")
        print("\n3. Check that the src/ directory structure is intact")
        return 1

    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n🐛 This appears to be a bug. Please check:")
        print("1. All dependencies are properly installed")
        print("2. No files are missing from the src/ directory")
        print("3. You have proper permissions to read/write project files")

        # Log detailed error information
        if args.log_level == "DEBUG":
            import traceback
            traceback.print_exc()

        return 1


def main() -> int:
    """Main application entry point (sync wrapper)."""
    try:
        # Check if we're running in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we reach here, we're already in an event loop
            # This shouldn't happen in normal usage, but handle gracefully
            print("Warning: Already running in an event loop")
            return asyncio.create_task(main_async()).result()
        except RuntimeError:
            # No event loop running, which is the normal case
            return asyncio.run(main_async())

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