"""Integration utilities for sono-eval.

Provides pattern library integration for sono-eval assessment engine.
"""

import logging
from typing import Any, Dict, List, Optional

from shared_ai_utils.assessment.pattern_checks import (
    PatternViolation,
    detect_pattern_violations,
)
from shared_ai_utils.patterns import PatternManager

logger = logging.getLogger(__name__)


class SonoEvalPatternIntegration:
    """Integrates pattern library into sono-eval assessment engine."""

    def __init__(self, pattern_library_path: Optional[str] = None):
        """Initialize pattern integration.

        Args:
            pattern_library_path: Optional path to pattern library JSON file
        """
        self.pattern_manager = PatternManager(
            pattern_library_path=pattern_library_path or "patterns.json"
        )

    def check_patterns_in_submission(
        self, code: str, submission_type: str = "code"
    ) -> List[PatternViolation]:
        """Check for pattern violations in submission.

        Args:
            code: Code content to check
            submission_type: Type of submission (default: "code")

        Returns:
            List of pattern violations found
        """
        if submission_type != "code":
            return []

        violations = detect_pattern_violations(code)
        logger.debug(f"Found {len(violations)} pattern violations")
        return violations

    def get_pattern_recommendations(
        self, context: str, code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pattern recommendations based on context.

        Args:
            context: Context description (e.g., "error handling in async code")
            code: Optional code snippet for pattern matching

        Returns:
            List of recommended patterns
        """
        try:
            recommendations = self.pattern_manager.suggest_patterns(context)
            return recommendations
        except Exception as e:
            logger.error(f"Failed to get pattern recommendations: {e}")
            return []

    def enhance_assessment_with_patterns(
        self, assessment_result: Dict[str, Any], violations: List[PatternViolation]
    ) -> Dict[str, Any]:
        """Enhance assessment result with pattern violation information.

        Args:
            assessment_result: Assessment result dictionary
            violations: List of pattern violations

        Returns:
            Enhanced assessment result
        """
        if not violations:
            return assessment_result

        # Add pattern violation metadata
        assessment_result["pattern_violations"] = {
            "count": len(violations),
            "violations": [v.to_dict() for v in violations],
            "severity_breakdown": self._get_severity_breakdown(violations),
        }

        # Add recommendations based on violations
        recommendations = []
        for violation in violations:
            pattern_info = self.pattern_manager.get_pattern(violation.pattern)
            if pattern_info:
                recommendations.append({
                    "pattern": violation.pattern,
                    "description": pattern_info.get("description", ""),
                    "good_example": pattern_info.get("good_example", ""),
                    "line": violation.line,
                })

        if recommendations:
            assessment_result.setdefault("recommendations", []).extend(recommendations)

        return assessment_result

    def _get_severity_breakdown(self, violations: List[PatternViolation]) -> Dict[str, int]:
        """Get breakdown of violations by severity.

        Args:
            violations: List of pattern violations

        Returns:
            Dictionary mapping severity to count
        """
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for violation in violations:
            severity = violation.severity.lower()
            if severity in breakdown:
                breakdown[severity] += 1
        return breakdown
