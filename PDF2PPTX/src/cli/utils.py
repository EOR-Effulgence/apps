"""
CLI utility classes and functions.
Provides comprehensive CLI support with professional formatting and progress tracking.
"""

from __future__ import annotations

import sys
import logging
import time
from typing import Optional, TextIO
from pathlib import Path


class CLIFormatter:
    """
    Professional CLI output formatter with color support and consistent styling.
    """

    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m'
    }

    def __init__(self, use_colors: bool = None, output: TextIO = None):
        """
        Initialize formatter.

        Args:
            use_colors: Whether to use colors (auto-detect if None)
            output: Output stream (defaults to stdout)
        """
        self.output = output or sys.stdout
        self.use_colors = self._should_use_colors() if use_colors is None else use_colors

    def _should_use_colors(self) -> bool:
        """Determine if colors should be used."""
        # Check if output is a terminal and supports colors
        if not hasattr(self.output, 'isatty') or not self.output.isatty():
            return False

        # Check environment variables
        import os
        if os.environ.get('NO_COLOR'):
            return False
        if os.environ.get('FORCE_COLOR'):
            return True

        # Check terminal type
        term = os.environ.get('TERM', '')
        if 'color' in term or term in ('xterm', 'xterm-256color', 'screen'):
            return True

        # Windows specific check
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                # Try to enable ANSI support on Windows 10+
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                    return True
                except:
                    return False

        return False

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self.use_colors or color not in self.COLORS:
            return text
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"

    def header(self, text: str) -> None:
        """Print header text."""
        border = '=' * min(len(text), 60)
        self.print(self._colorize(border, 'bright_blue'))
        self.print(self._colorize(text, 'bright_blue'))
        self.print(self._colorize(border, 'bright_blue'))

    def section(self, text: str) -> None:
        """Print section header."""
        self.print(self._colorize(f"\\n{text}", 'bright_cyan'))
        self.print(self._colorize('-' * min(len(text), 40), 'cyan'))

    def success(self, text: str) -> None:
        """Print success message."""
        self.print(self._colorize(f"✓ {text}", 'bright_green'))

    def error(self, text: str) -> None:
        """Print error message."""
        self.print(self._colorize(f"✗ {text}", 'bright_red'), file=sys.stderr)

    def warning(self, text: str) -> None:
        """Print warning message."""
        self.print(self._colorize(f"⚠ {text}", 'bright_yellow'))

    def info(self, text: str) -> None:
        """Print info message."""
        self.print(text)

    def debug(self, text: str) -> None:
        """Print debug message."""
        self.print(self._colorize(f"DEBUG: {text}", 'dim'))

    def progress(self, current: int, total: int, message: str = "") -> None:
        """Print progress information."""
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * current // total) if total > 0 else 0

        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        colored_bar = self._colorize(bar, 'bright_blue')

        progress_text = f"[{colored_bar}] {percentage:6.1f}% ({current}/{total})"
        if message:
            progress_text += f" - {message}"

        # Clear line and print progress
        self.print(f"\\r{progress_text}", end='', flush=True)

        # Print newline when complete
        if current >= total:
            self.print()

    def print(self, text: str = "", end: str = "\\n", file: Optional[TextIO] = None, flush: bool = False) -> None:
        """Print text to output."""
        output = file or self.output
        print(text, end=end, file=output, flush=flush)

    def table(self, headers: list, rows: list, title: Optional[str] = None) -> None:
        """Print formatted table."""
        if not rows:
            return

        if title:
            self.section(title)

        # Calculate column widths
        col_widths = [max(len(str(header)), max(len(str(row[i])) for row in rows))
                      for i, header in enumerate(headers)]

        # Print header
        header_row = " | ".join(str(header).ljust(col_widths[i]) for i, header in enumerate(headers))
        self.print(self._colorize(header_row, 'bright_white'))

        # Print separator
        separator = "-+-".join("-" * width for width in col_widths)
        self.print(self._colorize(separator, 'dim'))

        # Print rows
        for row in rows:
            row_text = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
            self.print(row_text)


class CLIProgressTracker:
    """
    Progress tracker for CLI operations with time estimation.
    """

    def __init__(self, formatter: CLIFormatter, total_items: int):
        self.formatter = formatter
        self.total_items = total_items
        self.current_item = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

    def update(self, increment: int = 1, message: str = "") -> None:
        """Update progress."""
        self.current_item = min(self.current_item + increment, self.total_items)
        current_time = time.time()

        # Update at most once per second, or on completion
        if (current_time - self.last_update_time >= 1.0 or
            self.current_item >= self.total_items):

            self.last_update_time = current_time
            self._show_progress(message)

    def _show_progress(self, message: str = "") -> None:
        """Show current progress."""
        elapsed_time = time.time() - self.start_time

        # Calculate ETA
        if self.current_item > 0 and self.current_item < self.total_items:
            avg_time_per_item = elapsed_time / self.current_item
            remaining_items = self.total_items - self.current_item
            eta_seconds = remaining_items * avg_time_per_item
            eta_text = f" ETA: {self._format_time(eta_seconds)}"
        else:
            eta_text = ""

        # Format message
        if message:
            full_message = f"{message}{eta_text}"
        else:
            full_message = f"Processing{eta_text}"

        self.formatter.progress(self.current_item, self.total_items, full_message)

    def _format_time(self, seconds: float) -> str:
        """Format time duration."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def complete(self, message: str = "Completed") -> None:
        """Mark as completed."""
        self.current_item = self.total_items
        elapsed_time = time.time() - self.start_time
        final_message = f"{message} in {self._format_time(elapsed_time)}"
        self.formatter.progress(self.total_items, self.total_items, final_message)


def setup_cli_logging(
    log_level: str = "INFO",
    verbose: bool = False,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up logging for CLI application.

    Args:
        log_level: Logging level
        verbose: Enable verbose logging
        log_file: Optional log file path

    Returns:
        Configured logger
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Adjust level for verbose mode
    if verbose:
        numeric_level = min(numeric_level, logging.DEBUG)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )

    logger = logging.getLogger('pdf2pptx')

    # Console handler (only for errors and warnings)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Verbose console handler
    if verbose:
        verbose_handler = logging.StreamHandler(sys.stdout)
        verbose_handler.setLevel(logging.DEBUG)
        verbose_formatter = logging.Formatter('DEBUG: %(name)s - %(message)s')
        verbose_handler.setFormatter(verbose_formatter)
        logger.addHandler(verbose_handler)

    return logger


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        message: Confirmation message
        default: Default response

    Returns:
        True if user confirms
    """
    suffix = " [Y/n]" if default else " [y/N]"
    try:
        response = input(f"{message}{suffix}: ").strip().lower()
        if not response:
            return default
        return response in ('y', 'yes', 'true', '1')
    except (KeyboardInterrupt, EOFError):
        print()
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"