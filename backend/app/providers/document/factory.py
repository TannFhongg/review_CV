"""Document parser factory for selecting appropriate parser by extension."""

from pathlib import Path

from app.providers.document.base import DocumentParser
from app.providers.document.pdf_parser import PDFParser
from app.providers.document.docx_parser import DOCXParser
from app.providers.document.txt_parser import TXTParser


class DocumentParserFactory:
    """Factory to instantiate and select appropriate document parsers."""

    def __init__(self) -> None:
        self._parsers: list[DocumentParser] = [
            PDFParser(),
            DOCXParser(),
            TXTParser(),
        ]

    def register_parser(self, parser: DocumentParser) -> None:
        """Register a new parser implementation."""
        self._parsers.append(parser)

    def get_parser(self, file_path_or_ext: str) -> DocumentParser:
        """Get the appropriate parser for a given file path or extension.

        Args:
            file_path_or_ext: File path or extension (e.g., 'resume.pdf' or '.pdf').

        Returns:
            Matching DocumentParser instance.

        Raises:
            ValueError: If no parser supports the given extension.
        """
        ext = file_path_or_ext.lower()
        if "." in ext and not ext.startswith("."):
            ext = "." + Path(file_path_or_ext).suffix.lstrip(".").lower()
        elif not ext.startswith("."):
            ext = f".{ext}"

        for parser in self._parsers:
            if parser.supports(ext):
                return parser

        raise ValueError(
            f"Định dạng tệp '{ext}' chưa được hỗ trợ. "
            f"Các định dạng hỗ trợ hiện tại: .pdf, .docx, .txt"
        )


# Global default factory
parser_factory = DocumentParserFactory()
