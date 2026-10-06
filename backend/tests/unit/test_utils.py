"""Tests for utility functions."""

import os
import pytest

from app.utils.file_utils import validate_file_extension, validate_file_size
from app.utils.text_utils import clean_whitespace, truncate_text
from app.utils.security import sanitize_filename, is_safe_path


# === File Utils ===

class TestValidateFileExtension:
    def test_valid_pdf(self):
        ext = validate_file_extension("resume.pdf")
        assert ext == ".pdf"

    def test_valid_docx(self):
        ext = validate_file_extension("resume.docx")
        assert ext == ".docx"

    def test_valid_txt(self):
        ext = validate_file_extension("resume.txt")
        assert ext == ".txt"

    def test_valid_doc(self):
        ext = validate_file_extension("resume.doc")
        assert ext == ".doc"

    def test_case_insensitive(self):
        ext = validate_file_extension("resume.PDF")
        assert ext == ".pdf"

    def test_invalid_extension(self):
        with pytest.raises(ValueError):
            validate_file_extension("resume.xlsx")

    def test_no_extension(self):
        with pytest.raises(ValueError):
            validate_file_extension("resume")


class TestValidateFileSize:
    def test_valid_size(self):
        # Should not raise
        validate_file_size(1024 * 1024)  # 1MB

    def test_exactly_max(self):
        # Should not raise at exactly max
        validate_file_size(10 * 1024 * 1024)  # 10MB

    def test_too_large(self):
        with pytest.raises(ValueError):
            validate_file_size(11 * 1024 * 1024)  # 11MB


class TestTempFileHandling:
    @pytest.mark.asyncio
    async def test_save_and_cleanup_temp_file(self):
        from app.utils.file_utils import save_temp_file, cleanup_temp_file
        content = b"sample pdf content bytes"
        temp_path = await save_temp_file(content, ".pdf")
        assert os.path.exists(temp_path)
        with open(temp_path, "rb") as f:
            assert f.read() == content

        cleanup_temp_file(temp_path)
        assert not os.path.exists(temp_path)


# === Text Utils ===

class TestCleanWhitespace:
    def test_multiple_newlines(self):
        text = "Hello\n\n\n\n\nWorld"
        result = clean_whitespace(text)
        assert "\n\n\n" not in result

    def test_multiple_spaces(self):
        text = "Hello    World"
        result = clean_whitespace(text)
        assert "    " not in result
        assert "Hello World" in result

    def test_strip_lines(self):
        text = "  Hello  \n  World  "
        result = clean_whitespace(text)
        assert result == "Hello\nWorld"


class TestTruncateText:
    def test_short_text(self):
        assert truncate_text("Hello", 10) == "Hello"

    def test_long_text(self):
        result = truncate_text("Hello World", 5)
        assert result.endswith("...")
        assert len(result) <= 8  # 5 + "..."

    def test_exact_length(self):
        assert truncate_text("Hello", 5) == "Hello"


# === Security Utils ===

class TestSanitizeFilename:
    def test_simple_filename(self):
        assert sanitize_filename("resume.pdf") == "resume.pdf"

    def test_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert ".." not in result

    def test_windows_path(self):
        result = sanitize_filename("C:\\Users\\hack\\resume.pdf")
        assert result == "resume.pdf"

    def test_special_characters(self):
        result = sanitize_filename("resume<script>.pdf")
        assert "<" not in result
        assert ">" not in result


class TestIsSafePath:
    def test_safe_path(self):
        base = os.path.dirname(__file__)
        path = os.path.join(base, "test_file.txt")
        assert is_safe_path(path, base) is True

    def test_unsafe_path(self):
        base = os.path.dirname(__file__)
        path = os.path.join(base, "..", "..", "etc", "passwd")
        # This will be outside base on most systems
        result = is_safe_path(path, base)
        assert result is False
