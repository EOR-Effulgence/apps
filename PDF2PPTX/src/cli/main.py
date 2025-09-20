"""
Main CLI entry point for PDF2PPTX application.
Provides comprehensive command-line interface with professional output formatting.
"""

from __future__ import annotations

import sys
import logging
import traceback
from pathlib import Path
from typing import Optional, List

from .parsers import create_main_parser
from .commands import create_command_registry
from .utils import CLIFormatter, setup_cli_logging
from ..utils.error_handling import UserFriendlyError
from ..config import get_app_config


class CLIApplication:
    """
    Main CLI application class that coordinates command execution.
    """

    def __init__(self):
        self.formatter = CLIFormatter()
        self.logger: Optional[logging.Logger] = None
        self.config = get_app_config()

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.

        Args:
            args: Command line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Parse command line arguments
            parser = create_main_parser()
            parsed_args = parser.parse_args(args)

            # Set up logging
            self.logger = setup_cli_logging(parsed_args.log_level, parsed_args.verbose)

            # Show header
            if not parsed_args.quiet:
                self._show_header()

            # Handle version request
            if getattr(parsed_args, 'version', False):
                return self._show_version()

            # Validate environment
            self._validate_environment()

            # Get command registry
            commands = create_command_registry()

            # Execute command
            if hasattr(parsed_args, 'func'):
                try:
                    result = parsed_args.func(parsed_args, self.formatter, self.logger)
                    return result if isinstance(result, int) else 0
                except UserFriendlyError as e:
                    self.formatter.error(str(e))
                    if e.suggestion:
                        self.formatter.info(f"Suggestion: {e.suggestion}")
                    return 1
                except KeyboardInterrupt:
                    self.formatter.warning("Operation cancelled by user")
                    return 130
                except Exception as e:
                    self.logger.error(f"Command execution failed: {e}", exc_info=True)
                    self.formatter.error(f"Unexpected error: {e}")
                    if parsed_args.verbose:
                        self.formatter.error("Full traceback:")
                        traceback.print_exc()
                    return 1
            else:
                # No command specified, show help
                parser.print_help()
                return 0

        except KeyboardInterrupt:
            self.formatter.warning("\\nApplication interrupted by user")
            return 130
        except Exception as e:
            # Fatal error
            if self.logger:
                self.logger.critical(f"Fatal error: {e}", exc_info=True)
            print(f"Fatal error: {e}", file=sys.stderr)
            if '--verbose' in (args or sys.argv):
                traceback.print_exc()
            return 1

    def _show_header(self) -> None:
        """Show application header."""
        self.formatter.header("PDF2PPTX Converter v3.0")
        self.formatter.info("Professional PDF to PNG/PowerPoint conversion tool")
        self.formatter.info("")

    def _show_version(self) -> int:
        """Show version information."""
        from .. import __version__
        self.formatter.success(f"PDF2PPTX Converter version {__version__}")
        self.formatter.info("Copyright (c) 2025 PDF2PPTX Project")
        return 0

    def _validate_environment(self) -> None:
        """Validate application environment."""
        from ..utils.path_utils import PathManager

        try:
            path_manager = PathManager()
            path_manager.validate_working_directory()
        except Exception as e:
            raise UserFriendlyError(
                message="Application environment validation failed",
                suggestion="Ensure you're running from the correct directory with proper permissions",
                original_error=e
            )


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for CLI application.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    app = CLIApplication()
    return app.run(args)


if __name__ == '__main__':
    sys.exit(main())