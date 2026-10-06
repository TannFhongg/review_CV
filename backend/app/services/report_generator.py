"""Markdown report generator for CV-JD analysis results."""

from app.domain.enums import MatchStatus
from app.domain.models import AnalysisResult


class ReportGenerator:
    """Generates structured Markdown reports from analysis results."""

    @staticmethod
    def generate_markdown(result: AnalysisResult) -> str:
        """Create a Markdown report from AnalysisResult."""
        lines: list[str] = []

        # 1. Header
        lines.append("# 📄 BÁO CÁO PHÂN TÍCH & TỐI ƯU HÓA CV")
        lines.append(f"**Vị trí ứng tuyển:** {result.structured_jd.job_title}")
        if result.structured_jd.company:
            lines.append(f"**Công ty:** {result.structured_jd.company}")
        lines.append(f"**Ứng viên:** {result.structured_cv.name}")
        lines.append(f"**Thời gian phân tích:** {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 2. Executive Score Summary
        score = result.alignment_score
        lines.append("## 📊 1. ĐIỂM SỐ CV ↔ JD ALIGNMENT")
        lines.append(f"### Tổng điểm: **{score.overall}/100**")
        lines.append("")
        lines.append("| Tiêu chí đánh giá | Điểm số | Trọng số |")
        lines.append("|---|---|---|")
        lines.append(f"| Kỹ năng kỹ thuật (Technical Skills) | **{score.technical_skills}/100** | 30% |")
        lines.append(f"| Kinh nghiệm thực tế (Experience Relevance) | **{score.experience_relevance}/100** | 25% |")
        lines.append(f"| Trách nhiệm công việc (Responsibilities) | **{score.responsibilities_alignment}/100** | 20% |")
        lines.append(f"| Phủ từ khóa (Keyword Coverage) | **{score.keyword_coverage}/100** | 10% |")
        lines.append(f"| Học vấn & Bằng cấp (Education) | **{score.education_alignment}/100** | 10% |")
        lines.append(f"| Cấu trúc & Độ rõ ràng (CV Clarity) | **{score.cv_clarity}/100** | 5% |")
        lines.append("")

        # 3. Match Statistics
        lines.append("### Thống kê mức độ phù hợp")
        lines.append(f"- 🟢 **Phù hợp mạnh (Strong Match):** {result.strong_count}")
        lines.append(f"- 🟡 **Phù hợp một phần (Partial Match):** {result.partial_count}")
        lines.append(f"- 🟠 **Bằng chứng yếu (Weak Evidence):** {result.weak_count}")
        lines.append(f"- 🔴 **Còn thiếu (Missing Requirements):** {result.missing_count}")
        lines.append("")

        # 4. Top 5 Things To Fix
        lines.append("## 🎯 2. TOP CẦN CẢI THIỆN ĐẦU TIÊN")
        for i, rec in enumerate(result.top_recommendations, 1):
            badge = {
                "must_fix": "🔴 MUST FIX",
                "should_fix": "🟠 SHOULD FIX",
                "nice_to_have": "🟡 NICE TO HAVE",
                "already_strong": "🟢 ALREADY STRONG",
            }.get(rec.priority.value, "ℹ️")

            lines.append(f"### {i}. {rec.requirement} — {badge}")
            if rec.status == MatchStatus.MISSING:
                lines.append("*(Không tìm thấy trong CV)*")
            lines.append(f"**Gợi ý hành động:** {rec.recommendation}")
            if rec.evidence:
                lines.append("**Bằng chứng hiện có:**")
                for ev in rec.evidence:
                    lines.append(f"- *[{ev.source_section}]*: \"{ev.source_text}\" — {ev.explanation}")
            lines.append("")

        # 5. Before / After Rewrite Suggestions
        if result.suggestions:
            lines.append("## ✏️ 3. GỢI Ý VIẾT LẠI CHI TIẾT (BEFORE / AFTER)")
            for i, sug in enumerate(result.suggestions, 1):
                lines.append(f"### Gợi ý #{i} — Phần: {sug.section}")
                lines.append(f"**Yêu cầu JD liên quan:** {sug.jd_requirement}")
                lines.append("")
                lines.append("```text")
                lines.append("[TRƯỚC - ORIGINAL]")
                lines.append(sug.original_text)
                lines.append("")
                lines.append("[SAU - REVISED]")
                lines.append(sug.suggested_text)
                lines.append("```")
                lines.append(f"- **Thay đổi gì:** {sug.change_description}")
                lines.append(f"- **Lý do:** {sug.reason}")
                lines.append(f"- **Bằng chứng từ CV:** {sug.evidence}")
                lines.append("")

        # 6. Privacy & Policy footer
        lines.append("---")
        lines.append(
            "🔒 **Chính sách:** Dữ liệu CV được xử lý an toàn và không bị lưu trữ dài hạn trên hệ thống. "
            "Các gợi ý dựa trên nguyên tắc **Evidence First**, không bịa đặt kinh nghiệm."
        )

        return "\n".join(lines)
