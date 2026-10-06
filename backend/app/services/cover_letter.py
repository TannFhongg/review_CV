"""Cover Letter generator service grounded strictly in candidate CV evidence and target JD."""

from datetime import datetime
import structlog
from pydantic import BaseModel

from app.api.schemas.response import (
    CoverLetterResponse,
    StructuredCVResponse,
    StructuredJDResponse,
)
from app.domain.models import StructuredCV, StructuredJD
from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()

COVER_LETTER_SYSTEM_PROMPT = """You are an elite Executive Career Coach and Technical Cover Letter Specialist.
Your mission is to craft a highly compelling, authentic, and professionally formatted Cover Letter tailored specifically for the candidate applying to the provided Job Description.

CRITICAL RULES — STRICTLY NO FABRICATION:
1. The letter MUST be strictly anchored in the candidate's actual projects, technical skills, education, and experience from their CV.
2. NEVER invent past companies, degrees, unverified metrics, or tools that have no basis in the CV.
3. Explicitly link the candidate's actual project accomplishments to the key requirements and challenges outlined in the JD.
4. Tone Guidelines:
   - "professional": Polished, articulate, confident, and formal corporate tone.
   - "enthusiastic": High energy, passion for the company's domain, forward-looking and proactive.
   - "concise": Direct to the point, impactful, bulleted project highlights, executive brief format.
5. Language:
   - If language is "vi", output entirely in natural, professional Vietnamese.
   - If language is "en", output entirely in idiomatic, professional English.
"""


class _CoverLetterLLMOutput(BaseModel):
    subject: str
    salutation: str
    opening: str
    body_paragraphs: list[str]
    closing: str
    sign_off: str
    key_strengths_highlighted: list[str] = []


class CoverLetterService:
    """Generates customized Cover Letters based on JD requirements and CV evidence."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm = llm_provider

    async def generate_cover_letter(
        self,
        jd: StructuredJD | StructuredJDResponse,
        cv: StructuredCV | StructuredCVResponse,
        tone: str = "professional",
        language: str = "vi",
        custom_instructions: str | None = None,
    ) -> CoverLetterResponse:
        """Generate a tailored cover letter using LLM with deterministic fallback."""
        tone_normalized = tone.lower().strip() if tone else "professional"
        lang_normalized = language.lower().strip() if language else "vi"

        # Build context
        candidate_name = cv.name or "Ứng viên"
        company_name = jd.company or "Quý công ty"
        target_role = jd.job_title

        # Collect candidate projects & skills
        projects_summary = []
        for p in cv.projects[:4]:
            tech_str = ", ".join(p.technologies) if p.technologies else ""
            desc = p.description or (" | ".join(p.highlights) if hasattr(p, "highlights") and p.highlights else "")
            projects_summary.append(f"- Dự án {p.name}: {desc} (Công nghệ: {tech_str})")

        skills_str = ", ".join(cv.technical_skills[:12]) if cv.technical_skills else "N/A"
        reqs_str = ", ".join([r.name for r in jd.required_skills[:8]]) if jd.required_skills else "Theo mô tả công việc"

        prompt = f"""Target Position: {target_role}
Company: {company_name}
Target Language: {'Tiếng Việt' if lang_normalized == 'vi' else 'English'}
Requested Tone: {tone_normalized}

KEY JD REQUIREMENTS:
{reqs_str}

CANDIDATE PROFILE (ACTUAL CV EVIDENCE ONLY):
Candidate Name: {candidate_name}
Education: {', '.join(f'{e.degree} tại {e.institution}' for e in cv.education[:2]) if cv.education else 'N/A'}
Core Technical Skills: {skills_str}
Key Projects:
{chr(10).join(projects_summary) if projects_summary else 'N/A'}
Experience: {', '.join(f'{w.title} tại {w.company}' for w in cv.experience[:2]) if cv.experience else 'N/A'}

ADDITIONAL USER INSTRUCTIONS:
{custom_instructions if custom_instructions else 'None'}

TASK:
Generate a structured Cover Letter strictly based on the above candidate facts.
Ensure the body paragraphs demonstrate how the candidate's concrete project experience directly answers the job's requirements.
"""

        try:
            logger.info("generating_cover_letter_started", candidate=candidate_name, role=target_role, tone=tone_normalized)
            llm_result: _CoverLetterLLMOutput = await self.llm.generate_structured(
                prompt=prompt,
                response_model=_CoverLetterLLMOutput,
                system_prompt=COVER_LETTER_SYSTEM_PROMPT,
                temperature=0.3,
            )

            full_letter = self._assemble_full_letter(
                candidate_name=candidate_name,
                contact=cv.contact,
                company_name=company_name,
                subject=llm_result.subject,
                salutation=llm_result.salutation,
                opening=llm_result.opening,
                body_paragraphs=llm_result.body_paragraphs,
                closing=llm_result.closing,
                sign_off=llm_result.sign_off,
            )

            return CoverLetterResponse(
                subject=llm_result.subject,
                salutation=llm_result.salutation,
                opening=llm_result.opening,
                body_paragraphs=llm_result.body_paragraphs,
                closing=llm_result.closing,
                sign_off=llm_result.sign_off,
                full_letter=full_letter,
                tone=tone_normalized,
                language=lang_normalized,
                word_count=len(full_letter.split()),
                key_strengths_highlighted=llm_result.key_strengths_highlighted or cv.technical_skills[:5],
            )
        except Exception as e:
            logger.warning("cover_letter_llm_failed_falling_back_to_template", error=str(e))
            return self._generate_fallback_cover_letter(
                jd=jd,
                cv=cv,
                tone=tone_normalized,
                language=lang_normalized,
            )

    def _assemble_full_letter(
        self,
        candidate_name: str,
        contact: any,
        company_name: str,
        subject: str,
        salutation: str,
        opening: str,
        body_paragraphs: list[str],
        closing: str,
        sign_off: str,
    ) -> str:
        """Combine parts into a standard Markdown formatted Cover Letter."""
        lines: list[str] = []

        # Candidate Header
        lines.append(f"**{candidate_name}**")
        contact_parts = []
        if getattr(contact, "email", None):
            contact_parts.append(f"Email: {contact.email}")
        if getattr(contact, "phone", None):
            contact_parts.append(f"SĐT: {contact.phone}")
        if getattr(contact, "location", None):
            contact_parts.append(f"Địa chỉ: {contact.location}")
        if contact_parts:
            lines.append(" | ".join(contact_parts))

        lines.append(f"Ngày: {datetime.now().strftime('%d/%m/%Y')}")
        lines.append("")
        lines.append(f"**Kính gửi:** Ban Tuyển dụng {company_name}")
        lines.append(f"**Tiêu đề:** {subject}")
        lines.append("")
        lines.append(salutation)
        lines.append("")
        lines.append(opening)
        lines.append("")

        for p in body_paragraphs:
            lines.append(p)
            lines.append("")

        lines.append(closing)
        lines.append("")
        lines.append(sign_off)
        if candidate_name not in sign_off:
            lines.append(f"**{candidate_name}**")

        return "\n".join(lines).strip()

    def _generate_fallback_cover_letter(
        self,
        jd: StructuredJD | StructuredJDResponse,
        cv: StructuredCV | StructuredCVResponse,
        tone: str,
        language: str,
    ) -> CoverLetterResponse:
        """Deterministic template-based fallback Cover Letter ensuring zero-fabrication."""
        candidate_name = cv.name or "Ứng viên"
        company_name = jd.company or "Quý công ty"
        target_role = jd.job_title

        top_skills = ", ".join(cv.technical_skills[:6]) if cv.technical_skills else "các kỹ năng chuyên môn cốt lõi"
        top_projects = cv.projects[:2]

        if language == "en":
            subject = f"Application for {target_role} — {candidate_name}"
            salutation = f"Dear Hiring Team at {company_name},"
            opening = (
                f"I am writing to express my strong interest in the {target_role} position at {company_name}. "
                f"With a solid technical foundation in {top_skills} and hands-on project experience, "
                f"I am eager to contribute effectively to your engineering goals."
            )
            body1 = (
                f"Throughout my academic and practical endeavors, I have cultivated hands-on expertise aligned directly with your requirements. "
                + (
                    f"Specifically, in my project '{top_projects[0].name}', I implemented solutions utilizing {', '.join(top_projects[0].technologies)}, "
                    f"focusing on performance and system reliability."
                    if top_projects
                    else f"My background demonstrates a proven dedication to delivering high-quality software."
                )
            )
            body2 = (
                f"I am particularly impressed by {company_name}'s technical standards and industry impact. "
                f"My disciplined problem-solving approach and continuous learning mindset will enable me to ramp up quickly "
                f"and add tangible value to your team from day one."
            )
            closing = (
                f"Thank you for your time and consideration. I would welcome the opportunity to discuss further "
                f"how my background and drive match the needs of {company_name}."
            )
            sign_off = f"Sincerely,\n**{candidate_name}**"
        else:
            subject = f"Đơn ứng tuyển vị trí {target_role} — {candidate_name}"
            salutation = f"Kính gửi Ban Tuyển dụng {company_name},"
            opening = (
                f"Tôi viết thư này để bày tỏ nguyện vọng được ứng tuyển vào vị trí {target_role} tại {company_name}. "
                f"Với nền tảng kỹ thuật vững chắc về {top_skills} cùng tinh thần trách nhiệm cao, tôi tin rằng "
                f"mình có thể đóng góp hiệu quả vào các mục tiêu phát triển của quý công ty."
            )
            body1 = (
                f"Trong quá trình học tập và thực hiện các dự án thực tế, tôi luôn chú trọng áp dụng đúng các tiêu chuẩn kỹ thuật. "
                + (
                    f"Tiêu biểu là trong dự án '{top_projects[0].name}', tôi đã vận dụng {', '.join(top_projects[0].technologies)} "
                    f"để hoàn thành tốt các yêu cầu đề ra với tính kỷ luật và độ chính xác cao."
                    if top_projects
                    else f"Tôi luôn chủ động giải quyết các bài toán kỹ thuật phức tạp với tinh thần học hỏi không ngừng."
                )
            )
            body2 = (
                f"Tìm hiểu về {company_name}, tôi rất ấn tượng với môi trường chuyên nghiệp và các sản phẩm mà công ty đang phát triển. "
                f"Tôi tin rằng khả năng thích ứng nhanh, tư duy kỹ thuật rõ ràng và sự cầu tiến sẽ giúp tôi hòa nhập tốt "
                f"và tạo ra giá trị thiết thực cho đội ngũ."
            )
            closing = (
                f"Tôi xin chân thành cảm ơn Quý công ty đã dành thời gian xem xét hồ sơ. Tôi rất mong có cơ hội được trao đổi chi tiết hơn "
                f"trong buổi phỏng vấn sắp tới."
            )
            sign_off = f"Trân trọng,\n**{candidate_name}**"

        body_paragraphs = [body1, body2]
        full_letter = self._assemble_full_letter(
            candidate_name=candidate_name,
            contact=cv.contact,
            company_name=company_name,
            subject=subject,
            salutation=salutation,
            opening=opening,
            body_paragraphs=body_paragraphs,
            closing=closing,
            sign_off=sign_off,
        )

        return CoverLetterResponse(
            subject=subject,
            salutation=salutation,
            opening=opening,
            body_paragraphs=body_paragraphs,
            closing=closing,
            sign_off=sign_off,
            full_letter=full_letter,
            tone=tone,
            language=language,
            word_count=len(full_letter.split()),
            key_strengths_highlighted=cv.technical_skills[:5],
        )
