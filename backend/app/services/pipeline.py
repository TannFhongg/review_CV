"""Main Analysis Pipeline orchestrating the full end-to-end CV-JD copilot flow."""

import time
from datetime import datetime

import structlog

from app.domain.models import AnalysisResult, StructuredCV, StructuredJD
from app.providers.document.factory import parser_factory
from app.providers.llm.base import LLMProvider
from app.providers.llm.factory import get_llm_provider
from app.services.cv_parser import CVParserService
from app.services.cv_rewriter import CVRewriterService
from app.services.gap_analyzer import GapAnalyzer
from app.services.jd_parser import JDParserService
from app.services.matching import MatchingEngine
from app.services.priority_analyzer import PriorityAnalyzer
from app.services.scoring import ScoringService

logger = structlog.get_logger()


class AnalysisPipeline:
    """Orchestrates document extraction, parsing, matching, scoring, and optimization."""

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm = llm_provider or get_llm_provider()
        self.jd_parser = JDParserService(self.llm)
        self.cv_parser = CVParserService(self.llm)
        self.matching_engine = MatchingEngine(self.llm)
        self.scoring_service = ScoringService()
        self.cv_rewriter = CVRewriterService(self.llm)

    async def run(
        self,
        jd_text: str | None = None,
        cv_text: str | None = None,
        jd_file_path: str | None = None,
        cv_file_path: str | None = None,
    ) -> AnalysisResult:
        """Run the end-to-end analysis pipeline.

        Args:
            jd_text: Raw JD text if provided directly.
            cv_text: Raw CV text if provided directly.
            jd_file_path: Path to JD document if uploaded.
            cv_file_path: Path to CV document if uploaded.

        Returns:
            Complete AnalysisResult domain model.
        """
        start_time = time.time()
        logger.info("pipeline_started")

        # Step 1: Extract JD text
        if jd_file_path:
            logger.info("extracting_jd_file", path=jd_file_path)
            parser = parser_factory.get_parser(jd_file_path)
            resolved_jd_text = await parser.extract_text(jd_file_path)
        elif jd_text:
            resolved_jd_text = jd_text
        else:
            raise ValueError("Không có nội dung Job Description.")

        # Step 2: Extract CV text
        if cv_file_path:
            logger.info("extracting_cv_file", path=cv_file_path)
            parser = parser_factory.get_parser(cv_file_path)
            resolved_cv_text = await parser.extract_text(cv_file_path)
        elif cv_text:
            resolved_cv_text = cv_text
        else:
            raise ValueError("Không có nội dung CV.")

        # Step 3: Parse JD into structured representation
        logger.info("pipeline_parsing_jd")
        structured_jd: StructuredJD = await self.jd_parser.parse(resolved_jd_text)

        # Step 4: Parse CV into structured representation
        logger.info("pipeline_parsing_cv")
        structured_cv: StructuredCV = await self.cv_parser.parse(resolved_cv_text)

        # Step 5: Semantic Matching Engine & Evidence Mapping
        logger.info("pipeline_matching_engine")
        matches = await self.matching_engine.match(structured_jd, structured_cv)

        # Step 6: Gap Analysis
        gap_summary = GapAnalyzer.summarize(matches)

        # Step 7: Transparent Alignment Scoring
        logger.info("pipeline_scoring")
        alignment_score = self.scoring_service.calculate_alignment(
            jd=structured_jd,
            cv=structured_cv,
            matches=matches,
        )

        # Step 8: Priority ranking & Top 5 recommendations
        top_recommendations = PriorityAnalyzer.get_top_recommendations(matches, limit=5)

        # Step 9: Before / After CV Rewriting suggestions
        logger.info("pipeline_cv_rewriting")
        suggestions = await self.cv_rewriter.generate_suggestions(
            jd=structured_jd,
            cv=structured_cv,
            matches=matches,
        )

        total_time = round(time.time() - start_time, 2)
        logger.info(
            "pipeline_finished_successfully",
            duration_seconds=total_time,
            overall_score=alignment_score.overall,
        )

        return AnalysisResult(
            structured_jd=structured_jd,
            structured_cv=structured_cv,
            matches=matches,
            alignment_score=alignment_score,
            top_recommendations=top_recommendations,
            suggestions=suggestions,
            strong_count=gap_summary.strong_count,
            partial_count=gap_summary.partial_count,
            weak_count=gap_summary.weak_count,
            missing_count=gap_summary.missing_count,
            analyzed_at=datetime.now(),
            processing_time_seconds=total_time,
        )
