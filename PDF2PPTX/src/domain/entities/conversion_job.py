"""
Conversion Job Domain Entity

Represents a conversion operation with its lifecycle and business rules.
Manages the state and progress of PDF conversion operations.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable

from .pdf_document import PDFDocument
from ..value_objects.conversion_config import ConversionConfig
from ..value_objects.conversion_result import ConversionResult


class ConversionStatus(Enum):
    """Status of a conversion job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ConversionType(Enum):
    """Type of conversion operation."""
    PDF_TO_IMAGES = "pdf_to_images"
    PDF_TO_PPTX = "pdf_to_pptx"
    PDF_TO_PDF = "pdf_to_pdf"  # For optimization/compression


@dataclass
class ConversionProgress:
    """Represents the progress of a conversion operation."""
    current_page: int = 0
    total_pages: int = 0
    current_file: Optional[str] = None
    current_operation: Optional[str] = None
    bytes_processed: int = 0
    total_bytes: int = 0

    @property
    def page_percentage(self) -> float:
        """Calculate percentage based on pages."""
        if self.total_pages <= 0:
            return 0.0
        return min(100.0, (self.current_page / self.total_pages) * 100)

    @property
    def byte_percentage(self) -> float:
        """Calculate percentage based on bytes."""
        if self.total_bytes <= 0:
            return 0.0
        return min(100.0, (self.bytes_processed / self.total_bytes) * 100)

    @property
    def overall_percentage(self) -> float:
        """Calculate overall progress percentage."""
        # Prefer page-based progress, fall back to byte-based
        if self.total_pages > 0:
            return self.page_percentage
        return self.byte_percentage


@dataclass
class ConversionJob:
    """
    Represents a PDF conversion job in the domain model.

    This entity manages the lifecycle of conversion operations,
    including validation, progress tracking, and result management.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    documents: List[PDFDocument] = field(default_factory=list)
    config: ConversionConfig = field(default_factory=ConversionConfig)
    conversion_type: ConversionType = ConversionType.PDF_TO_IMAGES
    status: ConversionStatus = ConversionStatus.PENDING
    progress: ConversionProgress = field(default_factory=ConversionProgress)
    results: List[ConversionResult] = field(default_factory=list)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_directory: Optional[Path] = None

    def __post_init__(self):
        """Initialize the job after creation."""
        self._validate_documents()
        self._calculate_total_work()

    def _validate_documents(self) -> None:
        """Validate that documents are suitable for conversion."""
        if not self.documents:
            raise ValueError("No documents provided for conversion")

        for doc in self.documents:
            errors = doc.validate_for_conversion()
            if errors:
                raise ValueError(f"Document {doc.file_name} validation failed: {'; '.join(errors)}")

    def _calculate_total_work(self) -> None:
        """Calculate total work for progress tracking."""
        self.progress.total_pages = sum(doc.page_count for doc in self.documents)
        self.progress.total_bytes = sum(doc.file_size for doc in self.documents)

    @property
    def document_count(self) -> int:
        """Get number of documents in the job."""
        return len(self.documents)

    @property
    def total_pages(self) -> int:
        """Get total number of pages across all documents."""
        return sum(doc.page_count for doc in self.documents)

    @property
    def total_file_size(self) -> int:
        """Get total file size of all documents."""
        return sum(doc.file_size for doc in self.documents)

    @property
    def estimated_duration(self) -> timedelta:
        """Estimate job duration based on complexity."""
        # Base time per page (empirically determined)
        base_seconds_per_page = 0.5

        # Complexity factors
        complexity_factor = 1.0
        if self.conversion_type == ConversionType.PDF_TO_PPTX:
            complexity_factor = 1.5  # PPT conversion is more complex

        # Scale factor impact
        scale_factor = getattr(self.config, 'scale_factor', 1.0)
        scale_impact = 1.0 + (scale_factor - 1.0) * 0.3

        # Document complexity
        avg_complexity = sum(doc.estimate_conversion_complexity() for doc in self.documents) / len(self.documents)
        complexity_impact = 1.0 + (avg_complexity - 1) * 0.1

        total_seconds = (self.total_pages * base_seconds_per_page *
                        complexity_factor * scale_impact * complexity_impact)

        return timedelta(seconds=max(1, int(total_seconds)))

    @property
    def is_completed(self) -> bool:
        """Check if job is in a completed state."""
        return self.status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED]

    @property
    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status == ConversionStatus.RUNNING

    @property
    def can_be_cancelled(self) -> bool:
        """Check if job can be cancelled."""
        return self.status in [ConversionStatus.PENDING, ConversionStatus.RUNNING, ConversionStatus.PAUSED]

    @property
    def duration(self) -> Optional[timedelta]:
        """Get actual job duration if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return datetime.now() - self.started_at
        return None

    def start(self) -> None:
        """Start the conversion job."""
        if self.status != ConversionStatus.PENDING:
            raise ValueError(f"Cannot start job in status: {self.status}")

        self.status = ConversionStatus.RUNNING
        self.started_at = datetime.now()
        self.error_message = None

    def pause(self) -> None:
        """Pause the conversion job."""
        if self.status != ConversionStatus.RUNNING:
            raise ValueError(f"Cannot pause job in status: {self.status}")

        self.status = ConversionStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused conversion job."""
        if self.status != ConversionStatus.PAUSED:
            raise ValueError(f"Cannot resume job in status: {self.status}")

        self.status = ConversionStatus.RUNNING

    def cancel(self) -> None:
        """Cancel the conversion job."""
        if not self.can_be_cancelled:
            raise ValueError(f"Cannot cancel job in status: {self.status}")

        self.status = ConversionStatus.CANCELLED
        self.completed_at = datetime.now()

    def complete_successfully(self, results: List[ConversionResult]) -> None:
        """Mark job as successfully completed."""
        if self.status != ConversionStatus.RUNNING:
            raise ValueError(f"Cannot complete job in status: {self.status}")

        self.status = ConversionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.results = results
        self.progress.current_page = self.progress.total_pages

    def fail(self, error_message: str) -> None:
        """Mark job as failed."""
        if self.status not in [ConversionStatus.RUNNING, ConversionStatus.PAUSED]:
            raise ValueError(f"Cannot fail job in status: {self.status}")

        self.status = ConversionStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message

    def update_progress(
        self,
        current_page: Optional[int] = None,
        current_file: Optional[str] = None,
        current_operation: Optional[str] = None,
        bytes_processed: Optional[int] = None
    ) -> None:
        """Update job progress."""
        if current_page is not None:
            self.progress.current_page = min(current_page, self.progress.total_pages)

        if current_file is not None:
            self.progress.current_file = current_file

        if current_operation is not None:
            self.progress.current_operation = current_operation

        if bytes_processed is not None:
            self.progress.bytes_processed = min(bytes_processed, self.progress.total_bytes)

    def add_result(self, result: ConversionResult) -> None:
        """Add a conversion result to the job."""
        self.results.append(result)

    def get_results_for_document(self, document: PDFDocument) -> List[ConversionResult]:
        """Get results for a specific document."""
        return [result for result in self.results if result.source_document_id == document.id]

    def validate_configuration(self) -> List[str]:
        """
        Validate job configuration against business rules.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check output directory
        if self.output_directory and not self.output_directory.exists():
            try:
                self.output_directory.mkdir(parents=True, exist_ok=True)
            except Exception:
                errors.append(f"Cannot create output directory: {self.output_directory}")

        # Check available disk space
        if self.output_directory:
            try:
                import shutil
                free_space = shutil.disk_usage(self.output_directory).free
                estimated_output_size = self._estimate_output_size()

                if estimated_output_size > free_space:
                    errors.append(
                        f"Insufficient disk space. Need: {estimated_output_size // (1024**2)}MB, "
                        f"Available: {free_space // (1024**2)}MB"
                    )
            except Exception:
                pass  # Skip disk space check if not available

        # Validate conversion-specific rules
        if self.conversion_type == ConversionType.PDF_TO_PPTX:
            if self.total_pages > 500:
                errors.append("PowerPoint conversion supports maximum 500 pages")

        # Check for very large files
        max_file_size = 200 * 1024 * 1024  # 200MB
        large_files = [doc.file_name for doc in self.documents if doc.file_size > max_file_size]
        if large_files:
            errors.append(f"Files too large for processing: {', '.join(large_files)}")

        return errors

    def _estimate_output_size(self) -> int:
        """Estimate total output file size in bytes."""
        scale_factor = getattr(self.config, 'scale_factor', 1.0)
        base_size_per_page = 1024 * 1024  # 1MB per page base

        if self.conversion_type == ConversionType.PDF_TO_IMAGES:
            # Image files are typically larger
            size_multiplier = (scale_factor ** 2) * 2
        elif self.conversion_type == ConversionType.PDF_TO_PPTX:
            # PowerPoint files are compressed
            size_multiplier = 0.5
        else:
            size_multiplier = 1.0

        return int(self.total_pages * base_size_per_page * size_multiplier)

    def to_summary_dict(self) -> Dict[str, Any]:
        """Create a summary dictionary for logging/display."""
        return {
            'id': self.id,
            'status': self.status.value,
            'conversion_type': self.conversion_type.value,
            'document_count': self.document_count,
            'total_pages': self.total_pages,
            'total_file_size_mb': round(self.total_file_size / (1024**2), 2),
            'progress_percentage': round(self.progress.overall_percentage, 1),
            'current_page': self.progress.current_page,
            'current_file': self.progress.current_file,
            'current_operation': self.progress.current_operation,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            'estimated_duration_seconds': self.estimated_duration.total_seconds(),
            'results_count': len(self.results)
        }

    def __str__(self) -> str:
        """String representation of the job."""
        return f"ConversionJob({self.conversion_type.value}, {self.status.value}, {self.document_count} docs)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"ConversionJob(id='{self.id}', type='{self.conversion_type.value}', "
                f"status='{self.status.value}', documents={self.document_count})")