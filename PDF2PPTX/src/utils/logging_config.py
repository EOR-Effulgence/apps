"""
Comprehensive logging configuration for PDF2PPTX application.
Provides structured logging with multiple handlers and formatters.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info'):
                log_entry[key] = value

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output.
    """

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format with colors if supported."""
        if sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


class StructuredLogger:
    """
    Structured logger with multiple handlers and context management.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """Set logging context."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear logging context."""
        self.context.clear()

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Log message with context."""
        extra = {**self.context, **kwargs}
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs['exc_info'] = True
        self._log(logging.ERROR, message, **kwargs)


def setup_application_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_json_logs: bool = True,
    enable_console_logs: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> StructuredLogger:
    """
    Set up comprehensive logging configuration.

    Args:
        log_level: Logging level
        log_dir: Directory for log files
        enable_json_logs: Enable JSON formatted file logs
        enable_console_logs: Enable console logging
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured StructuredLogger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create main application logger
    logger = logging.getLogger('pdf2pptx')
    logger.setLevel(numeric_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create log directory if specified
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler for general logs
        if enable_json_logs:
            json_log_file = log_dir / f"pdf2pptx_{datetime.now().strftime('%Y%m%d')}.json"
            json_handler = logging.handlers.RotatingFileHandler(
                json_log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(JSONFormatter())
            logger.addHandler(json_handler)

        # Text file handler for human-readable logs
        text_log_file = log_dir / f"pdf2pptx_{datetime.now().strftime('%Y%m%d')}.log"
        text_handler = logging.handlers.RotatingFileHandler(
            text_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        text_handler.setLevel(logging.DEBUG)
        text_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        text_handler.setFormatter(text_formatter)
        logger.addHandler(text_handler)

        # Error-only file handler
        error_log_file = log_dir / f"pdf2pptx_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(text_formatter)
        logger.addHandler(error_handler)

    # Console handler
    if enable_console_logs:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(max(logging.WARNING, numeric_level))
        console_formatter = ColoredFormatter(
            '%(levelname)s: %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Configure third-party loggers
    _configure_third_party_loggers(numeric_level)

    return StructuredLogger('pdf2pptx')


def _configure_third_party_loggers(level: int) -> None:
    """Configure third-party library loggers."""
    # Reduce noise from third-party libraries
    third_party_loggers = [
        'PIL',
        'matplotlib',
        'urllib3',
        'requests'
    ]

    for logger_name in third_party_loggers:
        third_party_logger = logging.getLogger(logger_name)
        third_party_logger.setLevel(max(logging.WARNING, level))


def create_operation_logger(operation_name: str, operation_id: str) -> StructuredLogger:
    """
    Create a logger for a specific operation.

    Args:
        operation_name: Name of the operation
        operation_id: Unique identifier for the operation

    Returns:
        Configured StructuredLogger with operation context
    """
    logger = StructuredLogger(f'pdf2pptx.{operation_name}')
    logger.set_context(
        operation_name=operation_name,
        operation_id=operation_id,
        start_time=datetime.now().isoformat()
    )
    return logger


def log_performance(func):
    """
    Decorator to log function performance.
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f'pdf2pptx.performance.{func.__module__}.{func.__name__}')
        start_time = datetime.now()

        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(
                f"Function executed successfully",
                extra={
                    'function': func.__name__,
                    'module': func.__module__,
                    'duration_seconds': duration,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
            )
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.error(
                f"Function execution failed",
                extra={
                    'function': func.__name__,
                    'module': func.__module__,
                    'duration_seconds': duration,
                    'error': str(e),
                    'error_type': type(e).__name__
                },
                exc_info=True
            )
            raise

    return wrapper


def log_method_calls(cls):
    """
    Class decorator to log all method calls.
    """
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, log_performance(attr))
    return cls


class LoggingContext:
    """
    Context manager for logging with additional context.
    """

    def __init__(self, logger: StructuredLogger, **context):
        self.logger = logger
        self.context = context
        self.original_context = {}

    def __enter__(self):
        # Save original context
        self.original_context = self.logger.context.copy()
        # Set new context
        self.logger.set_context(**self.context)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original context
        self.logger.context = self.original_context

        # Log exception if occurred
        if exc_type is not None:
            self.logger.exception(
                f"Exception in logging context",
                exception_type=exc_type.__name__,
                exception_message=str(exc_val)
            )