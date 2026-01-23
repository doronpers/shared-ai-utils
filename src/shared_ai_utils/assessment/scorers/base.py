"""Base scorer interface for assessment engine."""

from abc import ABC, abstractmethod
from typing import List, Optional

from shared_ai_utils.assessment.models import (
    AssessmentInput,
    MicroMotive,
    PathScore,
    PathType,
    ScoringMetric,
)
from shared_ai_utils.assessment.pattern_checks import PatternViolation


class BaseScorer(ABC):
    """Base class for assessment scorers.

    Scorers can implement either or both methods depending on their purpose.
    """

    def generate_metrics_for_path(
        self,
        path: PathType,
        input_data: AssessmentInput,
        pattern_violations: Optional[List[PatternViolation]] = None,
    ) -> List[ScoringMetric]:
        """Generate scoring metrics for a specific path.

        Args:
            path: The assessment path to evaluate
            input_data: The assessment input data
            pattern_violations: Optional list of detected pattern violations

        Returns:
            List of scoring metrics for this path
        """
        return []  # Default: no metrics

    def identify_micro_motives(
        self, path: PathType, input_data: AssessmentInput
    ) -> List[MicroMotive]:
        """Identify micro-motives for a specific path.

        Args:
            path: The assessment path
            input_data: The assessment input data

        Returns:
            List of identified micro-motives
        """
        return []  # Default: no motives
