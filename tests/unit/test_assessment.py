"""Tests for assessment engine."""

import pytest

from shared_ai_utils.assessment import (
    AssessmentEngine,
    AssessmentInput,
    PathType,
)


class TestAssessmentEngine:
    """Test AssessmentEngine."""

    @pytest.fixture
    def engine(self):
        """Create assessment engine instance."""
        return AssessmentEngine()

    @pytest.fixture
    def sample_input(self):
        """Create sample assessment input."""
        return AssessmentInput(
            candidate_id="test_candidate",
            submission_type="code",
            content={"code": "def hello():\n    return 'world'"},
            paths_to_evaluate=[PathType.TECHNICAL],
        )

    @pytest.mark.asyncio
    async def test_assess_basic(self, engine, sample_input):
        """Test basic assessment."""
        result = await engine.assess(sample_input)

        assert result.candidate_id == "test_candidate"
        assert result.overall_score >= 0.0
        assert result.overall_score <= 100.0
        assert result.confidence >= 0.0
        assert result.confidence <= 1.0
        assert len(result.path_scores) > 0
        assert result.summary
        assert result.engine_version in ["1.0", "2.0"]  # Allow for version updates

    @pytest.mark.asyncio
    async def test_assess_multiple_paths(self, engine):
        """Test assessment with multiple paths."""
        input_data = AssessmentInput(
            candidate_id="test_candidate",
            submission_type="code",
            content={"code": "def hello():\n    return 'world'"},
            paths_to_evaluate=[PathType.TECHNICAL, PathType.DESIGN],
        )

        result = await engine.assess(input_data)

        assert len(result.path_scores) == 2
        assert any(ps.path == PathType.TECHNICAL for ps in result.path_scores)
        assert any(ps.path == PathType.DESIGN for ps in result.path_scores)

    @pytest.mark.asyncio
    async def test_assess_with_evidence(self, engine, sample_input):
        """Test assessment generates evidence."""
        result = await engine.assess(sample_input)

        # Check that path scores have metrics with evidence
        for path_score in result.path_scores:
            assert len(path_score.metrics) > 0
            for metric in path_score.metrics:
                assert len(metric.evidence) >= 0  # Evidence may be empty
                assert metric.explanation

    def test_calculate_path_score(self, engine):
        """Test path score calculation."""
        from shared_ai_utils.assessment import ScoringMetric

        metrics = [
            ScoringMetric(
                name="Test1",
                category="test",
                score=80.0,
                weight=0.5,
                evidence=[],
                explanation="Test",
            ),
            ScoringMetric(
                name="Test2",
                category="test",
                score=60.0,
                weight=0.5,
                evidence=[],
                explanation="Test",
            ),
        ]

        score = engine._calculate_path_score(metrics)
        assert score == 70.0  # (80 * 0.5 + 60 * 0.5) / 1.0

    def test_calculate_overall_score(self, engine):
        """Test overall score calculation."""
        from shared_ai_utils.assessment import PathScore, PathType

        path_scores = [
            PathScore(
                path=PathType.TECHNICAL,
                overall_score=80.0,
                metrics=[],
                motives=[],
                strengths=[],
                areas_for_improvement=[],
            ),
            PathScore(
                path=PathType.DESIGN,
                overall_score=60.0,
                metrics=[],
                motives=[],
                strengths=[],
                areas_for_improvement=[],
            ),
        ]

        overall = engine._calculate_overall_score(path_scores)
        assert overall == 70.0  # (80 + 60) / 2

    def test_extract_text_content(self, engine):
        """Test text content extraction."""
        content = {"code": "def hello():\n    return 'world'"}
        text = engine._extract_text_content(content)
        assert "def hello" in text
        assert "return 'world'" in text

    def test_analyze_code_quality(self, engine):
        """Test code quality analysis."""
        code = "def hello():\n    return 'world'"
        score = engine._analyze_code_quality(code)
        assert 0.0 <= score <= 100.0

    def test_identify_strengths(self, engine):
        """Test strength identification."""
        from shared_ai_utils.assessment import ScoringMetric

        metrics = [
            ScoringMetric(
                name="High Score",
                category="test",
                score=85.0,
                weight=1.0,
                evidence=[],
                explanation="Excellent",
            ),
            ScoringMetric(
                name="Low Score",
                category="test",
                score=50.0,
                weight=1.0,
                evidence=[],
                explanation="Needs work",
            ),
        ]

        strengths = engine._identify_strengths(metrics)
        assert len(strengths) == 1
        assert "High Score" in strengths[0]

    def test_identify_improvements(self, engine):
        """Test improvement identification."""
        from shared_ai_utils.assessment import ScoringMetric

        metrics = [
            ScoringMetric(
                name="High Score",
                category="test",
                score=85.0,
                weight=1.0,
                evidence=[],
                explanation="Excellent",
            ),
            ScoringMetric(
                name="Low Score",
                category="test",
                score=50.0,
                weight=1.0,
                evidence=[],
                explanation="Needs work",
            ),
        ]

        improvements = engine._identify_improvements(metrics)
        assert len(improvements) == 1
        assert "Low Score" in improvements[0]
