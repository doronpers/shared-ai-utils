"""Integration utilities for feedback-loop.

Provides assessment engine integration for pattern validation.
"""

import logging
from typing import Any, Dict, List, Optional

from shared_ai_utils.assessment import (
    AssessmentEngine,
    AssessmentInput,
    PathType,
)
from shared_ai_utils.assessment.pattern_checks import detect_pattern_violations

logger = logging.getLogger(__name__)


class FeedbackLoopAssessmentIntegration:
    """Integrates assessment engine into feedback-loop for pattern validation."""

    def __init__(self, enable_council: bool = False, council_api_key: Optional[str] = None):
        """Initialize assessment integration.

        Args:
            enable_council: Enable Council AI for pattern reviews
            council_api_key: Optional API key for Council AI
        """
        self.assessment_engine = AssessmentEngine(
            council_domain="coding" if enable_council else None,
            council_api_key=council_api_key,
            enable_assessment=True,
        )

    async def validate_pattern_example(
        self,
        pattern_name: str,
        good_example: str,
        bad_example: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validate pattern examples using assessment engine.

        Args:
            pattern_name: Name of the pattern
            good_example: Good example code
            bad_example: Optional bad example code

        Returns:
            Validation results
        """
        # Assess good example
        good_content = {"code": good_example, "pattern": pattern_name}
        good_input = AssessmentInput(
            candidate_id=f"pattern_{pattern_name}_good",
            submission_type="code",
            content=good_content,
            paths_to_evaluate=[PathType.TECHNICAL],
        )

        try:
            good_result = await self.assessment_engine.assess(good_input)

            # Assess bad example if provided
            bad_result = None
            if bad_example:
                bad_content = {"code": bad_example, "pattern": pattern_name}
                bad_input = AssessmentInput(
                    candidate_id=f"pattern_{pattern_name}_bad",
                    submission_type="code",
                    content=bad_content,
                    paths_to_evaluate=[PathType.TECHNICAL],
                )
                bad_result = await self.assessment_engine.assess(bad_input)

            # Check for pattern violations
            good_violations = detect_pattern_violations(good_example)
            bad_violations = detect_pattern_violations(bad_example) if bad_example else []

            return {
                "pattern_name": pattern_name,
                "good_example_score": good_result.overall_score,
                "bad_example_score": bad_result.overall_score if bad_result else None,
                "good_example_violations": len(good_violations),
                "bad_example_violations": len(bad_violations),
                "validation_passed": (
                    good_result.overall_score > 70
                    and (bad_result is None or bad_result.overall_score < 50)
                    and len(good_violations) == 0
                ),
                "recommendations": good_result.recommendations,
            }
        except Exception as e:
            logger.error(f"Pattern validation failed: {e}")
            return {"error": str(e)}

    async def assess_pattern_effectiveness(
        self,
        pattern_name: str,
        code_samples: List[str],
        success_indicators: List[str],
    ) -> Dict[str, Any]:
        """Assess pattern effectiveness using multiple code samples.

        Args:
            pattern_name: Name of the pattern
            code_samples: List of code samples using the pattern
            success_indicators: List of indicators of successful pattern application

        Returns:
            Effectiveness assessment results
        """
        scores = []
        all_violations = []

        for i, code in enumerate(code_samples):
            content = {"code": code, "pattern": pattern_name}
            input_data = AssessmentInput(
                candidate_id=f"pattern_{pattern_name}_sample_{i}",
                submission_type="code",
                content=content,
                paths_to_evaluate=[PathType.TECHNICAL],
            )

            try:
                result = await self.assessment_engine.assess(input_data)
                scores.append(result.overall_score)
                violations = detect_pattern_violations(code)
                all_violations.extend(violations)
            except Exception as e:
                logger.error(f"Failed to assess sample {i}: {e}")

        if not scores:
            return {"error": "No valid assessments"}

        avg_score = sum(scores) / len(scores)
        violation_count = len(all_violations)

        return {
            "pattern_name": pattern_name,
            "average_score": avg_score,
            "sample_count": len(code_samples),
            "violation_count": violation_count,
            "effectiveness_score": avg_score - (violation_count * 5),  # Penalize violations
            "recommendations": [
                "Pattern appears effective" if avg_score > 75 else "Pattern needs improvement"
            ],
        }
