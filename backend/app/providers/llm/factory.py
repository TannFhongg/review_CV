"""LLM provider factory for obtaining configured LLM instance."""

from app.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.gemini import GeminiProvider


class LLMProviderFactory:
    """Factory to instantiate configured LLM provider."""

    @staticmethod
    def get_provider() -> LLMProvider:
        """Instantiate and return LLM provider based on application settings."""
        provider_name = settings.llm_provider.lower().strip()

        if provider_name == "gemini":
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
            )
        elif provider_name == "openai":
            # Lazy import to avoid unnecessary dependency if not used
            try:
                from app.providers.llm.openai import OpenAIProvider
                return OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model,
                )
            except ImportError:
                raise ValueError("OpenAI provider requires openai package installed.")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")


def get_llm_provider() -> LLMProvider:
    """Convenience helper to get current LLM provider."""
    return LLMProviderFactory.get_provider()
