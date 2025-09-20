"""
Argument parsers for CLI commands.
Provides comprehensive argument parsing with validation and help.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional


def create_main_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser with all subcommands.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="pdf2pptx",
        description="Convert PDF files to PNG images or PowerPoint presentations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDFs in current directory to PNG images
  pdf2pptx convert png --input-dir ./pdfs --output-dir ./images

  # Convert specific PDF to PowerPoint with custom settings
  pdf2pptx convert pptx document.pdf --scale 2.0 --auto-rotate

  # Reset input/output directories
  pdf2pptx reset --confirm

  # Show detailed help for convert command
  pdf2pptx convert --help

For more information, visit: https://github.com/your-repo/pdf2pptx
        """
    )

    # Global options
    parser.add_argument(
        "--version",
        action="version",
        version="PDF2PPTX Converter v3.0"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-essential output"
    )

    parser.add_argument(
        "--config-dir",
        type=Path,
        help="Custom configuration directory"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands",
        help="Command to execute",
        dest="command"
    )

    # Convert command
    _add_convert_parser(subparsers)

    # Reset command
    _add_reset_parser(subparsers)

    # Info command
    _add_info_parser(subparsers)

    # Config command
    _add_config_parser(subparsers)

    return parser


def _add_convert_parser(subparsers) -> None:
    """Add convert command parser."""
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert PDF files to images or PowerPoint",
        description="Convert PDF files to PNG images or PowerPoint presentations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to PNG images with default settings
  pdf2pptx convert png file1.pdf file2.pdf

  # Convert to PowerPoint with custom scale
  pdf2pptx convert pptx --scale 2.0 --output output.pptx *.pdf

  # Batch convert all PDFs in directory
  pdf2pptx convert png --input-dir ./pdfs --output-dir ./images
        """
    )

    # Output format subcommands
    format_subparsers = convert_parser.add_subparsers(
        title="output formats",
        description="Available output formats",
        help="Output format",
        dest="format"
    )

    # PNG conversion
    png_parser = format_subparsers.add_parser(
        "png",
        help="Convert to PNG images",
        description="Convert PDF files to high-quality PNG images"
    )
    _add_common_convert_options(png_parser)
    _add_image_specific_options(png_parser)

    # PPTX conversion
    pptx_parser = format_subparsers.add_parser(
        "pptx",
        help="Convert to PowerPoint presentation",
        description="Convert PDF files to PowerPoint presentation"
    )
    _add_common_convert_options(pptx_parser)
    _add_pptx_specific_options(pptx_parser)

    # Set command function
    from .commands import ConvertCommand
    convert_parser.set_defaults(func=ConvertCommand().execute)


def _add_common_convert_options(parser: argparse.ArgumentParser) -> None:
    """Add common conversion options."""
    # Input specification
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="PDF files to convert"
    )
    input_group.add_argument(
        "--input-dir",
        type=Path,
        help="Directory containing PDF files"
    )

    # Output specification
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: ./output)"
    )

    # Conversion settings
    parser.add_argument(
        "--scale",
        type=float,
        default=1.5,
        help="Scale factor for images (default: 1.5)"
    )

    parser.add_argument(
        "--auto-rotate",
        action="store_true",
        default=True,
        help="Auto-rotate portrait pages to landscape (default: enabled)"
    )

    parser.add_argument(
        "--no-auto-rotate",
        action="store_false",
        dest="auto_rotate",
        help="Disable auto-rotation"
    )

    # Processing options
    parser.add_argument(
        "--threads",
        type=int,
        default=2,
        help="Number of processing threads (default: 2)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually converting"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files"
    )


def _add_image_specific_options(parser: argparse.ArgumentParser) -> None:
    """Add image-specific conversion options."""
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Target DPI for images (default: 150)"
    )

    parser.add_argument(
        "--format",
        choices=["png", "jpeg", "tiff"],
        default="png",
        help="Image format (default: png)"
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="JPEG quality (1-100, default: 95)"
    )


def _add_pptx_specific_options(parser: argparse.ArgumentParser) -> None:
    """Add PowerPoint-specific conversion options."""
    parser.add_argument(
        "--output",
        type=Path,
        help="Output PowerPoint file name"
    )

    parser.add_argument(
        "--slide-size",
        choices=["A3", "A4", "16:9", "4:3", "custom"],
        default="A3",
        help="Slide size (default: A3)"
    )

    parser.add_argument(
        "--slide-width",
        type=float,
        help="Custom slide width in mm"
    )

    parser.add_argument(
        "--slide-height",
        type=float,
        help="Custom slide height in mm"
    )

    # Label settings
    label_group = parser.add_argument_group("label settings")
    label_group.add_argument(
        "--label-position",
        choices=["top-left", "top-right", "bottom-left", "bottom-right", "none"],
        default="bottom-right",
        help="Label position (default: bottom-right)"
    )

    label_group.add_argument(
        "--label-font",
        default="Arial",
        help="Label font family (default: Arial)"
    )

    label_group.add_argument(
        "--label-size",
        type=int,
        default=12,
        help="Label font size (default: 12)"
    )

    label_group.add_argument(
        "--label-color",
        default="#000000",
        help="Label text color (default: #000000)"
    )


def _add_reset_parser(subparsers) -> None:
    """Add reset command parser."""
    reset_parser = subparsers.add_parser(
        "reset",
        help="Reset input/output directories",
        description="Clean up input and output directories"
    )

    reset_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )

    reset_parser.add_argument(
        "--input-only",
        action="store_true",
        help="Reset only input directory"
    )

    reset_parser.add_argument(
        "--output-only",
        action="store_true",
        help="Reset only output directory"
    )

    # Set command function
    from .commands import ResetCommand
    reset_parser.set_defaults(func=ResetCommand().execute)


def _add_info_parser(subparsers) -> None:
    """Add info command parser."""
    info_parser = subparsers.add_parser(
        "info",
        help="Show information about PDF files",
        description="Display detailed information about PDF files"
    )

    info_parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="PDF files to analyze"
    )

    info_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed page information"
    )

    # Set command function
    from .commands import InfoCommand
    info_parser.set_defaults(func=InfoCommand().execute)


def _add_config_parser(subparsers) -> None:
    """Add config command parser."""
    config_parser = subparsers.add_parser(
        "config",
        help="Manage application configuration",
        description="View and modify application configuration"
    )

    config_subparsers = config_parser.add_subparsers(
        title="config commands",
        description="Configuration management commands",
        help="Config command",
        dest="config_command"
    )

    # Show config
    show_parser = config_subparsers.add_parser(
        "show",
        help="Show current configuration"
    )

    # Set config
    set_parser = config_subparsers.add_parser(
        "set",
        help="Set configuration value"
    )
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Configuration value")

    # Reset config
    reset_parser = config_subparsers.add_parser(
        "reset",
        help="Reset configuration to defaults"
    )

    # Set command function
    from .commands import ConfigCommand
    config_parser.set_defaults(func=ConfigCommand().execute)