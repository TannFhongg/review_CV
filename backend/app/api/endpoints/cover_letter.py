"""Cover Letter API endpoint."""

import structlog
from fastapi import APIRouter, HTTPException

from app.api.schemas.request import CoverLetterGenerateRequest
from app.api.schemas.response import CoverLetterResponse, ErrorResponse
from app.providers.llm.factory import get_llm_provider
from app.services.cover_letter import CoverLetterService

logger = structlog.get_logger()
router = APIRouter()


@router.post(
    "/cover-letter/generate",
    response_model=CoverLetterResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Tạo Cover Letter theo JD và bằng chứng CV",
    description=(
        "Tạo thư ứng tuyển chuyên nghiệp, cá nhân hóa cao dựa trên các yêu cầu cụ thể "
        "của Job Description và bằng chứng thực tế từ CV (cam kết không bịa đặt)."
    ),
)
async def generate_cover_letter(payload: CoverLetterGenerateRequest) -> CoverLetterResponse:
    """Generate a highly tailored Cover Letter grounded in CV evidence."""
    try:
        llm = get_llm_provider()
        service = CoverLetterService(llm_provider=llm)

        result = await service.generate_cover_letter(
            jd=payload.structured_jd,
            cv=payload.structured_cv,
            tone=payload.tone,
            language=payload.language,
            custom_instructions=payload.custom_instructions,
        )
        return result
    except Exception as e:
        logger.error("generate_cover_letter_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "code": "COVER_LETTER_GENERATION_FAILED",
                "message": f"Không thể tạo Cover Letter: {str(e)}",
            },
        )
