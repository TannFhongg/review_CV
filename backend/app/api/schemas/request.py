"""Request validation schemas."""

from fastapi import UploadFile, HTTPException

from app.config import settings

# Maximum text input length (50,000 characters)
MAX_TEXT_LENGTH = 50_000


def validate_analysis_input(
    jd_file: UploadFile | None,
    cv_file: UploadFile | None,
    jd_text: str | None,
    cv_text: str | None,
) -> None:
    """Validate analysis input — at least one source for JD and CV required.

    Raises:
        HTTPException: If validation fails.
    """
    # Check JD input
    has_jd = (jd_file is not None and jd_file.filename) or (jd_text and jd_text.strip())
    if not has_jd:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "MISSING_JD",
                "message": "Vui lòng cung cấp Job Description (file hoặc text).",
            },
        )

    # Check CV input
    has_cv = (cv_file is not None and cv_file.filename) or (cv_text and cv_text.strip())
    if not has_cv:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "MISSING_CV",
                "message": "Vui lòng cung cấp CV (file hoặc text).",
            },
        )

    # Validate file types
    allowed = settings.allowed_extensions_list
    for label, file in [("JD", jd_file), ("CV", cv_file)]:
        if file is not None and file.filename:
            ext = _get_extension(file.filename)
            if ext not in allowed:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_FILE_FORMAT",
                        "message": f"Định dạng file {label} không được hỗ trợ. Vui lòng sử dụng: {', '.join(allowed)}",
                        "details": {
                            "file_name": file.filename,
                            "detected_format": ext,
                            "supported_formats": allowed,
                        },
                    },
                )

    # Validate file sizes
    for label, file in [("JD", jd_file), ("CV", cv_file)]:
        if file is not None and file.size is not None:
            if file.size > settings.max_file_size_bytes:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "FILE_TOO_LARGE",
                        "message": (
                            f"File {label} vượt quá {settings.max_file_size_mb}MB. "
                            f"Vui lòng chọn file nhỏ hơn."
                        ),
                        "details": {
                            "file_size_bytes": file.size,
                            "max_size_bytes": settings.max_file_size_bytes,
                        },
                    },
                )

    # Validate text length
    for label, text in [("JD", jd_text), ("CV", cv_text)]:
        if text and len(text) > MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "TEXT_TOO_LONG",
                    "message": (
                        f"Text {label} vượt quá {MAX_TEXT_LENGTH:,} ký tự. "
                        f"Vui lòng rút ngắn nội dung."
                    ),
                    "details": {
                        "text_length": len(text),
                        "max_length": MAX_TEXT_LENGTH,
                    },
                },
            )


def _get_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


from pydantic import BaseModel
from app.api.schemas.response import StructuredCVResponse, StructuredJDResponse


class CoverLetterGenerateRequest(BaseModel):
    """Payload for generating a cover letter."""
    structured_jd: StructuredJDResponse
    structured_cv: StructuredCVResponse
    tone: str = "professional"  # professional | enthusiastic | concise
    language: str = "vi"  # vi | en
    custom_instructions: str | None = None

