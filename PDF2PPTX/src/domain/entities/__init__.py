"""
Domain Entities

Entities are objects with identity that encapsulate business logic.
They maintain state and behavior that is central to the business domain.
"""

from .pdf_document import PDFDocument, PDFPage
from .conversion_job import ConversionJob, ConversionStatus

__all__ = [
    "PDFDocument",
    "PDFPage",
    "ConversionJob",
    "ConversionStatus"
]