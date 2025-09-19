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
                continue

        current_page = 0

        for file_path in job.files:
            try:
                progress_callback(current_page, total_pages, file_path.name)

                converted_files = self.pdf_processor.convert_to_images(
                    file_path,
                    job.config,
                    self.path_manager,
                    lambda: progress_callback(current_page + 1, total_pages, file_path.name)
                )

                output_files.extend(converted_files)
                current_page += self.pdf_processor.count_pages(file_path)

            except Exception as e:
                # Log error but continue with other files
                job.error_message = f"Error converting {file_path.name}: {str(e)}"
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

        for file_path in files:
            try:
                page_count = self.pdf_processor.count_pages(file_path)
                total_pages += page_count
            except Exception:
                total_pages += 5  # Assume 5 pages for unreadable files

        # Estimate based on scale factor and page count
        # Base time: 0.5 seconds per page
        # Scale factor impact: linear increase
        base_time_per_page = 0.5
        scale_impact = config.scale_factor

        estimated_time = total_pages * base_time_per_page * scale_impact

        # Add overhead for file I/O and processing
        overhead = len(files) * 2  # 2 seconds per file for I/O

        return estimated_time + overhead

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

        # Estimate memory usage
        estimated_time = self.estimate_conversion_time(files, config)
        if estimated_time > 300:  # 5 minutes
            return "変換時間が長すぎる可能性があります。ファイル数を減らすかスケール倍率を下げてください。"

        return None

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)