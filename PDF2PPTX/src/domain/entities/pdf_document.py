"""
PDF Document Domain Entity

Represents a PDF document and its pages in the business domain.
Contains business logic for PDF manipulation and validation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class PDFPage:
    """Represents a single page within a PDF document."""

    number: int
    width: float
    height: float
    rotation: int = 0
    has_text: bool = False
    has_images: bool = False

    @property
    def is_portrait(self) -> bool:
        """Check if page is in portrait orientation."""
        return self.height > self.width

    @property
    def is_landscape(self) -> bool:
        """Check if page is in landscape orientation."""
        return self.width > self.height

    @property
    def aspect_ratio(self) -> float:
        """Calculate page aspect ratio (width/height)."""
        return self.width / self.height if self.height > 0 else 1.0

    def should_auto_rotate(self) -> bool:
        """Determine if page should be auto-rotated based on business rules."""
        return self.is_portrait and self.has_text


@dataclass
class PDFDocument:
    """
    Represents a PDF document in the domain model.

    This entity encapsulates all business logic related to PDF documents,
    including validation, metadata management, and page operations.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: Path = field(default_factory=lambda: Path())
    pages: List[PDFPage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the document after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate document state."""
        if not self.file_path.exists():
            raise ValueError(f"PDF file does not exist: {self.file_path}")

        if self.file_path.suffix.lower() != '.pdf':
            raise ValueError(f"File is not a PDF: {self.file_path}")

    @property
    def page_count(self) -> int:
        """Get the total number of pages."""
        return len(self.pages)

    @property
    def file_name(self) -> str:
        """Get the file name without path."""
        return self.file_path.name

    @property
    def file_size(self) -> int:
        """Get file size in bytes."""
        return self.file_path.stat().st_size if self.file_path.exists() else 0

    @property
    def title(self) -> str:
        """Get document title from metadata or filename."""
        return self.metadata.get('title', self.file_path.stem)

    @property
    def author(self) -> str:
        """Get document author from metadata."""
        return self.metadata.get('author', '')

    @property
    def has_portrait_pages(self) -> bool:
        """Check if document contains any portrait pages."""
        return any(page.is_portrait for page in self.pages)

    @property
    def has_landscape_pages(self) -> bool:
        """Check if document contains any landscape pages."""
        return any(page.is_landscape for page in self.pages)

    @property
    def mixed_orientation(self) -> bool:
        """Check if document has mixed page orientations."""
        return self.has_portrait_pages and self.has_landscape_pages

    def get_page(self, page_number: int) -> Optional[PDFPage]:
        """
        Get a specific page by number (1-based indexing).

        Args:
            page_number: Page number (starting from 1)

        Returns:
            PDFPage if found, None otherwise
        """
        if 1 <= page_number <= len(self.pages):
            return self.pages[page_number - 1]
        return None

    def get_pages_requiring_rotation(self) -> List[PDFPage]:
        """Get pages that should be auto-rotated based on business rules."""
        return [page for page in self.pages if page.should_auto_rotate()]

    def get_portrait_pages(self) -> List[PDFPage]:
        """Get all portrait pages."""
        return [page for page in self.pages if page.is_portrait]

    def get_landscape_pages(self) -> List[PDFPage]:
        """Get all landscape pages."""
        return [page for page in self.pages if page.is_landscape]

    def add_page(self, page: PDFPage) -> None:
        """
        Add a page to the document.

        Args:
            page: Page to add
        """
        self.pages.append(page)

    def remove_page(self, page_number: int) -> bool:
        """
        Remove a page by number.

        Args:
            page_number: Page number to remove (1-based)

        Returns:
            True if page was removed, False if not found
        """
        if 1 <= page_number <= len(self.pages):
            self.pages.pop(page_number - 1)
            # Renumber remaining pages
            for i, page in enumerate(self.pages):
                page.number = i + 1
            return True
        return False

    def validate_for_conversion(self) -> List[str]:
        """
        Validate document for conversion operations.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.pages:
            errors.append("Document has no pages")

        if self.file_size == 0:
            errors.append("Document file is empty")

        if self.file_size > 100 * 1024 * 1024:  # 100MB
            errors.append("Document file is too large (>100MB)")

        # Check for damaged pages
        for page in self.pages:
            if page.width <= 0 or page.height <= 0:
                errors.append(f"Page {page.number} has invalid dimensions")

        return errors

    def estimate_conversion_complexity(self) -> int:
        """
        Estimate conversion complexity score for resource planning.

        Returns:
            Complexity score (1-10, where 10 is most complex)
        """
        base_score = 1

        # Page count factor
        if self.page_count > 50:
            base_score += 3
        elif self.page_count > 20:
            base_score += 2
        elif self.page_count > 10:
            base_score += 1

        # File size factor
        size_mb = self.file_size / (1024 * 1024)
        if size_mb > 50:
            base_score += 3
        elif size_mb > 20:
            base_score += 2
        elif size_mb > 10:
            base_score += 1

        # Mixed orientation complexity
        if self.mixed_orientation:
            base_score += 1

        # Content complexity (images and text)
        complex_pages = sum(1 for page in self.pages if page.has_images and page.has_text)
        if complex_pages > self.page_count * 0.5:
            base_score += 1

        return min(base_score, 10)

    def to_summary_dict(self) -> Dict[str, Any]:
        """
        Create a summary dictionary for logging/display purposes.

        Returns:
            Dictionary with document summary information
        """
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_path': str(self.file_path),
            'page_count': self.page_count,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2),
            'title': self.title,
            'author': self.author,
            'has_portrait_pages': self.has_portrait_pages,
            'has_landscape_pages': self.has_landscape_pages,
            'mixed_orientation': self.mixed_orientation,
            'complexity_score': self.estimate_conversion_complexity(),
            'created_at': self.created_at.isoformat()
        }

    def __str__(self) -> str:
        """String representation of the document."""
        return f"PDFDocument('{self.file_name}', {self.page_count} pages)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"PDFDocument(id='{self.id}', file_path='{self.file_path}', "
                f"page_count={self.page_count}, file_size={self.file_size})")

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, PDFDocument):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dictionaries."""
        return hash(self.id)