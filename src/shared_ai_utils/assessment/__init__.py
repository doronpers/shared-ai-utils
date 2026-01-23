"""
Assessment Engine

Evidence-based multi-path assessment system with explainable scoring.
"""

from shared_ai_utils.assessment.engine import AssessmentEngine
from shared_ai_utils.assessment.helpers import extract_text_content
from shared_ai_utils.assessment.models import (
    AssessmentInput,
    AssessmentResult,
    Evidence,
    EvidenceType,
    MicroMotive,
    MotiveType,
    PathScore,
    PathType,
    ScoringMetric,
)
from shared_ai_utils.assessment.pattern_checks import (
    PatternViolation,
    calculate_pattern_penalty,
    detect_pattern_violations,
    violations_to_metadata,
)
from shared_ai_utils.assessment.scorers import (
    CouncilAdapter,
    HeuristicScorer,
    MicroMotiveScorer,
)
from shared_ai_utils.assessment.scorers.heuristic import HeuristicScorerConfig

__all__ = [
    "AssessmentEngine",
    "AssessmentInput",
    "AssessmentResult",
    "PathScore",
    "ScoringMetric",
    "Evidence",
    "EvidenceType",
    "MicroMotive",
    "MotiveType",
    "PathType",
    "PatternViolation",
    "detect_pattern_violations",
    "calculate_pattern_penalty",
    "violations_to_metadata",
    "HeuristicScorer",
    "MicroMotiveScorer",
    "CouncilAdapter",
    "HeuristicScorerConfig",
    "extract_text_content",
]
