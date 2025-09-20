"""
PDF2PNG/PDF2PPTX Converter Application

A refactored PDF conversion tool with improved architecture, error handling,
and maintainability. Supports conversion from PDF to PNG images and PowerPoint
presentations with automatic orientation correction.

Architecture Overview:
---------------------

src/
├── core/                    # Core business logic (no UI dependencies)
│   └── pdf_processor.py     # PDF processing and conversion utilities
├── ui/                      # User interface layer
│   ├── main_window.py       # Main GUI application
│   └── converters.py        # Conversion implementations
├── utils/                   # Utility modules
│   ├── error_handling.py    # Error handling and user feedback
│   └── path_utils.py        # File system operations
└── config.py               # Configuration management

Key Improvements:
----------------

1. **Code Deduplication**: Unified PDF processing logic eliminates ~60% duplication
2. **Error Handling**: Comprehensive error handling with user-friendly messages
3. **Type Safety**: Full type hints and validation throughout
4. **Resource Management**: Proper cleanup and memory management
5. **Modular Architecture**: Clear separation of concerns
6. **Configuration**: Centralized, persistent configuration management
7. **Testing**: Testable architecture with dependency injection
8. **Security**: Path traversal protection and input validation

Usage Examples:
--------------

# GUI Application
from src.ui.main_window import main
main()

# Programmatic Usage
from src.core.pdf_processor import ConversionConfig, open_pdf_document
from src.utils.path_utils import PathManager

config = ConversionConfig(scale_factor=2.0, auto_rotate=True)
path_manager = PathManager()
# ... conversion logic

Migration Guide:
---------------

Old → New:
- PDF2PPTX.py → src/ui/main_window.py (GUI)
- 1_image_PDF2IMG.py → src/ui/converters.ImageConverter
- 2_ppt_PAF2PPT.py → src/ui/converters.PPTXConverter
- reset.py → path_manager.clean_directory()

Version: 2.0.0 (Refactored)
"""

# Version information
__version__ = "3.0.0"
__version_info__ = (3, 0, 0)
__author__ = "PDF2PPTX Project"
__email__ = "support@pdf2pptx.example.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 PDF2PPTX Project"

# Package metadata
__title__ = "PDF2PPTX Converter"
__description__ = "Professional PDF to PNG/PowerPoint conversion tool"
__url__ = "https://github.com/example/pdf2pptx"

# Public API exports
from .core.pdf_processor import PDFProcessor, ConversionConfig
from .core.image_converter import ImageConversionService
from .core.powerpoint_converter import PowerPointConversionService
from .utils.error_handling import (
    UserFriendlyError,
    ErrorSeverity,
    PDFConversionError,
    FileSystemError,
    ValidationError
)
from .utils.path_utils import PathManager
from .config import get_app_config, ApplicationConfig

__all__ = [
    # Version info
    "__version__",
    "__version_info__",
    "__author__",
    "__title__",
    "__description__",

    # Core functionality
    "PDFProcessor",
    "ConversionConfig",
    "ImageConversionService",
    "PowerPointConversionService",

    # Error handling
    "UserFriendlyError",
    "ErrorSeverity",
    "PDFConversionError",
    "FileSystemError",
    "ValidationError",

    # Utilities
    "PathManager",

    # Configuration
    "get_app_config",
    "ApplicationConfig"
]


# Module level functions for convenience
def create_pdf_processor(config: ConversionConfig = None) -> PDFProcessor:
    """
    Create a PDFProcessor instance with optional configuration.

    Args:
        config: Optional conversion configuration

    Returns:
        Configured PDFProcessor instance
    """
    return PDFProcessor(config)


def create_image_converter(config: ConversionConfig = None) -> ImageConversionService:
    """
    Create an ImageConversionService instance.

    Args:
        config: Optional conversion configuration

    Returns:
        Configured ImageConversionService instance
    """
    if config is None:
        config = ConversionConfig()
    return ImageConversionService(config)


def create_powerpoint_converter(config: ConversionConfig = None) -> PowerPointConversionService:
    """
    Create a PowerPointConversionService instance.

    Args:
        config: Optional conversion configuration

    Returns:
        Configured PowerPointConversionService instance
    """
    if config is None:
        config = ConversionConfig()
    return PowerPointConversionService(config)


# Add convenience functions to __all__
__all__.extend([
    "create_pdf_processor",
    "create_image_converter",
    "create_powerpoint_converter"
])