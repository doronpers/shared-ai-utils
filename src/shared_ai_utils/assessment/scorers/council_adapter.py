"""Council AI adapter for assessment scoring.

This adapter bridges Council AI consultations with the assessment framework,
enabling any repository to use Council AI personas for assessment and review.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from shared_ai_utils.assessment.helpers import extract_text_content
from shared_ai_utils.assessment.models import (
    AssessmentInput,
    Evidence,
    EvidenceType,
    PathType,
    ScoringMetric,
)

logger = logging.getLogger(__name__)


class CouncilAdapter:
    """
    Adapter that leverages Council AI personas for deep, multi-perspective assessment.

    This adapter provides a bridge between Council AI consultations and the
    assessment framework, making it easy to integrate Council AI into any
    assessment workflow.
    """

    def __init__(self, council_domain: str = "coding", api_key: Optional[str] = None):
        """Initialize Council AI adapter.

        Args:
            council_domain: Domain preset to use for Council (default: "coding")
            api_key: Optional API key (uses environment variables if not provided)
        """
        self._council = None
        self._available = False
        self.council_domain = council_domain
        self.api_key = api_key

    def load_if_available(self) -> bool:
        """Initialize Council AI if available.

        Returns:
            True if Council AI is available, False otherwise
        """
        if self._council is not None:
            return True

        try:
            # Try to import Council AI
            try:
                from council_ai import Council  # type: ignore
            except ImportError:
                logger.warning("Council AI not available (council-ai package not installed)")
                return False

            # Initialize with specified domain
            if self.api_key:
                self._council = Council.for_domain(self.council_domain, api_key=self.api_key)
            else:
                self._council = Council.for_domain(self.council_domain)

            self._available = True
            logger.info(f"Council AI initialized successfully for assessment (domain: {self.council_domain})")
            return True
        except Exception as e:
            logger.warning(f"Council AI initialization failed: {e}")
            self._available = False
            return False

    async def get_insights(
        self, content: Any, path: PathType
    ) -> Optional[Dict[str, Any]]:
        """
        Consult the council for insights on the provided content.

        Args:
            content: The submission content (code, text, etc.)
            path: The assessment path (technical, creative, etc.)

        Returns:
            Dictionary containing synthesis, score_estimation, and detailed feedback,
            or None if Council AI is not available
        """
        if not self._available or self._council is None:
            return None

        text = extract_text_content(content)
        if not text:
            return None

        # Construct a prompt that asks for specific assessment criteria
        query = (
            f"Assess this submission for the '{path.value}' path.\n"
            f"Provide a critical review focusing on:\n"
            f"1. Strengths\n"
            f"2. Weaknesses\n"
            f"3. A numerical score estimation (0-100) based on quality and best practices.\n\n"
            f"Code/Content:\n{text[:8000]}"  # Truncate to avoid context limits
        )

        try:
            # Use async consultation
            result = await self._council.consult_async(query)

            # Extract score from synthesis if possible (naive regex extraction)
            score_match = re.search(r"score[:\s]+(\d+)/100", result.synthesis, re.IGNORECASE)
            score_est = float(score_match.group(1)) if score_match else None

            return {
                "synthesis": result.synthesis,
                "responses": [
                    {"persona": r.persona.name, "content": r.content} for r in result.responses
                ],
                "score": score_est,
                "confidence": 0.85,  # High confidence in AI council
            }
        except Exception as e:
            logger.error(f"Council consultation error: {e}")
            return None

    def enhance_metrics(
        self,
        metrics: List[ScoringMetric],
        council_insights: Dict[str, Any],
        path: PathType,
    ) -> List[ScoringMetric]:
        """Enhance heuristic metrics with Council insights.

        Args:
            metrics: Existing scoring metrics
            council_insights: Insights from Council AI consultation
            path: The assessment path

        Returns:
            Enhanced list of metrics with Council AI assessment added
        """
        if not council_insights:
            return metrics

        # Extract Council metric
        synthesis = council_insights.get("synthesis", "No synthesis provided.")
        score = council_insights.get("score")

        # Create a new metric for the Council's assessment
        council_metric = ScoringMetric(
            name="AI Council Review",
            category="ai_assessment",
            score=score if score is not None else 80.0,  # Fallback score
            weight=0.4,  # Significant weight
            evidence=[
                Evidence(
                    type=EvidenceType.CODE_QUALITY,
                    description="Council Consensus",
                    source="council_ai",
                    weight=1.0,
                    metadata={"synthesis": synthesis},
                )
            ],
            explanation=(
                f"The AI Council (various personas) reviewed the submission. "
                f"Consensus: {synthesis[:200]}..."
            ),
            confidence=council_insights.get("confidence", 0.8),
        )

        metrics.append(council_metric)
        return metrics

    def generate_metrics_for_path(
        self,
        path: PathType,
        input_data: AssessmentInput,
        pattern_violations=None,
    ) -> List[ScoringMetric]:
        """CouncilAdapter doesn't generate metrics directly (use enhance_metrics)."""
        return []

    def identify_micro_motives(
        self, path: PathType, input_data: AssessmentInput
    ) -> List:
        """CouncilAdapter doesn't identify micro-motives (use MicroMotiveScorer)."""
        return []
