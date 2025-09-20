"""
Unified error handling and user feedback system.
Provides consistent error reporting across GUI and CLI modes.
"""

from __future__ import annotations

import logging
import os
import traceback
from enum import Enum
from typing import Any, Callable, Optional, TypeVar
from pathlib import Path
from contextlib import contextmanager
from functools import wraps

# Type for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


class ErrorSeverity(Enum):
    """Error severity levels for consistent categorization."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class UserFriendlyError(Exception):
    """
    Exception with user-friendly messages and recovery suggestions.
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.suggestion = suggestion
        self.severity = severity
        self.original_error = original_error
        super().__init__(message)

    def __str__(self) -> str:
        result = self.message
        if self.suggestion:
            result += f"\n\n💡 解決方法: {self.suggestion}"
        return result


class PDFConversionError(UserFriendlyError):
    """PDF conversion specific errors."""
    pass


class FileSystemError(UserFriendlyError):
    """File system operation errors."""
    pass


class ValidationError(UserFriendlyError):
    """Input validation errors."""
    pass


# Error handling decorators
def handle_pdf_errors(func: F) -> F:
    """
    Decorator to catch and convert PDF-related exceptions to user-friendly errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, UserFriendlyError):
                raise  # Re-raise user-friendly errors as-is

            # Convert common errors to user-friendly messages
            error_msg, suggestion = _analyze_pdf_error(e)
            raise PDFConversionError(
                message=error_msg,
                suggestion=suggestion,
                original_error=e
            )
    return wrapper


def handle_file_errors(func: F) -> F:
    """
    Decorator to catch and convert file operation exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, UserFriendlyError):
                raise

            error_msg, suggestion = _analyze_file_error(e)
            raise FileSystemError(
                message=error_msg,
                suggestion=suggestion,
                original_error=e
            )
    return wrapper


def _analyze_pdf_error(error: Exception) -> tuple[str, str]:
    """
    Analyze PDF-related errors and provide user-friendly messages.

    Returns:
        Tuple of (error_message, suggestion)
    """
    error_str = str(error).lower()

    if "password" in error_str or "encrypted" in error_str:
        return (
            "PDFファイルがパスワードで保護されています",
            "パスワードを解除してから再度お試しください"
        )

    if "corrupted" in error_str or "invalid" in error_str:
        return (
            "PDFファイルが破損している可能性があります",
            "別のPDFファイルでお試しいただくか、元ファイルを確認してください"
        )

    if "memory" in error_str or "out of memory" in error_str:
        return (
            "PDFファイルが大きすぎて処理できません",
            "スケール倍率を下げるか、ファイルサイズの小さいPDFをお使いください"
        )

    if "permission" in error_str or "access denied" in error_str:
        return (
            "ファイルへのアクセス権限がありません",
            "ファイルが他のアプリケーションで開かれていないか確認してください"
        )

    # Generic PDF error
    return (
        f"PDFの処理中にエラーが発生しました: {error}",
        "PDFファイルが正常に読み込めることを確認してください"
    )


def _analyze_file_error(error: Exception) -> tuple[str, str]:
    """
    Analyze file system errors and provide user-friendly messages.

    Returns:
        Tuple of (error_message, suggestion)
    """
    error_str = str(error).lower()

    if "no such file" in error_str or "not found" in error_str:
        return (
            "指定されたファイルまたはフォルダが見つかりません",
            "ファイルパスが正しいことを確認してください"
        )

    if "permission denied" in error_str or "access denied" in error_str:
        return (
            "ファイルまたはフォルダへのアクセス権限がありません",
            "管理者権限で実行するか、ファイルの権限設定を確認してください"
        )

    if "disk full" in error_str or "no space" in error_str:
        return (
            "ディスク容量が不足しています",
            "不要なファイルを削除して容量を確保してください"
        )

    if "file exists" in error_str:
        return (
            "同名のファイルが既に存在します",
            "既存ファイルを削除するか、別の名前で保存してください"
        )

    # Generic file error
    return (
        f"ファイル操作中にエラーが発生しました: {error}",
        "ファイルパスとアクセス権限を確認してください"
    )


@contextmanager
def error_context(operation_name: str, logger: Optional[logging.Logger] = None):
    """
    Context manager for operation error handling with logging.

    Args:
        operation_name: Name of the operation for error reporting
        logger: Optional logger for error recording

    Yields:
        None

    Raises:
        UserFriendlyError: Converted from any caught exceptions
    """
    try:
        yield
    except UserFriendlyError:
        # Re-raise user-friendly errors as-is
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error in {operation_name}: {e}", exc_info=True)

        # Create user-friendly error
        raise UserFriendlyError(
            message=f"{operation_name}中にエラーが発生しました",
            suggestion="操作を再試行するか、入力データを確認してください",
            original_error=e
        )


def validate_input_path(path: Path, must_exist: bool = True) -> None:
    """
    Validate input file/directory path.

    Args:
        path: Path to validate
        must_exist: Whether path must exist

    Raises:
        ValidationError: If path is invalid
    """
    if must_exist and not path.exists():
        raise ValidationError(
            message=f"指定されたパス '{path}' が見つかりません",
            suggestion="正しいファイルパスを指定してください"
        )

    if must_exist and path.is_file() and not path.suffix.lower() == '.pdf':
        raise ValidationError(
            message=f"'{path}' はPDFファイルではありません",
            suggestion="拡張子が.pdfのファイルを指定してください"
        )


def validate_output_path(path: Path) -> None:
    """
    Validate output file/directory path.

    Args:
        path: Output path to validate

    Raises:
        ValidationError: If path is invalid
    """
    # Check if parent directory exists or can be created
    parent = path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValidationError(
                message=f"出力ディレクトリ '{parent}' を作成できません",
                suggestion="書き込み権限のあるディレクトリを指定してください",
                original_error=e
            )

    # Check write permissions
    if parent.exists() and not os.access(parent, os.W_OK):
        raise ValidationError(
            message=f"出力ディレクトリ '{parent}' への書き込み権限がありません",
            suggestion="書き込み権限のあるディレクトリを指定してください"
        )


def setup_logging(log_file: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the application.

    Note: This is a simplified logging setup. For advanced logging features,
    use the logging_config module.

    Args:
        log_file: Optional file to write logs to
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("pdf2pptx")

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def format_exception_for_user(error: Exception) -> str:
    """
    Format exception for display to end users.

    Args:
        error: Exception to format

    Returns:
        User-friendly error message
    """
    if isinstance(error, UserFriendlyError):
        return str(error)

    # For unexpected errors, provide generic message
    return (
        f"予期しないエラーが発生しました: {type(error).__name__}\n\n"
        "💡 解決方法: アプリケーションを再起動してお試しください。"
        "問題が続く場合は、入力ファイルを確認してください。"
    )


def log_function_calls(func):
    """
    Decorator to log function entry and exit.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"pdf2pptx.{func.__module__}.{func.__name__}")

        # Log function entry
        logger.debug(f"Entering {func.__name__} with {len(args)} args, {len(kwargs)} kwargs")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise

    return wrapper


class ErrorCollector:
    """
    Collect multiple errors for batch processing and reporting.
    """

    def __init__(self):
        self.errors: list[Exception] = []
        self.logger = logging.getLogger("pdf2pptx.error_collector")

    def add_error(self, error: Exception, context: str = "") -> None:
        """Add an error to the collection."""
        self.errors.append(error)

        if context:
            self.logger.error(f"Error in {context}: {error}", exc_info=error)
        else:
            self.logger.error(f"Error collected: {error}", exc_info=error)

    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0

    def get_error_count(self) -> int:
        """Get number of collected errors."""
        return len(self.errors)

    def get_summary(self) -> str:
        """Get a summary of all collected errors."""
        if not self.errors:
            return "エラーはありません"

        summary = f"収集されたエラー ({len(self.errors)}件):\n\n"

        for i, error in enumerate(self.errors, 1):
            error_msg = format_exception_for_user(error)
            summary += f"{i}. {error_msg}\n\n"

        return summary

    def get_first_error(self) -> Optional[Exception]:
        """Get the first error if any."""
        return self.errors[0] if self.errors else None

    def clear(self) -> None:
        """Clear all collected errors."""
        self.logger.info(f"Clearing {len(self.errors)} collected errors")
        self.errors.clear()

    def raise_if_errors(self) -> None:
        """Raise the first error if any errors were collected."""
        if self.errors:
            first_error = self.errors[0]
            if isinstance(first_error, UserFriendlyError):
                raise first_error
            else:
                raise UserFriendlyError(
                    message="複数のエラーが発生しました",
                    suggestion=f"最初のエラー: {format_exception_for_user(first_error)}",
                    original_error=first_error
                )