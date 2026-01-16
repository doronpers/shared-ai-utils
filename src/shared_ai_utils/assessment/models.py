"""Data models for the assessment system."""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MotiveType(str, Enum):
    """Types of micro-motives in the Dark Horse model."""

    EXPLORATION = "exploration"
    MASTERY = "mastery"
    COLLABORATION = "collaboration"
    INNOVATION = "innovation"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"


class PathType(str, Enum):
    """Different assessment paths."""

    TECHNICAL = "technical"
    DESIGN = "design"
    COLLABORATION = "collaboration"
    PROBLEM_SOLVING = "problem_solving"
    COMMUNICATION = "communication"


class EvidenceType(str, Enum):
    """Types of evidence for scoring."""

    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    COLLABORATION = "collaboration"
    COMMUNICATION = "communication"


class Evidence(BaseModel):
    """Evidence supporting a score."""

    type: EvidenceType
    description: str
    source: str  # File path, line number, or reference
    weight: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MicroMotive(BaseModel):
    """Micro-motive tracking for Dark Horse model."""

    motive_type: MotiveType
    strength: float = Field(ge=0.0, le=1.0)
    indicators: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    path_alignment: PathType


class ScoringMetric(BaseModel):
    """Individual scoring metric with explainability."""

    name: str
    category: str
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class PathScore(BaseModel):
    """Score for a specific assessment path."""

    path: PathType
    overall_score: float = Field(ge=0.0, le=100.0)
    metrics: List[ScoringMetric] = Field(default_factory=list)
    motives: List[MicroMotive] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    """Complete assessment result with explainability."""

    candidate_id: str
    assessment_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Overall scores
    overall_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)

    # Multi-path scores
    path_scores: List[PathScore] = Field(default_factory=list)

    # Dark Horse tracking
    micro_motives: List[MicroMotive] = Field(default_factory=list)
    dominant_path: Optional[PathType] = None

    # Explainability
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    # Metadata
    engine_version: str = "1.0"
    processing_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssessmentInput(BaseModel):
    """Input for assessment."""

    candidate_id: str = Field(..., min_length=1, max_length=100)
    submission_type: str = Field(..., min_length=1, max_length=50)
    content: Dict[str, Any]  # Flexible content structure
    paths_to_evaluate: List[PathType] = Field(default_factory=lambda: list(PathType))
    options: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, v: str) -> str:
        """Validate candidate_id to prevent injection attacks."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "candidate_id must contain only alphanumeric characters, dashes, and underscores"
            )
        return v

    @field_validator("submission_type")
    @classmethod
    def validate_submission_type(cls, v: str) -> str:
        """Validate submission_type."""
        allowed_types = ["code", "project", "interview", "portfolio", "test"]
        if v not in allowed_types:
            raise ValueError(f'submission_type must be one of: {", ".join(allowed_types)}')
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content structure."""
        if not v:
            raise ValueError("content cannot be empty")
        # Check for reasonable size (prevent DoS via large payloads)
        content_str = json.dumps(v)
        if len(content_str) > 10_000_000:  # 10MB limit
            raise ValueError("content size exceeds maximum allowed (10MB)")
        return v
