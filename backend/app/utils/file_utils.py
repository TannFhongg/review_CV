"""File handling utilities with security validation and temp file management."""

import os
import tempfile
import uuid
from pathlib import Path

import structlog

from app.config import settings

logger = structlog.get_logger()

# Temp directory prefix for isolation
TEMP_PREFIX = "copilot_"


def validate_file_extension(filename: str) -> str:
    """Validate file extension and return it.

    Args:
        filename: Original filename.

    Returns:
        Lowercase file extension including dot.

    Raises:
        ValueError: If extension is not allowed.
    """
    if "." not in filename:
        raise ValueError(f"File has no extension: {filename}")

    ext = "." + filename.rsplit(".", 1)[-1].lower()
    allowed = settings.allowed_extensions_list

    if ext not in allowed:
        raise ValueError(
            f"File extension '{ext}' not allowed. Supported: {', '.join(allowed)}"
        )

    return ext


def validate_file_size(size_bytes: int) -> None:
    """Validate file size.

    Args:
        size_bytes: File size in bytes.

    Raises:
        ValueError: If file exceeds maximum size.
    """
    if size_bytes > settings.max_file_size_bytes:
        raise ValueError(
            f"File size ({size_bytes:,} bytes) exceeds maximum "
            f"({settings.max_file_size_bytes:,} bytes / {settings.max_file_size_mb}MB)"
        )


async def save_temp_file(content: bytes, extension: str) -> str:
    """Save content to a temporary file.

    The file is created in a dedicated temp directory and should be
    cleaned up after use via `cleanup_temp_file()`.

    Args:
        content: File content bytes.
        extension: File extension (e.g., ".pdf").

    Returns:
        Absolute path to the temporary file.
    """
    temp_dir = tempfile.mkdtemp(prefix=TEMP_PREFIX)
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(temp_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    logger.debug(
        "temp_file_saved",
        file_path=file_path,
        size_bytes=len(content),
    )

    return file_path


def cleanup_temp_file(file_path: str) -> None:
    """Remove a temporary file and its parent directory.

    Silently ignores errors (file may already be deleted).

    Args:
        file_path: Path to the temporary file.
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()

        # Also remove parent temp directory if empty
        parent = path.parent
        if parent.exists() and parent.name.startswith(TEMP_PREFIX):
            try:
                parent.rmdir()
            except OSError:
                pass  # Directory not empty, skip

        logger.debug("temp_file_cleaned", file_path=file_path)
    except Exception:
        logger.warning("temp_file_cleanup_failed", file_path=file_path)
