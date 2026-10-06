"""Base abstract class for document parsers."""

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentParser(ABC):
    """Abstract base class for document extraction providers."""

    @abstractmethod
    async def extract_text(self, file_path: str) -> str:
        """Extract plain text from document file.

        Args:
            file_path: Absolute or relative path to the document.

        Returns:
            Extracted text content cleaned of formatting artifacts.

        Raises:
            ValueError: If file is empty or corrupted.
            FileNotFoundError: If file does not exist.
        """
        pass

    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """Check if parser supports the given extension.

        Args:
            file_extension: Extension including dot (e.g. '.pdf').

        Returns:
            True if supported, False otherwise.
        """
        pass

    def validate_file_exists(self, file_path: str) -> Path:
        """Check if file exists and is not empty.

        Args:
            file_path: Path to document.

        Returns:
            Path object.

        Raises:
            FileNotFoundError: If file not found.
            ValueError: If file is 0 bytes.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        if path.stat().st_size == 0:
            raise ValueError(f"File is empty (0 bytes): {file_path}")
        return path
