"""Scoring service for transparent CV ↔ JD Alignment calculation."""

import re
import structlog

from app.domain.enums import Importance, MatchStatus
from app.domain.models import AlignmentScore, RequirementMatch, StructuredCV, StructuredJD
from app.services.matching import SKILL_ALIASES

logger = structlog.get_logger()


class ScoringService:
    """Calculates multidimensional transparent alignment scores without artificial inflation."""

    @staticmethod
    def calculate_technical_skills_score(matches: list[RequirementMatch]) -> int:
        """Calculate Technical Skills score (30% weight).

        Required skills have 3x weight, preferred skills have 1x weight.
        - Strong Match: 1.0
        - Partial Match: 0.6
        - Weak Evidence: 0.3
        - Missing: 0.0
        """
        if not matches:
            return 50

        total_weight = 0.0
        weighted_score = 0.0

        status_weights = {
            MatchStatus.STRONG: 1.0,
            MatchStatus.PARTIAL: 0.6,
            MatchStatus.WEAK: 0.3,
            MatchStatus.MISSING: 0.0,
            MatchStatus.UNKNOWN: 0.0,
        }

        for m in matches:
            weight = 3.0 if m.requirement_importance == Importance.REQUIRED else 1.0
            score_factor = status_weights.get(m.status, 0.0)

            weighted_score += score_factor * weight
            total_weight += weight

        if total_weight == 0:
            return 50

        return max(0, min(100, round((weighted_score / total_weight) * 100)))

    @staticmethod
    def calculate_keyword_coverage(jd: StructuredJD, cv: StructuredCV) -> int:
        """Calculate Keyword Coverage score (10% weight).

        Checks presence of JD keywords and skill aliases within CV raw text.
        """
        keywords_to_check = set()
        for k in jd.keywords:
            if len(k.strip()) > 1:
                keywords_to_check.add(k.lower().strip())
        for req in jd.required_skills:
            keywords_to_check.add(req.name.lower().strip())
        for pref in jd.preferred_skills:
            keywords_to_check.add(pref.name.lower().strip())

        if not keywords_to_check:
            return 75

        cv_text = cv.raw_text.lower()
        matched = 0

        def _matches_term(term: str, text: str) -> bool:
            # Handle keywords containing symbols (C++, C#, etc.)
            escaped = re.escape(term)
            pattern = rf"(?:^|[\s,.;:/\(\)\[\]]){escaped}(?:$|[\s,.;:/\(\)\[\]])"
            return bool(re.search(pattern, text))

        for kw in keywords_to_check:
            # Check exact keyword
            if _matches_term(kw, cv_text):
                matched += 1
                continue

            # Check known aliases
            aliases = SKILL_ALIASES.get(kw, [])
            if any(_matches_term(a, cv_text) for a in aliases):
                matched += 1

        score = round((matched / len(keywords_to_check)) * 100)
        return max(0, min(100, score))

    @staticmethod
    def calculate_responsibilities_alignment(matches: list[RequirementMatch]) -> int:
        """Calculate Responsibilities Alignment score (20% weight)."""
        resp_matches = [m for m in matches if m.requirement.lower().startswith("responsibility:")]
        if not resp_matches:
            # If no explicit responsibility items, use general match ratio
            strong_and_partial = sum(
                1 for m in matches if m.status in {MatchStatus.STRONG, MatchStatus.PARTIAL}
            )
            return round((strong_and_partial / max(1, len(matches))) * 100)

        total = len(resp_matches)
        score_sum = sum(
            1.0 if m.status == MatchStatus.STRONG
            else 0.6 if m.status == MatchStatus.PARTIAL
            else 0.3 if m.status == MatchStatus.WEAK
            else 0.0
            for m in resp_matches
        )
        return max(0, min(100, round((score_sum / total) * 100)))

    @staticmethod
    def calculate_experience_relevance(cv: StructuredCV, matches: list[RequirementMatch]) -> int:
        """Calculate Experience Relevance score (25% weight).

        Evaluates project & work history depth against JD matches.
        """
        has_projects = len(cv.projects) > 0
        has_work_exp = len(cv.experience) > 0

        # Project and work experience evidence count
        evidence_count = 0
        for m in matches:
            for ev in m.evidence:
                if ev.source_section.lower() in {"projects", "experience", "work_experience"}:
                    evidence_count += 1

        base = 50
        if has_projects:
            base += 15
        if has_work_exp:
            base += 15

        evidence_bonus = min(20, evidence_count * 5)
        return min(100, max(20, base + evidence_bonus))

    @staticmethod
    def calculate_education_alignment(jd: StructuredJD, cv: StructuredCV) -> int:
        """Calculate Education Alignment score (10% weight)."""
        if not jd.education_requirements:
            return 90  # Not heavily restricted

        if not cv.education:
            return 40

        # Typical degrees in tech
        tech_fields = {"computer", "software", "electronic", "electrical", "telecom", "it", "công nghệ"}
        matched_field = False
        for edu in cv.education:
            combined = f"{edu.degree} {edu.field or ''}".lower()
            if any(tf in combined for tf in tech_fields):
                matched_field = True
                break

        return 95 if matched_field else 70

    @staticmethod
    def calculate_cv_clarity(cv: StructuredCV) -> int:
        """Calculate CV Clarity score (5% weight)."""
        score = 70
        if cv.summary or cv.title:
            score += 10
        if cv.contact.email and cv.contact.phone:
            score += 10
        if cv.projects or cv.experience:
            score += 10
        return min(100, score)

    def calculate_alignment(
        self,
        jd: StructuredJD,
        cv: StructuredCV,
        matches: list[RequirementMatch],
    ) -> AlignmentScore:
        """Calculate full alignment breakdown and overall score."""
        tech_score = self.calculate_technical_skills_score(matches)
        exp_score = self.calculate_experience_relevance(cv, matches)
        resp_score = self.calculate_responsibilities_alignment(matches)
        kw_score = self.calculate_keyword_coverage(jd, cv)
        edu_score = self.calculate_education_alignment(jd, cv)
        clarity_score = self.calculate_cv_clarity(cv)

        # Weighted calculation:
        # Technical (30%) + Experience (25%) + Responsibilities (20%) +
        # Keywords (10%) + Education (10%) + Clarity (5%)
        overall = round(
            (tech_score * 0.30)
            + (exp_score * 0.25)
            + (resp_score * 0.20)
            + (kw_score * 0.10)
            + (edu_score * 0.10)
            + (clarity_score * 0.05)
        )
        overall = max(0, min(100, overall))

        methodology = (
            "Phương pháp tính điểm CV ↔ JD Alignment:\n"
            "- Kỹ năng kỹ thuật (30%): Tỷ lệ đáp ứng các yêu cầu bắt buộc (x3) và ưu tiên (x1).\n"
            "- Kinh nghiệm thực tế (25%): Mức độ liên quan của dự án và công việc trong quá khứ.\n"
            "- Trách nhiệm công việc (20%): Khả năng đáp ứng các đầu việc cốt lõi của JD.\n"
            "- Phủ từ khóa (10%): Tỷ lệ xuất hiện từ khóa và thuật ngữ liên quan trong CV.\n"
            "- Trình độ học vấn (10%): Phù hợp chuyên ngành và cấp bậc bằng cấp.\n"
            "- Độ rõ ràng & cấu trúc (5%): Bố cục thông tin, mục tiêu nghề nghiệp và liên hệ."
        )

        logger.info(
            "score_calculated",
            overall=overall,
            technical=tech_score,
            experience=exp_score,
            keywords=kw_score,
        )

        return AlignmentScore(
            overall=overall,
            technical_skills=tech_score,
            experience_relevance=exp_score,
            responsibilities_alignment=resp_score,
            keyword_coverage=kw_score,
            education_alignment=edu_score,
            cv_clarity=clarity_score,
            methodology_notes=methodology,
        )
