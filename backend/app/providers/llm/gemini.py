"""Google Gemini LLM provider implementation using google-genai SDK."""

import json
from typing import TypeVar

import structlog
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        if not api_key:
            logger.warning("gemini_api_key_missing")
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key) if api_key else None

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Generate unstructured text from Gemini."""
        if not self.client:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env.")

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt if system_prompt else None,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            logger.error("gemini_generate_error", model=self.model, error=str(e))
            raise RuntimeError(f"Lỗi khi gọi mô hình Gemini: {e}") from e

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured output validated against a Pydantic model."""
        if not self.client:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env.")

        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_model,
            system_instruction=system_prompt if system_prompt else None,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
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
            logger.error("gemini_structured_generate_error", model=self.model, error=str(e))
            raise RuntimeError(f"Lỗi khi trích xuất dữ liệu có cấu trúc từ Gemini: {e}") from e
