"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # === Application ===
    app_env: str = Field(default="development", description="Environment: development, production")
    app_debug: bool = Field(default=True, description="Enable debug mode")
    app_host: str = Field(default="0.0.0.0", description="Server host")
    app_port: int = Field(default=8000, description="Server port")
    app_version: str = Field(default="1.0.0", description="Application version")

    # === LLM Provider ===
    llm_provider: str = Field(default="gemini", description="LLM provider: gemini, openai")
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")

    # === File Upload ===
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_extensions: str = Field(
        default=".pdf,.docx,.doc,.txt",
        description="Comma-separated allowed file extensions",
    )

    # === CORS ===
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated CORS origins",
    )

    # === Logging ===
    log_level: str = Field(default="INFO", description="Log level")

    @property
    def max_file_size_bytes(self) -> int:
        """Maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_extensions_list(self) -> list[str]:
        """List of allowed file extensions."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def cors_origins_list(self) -> list[str]:
        """List of CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance
settings = Settings()
