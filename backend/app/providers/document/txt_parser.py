"""Plain text document parser with automatic encoding detection."""

import chardet
import structlog

from app.providers.document.base import DocumentParser
from app.utils.text_utils import clean_whitespace

logger = structlog.get_logger()


class TXTParser(DocumentParser):
    """Extracts text from plain text files (.txt, .md, .text)."""

    SUPPORTED_EXTENSIONS = {".txt", ".text", ".md"}

    def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def extract_text(self, file_path: str) -> str:
        """Extract text from plain text file using detected encoding.

        Args:
            file_path: Path to the text file.

        Returns:
            Decoded and normalized string.

        Raises:
            FileNotFoundError: If file not found.
            ValueError: If file is empty or cannot be decoded.
        """
        path = self.validate_file_exists(file_path)

        try:
            with open(path, "rb") as f:
                raw_bytes = f.read()

            if not raw_bytes:
                raise ValueError("File văn bản trống.")

            # Detect encoding
            detected = chardet.detect(raw_bytes)
            encoding = detected.get("encoding") or "utf-8"

            # Try detected encoding first, fallback to utf-8 with replacement
            try:
                decoded_text = raw_bytes.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                logger.warning(
                    "txt_decode_failed_fallback_utf8",
                    detected_encoding=encoding,
                    path=str(path),
                )
                decoded_text = raw_bytes.decode("utf-8", errors="replace")

            cleaned_text = clean_whitespace(decoded_text)
            if not cleaned_text.strip():
                raise ValueError("File văn bản không chứa nội dung hợp lệ.")

            logger.info(
                "txt_extracted_successfully",
                path=str(path),
                encoding=encoding,
                char_count=len(cleaned_text),
            )
            return cleaned_text

        except ValueError:
            raise
        except Exception as e:
            logger.error("txt_read_failed", path=str(path), error=str(e))
            raise ValueError(f"Không thể đọc file văn bản: {e}") from e
