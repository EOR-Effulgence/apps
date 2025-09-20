"""
Core PDF processing functionality with unified conversion logic.
Eliminates code duplication across GUI and standalone scripts.
"""

from __future__ import annotations

import fitz
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Iterator, Optional, Tuple, List, Dict, Any
from io import BytesIO
from abc import ABC, abstractmethod


@dataclass
class ConversionConfig:
    """Configuration for PDF conversion operations."""
    scale_factor: float = 1.5
    auto_rotate: bool = True
    slide_width_mm: float = 420.0
    slide_height_mm: float = 297.0
    target_dpi: int = 150

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.scale_factor <= 0:
            raise ValueError("Scale factor must be positive")
        if self.target_dpi < 72:
            raise ValueError("DPI must be at least 72")


@dataclass
class PageInfo:
    """Information about a processed PDF page."""
    page_number: int
    original_size: Tuple[float, float]  # width, height in points
    is_portrait: bool
    was_rotated: bool
    final_size: Tuple[float, float]  # after rotation


class PDFProcessingError(Exception):
    """Raised when PDF processing fails."""
    pass


class PDFProcessor:
    """High-level PDF processing interface."""

    def __init__(self, config: Optional[ConversionConfig] = None):
        """Initialize processor with configuration."""
        self.config = config or ConversionConfig()

    def count_pages(self, pdf_path: Path) -> int:
        """Count pages in PDF file."""
        try:
            with open_pdf_document(pdf_path) as doc:
                return len(doc)
        except Exception as e:
            raise PDFProcessingError(f"Failed to count pages in {pdf_path}: {e}")

    def convert_pdf_to_images(self, pdf_path: Path, config: ConversionConfig, path_manager, progress_callback=None) -> List[Path]:
        """Convert PDF to images using image converter service."""
        try:
            from .image_converter import ImageConversionService
            service = ImageConversionService(config)
            if progress_callback:
                service.set_progress_callback(progress_callback)

            output_dir = path_manager.output_dir
            return service.convert_pdf_to_images(pdf_path, output_dir)
        except Exception as e:
            raise PDFProcessingError(f"Failed to convert {pdf_path} to images: {e}")

    def convert_to_pptx(self, files: List[Path], config: ConversionConfig, path_manager) -> Optional[Path]:
        """Convert PDFs to PowerPoint using powerpoint converter service."""
        try:
            from .powerpoint_converter import PowerPointConversionService
            service = PowerPointConversionService(config)

            # Use the first PDF file's name for the output PowerPoint
            if files:
                first_pdf_name = files[0].stem
                output_filename = f"{first_pdf_name}.pptx"
                output_path = path_manager.output_dir / output_filename
            else:
                output_path = path_manager.output_dir / "presentation.pptx"

            if len(files) == 1:
                return service.convert_pdf_to_powerpoint(files[0], path_manager.output_dir, output_filename)
            else:
                # Multiple files to single presentation
                return service.convert_multiple_pdfs_to_single_presentation(files, output_path)
        except Exception as e:
            raise PDFProcessingError(f"Failed to convert PDFs to PowerPoint: {e}")

    def convert_to_images(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """Convert PDF to PNG images."""
        try:
            from .image_converter import ImageConversionService
            service = ImageConversionService(self.config)
            return service.convert_pdf_to_images(pdf_path, output_dir)
        except Exception as e:
            raise PDFProcessingError(f"Failed to convert {pdf_path} to images: {e}")

    def convert_to_powerpoint(self, pdf_path: Path, output_dir: Path) -> Path:
        """Convert PDF to PowerPoint presentation."""
        try:
            from .powerpoint_converter import PowerPointConversionService
            service = PowerPointConversionService(self.config)
            return service.convert_pdf_to_powerpoint(pdf_path, output_dir)
        except Exception as e:
            raise PDFProcessingError(f"Failed to convert {pdf_path} to PowerPoint: {e}")

    def get_pdf_info(self, pdf_path: Path) -> dict:
        """Get information about PDF file."""
        try:
            with open_pdf_document(pdf_path) as doc:
                return {
                    'page_count': len(doc),
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'subject': doc.metadata.get('subject', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'pages': [
                        PageInfo(
                            page_number=i + 1,
                            original_size=(page.rect.width, page.rect.height),
                            is_portrait=page.rect.width < page.rect.height,
                            was_rotated=False,
                            final_size=(page.rect.width, page.rect.height)
                        )
                        for i, page in enumerate(doc)
                    ]
                }
        except Exception as e:
            raise PDFProcessingError(f"Failed to get PDF info: {e}")


@contextmanager
def open_pdf_document(file_path: Path) -> Generator[fitz.Document, None, None]:
    """
    Safely open and close PDF document with proper resource management.

    Args:
        file_path: Path to PDF file

    Yields:
        Opened PyMuPDF document

    Raises:
        PDFProcessingError: If PDF cannot be opened
    """
    if not file_path.exists():
        raise PDFProcessingError(f"PDF file not found: {file_path}")

    if not file_path.suffix.lower() == '.pdf':
        raise PDFProcessingError(f"Not a PDF file: {file_path}")

    try:
        doc = fitz.open(str(file_path))
        yield doc
    except Exception as e:
        raise PDFProcessingError(f"Failed to open PDF {file_path}: {e}")
    finally:
        if 'doc' in locals():
            doc.close()


def analyze_page_orientation(page: fitz.Page) -> Tuple[bool, Tuple[float, float]]:
    """
    Analyze page orientation and dimensions.

    Args:
        page: PyMuPDF page object

    Returns:
        Tuple of (is_portrait, (width, height))
    """
    rect = page.rect
    width, height = rect.width, rect.height
    is_portrait = width < height
    return is_portrait, (width, height)


def process_page_to_pixmap(
    page: fitz.Page,
    config: ConversionConfig
) -> Tuple[fitz.Pixmap, PageInfo]:
    """
    Process a PDF page to pixmap with optional rotation.

    Args:
        page: PyMuPDF page to process
        config: Conversion configuration

    Returns:
        Tuple of (processed pixmap, page info)

    Raises:
        PDFProcessingError: If page processing fails
    """
    try:
        is_portrait, original_size = analyze_page_orientation(page)

        # Determine rotation
        rotation = 90 if (config.auto_rotate and is_portrait) else 0

        # Create transformation matrix with rotation
        if rotation == 90:
            # Rotate 90 degrees: apply rotation to matrix
            matrix = fitz.Matrix(config.scale_factor, config.scale_factor) * fitz.Matrix(90)
        else:
            matrix = fitz.Matrix(config.scale_factor, config.scale_factor)

        # Generate pixmap with scaling and rotation
        pixmap = page.get_pixmap(matrix=matrix)

        # Calculate final size after rotation
        if rotation == 90:
            final_size = (original_size[1], original_size[0])  # Swap width/height
        else:
            final_size = original_size

        page_info = PageInfo(
            page_number=page.number + 1,
            original_size=original_size,
            is_portrait=is_portrait,
            was_rotated=(rotation == 90),
            final_size=final_size
        )

        return pixmap, page_info

    except Exception as e:
        raise PDFProcessingError(f"Failed to process page {page.number + 1}: {e}")


def process_page_to_bytes(
    page: fitz.Page,
    config: ConversionConfig,
    format: str = "png"
) -> Tuple[bytes, PageInfo]:
    """
    Process PDF page directly to image bytes.

    Args:
        page: PyMuPDF page to process
        config: Conversion configuration
        format: Output format ("png", "jpeg", etc.)

    Returns:
        Tuple of (image bytes, page info)
    """
    pixmap, page_info = process_page_to_pixmap(page, config)

    try:
        image_bytes = pixmap.tobytes(format)
        return image_bytes, page_info
    finally:
        # Clean up pixmap memory
        pixmap = None


def get_pdf_pages(pdf_path: Path) -> Iterator[fitz.Page]:
    """
    Iterator over PDF pages with proper resource management.

    Args:
        pdf_path: Path to PDF file

    Yields:
        PDF pages one at a time
    """
    with open_pdf_document(pdf_path) as doc:
        for page_num in range(len(doc)):
            yield doc[page_num]


def extract_pdf_metadata(pdf_path: Path) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary containing PDF metadata

    Raises:
        PDFProcessingError: If metadata extraction fails
    """
    try:
        with open_pdf_document(pdf_path) as doc:
            metadata = doc.metadata or {}

            # Basic information
            info = {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'keywords': metadata.get('keywords', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(doc),
                'file_size': pdf_path.stat().st_size,
                'encrypted': doc.needs_pass,
                'pdf_version': getattr(doc, 'pdf_version', 'unknown')
            }

            # Page analysis
            pages_info = []
            for page_num, page in enumerate(doc):
                rect = page.rect
                pages_info.append({
                    'page_number': page_num + 1,
                    'width': rect.width,
                    'height': rect.height,
                    'rotation': page.rotation,
                    'has_images': bool(page.get_images()),
                    'has_text': bool(page.get_text().strip()),
                    'mediabox': [rect.x0, rect.y0, rect.x1, rect.y1]
                })

            info['pages'] = pages_info
            return info

    except Exception as e:
        raise PDFProcessingError(f"Failed to extract metadata from {pdf_path}: {e}")


def count_total_pages(pdf_files: list[Path]) -> int:
    """
    Count total pages across multiple PDF files.

    Args:
        pdf_files: List of PDF file paths

    Returns:
        Total page count

    Raises:
        PDFProcessingError: If any PDF cannot be read
    """
    total = 0
    for pdf_path in pdf_files:
        try:
            with open_pdf_document(pdf_path) as doc:
                total += len(doc)
        except PDFProcessingError:
            # Re-raise with context about which file failed
            raise PDFProcessingError(f"Failed to count pages in {pdf_path}")

    return total


# Unit conversion utilities
def mm_to_emu(mm: float) -> int:
    """Convert millimeters to EMU (English Metric Units)."""
    return int((mm / 25.4) * 914400)


def points_to_emu(points: float) -> int:
    """Convert PDF points to EMU."""
    return int((points / 72) * 914400)


def emu_to_inches(emu: int) -> float:
    """Convert EMU to inches."""
    return emu / 914400


def validate_conversion_config(config: ConversionConfig) -> None:
    """
    Validate conversion configuration parameters.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    if config.scale_factor <= 0 or config.scale_factor > 10:
        raise ValueError("Scale factor must be between 0 and 10")

    if config.slide_width_mm <= 0 or config.slide_height_mm <= 0:
        raise ValueError("Slide dimensions must be positive")

    if config.target_dpi < 72 or config.target_dpi > 600:
        raise ValueError("DPI must be between 72 and 600")


class ConversionService(ABC):
    """
    Abstract base class for conversion services.
    Defines the interface for PDF conversion operations.
    """

    def __init__(self, config: ConversionConfig):
        self.config = config
        self.validate_config()

    def validate_config(self) -> None:
        """Validate the conversion configuration."""
        validate_conversion_config(self.config)

    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """Abstract method for conversion operation."""
        pass