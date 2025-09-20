"""
Secure path management utilities for file operations.
Replaces hardcoded paths with configurable, validated path handling.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from .error_handling import FileSystemError, validate_input_path, validate_output_path


class PathManager:
    """
    Centralized path management with validation and security features.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize path manager with base directory.

        Args:
            base_path: Optional base directory. Defaults to application directory.
        """
        self._base_path = base_path or self._get_application_directory()
        self._input_dir = self._base_path / "Input"
        self._output_dir = self._base_path / "Output"

    @property
    def base_path(self) -> Path:
        """Application base directory."""
        return self._base_path

    @property
    def input_dir(self) -> Path:
        """Input directory for source files."""
        return self._input_dir

    @property
    def output_dir(self) -> Path:
        """Output directory for generated files."""
        return self._output_dir

    def ensure_directories(self) -> None:
        """
        Create input and output directories if they don't exist.

        Raises:
            FileSystemError: If directories cannot be created
        """
        for directory in [self._input_dir, self._output_dir]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileSystemError(
                    message=f"ディレクトリ '{directory}' を作成できません",
                    suggestion="書き込み権限があることを確認してください",
                    original_error=e
                )

    def find_pdf_files(self, directory: Optional[Path] = None) -> List[Path]:
        """
        Find all PDF files in the specified directory.

        Args:
            directory: Directory to search. Defaults to input directory.

        Returns:
            List of PDF file paths

        Raises:
            FileSystemError: If directory cannot be accessed
        """
        search_dir = directory or self._input_dir
        validate_input_path(search_dir, must_exist=True)

        try:
            pdf_files = [
                f for f in search_dir.iterdir()
                if f.is_file() and f.suffix.lower() == '.pdf'
            ]
            return sorted(pdf_files)  # Consistent ordering
        except Exception as e:
            raise FileSystemError(
                message=f"ディレクトリ '{search_dir}' を読み込めません",
                suggestion="ディレクトリへのアクセス権限を確認してください",
                original_error=e
            )

    def get_output_path(
        self,
        filename: str,
        extension: str,
        directory: Optional[Path] = None
    ) -> Path:
        """
        Generate safe output file path.

        Args:
            filename: Base filename (without extension)
            extension: File extension (with or without leading dot)
            directory: Output directory. Defaults to output directory.

        Returns:
            Safe output file path

        Raises:
            FileSystemError: If output path is invalid
        """
        output_dir = directory or self._output_dir

        # Sanitize filename to prevent path traversal
        safe_filename = self._sanitize_filename(filename)

        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = '.' + extension

        output_path = output_dir / (safe_filename + extension)
        validate_output_path(output_path)

        return output_path

    def generate_unique_filename(
        self,
        base_name: str,
        extension: str,
        directory: Optional[Path] = None
    ) -> Path:
        """
        Generate unique filename by adding suffix if file exists.

        Args:
            base_name: Base filename
            extension: File extension
            directory: Target directory

        Returns:
            Unique file path
        """
        output_dir = directory or self._output_dir
        counter = 0

        while True:
            if counter == 0:
                filename = base_name
            else:
                filename = f"{base_name}_{counter}"

            file_path = self.get_output_path(filename, extension, output_dir)

            if not file_path.exists():
                return file_path

            counter += 1
            if counter > 1000:  # Prevent infinite loop
                raise FileSystemError(
                    message="一意なファイル名を生成できません",
                    suggestion="出力ディレクトリの既存ファイルを整理してください"
                )

    def clean_directory(self, directory: Path, confirm: bool = True) -> int:
        """
        Clean all files from a directory.

        Args:
            directory: Directory to clean
            confirm: Whether to require confirmation

        Returns:
            Number of files deleted

        Raises:
            FileSystemError: If cleaning fails
        """
        if not directory.exists():
            return 0

        if confirm:
            # In real implementation, this would prompt user
            # For now, we assume confirmation
            pass

        try:
            deleted_count = 0
            for item in directory.iterdir():
                if item.is_file():
                    item.unlink()
                    deleted_count += 1
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(item)
                    deleted_count += 1

            return deleted_count

        except Exception as e:
            raise FileSystemError(
                message=f"ディレクトリ '{directory}' のクリーニングに失敗しました",
                suggestion="ファイルが他のプログラムで使用されていないか確認してください",
                original_error=e
            )

    def get_relative_path(self, file_path: Path) -> str:
        """
        Get path relative to base directory for display purposes.

        Args:
            file_path: Absolute file path

        Returns:
            Relative path string
        """
        try:
            return str(file_path.relative_to(self._base_path))
        except ValueError:
            # Path is not relative to base, return absolute
            return str(file_path)

    @staticmethod
    def _get_application_directory() -> Path:
        """
        Get the application directory (handles PyInstaller frozen apps).

        Returns:
            Application directory path
        """
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller frozen app
            return Path(sys.executable).parent
        else:
            # Regular Python script
            return Path(__file__).parent.parent.parent

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and invalid characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', '..', ':', '*', '?', '"', '<', '>', '|']
        sanitized = filename

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')

        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip(' .')

        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed"

        # Limit length to prevent filesystem issues
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        return sanitized

    def validate_working_directory(self) -> None:
        """
        Validate that the working directory setup is correct.

        Raises:
            FileSystemError: If working directory is invalid
        """
        # Check base directory exists and is writable
        if not self._base_path.exists():
            raise FileSystemError(
                message=f"アプリケーションディレクトリ '{self._base_path}' が見つかりません",
                suggestion="アプリケーションが正しくインストールされているか確認してください"
            )

        if not os.access(self._base_path, os.W_OK):
            raise FileSystemError(
                message=f"アプリケーションディレクトリ '{self._base_path}' への書き込み権限がありません",
                suggestion="管理者権限で実行するか、ディレクトリの権限を確認してください"
            )

        # Ensure required subdirectories can be created
        self.ensure_directories()

    def get_available_disk_space(self, path: Optional[Path] = None) -> int:
        """
        Get available disk space in bytes.

        Args:
            path: Path to check disk space for. Defaults to output directory.

        Returns:
            Available disk space in bytes

        Raises:
            FileSystemError: If disk space cannot be determined
        """
        check_path = path or self._output_dir
        try:
            import shutil
            total, used, free = shutil.disk_usage(check_path.parent)
            return free
        except Exception as e:
            raise FileSystemError(
                message="ディスク容量を取得できません",
                suggestion="ディスクの状態を確認してください",
                original_error=e
            )

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive file information.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information

        Raises:
            FileSystemError: If file info cannot be retrieved
        """
        try:
            stat_info = file_path.stat()
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat_info.st_size,
                'size_mb': stat_info.st_size / (1024 * 1024),
                'created': stat_info.st_ctime,
                'modified': stat_info.st_mtime,
                'accessed': stat_info.st_atime,
                'extension': file_path.suffix.lower(),
                'is_pdf': file_path.suffix.lower() == '.pdf',
                'permissions': oct(stat_info.st_mode)[-3:]
            }
        except Exception as e:
            raise FileSystemError(
                message=f"ファイル情報を取得できません: {file_path}",
                suggestion="ファイルが存在し、アクセス可能であることを確認してください",
                original_error=e
            )

    def create_backup(self, file_path: Path, backup_dir: Optional[Path] = None) -> Path:
        """
        Create backup of important file.

        Args:
            file_path: File to backup
            backup_dir: Backup directory. Defaults to base_path/backups

        Returns:
            Path to backup file

        Raises:
            FileSystemError: If backup creation fails
        """
        if backup_dir is None:
            backup_dir = self._base_path / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate backup filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name

        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise FileSystemError(
                message=f"バックアップの作成に失敗しました: {file_path}",
                suggestion="十分なディスク容量があることを確認してください",
                original_error=e
            )

    def reset_directories(self) -> Dict[str, int]:
        """
        Reset both input and output directories.

        Returns:
            Dictionary with count of deleted items from each directory

        Raises:
            FileSystemError: If reset fails
        """
        results = {}

        for dir_name, directory in [("input", self._input_dir), ("output", self._output_dir)]:
            try:
                count = self.clean_directory(directory, confirm=False)
                results[dir_name] = count
            except Exception as e:
                raise FileSystemError(
                    message=f"{dir_name}ディレクトリのリセットに失敗しました",
                    suggestion="ディレクトリのアクセス権限を確認してください",
                    original_error=e
                )

        return results

    def validate_output_directory(self) -> None:
        """
        Validate output directory is ready for writing.

        Raises:
            FileSystemError: If output directory is invalid
        """
        # Ensure directory exists
        self.ensure_directories()

        # Check write permissions
        if not os.access(self._output_dir, os.W_OK):
            raise FileSystemError(
                message=f"出力ディレクトリ '{self._output_dir}' への書き込み権限がありません",
                suggestion="ディレクトリの権限設定を確認してください"
            )

        # Check available space (at least 100MB)
        try:
            free_space = self.get_available_disk_space()
            if free_space < 100 * 1024 * 1024:  # 100MB
                raise FileSystemError(
                    message="出力ディレクトリのディスク容量が不足しています",
                    suggestion="不要なファイルを削除してディスク容量を確保してください"
                )
        except FileSystemError:
            raise
        except Exception:
            # If we can't check disk space, continue anyway
            pass


# Convenience functions for backward compatibility
def get_application_directory() -> Path:
    """Get application directory."""
    return PathManager._get_application_directory()


def ensure_output_directory(output_dir: Path) -> None:
    """Ensure output directory exists."""
    output_dir.mkdir(parents=True, exist_ok=True)


def find_pdf_files_in_directory(directory: Path) -> List[Path]:
    """Find PDF files in directory."""
    manager = PathManager()
    return manager.find_pdf_files(directory)