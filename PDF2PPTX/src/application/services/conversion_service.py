"""
Application service for PDF conversion operations.

This service orchestrates the conversion process and provides a high-level interface
for the presentation layer while maintaining separation of concerns.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

from ...core.pdf_processor import PDFProcessor, ConversionConfig
from ...utils.error_handling import UserFriendlyError, handle_pdf_errors
from ...utils.path_utils import PathManager


class ConversionStatus(Enum):
    """Conversion operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConversionJob:
    """Represents a conversion job."""
    id: str
    files: List[Path]
    config: ConversionConfig
    output_type: str  # "png" or "pptx"
    status: ConversionStatus = ConversionStatus.PENDING
    progress: int = 0
    current_file: Optional[str] = None
    result_files: List[Path] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.result_files is None:
            self.result_files = []


class ConversionService:
    """
    High-level service for managing PDF conversion operations.

    This service provides:
    - Asynchronous conversion operations
    - Progress tracking
    - Job management
    - Error handling
    """

    def __init__(self, path_manager: PathManager, max_workers: int = 2):
        self.path_manager = path_manager
        self.pdf_processor = PDFProcessor()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_jobs: Dict[str, ConversionJob] = {}
        self._job_counter = 0

    async def convert_to_images_async(
        self,
        files: List[Path],
        config: ConversionConfig,
        progress_callback: Optional[Callable[[ConversionJob], None]] = None
    ) -> ConversionJob:
        """
        Convert PDF files to images asynchronously.

        Args:
            files: List of PDF files to convert
            config: Conversion configuration
            progress_callback: Callback for progress updates

        Returns:
            ConversionJob with results
        """
        job = self._create_job(files, config, "png")

        try:
            await self._execute_conversion_job(job, progress_callback, self._convert_to_images_sync)
        except Exception as e:
            job.status = ConversionStatus.FAILED
            job.error_message = str(e)
            if progress_callback:
                progress_callback(job)

        return job

    async def convert_to_pptx_async(
        self,
        files: List[Path],
        config: ConversionConfig,
        progress_callback: Optional[Callable[[ConversionJob], None]] = None
    ) -> ConversionJob:
        """
        Convert PDF files to PowerPoint asynchronously.

        Args:
            files: List of PDF files to convert
            config: Conversion configuration
            progress_callback: Callback for progress updates

        Returns:
            ConversionJob with results
        """
        job = self._create_job(files, config, "pptx")

        try:
            await self._execute_conversion_job(job, progress_callback, self._convert_to_pptx_sync)
        except Exception as e:
            job.status = ConversionStatus.FAILED
            job.error_message = str(e)
            if progress_callback:
                progress_callback(job)

        return job

    def _create_job(self, files: List[Path], config: ConversionConfig, output_type: str) -> ConversionJob:
        """Create a new conversion job."""
        self._job_counter += 1
        job_id = f"job_{self._job_counter}"

        job = ConversionJob(
            id=job_id,
            files=files,
            config=config,
            output_type=output_type
        )

        self.active_jobs[job_id] = job
        return job

    async def _execute_conversion_job(
        self,
        job: ConversionJob,
        progress_callback: Optional[Callable[[ConversionJob], None]],
        conversion_func: Callable[[ConversionJob, Callable], List[Path]]
    ) -> None:
        """Execute a conversion job asynchronously."""
        job.status = ConversionStatus.RUNNING
        if progress_callback:
            progress_callback(job)

        # Progress tracking function
        def update_progress(current: int, total: int, current_file: str = None):
            job.progress = int((current / total) * 100) if total > 0 else 0
            job.current_file = current_file
            if progress_callback:
                progress_callback(job)

        # Execute conversion in background thread
        loop = asyncio.get_event_loop()
        result_files = await loop.run_in_executor(
            self.executor,
            conversion_func,
            job,
            update_progress
        )

        job.result_files = result_files
        job.status = ConversionStatus.COMPLETED
        job.progress = 100
        job.current_file = None

        if progress_callback:
            progress_callback(job)

    @handle_pdf_errors
    def _convert_to_images_sync(
        self,
        job: ConversionJob,
        progress_callback: Callable[[int, int, str], None]
    ) -> List[Path]:
        """Synchronous image conversion."""
        output_files = []
        total_pages = 0

        # Count total pages for progress tracking
        for file_path in job.files:
            try:
                page_count = self.pdf_processor.count_pages(file_path)
                total_pages += page_count
            except Exception:
                total_pages += 1  # Estimate 1 page if counting fails
                continue

        current_page = 0

        for file_path in job.files:
            try:
                progress_callback(current_page, total_pages, file_path.name)

                # Convert using PDF processor
                converted_files = self.pdf_processor.convert_pdf_to_images(
                    file_path,
                    job.config,
                    self.path_manager,
                    lambda: progress_callback(current_page + 1, total_pages, file_path.name)
                )

                output_files.extend(converted_files)
                try:
                    current_page += self.pdf_processor.count_pages(file_path)
                except Exception:
                    current_page += 1  # Fallback increment

            except Exception as e:
                # Log error but continue with other files
                job.error_message = f"Error converting {file_path.name}: {str(e)}"
                current_page += 1  # Continue progress
                continue

        return output_files

    @handle_pdf_errors
    def _convert_to_pptx_sync(
        self,
        job: ConversionJob,
        progress_callback: Callable[[int, int, str], None]
    ) -> List[Path]:
        """Synchronous PPTX conversion."""
        try:
            progress_callback(0, 1, "Creating PowerPoint presentation...")

            # Convert using PDF processor
            output_file = self.pdf_processor.convert_to_pptx(
                job.files,
                job.config,
                self.path_manager
            )

            progress_callback(1, 1, "PowerPoint creation completed")
            return [output_file] if output_file else []

        except Exception as e:
            job.error_message = f"Error creating PowerPoint: {str(e)}"
            raise

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running conversion job.

        Args:
            job_id: ID of the job to cancel

        Returns:
            True if job was cancelled successfully
        """
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status == ConversionStatus.RUNNING:
                job.status = ConversionStatus.CANCELLED
                return True
        return False

    def get_job_status(self, job_id: str) -> Optional[ConversionJob]:
        """Get status of a conversion job."""
        return self.active_jobs.get(job_id)

    def cleanup_completed_jobs(self) -> None:
        """Remove completed jobs from memory."""
        completed_jobs = [
            job_id for job_id, job in self.active_jobs.items()
            if job.status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED]
        ]

        for job_id in completed_jobs:
            del self.active_jobs[job_id]

    def get_active_jobs(self) -> List[ConversionJob]:
        """Get list of all active jobs."""
        return list(self.active_jobs.values())

    def estimate_conversion_time(self, files: List[Path], config: ConversionConfig) -> float:
        """
        Estimate conversion time in seconds.

        Args:
            files: Files to convert
            config: Conversion configuration

        Returns:
            Estimated time in seconds
        """
        total_pages = 0
        total_file_size = 0

        for file_path in files:
            try:
                page_count = self.pdf_processor.count_pages(file_path)
                total_pages += page_count
                total_file_size += file_path.stat().st_size
            except Exception:
                total_pages += 5  # Assume 5 pages for unreadable files
                total_file_size += 1024 * 1024  # Assume 1MB

        # Improved estimation formula
        base_time_per_page = 0.3 + (config.scale_factor - 1.0) * 0.2
        size_factor = min(2.0, total_file_size / (1024 * 1024 * 10))  # Cap at 2x for 10MB+
        dpi_factor = getattr(config, 'target_dpi', 150) / 150.0

        estimated_time = total_pages * base_time_per_page * size_factor * dpi_factor

        # Add overhead for file I/O and processing
        overhead = len(files) * 1.0 + 2.0  # Per-file overhead plus startup

        return max(1.0, estimated_time + overhead)

    def validate_conversion_request(
        self,
        files: List[Path],
        config: ConversionConfig
    ) -> Optional[str]:
        """
        Validate a conversion request.

        Args:
            files: Files to convert
            config: Conversion configuration

        Returns:
            Error message if validation fails, None if valid
        """
        if not files:
            return "変換するファイルが選択されていません"

        # Check file existence and readability
        for file_path in files:
            if not file_path.exists():
                return f"ファイルが見つかりません: {file_path.name}"

            if not file_path.is_file():
                return f"指定されたパスはファイルではありません: {file_path.name}"

            if file_path.suffix.lower() != '.pdf':
                return f"PDFファイルではありません: {file_path.name}"

        # Check output directory
        try:
            self.path_manager.validate_output_directory()
        except Exception as e:
            return f"出力ディレクトリの確認に失敗しました: {str(e)}"

        # Check estimated processing time
        estimated_time = self.estimate_conversion_time(files, config)
        if estimated_time > 300:  # 5 minutes
            return "変換時間が長すぎる可能性があります。ファイル数を減らすかスケール倍率を下げてください。"

        # Check available disk space
        try:
            free_space = self.path_manager.get_available_disk_space()
            estimated_output_size = self._estimate_output_size(files, config)
            if estimated_output_size > free_space * 0.9:
                return f"ディスク容量が不足しています。必要: {estimated_output_size/1024/1024:.1f}MB, 利用可能: {free_space/1024/1024:.1f}MB"
        except Exception:
            pass  # Continue if disk space check fails

        return None

    def _estimate_output_size(self, files: List[Path], config: ConversionConfig) -> int:
        """
        Estimate total output file size in bytes.

        Args:
            files: Input PDF files
            config: Conversion configuration

        Returns:
            Estimated output size in bytes
        """
        total_pages = 0
        for file_path in files:
            try:
                page_count = self.pdf_processor.count_pages(file_path)
                total_pages += page_count
            except Exception:
                total_pages += 5

        # Rough estimation based on scale factor and DPI
        scale_factor = config.scale_factor
        dpi = getattr(config, 'target_dpi', 150)

        # Base size per page (A4 at 150 DPI ≈ 1MB)
        base_size_per_page = 1024 * 1024  # 1MB
        size_multiplier = (scale_factor ** 2) * (dpi / 150) ** 2

        estimated_size = total_pages * base_size_per_page * size_multiplier
        return int(estimated_size)

    def reset_folders(self) -> int:
        """
        Reset input and output folders.

        Returns:
            Total number of items deleted

        Raises:
            UserFriendlyError: If reset fails
        """
        try:
            results = self.path_manager.reset_directories()
            return sum(results.values())
        except Exception as e:
            raise UserFriendlyError(
                message="フォルダの初期化に失敗しました",
                suggestion="ファイルが他のプログラムで使用されていないか確認してください",
                original_error=e
            )

    def convert_to_images(self, config: ConversionConfig) -> List[Path]:
        """
        Synchronous image conversion for simple use cases.

        Args:
            config: Conversion configuration

        Returns:
            List of generated image files

        Raises:
            UserFriendlyError: If conversion fails
        """
        try:
            files = self.path_manager.find_pdf_files()
            if not files:
                raise UserFriendlyError(
                    message="変換するPDFファイルが見つかりません",
                    suggestion="InputフォルダにPDFファイルを配置してください"
                )

            output_files = []
            for file_path in files:
                converted_files = self.pdf_processor.convert_pdf_to_images(
                    file_path, config, self.path_manager
                )
                output_files.extend(converted_files)

            return output_files

        except Exception as e:
            if isinstance(e, UserFriendlyError):
                raise
            raise UserFriendlyError(
                message="PNG変換中にエラーが発生しました",
                suggestion="ファイルの形式と権限を確認してください",
                original_error=e
            )

    def convert_to_powerpoint(self, config: ConversionConfig) -> Optional[Path]:
        """
        Synchronous PowerPoint conversion for simple use cases.

        Args:
            config: Conversion configuration

        Returns:
            Path to generated PowerPoint file

        Raises:
            UserFriendlyError: If conversion fails
        """
        try:
            files = self.path_manager.find_pdf_files()
            if not files:
                raise UserFriendlyError(
                    message="変換するPDFファイルが見つかりません",
                    suggestion="InputフォルダにPDFファイルを配置してください"
                )

            return self.pdf_processor.convert_to_pptx(files, config, self.path_manager)

        except Exception as e:
            if isinstance(e, UserFriendlyError):
                raise
            raise UserFriendlyError(
                message="PowerPoint変換中にエラーが発生しました",
                suggestion="ファイルの形式と権限を確認してください",
                original_error=e
            )

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)