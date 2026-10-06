"""Abstract interfaces for providers and services."""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Allows swapping between different LLM providers (Gemini, OpenAI, etc.)
    without changing business logic.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt for context.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text.
        """
        ...

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured output matching a Pydantic model.

        Args:
            prompt: The user prompt.
            response_model: Pydantic model class for the response.
            system_prompt: Optional system prompt.
            temperature: Sampling temperature.

        Returns:
            Instance of response_model.
        """
        ...


class DocumentParser(ABC):
    """Abstract base class for document parsers.

    Allows adding new document format support without changing pipeline code.
    """

    @abstractmethod
    async def extract_text(self, file_path: str) -> str:
        """Extract text content from a document file.

        Args:
            file_path: Absolute path to the document file.

        Returns:
            Extracted text content.

        Raises:
            ValueError: If the file cannot be read or is empty.
            FileNotFoundError: If the file does not exist.
        """
        ...

    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """Check if this parser supports the given file extension.

        Args:
            file_extension: File extension including dot (e.g., ".pdf").

        Returns:
            True if supported.
        """
        ...
