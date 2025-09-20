"""
CLI command implementations for PDF2PPTX application.
Provides modular command structure with comprehensive functionality.
"""

from __future__ import annotations

import logging
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
import argparse

from ..core.pdf_processor import ConversionConfig, PDFProcessor
from ..core.image_converter import ImageConversionService
from ..core.powerpoint_converter import PowerPointConversionService
from ..utils.path_utils import PathManager
from ..utils.error_handling import UserFriendlyError
from ..config import get_app_config, save_app_config
from .utils import CLIFormatter, CLIProgressTracker


class BaseCommand(ABC):
    """
    Abstract base class for CLI commands.
    """

    def __init__(self):
        self.path_manager = PathManager()

    @abstractmethod
    def execute(
        self,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """
        Execute the command.

        Args:
            args: Parsed command line arguments
            formatter: CLI output formatter
            logger: Logger instance

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        pass

    def _validate_files(self, files: List[Path]) -> List[Path]:
        """Validate and filter PDF files."""
        valid_files = []
        for file_path in files:
            if not file_path.exists():
                raise UserFriendlyError(f"File not found: {file_path}")
            if not file_path.is_file():
                raise UserFriendlyError(f"Not a file: {file_path}")
            if file_path.suffix.lower() != '.pdf':
                raise UserFriendlyError(f"Not a PDF file: {file_path}")
            valid_files.append(file_path)
        return valid_files

    def _create_conversion_config(self, args: argparse.Namespace) -> ConversionConfig:
        """Create conversion configuration from arguments."""
        return ConversionConfig(
            scale_factor=getattr(args, 'scale', 1.5),
            auto_rotate=getattr(args, 'auto_rotate', True),
            target_dpi=getattr(args, 'dpi', 150),
            slide_width_mm=getattr(args, 'slide_width', 420.0),
            slide_height_mm=getattr(args, 'slide_height', 297.0)
        )


class ConvertCommand(BaseCommand):
    """Command for converting PDF files."""

    def execute(
        self,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """Execute PDF conversion."""
        try:
            # Determine input files
            files = self._get_input_files(args)
            if not files:
                formatter.error("No PDF files found to convert")
                return 1

            # Validate files
            valid_files = self._validate_files(files)
            formatter.info(f"Found {len(valid_files)} valid PDF file(s)")

            # Show dry run information
            if getattr(args, 'dry_run', False):
                return self._show_dry_run(args, valid_files, formatter)

            # Create output directory
            output_dir = self._prepare_output_directory(args)

            # Create conversion configuration
            config = self._create_conversion_config(args)

            # Execute conversion based on format
            if args.format == 'png':
                return self._convert_to_images(valid_files, config, output_dir, args, formatter, logger)
            elif args.format == 'pptx':
                return self._convert_to_pptx(valid_files, config, output_dir, args, formatter, logger)
            else:
                formatter.error(f"Unsupported format: {args.format}")
                return 1

        except UserFriendlyError as e:
            formatter.error(str(e))
            if e.suggestion:
                formatter.info(f"Suggestion: {e.suggestion}")
            return 1
        except KeyboardInterrupt:
            formatter.warning("Conversion cancelled by user")
            return 130
        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            formatter.error(f"Conversion failed: {e}")
            return 1

    def _get_input_files(self, args: argparse.Namespace) -> List[Path]:
        """Get list of input files from arguments."""
        if hasattr(args, 'files') and args.files:
            return list(args.files)
        elif hasattr(args, 'input_dir') and args.input_dir:
            if not args.input_dir.exists():
                raise UserFriendlyError(f"Input directory not found: {args.input_dir}")
            return list(args.input_dir.glob("*.pdf"))
        else:
            # Look in current directory
            return list(Path.cwd().glob("*.pdf"))

    def _prepare_output_directory(self, args: argparse.Namespace) -> Path:
        """Prepare output directory."""
        if hasattr(args, 'output_dir') and args.output_dir:
            output_dir = args.output_dir
        else:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _show_dry_run(
        self,
        args: argparse.Namespace,
        files: List[Path],
        formatter: CLIFormatter
    ) -> int:
        """Show what would be done in dry run mode."""
        formatter.header("Dry Run - Conversion Plan")
        formatter.info(f"Input files: {len(files)}")

        for i, file_path in enumerate(files, 1):
            formatter.info(f"  {i}. {file_path.name} ({file_path.stat().st_size / 1024:.1f} KB)")

        output_dir = self._prepare_output_directory(args)
        formatter.info(f"Output directory: {output_dir}")
        formatter.info(f"Output format: {args.format.upper()}")

        config = self._create_conversion_config(args)
        formatter.info(f"Scale factor: {config.scale_factor}")
        formatter.info(f"Auto-rotate: {config.auto_rotate}")

        if args.format == 'png':
            formatter.info(f"Target DPI: {config.target_dpi}")
        else:
            formatter.info(f"Slide size: {config.slide_width_mm}x{config.slide_height_mm}mm")

        formatter.success("Dry run completed - no files were processed")
        return 0

    def _convert_to_images(
        self,
        files: List[Path],
        config: ConversionConfig,
        output_dir: Path,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """Convert PDFs to images."""
        formatter.header("Converting PDFs to PNG Images")

        # Create progress tracker
        total_files = len(files)
        progress_tracker = CLIProgressTracker(formatter, total_files)

        # Initialize image converter
        converter = ImageConversionService(config)
        converter.set_progress_callback(progress_tracker.update)

        successful_conversions = 0
        all_output_files = []

        for i, file_path in enumerate(files):
            try:
                formatter.info(f"Processing {file_path.name}... ({i+1}/{total_files})")

                # Convert single file
                output_files = converter.convert_pdf_to_images(file_path, output_dir)
                all_output_files.extend(output_files)
                successful_conversions += 1

                formatter.success(f"✓ {file_path.name} → {len(output_files)} images")

            except Exception as e:
                logger.error(f"Failed to convert {file_path}: {e}")
                formatter.error(f"✗ {file_path.name}: {e}")
                continue

        # Show summary
        formatter.header("Conversion Summary")
        formatter.info(f"Files processed: {successful_conversions}/{total_files}")
        formatter.info(f"Images generated: {len(all_output_files)}")
        formatter.info(f"Output directory: {output_dir}")

        if successful_conversions == total_files:
            formatter.success("All conversions completed successfully!")
            return 0
        elif successful_conversions > 0:
            formatter.warning("Some conversions failed - check logs for details")
            return 2
        else:
            formatter.error("All conversions failed")
            return 1

    def _convert_to_pptx(
        self,
        files: List[Path],
        config: ConversionConfig,
        output_dir: Path,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """Convert PDFs to PowerPoint."""
        formatter.header("Converting PDFs to PowerPoint Presentation")

        # Determine output file
        if hasattr(args, 'output') and args.output:
            output_file = output_dir / args.output
        else:
            # Use first file name as base
            base_name = files[0].stem if files else "converted"
            output_file = output_dir / f"{base_name}.pptx"

        # Create progress tracker
        progress_tracker = CLIProgressTracker(formatter, len(files))

        # Initialize PowerPoint converter
        converter = PowerPointConversionService(config)
        converter.set_progress_callback(progress_tracker.update)

        try:
            formatter.info(f"Creating PowerPoint presentation...")
            formatter.info(f"Output file: {output_file}")

            # Convert all files to single presentation
            result_file = converter.convert_multiple_pdfs_to_single_presentation(
                files, output_file
            )

            # Show summary
            formatter.header("Conversion Summary")
            formatter.info(f"Files processed: {len(files)}")
            formatter.info(f"PowerPoint file: {result_file}")
            formatter.success("PowerPoint conversion completed successfully!")

            return 0

        except Exception as e:
            logger.error(f"PowerPoint conversion failed: {e}")
            formatter.error(f"PowerPoint conversion failed: {e}")
            return 1


class ResetCommand(BaseCommand):
    """Command for resetting directories."""

    def execute(
        self,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """Execute directory reset."""
        try:
            # Check what to reset
            reset_input = not getattr(args, 'output_only', False)
            reset_output = not getattr(args, 'input_only', False)

            # Confirm operation
            if not getattr(args, 'confirm', False):
                dirs_to_reset = []
                if reset_input:
                    dirs_to_reset.append("Input")
                if reset_output:
                    dirs_to_reset.append("Output")

                dir_list = " and ".join(dirs_to_reset)
                formatter.warning(f"This will delete all files in {dir_list} director{'ies' if len(dirs_to_reset) > 1 else 'y'}")

                response = input("Continue? [y/N]: ").strip().lower()
                if response not in ('y', 'yes'):
                    formatter.info("Operation cancelled")
                    return 0

            # Perform reset
            formatter.info("Resetting directories...")

            total_deleted = 0
            if reset_input:
                count = self.path_manager.clean_directory(self.path_manager.input_dir)
                total_deleted += count
                formatter.success(f"Input directory reset: {count} items deleted")

            if reset_output:
                count = self.path_manager.clean_directory(self.path_manager.output_dir)
                total_deleted += count
                formatter.success(f"Output directory reset: {count} items deleted")

            formatter.success(f"Reset completed: {total_deleted} total items deleted")
            return 0

        except Exception as e:
            logger.error(f"Reset failed: {e}")
            formatter.error(f"Reset failed: {e}")
            return 1


class InfoCommand(BaseCommand):
    """Command for showing PDF file information."""

    def execute(
        self,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """Execute info command."""
        try:
            files = self._validate_files(args.files)
            processor = PDFProcessor()

            formatter.header("PDF File Information")

            for file_path in files:
                try:
                    info = processor.get_pdf_info(file_path)
                    self._show_file_info(file_path, info, formatter, args)
                except Exception as e:
                    formatter.error(f"Failed to analyze {file_path.name}: {e}")

            return 0

        except Exception as e:
            logger.error(f"Info command failed: {e}")
            formatter.error(f"Info command failed: {e}")
            return 1

    def _show_file_info(
        self,
        file_path: Path,
        info: dict,
        formatter: CLIFormatter,
        args: argparse.Namespace
    ) -> None:
        """Show information for a single file."""
        formatter.section(f"File: {file_path.name}")
        formatter.info(f"  Path: {file_path}")
        formatter.info(f"  Size: {file_path.stat().st_size / 1024:.1f} KB")
        formatter.info(f"  Pages: {info['page_count']}")

        if info.get('title'):
            formatter.info(f"  Title: {info['title']}")
        if info.get('author'):
            formatter.info(f"  Author: {info['author']}")

        if getattr(args, 'detailed', False):
            formatter.info("  Page Details:")
            for page_info in info['pages'][:5]:  # Show first 5 pages
                size = f"{page_info.original_size[0]:.0f}x{page_info.original_size[1]:.0f}"
                orientation = "Portrait" if page_info.is_portrait else "Landscape"
                formatter.info(f"    Page {page_info.page_number}: {size} pts ({orientation})")

            if len(info['pages']) > 5:
                formatter.info(f"    ... and {len(info['pages']) - 5} more pages")


class ConfigCommand(BaseCommand):
    """Command for managing configuration."""

    def execute(
        self,
        args: argparse.Namespace,
        formatter: CLIFormatter,
        logger: logging.Logger
    ) -> int:
        """Execute config command."""
        try:
            if not hasattr(args, 'config_command') or not args.config_command:
                formatter.error("No config command specified")
                return 1

            if args.config_command == 'show':
                return self._show_config(formatter)
            elif args.config_command == 'set':
                return self._set_config(args.key, args.value, formatter)
            elif args.config_command == 'reset':
                return self._reset_config(formatter)
            else:
                formatter.error(f"Unknown config command: {args.config_command}")
                return 1

        except Exception as e:
            logger.error(f"Config command failed: {e}")
            formatter.error(f"Config command failed: {e}")
            return 1

    def _show_config(self, formatter: CLIFormatter) -> int:
        """Show current configuration."""
        config = get_app_config()

        formatter.header("Current Configuration")
        formatter.info(f"Application Title: {config.window_title}")
        formatter.info(f"Window Size: {config.window_width}x{config.window_height}")

        formatter.section("PowerPoint Label Settings")
        label_config = config.powerpoint_label
        formatter.info(f"  Position: {label_config.position}")
        formatter.info(f"  Font: {label_config.font_name} {label_config.font_size}pt")
        formatter.info(f"  Text Color: {label_config.text_color}")
        formatter.info(f"  Background Color: {label_config.background_color}")
        formatter.info(f"  Border Color: {label_config.border_color}")

        return 0

    def _set_config(self, key: str, value: str, formatter: CLIFormatter) -> int:
        """Set configuration value."""
        # This would implement configuration setting logic
        formatter.info(f"Setting {key} = {value}")
        formatter.warning("Configuration setting not yet implemented")
        return 0

    def _reset_config(self, formatter: CLIFormatter) -> int:
        """Reset configuration to defaults."""
        formatter.warning("This will reset all configuration to defaults")
        response = input("Continue? [y/N]: ").strip().lower()
        if response not in ('y', 'yes'):
            formatter.info("Operation cancelled")
            return 0

        formatter.warning("Configuration reset not yet implemented")
        return 0


def create_command_registry() -> Dict[str, Type[BaseCommand]]:
    """Create registry of available commands."""
    return {
        'convert': ConvertCommand,
        'reset': ResetCommand,
        'info': InfoCommand,
        'config': ConfigCommand
    }