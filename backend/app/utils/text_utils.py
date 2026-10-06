"""Text processing utilities."""


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length with ellipsis.

    Args:
        text: Text to truncate.
        max_length: Maximum length.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def clean_whitespace(text: str) -> str:
    """Clean excessive whitespace from extracted text.

    - Replace multiple newlines with double newline.
    - Replace multiple spaces with single space.
    - Strip leading/trailing whitespace.

    Args:
        text: Raw text.

    Returns:
        Cleaned text.
    """
    import re

    # Replace multiple newlines with double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Replace multiple spaces/tabs with single space
    text = re.sub(r"[^\S\n]+", " ", text)
    # Strip each line
    lines = [line.strip() for line in text.split("\n")]
    # Remove empty lines at start/end
    text = "\n".join(lines).strip()
    return text
