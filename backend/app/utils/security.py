"""Security utilities."""

import re


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal attacks.

    Args:
        filename: Original filename.

    Returns:
        Sanitized filename (basename only, no path components).
    """
    # Remove path separators
    filename = filename.replace("\\", "/")
    # Take only the basename
    filename = filename.split("/")[-1]
    # Remove potentially dangerous characters
    filename = re.sub(r"[^\w\s\-.]", "", filename)
    # Collapse multiple dots
    filename = re.sub(r"\.{2,}", ".", filename)
    return filename.strip()


def is_safe_path(path: str, base_dir: str) -> bool:
    """Check if a path is within the base directory (prevent path traversal).

    Args:
        path: Path to check.
        base_dir: Expected base directory.

    Returns:
        True if path is within base_dir.
    """
    import os

    real_path = os.path.realpath(path)
    real_base = os.path.realpath(base_dir)
    return real_path.startswith(real_base)
