"""Integration utilities for sono-platform.

Provides Council AI and assessment engine integration for:
- Code review workflows in XLayer
- Quality scoring for sensor implementations
- Documentation quality assessment
- Architecture decisions
- Security reviews
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from shared_ai_utils.assessment import (
    AssessmentEngine,
    AssessmentInput,
    CouncilAdapter,
    PathType,
)
from shared_ai_utils.assessment.pattern_checks import detect_pattern_violations

logger = logging.getLogger(__name__)


class SonoPlatformReviewer:
    """Code review and quality assessment for sono-platform using Council AI and assessment engine."""

    def __init__(
        self,
        council_domain: str = "coding",
        council_api_key: Optional[str] = None,
        enable_assessment: bool = True,
    ):
        """Initialize sono-platform reviewer.

        Args:
            council_domain: Council AI domain preset (default: "coding")
            council_api_key: Optional API key for Council AI
            enable_assessment: Enable assessment engine integration
        """
        self.council_adapter = CouncilAdapter(council_domain, council_api_key)
        self.council_adapter.load_if_available()
        self.assessment_engine = (
            AssessmentEngine(
                dark_horse_enabled=True,
                council_domain=council_domain,
                council_api_key=council_api_key,
            )
            if enable_assessment
            else None
        )

    async def review_code(
        self,
        file_path: str,
        code: str,
        review_type: str = "all",
    ) -> Dict[str, Any]:
        """Review code using Council AI personas.

        Args:
            file_path: Path to the code file
            code: Code content to review
            review_type: Type of review ("all", "security", "design", "quality")

        Returns:
            Review results with recommendations
        """
        if not self.council_adapter._available:
            logger.warning("Council AI not available for code review")
            return {"available": False, "error": "Council AI not available"}

        # Determine which personas to use based on review type
        if review_type == "security":
            query = (
                f"Review this code for security vulnerabilities:\n\n"
                f"File: {file_path}\n\n"
                f"Code:\n{code[:8000]}"
            )
            # Use Red Team personas
            self.council_adapter.council_domain = "coding"  # Will use PH, NT for security
        elif review_type == "design":
            query = (
                f"Review this code for design quality and architecture:\n\n"
                f"File: {file_path}\n\n"
                f"Code:\n{code[:8000]}"
            )
        elif review_type == "quality":
            query = (
                f"Review this code for quality, maintainability, and best practices:\n\n"
                f"File: {file_path}\n\n"
                f"Code:\n{code[:8000]}"
            )
        else:  # all
            query = (
                f"Perform a comprehensive code review covering security, design, quality, and best practices:\n\n"
                f"File: {file_path}\n\n"
                f"Code:\n{code[:8000]}"
            )

        try:
            if not self.council_adapter._council:
                return {"available": False, "error": "Council AI not initialized"}

            # Use Council AI for review
            result = await self.council_adapter._council.consult_async(query)

            # Detect pattern violations
            pattern_violations = detect_pattern_violations(code)

            return {
                "available": True,
                "synthesis": result.synthesis,
                "responses": [
                    {"persona": r.persona.name, "content": r.content}
                    for r in result.responses
                ],
                "pattern_violations": [v.to_dict() for v in pattern_violations],
                "file_path": file_path,
            }
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {"available": False, "error": str(e)}

    async def assess_sensor_implementation(
        self,
        sensor_name: str,
        sensor_code: str,
        sensor_doc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assess a sensor implementation using assessment engine.

        Args:
            sensor_name: Name of the sensor
            sensor_code: Sensor implementation code
            sensor_doc: Optional sensor documentation

        Returns:
            Assessment results with scores and recommendations
        """
        if not self.assessment_engine:
            return {"available": False, "error": "Assessment engine not enabled"}

        # Prepare assessment input
        content = {
            "code": sensor_code,
            "documentation": sensor_doc or "",
            "sensor_name": sensor_name,
        }

        assessment_input = AssessmentInput(
            candidate_id=f"sensor_{sensor_name}",
            submission_type="code",
            content=content,
            paths_to_evaluate=[PathType.TECHNICAL, PathType.DESIGN],
        )

        try:
            result = await self.assessment_engine.assess(assessment_input)
            return {
                "available": True,
                "overall_score": result.overall_score,
                "confidence": result.confidence,
                "path_scores": [
                    {
                        "path": ps.path.value,
                        "score": ps.overall_score,
                        "strengths": ps.strengths,
                        "improvements": ps.areas_for_improvement,
                    }
                    for ps in result.path_scores
                ],
                "recommendations": result.recommendations,
                "key_findings": result.key_findings,
            }
        except Exception as e:
            logger.error(f"Sensor assessment failed: {e}")
            return {"available": False, "error": str(e)}

    async def review_architecture_decision(
        self,
        decision_context: str,
        options: List[str],
    ) -> Dict[str, Any]:
        """Review an architecture decision using Council AI.

        Args:
            decision_context: Context for the decision
            options: List of options being considered

        Returns:
            Review results with recommendations
        """
        if not self.council_adapter._available:
            return {"available": False, "error": "Council AI not available"}

        query = (
            f"Review this architecture decision:\n\n"
            f"Context: {decision_context}\n\n"
            f"Options being considered:\n"
            + "\n".join(f"- {opt}" for opt in options)
            + "\n\n"
            f"Provide analysis of each option, trade-offs, and recommendation."
        )

        try:
            if not self.council_adapter._council:
                return {"available": False, "error": "Council AI not initialized"}

            result = await self.council_adapter._council.consult_async(query)
            return {
                "available": True,
                "synthesis": result.synthesis,
                "responses": [
                    {"persona": r.persona.name, "content": r.content}
                    for r in result.responses
                ],
            }
        except Exception as e:
            logger.error(f"Architecture review failed: {e}")
            return {"available": False, "error": str(e)}

    async def assess_documentation_quality(
        self,
        doc_path: str,
        doc_content: str,
    ) -> Dict[str, Any]:
        """Assess documentation quality using assessment engine.

        Args:
            doc_path: Path to documentation file
            doc_content: Documentation content

        Returns:
            Assessment results
        """
        if not self.assessment_engine:
            return {"available": False, "error": "Assessment engine not enabled"}

        content = {
            "text": doc_content,
            "file_path": doc_path,
        }

        assessment_input = AssessmentInput(
            candidate_id=f"doc_{Path(doc_path).stem}",
            submission_type="project",
            content=content,
            paths_to_evaluate=[PathType.COLLABORATION, PathType.COMMUNICATION],
        )

        try:
            result = await self.assessment_engine.assess(assessment_input)
            return {
                "available": True,
                "overall_score": result.overall_score,
                "recommendations": result.recommendations,
                "key_findings": result.key_findings,
            }
        except Exception as e:
            logger.error(f"Documentation assessment failed: {e}")
            return {"available": False, "error": str(e)}
