"""
Domain Layer - Pure Business Logic

This layer contains the core business logic and domain entities.
It has no dependencies on external frameworks or infrastructure.

Components:
- entities: Core business objects (PDFDocument, ConversionJob, etc.)
- value_objects: Immutable values (ConversionConfig, PageInfo, etc.)
- repositories: Interfaces for data access
- services: Domain services for complex business logic
"""

from .entities.pdf_document import PDFDocument, PDFPage
from .entities.conversion_job import ConversionJob
from .value_objects.conversion_config import ConversionConfig
from .value_objects.conversion_result import ConversionResult
from .value_objects.page_info import PageInfo
from .repositories.pdf_repository import PDFRepository
from .repositories.file_repository import FileRepository
from .services.conversion_service import ConversionDomainService

__all__ = [
    # Entities
    "PDFDocument",
    "PDFPage",
    "ConversionJob",

    # Value Objects
    "ConversionConfig",
    "ConversionResult",
    "PageInfo",

    # Repository Interfaces
    "PDFRepository",
    "FileRepository",

    # Domain Services
    "ConversionDomainService"
]