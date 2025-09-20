"""
Image conversion service for PDF to PNG conversion.
Provides modular, reusable image conversion functionality.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Callable
from io import BytesIO

from .pdf_processor import (
    ConversionConfig,
    ConversionService,
    open_pdf_document,
    process_page_to_pixmap,
    PDFProcessingError
)


class ImageConversionService(ConversionService):
    """
    Service for converting PDF files to PNG images.
    Provides high-quality image generation with configurable scaling and rotation.
    """

    def __init__(self, config: ConversionConfig):
        super().__init__(config)
        self.progress_callback: Optional[Callable[[int], None]] = None

    def set_progress_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback function for progress updates."""
        self.progress_callback = callback

    def convert_pdf_to_images(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        Convert a single PDF file to PNG images.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save PNG files

        Returns:
            List of generated PNG file paths

        Raises:
            PDFProcessingError: If conversion fails
        """
        if not pdf_path.exists() or not pdf_path.suffix.lower() == '.pdf':
            raise PDFProcessingError(f"Invalid PDF file: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_files = []
        base_name = pdf_path.stem

        try:
            with open_pdf_document(pdf_path) as doc:
                total_pages = len(doc)

                for page_num, page in enumerate(doc, start=1):
                    # Process page to pixmap
                    pixmap, page_info = process_page_to_pixmap(page, self.config)

                    try:
                        # Generate output filename
                        output_filename = f"{base_name}_page_{page_num:03d}.png"
                        output_path = output_dir / output_filename

                        # Save image with high quality
                        pixmap.save(str(output_path))
                        output_files.append(output_path)

                        # Update progress if callback is set
                        if self.progress_callback:
                            self.progress_callback(page_num)

                    finally:
                        # Clean up pixmap memory immediately
                        pixmap = None

        except Exception as e:
            raise PDFProcessingError(f"Failed to convert {pdf_path} to images: {e}")

        return output_files

    def convert_multiple_pdfs(self, pdf_files: List[Path], output_dir: Path) -> List[Path]:
        """
        Convert multiple PDF files to PNG images.

        Args:
            pdf_files: List of PDF file paths
            output_dir: Directory to save PNG files

        Returns:
            List of all generated PNG file paths

        Raises:
            PDFProcessingError: If any conversion fails
        """
        all_output_files = []

        for pdf_file in pdf_files:
            try:
                output_files = self.convert_pdf_to_images(pdf_file, output_dir)
                all_output_files.extend(output_files)
            except PDFProcessingError as e:
                # Re-raise with context about which file failed
                raise PDFProcessingError(f"Failed processing {pdf_file.name}: {e}")

        return all_output_files

    def get_image_info(self, pdf_path: Path) -> dict:
        """
        Get information about images that would be generated from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with image generation information

        Raises:
            PDFProcessingError: If PDF cannot be analyzed
        """
        try:
            with open_pdf_document(pdf_path) as doc:
                pages_info = []

                for page_num, page in enumerate(doc, start=1):
                    rect = page.rect
                    is_portrait = rect.width < rect.height

                    # Calculate final dimensions after potential rotation
                    if self.config.auto_rotate and is_portrait:
                        final_width = rect.height * self.config.scale_factor
                        final_height = rect.width * self.config.scale_factor
                        rotation = 90
                    else:
                        final_width = rect.width * self.config.scale_factor
                        final_height = rect.height * self.config.scale_factor
                        rotation = 0

                    pages_info.append({
                        'page_number': page_num,
                        'original_size': (rect.width, rect.height),
                        'final_size': (final_width, final_height),
                        'rotation': rotation,
                        'is_portrait': is_portrait,
                        'estimated_file_size_mb': (final_width * final_height * 3) / (1024 * 1024)  # Rough estimate
                    })

                return {
                    'pdf_name': pdf_path.name,
                    'total_pages': len(doc),
                    'pages': pages_info,
                    'total_estimated_size_mb': sum(p['estimated_file_size_mb'] for p in pages_info)
                }

        except Exception as e:
            raise PDFProcessingError(f"Failed to analyze PDF {pdf_path}: {e}")

    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convert single PDF to images (implementation of abstract method).

        Args:
            input_path: PDF file path
            output_path: Output directory path

        Returns:
            True if conversion successful

        Raises:
            PDFProcessingError: If conversion fails
        """
        output_files = self.convert_pdf_to_images(input_path, output_path)
        return len(output_files) > 0