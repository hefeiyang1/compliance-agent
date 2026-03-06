"""
RAG module for ComplianceAgent.

Provides document processing, vector storage, and retrieval capabilities.
"""

from .parsers import (
    DocumentType,
    ParsedDocument,
    BaseParser,
    PDFParser,
    DocxParser,
    MarkdownParser,
    TextParser,
    create_parser,
    parse_document,
)

__all__ = [
    # Parsers
    "DocumentType",
    "ParsedDocument",
    "BaseParser",
    "PDFParser",
    "DocxParser",
    "MarkdownParser",
    "TextParser",
    "create_parser",
    "parse_document",
]
