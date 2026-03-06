"""
Unit tests for document parsers.

Tests PDF, DOCX, Markdown, and text parsers to ensure correct content extraction
and metadata handling.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from src.rag.parsers import (
    DocumentType,
    ParsedDocument,
    PDFParser,
    DocxParser,
    MarkdownParser,
    TextParser,
    create_parser,
    parse_document,
)


class TestParsedDocument:
    """Test ParsedDocument dataclass."""

    def test_calculate_hash(self):
        """Test content hash calculation for deduplication."""
        doc = ParsedDocument(
            content="Test content",
            metadata={},
            page_count=1,
            total_tokens=0,
            document_type=DocumentType.TEXT
        )
        hash1 = doc.calculate_hash()
        hash2 = doc.calculate_hash()

        # Same content should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 character hex string

    def test_calculate_hash_different_content(self):
        """Test that different content produces different hashes."""
        doc1 = ParsedDocument(
            content="Test content one",
            metadata={},
            page_count=1,
            total_tokens=0,
            document_type=DocumentType.TEXT
        )
        doc2 = ParsedDocument(
            content="Test content two",
            metadata={},
            page_count=1,
            total_tokens=0,
            document_type=DocumentType.TEXT
        )

        assert doc1.calculate_hash() != doc2.calculate_hash()

    def test_estimate_tokens_english(self):
        """Test token estimation for English text."""
        doc = ParsedDocument(
            content="This is a test document with English text. " * 10,
            metadata={},
            page_count=1,
            total_tokens=0,
            document_type=DocumentType.TEXT
        )
        tokens = doc.estimate_tokens()

        # Should be approximately 1 token per 4 characters
        assert tokens > 0
        assert tokens < len(doc.content)  # Tokens should be less than characters

    def test_estimate_tokens_chinese(self):
        """Test token estimation for Chinese text."""
        doc = ParsedDocument(
            content="这是一个测试文档，包含中文内容。" * 10,
            metadata={},
            page_count=1,
            total_tokens=0,
            document_type=DocumentType.TEXT
        )
        tokens = doc.estimate_tokens()

        # Should be approximately 1 token per 1.5 characters for Chinese
        assert tokens > 0
        assert tokens > len(doc.content) / 2  # Chinese has more chars per token

    def test_estimate_tokens_mixed(self):
        """Test token estimation for mixed English and Chinese text."""
        doc = ParsedDocument(
            content="This is English. 这是中文。" * 10,
            metadata={},
            page_count=1,
            total_tokens=0,
            document_type=DocumentType.TEXT
        )
        tokens = doc.estimate_tokens()

        assert tokens > 0


class TestPDFParser:
    """Test PDF document parser."""

    def test_init_with_invalid_file(self, tmp_path):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            PDFParser(str(tmp_path / "nonexistent.pdf"))

    def test_init_with_non_pdf_file(self, tmp_path):
        """Test initialization with non-PDF file."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF")

        with pytest.raises(ValueError, match="Not a PDF file"):
            PDFParser(str(txt_file))

    @patch('src.rag.parsers.pdfplumber.open')
    def test_parse_with_pdfplumber(self, mock_pdf_open, tmp_path):
        """Test PDF parsing with pdfplumber."""
        # Create a mock PDF
        mock_pdf = MagicMock()
        mock_pdf.pages = 2
        mock_pdf.metadata = {'Title': 'Test PDF'}

        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"

        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdf_open.return_value = mock_pdf

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")

        parser = PDFParser(str(pdf_file), use_pdfplumber=True)
        result = parser.parse()

        assert result.document_type == DocumentType.PDF
        assert result.page_count == 2
        assert "Page 1 content" in result.content
        assert "Page 2 content" in result.content
        assert result.total_tokens > 0
        assert result.metadata["parser"] == "pdfplumber"
        assert result.metadata["page_count"] == 2

    @patch('src.rag.parsers.pdfplumber.open')
    def test_parse_with_pdfplumber_page_error(self, mock_pdf_open, tmp_path):
        """Test PDF parsing when page extraction fails."""
        # Create a mock PDF with a failing page
        mock_pdf = MagicMock()
        mock_pdf.pages = 2

        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"

        mock_page2 = MagicMock()
        mock_page2.extract_text.side_effect = Exception("Extraction failed")

        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdf_open.return_value = mock_pdf

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")

        parser = PDFParser(str(pdf_file), use_pdfplumber=True)
        result = parser.parse()

        # Should continue with other pages
        assert "Page 1 content" in result.content
        assert "Failed to extract text" in result.content

    @patch('src.rag.parsers.pypdf.PdfReader')
    def test_parse_with_pypdf(self, mock_pdf_reader_class, tmp_path):
        """Test PDF parsing with pypdf fallback."""
        # Create a mock PDF reader
        mock_reader = MagicMock()
        mock_reader.pages = 2
        mock_reader.metadata = {'/Title': 'Test PDF'}

        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content from pypdf"

        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content from pypdf"

        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader_class.return_value = mock_reader

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")

        parser = PDFParser(str(pdf_file), use_pdfplumber=False)
        result = parser.parse()

        assert result.document_type == DocumentType.PDF
        assert result.page_count == 2
        assert "Page 1 content from pypdf" in result.content
        assert "Page 2 content from pypdf" in result.content
        assert result.metadata["parser"] == "pypdf"


class TestDocxParser:
    """Test DOCX document parser."""

    def test_init_with_invalid_file(self, tmp_path):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            DocxParser(str(tmp_path / "nonexistent.docx"))

    def test_init_with_non_docx_file(self, tmp_path):
        """Test initialization with non-DOCX file."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a DOCX")

        with pytest.raises(ValueError, match="Not a Word document"):
            DocxParser(str(txt_file))

    @patch('src.rag.parsers.DocxDocument')
    def test_parse_docx(self, mock_docx_class, tmp_path):
        """Test DOCX parsing."""
        # Create mock document
        mock_doc = MagicMock()
        mock_doc.paragraphs = [
            MagicMock(text="First paragraph"),
            MagicMock(text="Second paragraph"),
            MagicMock(text=""),
            MagicMock(text="Third paragraph"),
        ]
        mock_doc.tables = []

        # Add core properties
        mock_doc.core_properties.title = "Test Document"
        mock_doc.core_properties.author = "Test Author"
        mock_doc.core_properties.created = None
        mock_doc.core_properties.modified = None

        mock_docx_class.return_value = mock_doc

        # Create a dummy file
        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"dummy docx content")

        parser = DocxParser(str(docx_file))
        result = parser.parse()

        assert result.document_type == DocumentType.DOCX
        assert "First paragraph" in result.content
        assert "Second paragraph" in result.content
        assert "Third paragraph" in result.content
        assert result.total_tokens > 0
        assert result.metadata["title"] == "Test Document"
        assert result.metadata["author"] == "Test Author"
        assert result.metadata["parser"] == "python-docx"

    @patch('src.rag.parsers.DocxDocument')
    def test_parse_docx_with_tables(self, mock_docx_class, tmp_path):
        """Test DOCX parsing with tables."""
        # Create mock document with tables
        mock_doc = MagicMock()
        mock_doc.paragraphs = [MagicMock(text="Text before table")]

        # Mock table
        mock_table = MagicMock()
        mock_row1 = MagicMock()
        mock_cell1_1 = MagicMock()
        mock_cell1_1.text = "Cell 1"
        mock_cell1_2 = MagicMock()
        mock_cell1_2.text = "Cell 2"
        mock_row1.cells = [mock_cell1_1, mock_cell1_2]

        mock_row2 = MagicMock()
        mock_cell2_1 = MagicMock()
        mock_cell2_1.text = "Cell 3"
        mock_cell2_2 = MagicMock()
        mock_cell2_2.text = "Cell 4"
        mock_row2.cells = [mock_cell2_1, mock_cell2_2]

        mock_table.rows = [mock_row1, mock_row2]
        mock_doc.tables = [mock_table]

        mock_doc.core_properties.title = None
        mock_doc.core_properties.author = None
        mock_doc.core_properties.created = None
        mock_doc.core_properties.modified = None

        mock_docx_class.return_value = mock_doc

        # Create a dummy file
        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"dummy docx content")

        parser = DocxParser(str(docx_file))
        result = parser.parse()

        assert "[Table]" in result.content
        assert "Cell 1" in result.content
        assert "Cell 2" in result.content
        assert result.metadata["table_count"] == 1


class TestMarkdownParser:
    """Test Markdown document parser."""

    def test_init_with_invalid_file(self, tmp_path):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            MarkdownParser(str(tmp_path / "nonexistent.md"))

    def test_init_with_non_markdown_file(self, tmp_path):
        """Test initialization with non-Markdown file."""
        txt_file = tmp_path / "test.pdf"
        txt_file.write_bytes(b"Not markdown")

        with pytest.raises(ValueError, match="Not a Markdown file"):
            MarkdownParser(str(txt_file))

    def test_parse_markdown_basic(self, tmp_path):
        """Test basic Markdown parsing."""
        content = """# Main Title

This is a paragraph.

## Subsection

More content here.
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(str(md_file))
        result = parser.parse()

        assert result.document_type == DocumentType.MARKDOWN
        assert "Main Title" in result.content
        assert "This is a paragraph" in result.content
        assert "Subsection" in result.content
        assert result.total_tokens > 0
        assert result.metadata["parser"] == "markdown"

    def test_parse_markdown_with_frontmatter(self, tmp_path):
        """Test Markdown parsing with YAML frontmatter."""
        content = """---
title: Test Document
author: John Doe
date: 2024-01-01
tags: [test, example]
---

# Content

This is the main content.
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(str(md_file))
        result = parser.parse()

        assert result.metadata["title"] == "Test Document"
        assert result.metadata["author"] == "John Doe"
        assert result.metadata["date"] == "2024-01-01"
        assert result.metadata["frontmatter"]["title"] == "Test Document"

    def test_parse_markdown_preserve_structure(self, tmp_path):
        """Test that structure is preserved when requested."""
        content = """# Title

**Bold** and *italic* text.

[Link text](https://example.com)
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(str(md_file), preserve_structure=True)
        result = parser.parse()

        assert "# Title" in result.content
        assert "**Bold**" in result.content
        assert "*italic*" in result.content

    def test_parse_markdown_remove_structure(self, tmp_path):
        """Test that structure is removed when requested."""
        content = """# Title

**Bold** and *italic* text.
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(str(md_file), preserve_structure=False)
        result = parser.parse()

        # Header markers should be removed
        assert result.content.count("#") < content.count("#")
        # Title text should still be there
        assert "Title" in result.content

    def test_count_sections(self, tmp_path):
        """Test that sections are counted correctly."""
        content = """# Title 1

Content 1.

## Title 2

Content 2.

### Title 3

Content 3.
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(str(md_file))
        result = parser.parse()

        assert result.metadata["section_count"] == 3


class TestTextParser:
    """Test plain text document parser."""

    def test_init_with_invalid_file(self, tmp_path):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            TextParser(str(tmp_path / "nonexistent.txt"))

    def test_init_with_non_text_file(self, tmp_path):
        """Test initialization with non-text file."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"Not text")

        with pytest.raises(ValueError, match="Not a text file"):
            TextParser(str(pdf_file))

    def test_parse_text_file(self, tmp_path):
        """Test text file parsing."""
        content = "Line 1\nLine 2\nLine 3"
        txt_file = tmp_path / "test.txt"
        txt_file.write_text(content, encoding='utf-8')

        parser = TextParser(str(txt_file))
        result = parser.parse()

        assert result.document_type == DocumentType.TEXT
        assert result.content == content
        assert result.total_tokens > 0
        assert result.metadata["parser"] == "text"
        assert result.metadata["line_count"] == 3

    def test_parse_text_file_multiline(self, tmp_path):
        """Test text file with multiple lines."""
        content = "\n".join([f"Line {i}" for i in range(100)])
        txt_file = tmp_path / "test.txt"
        txt_file.write_text(content, encoding='utf-8')

        parser = TextParser(str(txt_file))
        result = parser.parse()

        assert result.metadata["line_count"] == 100
        assert "Line 50" in result.content


class TestCreateParser:
    """Test parser factory function."""

    def test_create_pdf_parser(self, tmp_path):
        """Test creating PDF parser."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy")

        parser = create_parser(str(pdf_file))
        assert isinstance(parser, PDFParser)

    def test_create_docx_parser(self, tmp_path):
        """Test creating DOCX parser."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"dummy")

        parser = create_parser(str(docx_file))
        assert isinstance(parser, DocxParser)

    def test_create_markdown_parser(self, tmp_path):
        """Test creating Markdown parser."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        parser = create_parser(str(md_file))
        assert isinstance(parser, MarkdownParser)

    def test_create_text_parser(self, tmp_path):
        """Test creating text parser."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Test")

        parser = create_parser(str(txt_file))
        assert isinstance(parser, TextParser)

    def test_create_parser_unsupported_type(self, tmp_path):
        """Test creating parser for unsupported file type."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')

        with pytest.raises(ValueError, match="Unsupported file type"):
            create_parser(str(json_file))

    def test_create_parser_with_kwargs(self, tmp_path):
        """Test creating parser with additional arguments."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy")

        parser = create_parser(str(pdf_file), use_pdfplumber=False)
        assert isinstance(parser, PDFParser)
        assert parser.use_pdfplumber is False


class TestParseDocument:
    """Test convenience function for parsing documents."""

    @patch('src.rag.parsers.pdfplumber.open')
    def test_parse_document_convenience(self, mock_pdf_open, tmp_path):
        """Test the parse_document convenience function."""
        # Create a mock PDF
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content"
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {}
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdf_open.return_value = mock_pdf

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")

        result = parse_document(str(pdf_file))

        assert isinstance(result, ParsedDocument)
        assert "Test content" in result.content
        assert result.total_tokens > 0

    @patch('src.rag.parsers.pdfplumber.open')
    def test_parse_document_with_kwargs(self, mock_pdf_open, tmp_path):
        """Test parse_document with custom arguments."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content"
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {}
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdf_open.return_value = mock_pdf

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")

        result = parse_document(str(pdf_file), use_pdfplumber=True)

        assert isinstance(result, ParsedDocument)
        assert result.metadata["parser"] == "pdfplumber"
