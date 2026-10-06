"""PDF document parser using PyMuPDF (fitz)."""

import pymupdf as fitz
import structlog

from app.providers.document.base import DocumentParser
from app.utils.text_utils import clean_whitespace

logger = structlog.get_logger()


class PDFParser(DocumentParser):
    """Extracts text content from PDF files using PyMuPDF."""

    SUPPORTED_EXTENSIONS = {".pdf"}

    def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def extract_text(self, file_path: str) -> str:
        """Extract text from PDF document.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Extracted and normalized text.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is encrypted, corrupted, or contains no readable text.
        """
        path = self.validate_file_exists(file_path)

        try:
            doc = fitz.open(str(path))
        except Exception as e:
            logger.error("pdf_open_failed", path=str(path), error=str(e))
            raise ValueError(f"Không thể mở file PDF (file hỏng hoặc định dạng sai): {e}") from e

        try:
            if doc.is_encrypted:
                raise ValueError("File PDF được bảo vệ bằng mật khẩu. Vui lòng mở khóa trước khi tải lên.")

            if doc.page_count == 0:
                raise ValueError("File PDF không có trang nào.")

            extracted_pages: list[str] = []
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                page_text = page.get_text("text")
                if page_text and page_text.strip():
                    extracted_pages.append(page_text.strip())

            full_text = "\n\n".join(extracted_pages)
            cleaned_text = clean_whitespace(full_text)

            if not cleaned_text.strip():
                raise ValueError(
                    "Không thể trích xuất văn bản từ file PDF (có thể là file scan hoặc ảnh). "
                    "Vui lòng cung cấp file PDF có văn bản hoặc copy text trực tiếp."
                )

            logger.info(
                "pdf_extracted_successfully",
                path=str(path),
                pages=doc.page_count,
                char_count=len(cleaned_text),
            )
            return cleaned_text

        finally:
            doc.close()
