"""Google Gemini LLM provider implementation using google-genai SDK with automatic model failover."""

import json
from typing import TypeVar

import structlog
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

# Default model fallback list in case primary model is deprecated or overloaded
FALLBACK_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider with automated failover and structured output support."""

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite") -> None:
        if not api_key:
            logger.warning("gemini_api_key_missing")
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key) if api_key else None

    def _get_models_to_try(self) -> list[str]:
        """Return list of candidate models with user configured model first."""
        models: list[str] = [self.model]
        for fallback in FALLBACK_CANDIDATES:
            if fallback not in models:
                models.append(fallback)
        return models

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Generate unstructured text from Gemini with automatic failover."""
        if not self.client:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env.")

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt if system_prompt else None,
        )

        last_error: Exception | None = None
        models_to_try = self._get_models_to_try()

        for model_name in models_to_try:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                return response.text or ""
            except Exception as e:
                last_error = e
                err_msg = str(e)
                logger.warning(
                    "gemini_generate_attempt_failed",
                    model=model_name,
                    error=err_msg,
                )
                # Retry with next model on 404 (not found / deprecated) or 503 (high demand)
                if any(err in err_msg for err in ["404", "503", "NOT_FOUND", "UNAVAILABLE"]):
                    continue
                # For auth errors (401/403) or bad requests, do not retry
                break

        logger.error("gemini_generate_all_models_failed", error=str(last_error))
        raise RuntimeError(f"Lỗi khi gọi mô hình Gemini: {last_error}") from last_error

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured output validated against a Pydantic model with automatic failover."""
        if not self.client:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env.")

        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_model,
            system_instruction=system_prompt if system_prompt else None,
        )

        last_error: Exception | None = None
        models_to_try = self._get_models_to_try()

        for model_name in models_to_try:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )

                raw_text = response.text or "{}"
                # Attempt direct Pydantic JSON parsing
                try:
                    return response_model.model_validate_json(raw_text)
                except Exception:
                    # Cleanup potential code fences if returned
                    cleaned = raw_text.strip()
                    if cleaned.startswith("```"):
                        lines = cleaned.split("\n")
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        cleaned = "\n".join(lines).strip()
                    data = json.loads(cleaned)
                    return response_model.model_validate(data)

            except Exception as e:
                last_error = e
                err_msg = str(e)
                logger.warning(
                    "gemini_structured_generate_attempt_failed",
                    model=model_name,
                    error=err_msg,
                )
                # Retry with next model on 404 (deprecated) or 503 (overloaded)
                if any(err in err_msg for err in ["404", "503", "NOT_FOUND", "UNAVAILABLE"]):
                    continue
                # For auth errors (401/403) or bad requests, do not retry
                break

        logger.error("gemini_structured_all_models_failed", error=str(last_error))
        raise RuntimeError(
            f"Lỗi khi trích xuất dữ liệu có cấu trúc từ Gemini: {last_error}"
        ) from last_error
