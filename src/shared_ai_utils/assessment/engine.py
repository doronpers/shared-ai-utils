"""
Assessment Engine

Evidence-based multi-path assessment with explainable scoring.

Supports multi-scorer orchestration with:
- HeuristicScorer: Rule-based analysis
- CouncilAdapter: AI-powered multi-perspective review
- MicroMotiveScorer: Dark Horse micro-motive tracking
"""

import logging
import time
from typing import Any, Dict, List, Optional

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
from shared_ai_utils.assessment.scorers.council_adapter import CouncilAdapter
from shared_ai_utils.assessment.scorers.heuristic import (
    HeuristicScorer,
    HeuristicScorerConfig,
)
from shared_ai_utils.assessment.scorers.motive import MicroMotiveScorer

logger = logging.getLogger(__name__)


class AssessmentEngine:
    """
    Core assessment engine with explainable scoring.

    Features:
    - Multi-path evaluation (technical, design, collaboration, etc.)
    - Evidence-based scoring with explanations
    - Dark Horse micro-motive tracking
    - Confidence scoring
    - Multi-scorer orchestration (Heuristic, Council AI, Micro-Motive)
    - Pattern violation detection and penalty calculation

    Acts as an orchestrator for:
    - HeuristicScorer: Rule-based analysis
    - CouncilAdapter: AI-powered multi-perspective review
    - MicroMotiveScorer: Dark Horse tracking
    """

    def __init__(
        self,
        version: str = "2.0",
        enable_explanations: bool = True,
        multi_path_tracking: bool = True,
        pattern_checks_enabled: bool = True,
        dark_horse_enabled: bool = True,
        council_domain: str = "coding",
        council_api_key: Optional[str] = None,
        heuristic_config: Optional[HeuristicScorerConfig] = None,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """Initialize the assessment engine.

        Args:
            version: Engine version
            enable_explanations: Enable detailed explanations
            multi_path_tracking: Enable multi-path evaluation
            pattern_checks_enabled: Enable pattern violation detection
            dark_horse_enabled: Enable Dark Horse micro-motive tracking
            council_domain: Domain preset for Council AI (default: "coding")
            council_api_key: Optional API key for Council AI
            heuristic_config: Optional configuration for heuristic scorer
            logger_instance: Optional logger (uses module logger if None)
        """
        self.version = version
        self.enable_explanations = enable_explanations
        self.multi_path_tracking = multi_path_tracking
        self.pattern_checks_enabled = pattern_checks_enabled
        self.dark_horse_enabled = dark_horse_enabled
        self.logger = logger_instance or logger

        # Initialize Scorers
        self.heuristic_scorer = HeuristicScorer(heuristic_config or HeuristicScorerConfig())
        self.council_adapter = CouncilAdapter(council_domain, council_api_key)
        self.motive_scorer = MicroMotiveScorer()

        # Check for Council AI availability
        self.council_adapter.load_if_available()

        if not self.dark_horse_enabled:
            self.logger.info("Dark Horse micro-motive tracking is disabled")

        self.logger.info(f"Initialized AssessmentEngine v{self.version}")

    async def assess(self, assessment_input: AssessmentInput) -> AssessmentResult:
        """
        Perform comprehensive assessment with hybrid heuristics + AI approach.

        Args:
            assessment_input: Assessment input data

        Returns:
            Complete assessment result with scores and explanations
        """
        start_time = time.time()
        self.logger.info(f"Starting assessment for candidate {assessment_input.candidate_id}")

        # Generate unique assessment ID
        assessment_id = f"assess_{int(time.time() * 1000)}"

        # Detect pattern violations if enabled
        submission_text = extract_text_content(assessment_input.content)
        pattern_violations: List[PatternViolation] = []
        pattern_penalty = 0.0
        pattern_checks_active = (
            self.pattern_checks_enabled and assessment_input.submission_type == "code"
        )
        if pattern_checks_active:
            pattern_violations = detect_pattern_violations(submission_text)
            pattern_penalty = calculate_pattern_penalty(
                pattern_violations,
                self.heuristic_scorer.pattern_penalty_weights,
                self.heuristic_scorer.pattern_penalty_max,
            )

        # Evaluate each path
        path_scores = []
        all_motives = []
        all_confidences = []

        for path in assessment_input.paths_to_evaluate:
            path_score = await self._evaluate_path(path, assessment_input, pattern_violations)
            path_scores.append(path_score)
            all_motives.extend(path_score.motives)
            # Collect confidence from metrics
            if path_score.metrics:
                avg_confidence = sum(m.confidence for m in path_score.metrics) / len(
                    path_score.metrics
                )
                all_confidences.append(avg_confidence)

        # Calculate overall score
        overall_score = self._calculate_overall_score(path_scores)

        # Calculate overall confidence
        overall_confidence = (
            sum(all_confidences) / len(all_confidences) if all_confidences else 0.85
        )

        # Determine dominant path
        dominant_path = self._determine_dominant_path(path_scores)

        # Generate summary and recommendations
        summary = self._generate_summary(path_scores, all_motives)
        key_findings = self._extract_key_findings(path_scores)
        recommendations = self._generate_recommendations(path_scores)

        processing_time = (time.time() - start_time) * 1000

        result = AssessmentResult(
            candidate_id=assessment_input.candidate_id,
            assessment_id=assessment_id,
            overall_score=overall_score,
            confidence=overall_confidence,
            path_scores=path_scores,
            micro_motives=all_motives,
            dominant_path=dominant_path,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            engine_version=self.version,
            processing_time_ms=processing_time,
            metadata={
                "assessment_mode": "hybrid_council"
                if self.council_adapter._available
                else "heuristic",
                "council_available": self.council_adapter._available,
                "pattern_checks": {
                    "enabled": pattern_checks_active,
                    "violation_count": len(pattern_violations),
                    "penalty_points": pattern_penalty,
                    "violations": violations_to_metadata(pattern_violations),
                },
            },
        )

        self.logger.info(
            f"Assessment completed for {assessment_input.candidate_id}: "
            f"score={overall_score:.2f}, confidence={overall_confidence:.2%}, "
            f"mode={'hybrid_council' if self.council_adapter._available else 'heuristic'}, "
            f"time={processing_time:.2f}ms"
        )

        return result

    async def _evaluate_path(
        self,
        path: PathType,
        input_data: AssessmentInput,
        pattern_violations: Optional[List[PatternViolation]] = None,
    ) -> PathScore:
        """Evaluate a specific assessment path using multi-scorer orchestration."""
        self.logger.debug(f"Evaluating path: {path}")

        # 1. Heuristic Scoring
        metrics = self.heuristic_scorer.generate_metrics_for_path(
            path, input_data, pattern_violations
        )

        # 2. AI/Council Enhancement
        council_insights = await self.council_adapter.get_insights(input_data.content, path)
        if council_insights:
            metrics = self.council_adapter.enhance_metrics(metrics, council_insights, path)

        # 3. Micro-Motives
        if self.dark_horse_enabled:
            motives = self.motive_scorer.identify_micro_motives(path, input_data)
        else:
            motives = []

        # 4. Final Path Score Calculation
        path_score = self._calculate_path_score(metrics)
        strengths = self._identify_strengths(metrics)
        improvements = self._identify_improvements(metrics)

        return PathScore(
            path=path,
            overall_score=path_score,
            metrics=metrics,
            motives=motives,
            strengths=strengths,
            areas_for_improvement=improvements,
        )

    # Legacy methods kept for backward compatibility but now delegate to scorers
    def _generate_metrics_for_path(
        self, path: PathType, input_data: AssessmentInput
    ) -> List[ScoringMetric]:
        """Generate scoring metrics for a specific path (delegates to HeuristicScorer)."""
        return self.heuristic_scorer.generate_metrics_for_path(path, input_data)

        if path == PathType.TECHNICAL:
            # Code quality
            code_quality_score = self._analyze_code_quality(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Code Quality",
                    category="technical",
                    score=code_quality_score,
                    weight=0.3,
                    evidence=self._generate_code_quality_evidence(submission_text),
                    explanation=self._explain_code_quality(code_quality_score),
                    confidence=0.85,
                )
            )

            # Problem solving
            problem_solving_score = self._analyze_problem_solving(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Problem Solving",
                    category="technical",
                    score=problem_solving_score,
                    weight=0.3,
                    evidence=self._generate_problem_solving_evidence(submission_text),
                    explanation=self._explain_problem_solving(problem_solving_score),
                    confidence=0.8,
                )
            )

            # Testing
            testing_score = self._analyze_testing(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Testing",
                    category="technical",
                    score=testing_score,
                    weight=0.2,
                    evidence=self._generate_testing_evidence(submission_text),
                    explanation=self._explain_testing(testing_score),
                    confidence=0.75,
                )
            )

        elif path == PathType.DESIGN:
            # Architecture
            architecture_score = self._analyze_architecture(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Architecture",
                    category="design",
                    score=architecture_score,
                    weight=0.4,
                    evidence=self._generate_architecture_evidence(submission_text),
                    explanation=self._explain_architecture(architecture_score),
                    confidence=0.8,
                )
            )

            # Design thinking
            design_thinking_score = self._analyze_design_thinking(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Design Thinking",
                    category="design",
                    score=design_thinking_score,
                    weight=0.3,
                    evidence=self._generate_design_thinking_evidence(submission_text),
                    explanation=self._explain_design_thinking(design_thinking_score),
                    confidence=0.75,
                )
            )

        elif path == PathType.COLLABORATION:
            # Documentation
            documentation_score = self._analyze_documentation(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Documentation",
                    category="collaboration",
                    score=documentation_score,
                    weight=0.3,
                    evidence=self._generate_documentation_evidence(submission_text),
                    explanation=self._explain_documentation(documentation_score),
                    confidence=0.8,
                )
            )

            # Readability
            readability_score = self._analyze_readability(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Code Readability",
                    category="collaboration",
                    score=readability_score,
                    weight=0.35,
                    evidence=self._generate_readability_evidence(submission_text),
                    explanation=self._explain_readability(readability_score),
                    confidence=0.85,
                )
            )

        elif path == PathType.PROBLEM_SOLVING:
            # Analytical thinking
            analytical_score = self._analyze_analytical_thinking(submission_text)
            metrics.append(
                ScoringMetric(
                    name="Analytical Thinking",
                    category="problem_solving",
                    score=analytical_score,
                    weight=0.3,
                    evidence=self._generate_analytical_evidence(submission_text),
                    explanation=self._explain_analytical_thinking(analytical_score),
                    confidence=0.8,
                )
            )

        # Default: basic metric if path not fully implemented
        if not metrics:
            metrics.append(
                ScoringMetric(
                    name=f"{path.value.title()} Assessment",
                    category=path.value,
                    score=50.0,
                    weight=1.0,
                    evidence=[],
                    explanation=f"Basic assessment for {path.value} path",
                    confidence=0.7,
                )
            )

        return metrics

    def _identify_micro_motives(
        self, path: PathType, input_data: AssessmentInput
    ) -> List[MicroMotive]:
        """Identify micro-motives using Dark Horse model (delegates to MicroMotiveScorer)."""
        if self.dark_horse_enabled:
            return self.motive_scorer.identify_micro_motives(path, input_data)
        return []

    def _calculate_path_score(self, metrics: List[ScoringMetric]) -> float:
        """Calculate weighted average score for a path."""
        if not metrics:
            return 0.0

        total_weight = sum(m.weight for m in metrics)
        if total_weight == 0:
            return sum(m.score for m in metrics) / len(metrics)

        weighted_sum = sum(m.score * m.weight for m in metrics)
        return weighted_sum / total_weight

    def _calculate_overall_score(self, path_scores: List[PathScore]) -> float:
        """Calculate overall score from path scores."""
        if not path_scores:
            return 0.0
        return sum(ps.overall_score for ps in path_scores) / len(path_scores)

    def _determine_dominant_path(self, path_scores: List[PathScore]) -> Optional[PathType]:
        """Determine the dominant assessment path."""
        if not path_scores:
            return None
        return max(path_scores, key=lambda ps: ps.overall_score).path

    def _identify_strengths(self, metrics: List[ScoringMetric]) -> List[str]:
        """Identify strengths from metrics."""
        return [f"{m.name}: {m.explanation}" for m in metrics if m.score >= 75.0]

    def _identify_improvements(self, metrics: List[ScoringMetric]) -> List[str]:
        """Identify areas for improvement."""
        return [
            f"{m.name}: Consider enhancing this area (current score: {m.score:.0f})"
            for m in metrics
            if m.score < 75.0
        ]

    def _generate_summary(self, path_scores: List[PathScore], motives: List[MicroMotive]) -> str:
        """Generate assessment summary."""
        avg_score = self._calculate_overall_score(path_scores)
        top_path = self._determine_dominant_path(path_scores)

        summary = (
            f"Assessment shows an overall score of {avg_score:.1f}/100. "
            f"Strongest performance in {top_path.value if top_path else 'multiple areas'}. "
        )

        if motives:
            dominant_motive = max(motives, key=lambda m: m.strength)
            summary += (
                f"Primary micro-motive is {dominant_motive.motive_type.value} "
                f"with strength {dominant_motive.strength:.2f}."
            )

        return summary

    def _extract_key_findings(self, path_scores: List[PathScore]) -> List[str]:
        """Extract key findings from path scores."""
        findings = []
        for ps in path_scores:
            if ps.overall_score >= 80:
                findings.append(
                    f"Strong performance in {ps.path.value} (score: {ps.overall_score:.1f})"
                )
            elif ps.overall_score < 60:
                findings.append(
                    f"Opportunity for growth in {ps.path.value} (score: {ps.overall_score:.1f})"
                )
        return findings

    def _generate_recommendations(self, path_scores: List[PathScore]) -> List[str]:
        """Generate recommendations based on scores."""
        recommendations = []
        for ps in path_scores:
            if ps.areas_for_improvement:
                recommendations.append(
                    f"Focus on {ps.path.value}: {ps.areas_for_improvement[0]}"
                )
        return recommendations

    # Content Analysis Helper Methods (kept for backward compatibility)
    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """Extract text content from submission (delegates to helper)."""
        return extract_text_content(content)

    def _analyze_code_quality(self, text: str) -> float:
        """Analyze code quality using heuristics."""
        score = 50.0
        text_lower = text.lower()

        # Positive indicators
        if "def " in text or "function " in text or "class " in text:
            score += 10
        if "import " in text or "from " in text:
            score += 5
        if "try:" in text or "except" in text:
            score += 10
        if "test" in text_lower or "assert" in text_lower:
            score += 10
        if len(text.split("\n")) > 10:
            score += 5

        # Negative indicators
        if text.count("print(") > 5:
            score -= 5
        if "todo" in text_lower or "fixme" in text_lower:
            score -= 3

        return min(100.0, max(0.0, score))

    def _generate_code_quality_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for code quality."""
        evidence = []

        if "def " in text or "function " in text:
            evidence.append(
                Evidence(
                    type=EvidenceType.CODE_QUALITY,
                    description="Code uses functions/methods for organization",
                    source="code_structure",
                    weight=0.7,
                )
            )

        if "try:" in text or "except" in text:
            evidence.append(
                Evidence(
                    type=EvidenceType.CODE_QUALITY,
                    description="Error handling present in code",
                    source="error_handling",
                    weight=0.8,
                )
            )

        return evidence

    def _explain_code_quality(self, score: float) -> str:
        """Explain code quality score."""
        if score >= 80:
            return "Code demonstrates strong quality with good structure and practices"
        elif score >= 60:
            return "Code shows solid fundamentals with room for improvement"
        else:
            return "Code quality could be enhanced with better structure and practices"

    def _analyze_problem_solving(self, text: str) -> float:
        """Analyze problem-solving approach."""
        score = 50.0
        text_lower = text.lower()

        if any(word in text_lower for word in ["algorithm", "complexity", "optimize", "efficient"]):
            score += 15
        if any(word in text_lower for word in ["loop", "iterate", "recursion"]):
            score += 10
        if "if " in text or "else" in text:
            score += 5

        return min(100.0, max(0.0, score))

    def _generate_problem_solving_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for problem solving."""
        evidence = []
        text_lower = text.lower()

        if "optimize" in text_lower or "efficient" in text_lower:
            evidence.append(
                Evidence(
                    type=EvidenceType.CODE_QUALITY,
                    description="Shows awareness of optimization",
                    source="code_analysis",
                    weight=0.7,
                )
            )

        return evidence

    def _explain_problem_solving(self, score: float) -> str:
        """Explain problem-solving score."""
        if score >= 75:
            return "Demonstrates strong problem-solving with clear approach"
        elif score >= 55:
            return "Shows good problem-solving fundamentals"
        else:
            return "Problem-solving approach could be more systematic"

    def _analyze_testing(self, text: str) -> float:
        """Analyze testing approach."""
        score = 30.0
        text_lower = text.lower()

        if "test" in text_lower:
            score += 20
        if "assert" in text_lower:
            score += 15
        if "mock" in text_lower or "stub" in text_lower:
            score += 10

        return min(100.0, max(0.0, score))

    def _generate_testing_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for testing."""
        evidence = []
        text_lower = text.lower()

        if "test" in text_lower:
            evidence.append(
                Evidence(
                    type=EvidenceType.TESTING,
                    description="Testing mentioned or present",
                    source="code_analysis",
                    weight=0.6,
                )
            )

        return evidence

    def _explain_testing(self, score: float) -> str:
        """Explain testing score."""
        if score >= 70:
            return "Good testing awareness and practices"
        elif score >= 40:
            return "Some testing present but could be more comprehensive"
        else:
            return "Testing approach needs development"

    def _analyze_architecture(self, text: str) -> float:
        """Analyze architecture and design."""
        score = 50.0
        text_lower = text.lower()

        if "class " in text or "module" in text_lower:
            score += 15
        if "pattern" in text_lower or "design" in text_lower:
            score += 10

        return min(100.0, max(0.0, score))

    def _generate_architecture_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for architecture."""
        evidence = []

        if "class " in text:
            evidence.append(
                Evidence(
                    type=EvidenceType.ARCHITECTURE,
                    description="Object-oriented structure present",
                    source="code_structure",
                    weight=0.7,
                )
            )

        return evidence

    def _explain_architecture(self, score: float) -> str:
        """Explain architecture score."""
        if score >= 75:
            return "Well-structured architecture with clear organization"
        elif score >= 55:
            return "Good architectural awareness"
        else:
            return "Architecture could be more structured"

    def _analyze_design_thinking(self, text: str) -> float:
        """Analyze design thinking."""
        score = 50.0
        text_lower = text.lower()

        if any(word in text_lower for word in ["consider", "think", "approach", "design"]):
            score += 15
        if "alternative" in text_lower or "option" in text_lower:
            score += 10

        return min(100.0, max(0.0, score))

    def _generate_design_thinking_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for design thinking."""
        evidence = []
        text_lower = text.lower()

        if "consider" in text_lower or "think" in text_lower:
            evidence.append(
                Evidence(
                    type=EvidenceType.ARCHITECTURE,
                    description="Shows thoughtful design consideration",
                    source="content_analysis",
                    weight=0.6,
                )
            )

        return evidence

    def _explain_design_thinking(self, score: float) -> str:
        """Explain design thinking score."""
        if score >= 70:
            return "Demonstrates strong design thinking"
        elif score >= 50:
            return "Shows good design awareness"
        else:
            return "Design thinking could be more explicit"

    def _analyze_documentation(self, text: str) -> float:
        """Analyze documentation quality."""
        score = 40.0
        text_lower = text.lower()

        comment_ratio = text.count("#") + text.count("//") + text.count("/*")
        if comment_ratio > len(text) / 50:
            score += 20

        if '"""' in text or "'''" in text:  # Docstrings
            score += 15

        return min(100.0, max(0.0, score))

    def _generate_documentation_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for documentation."""
        evidence = []

        if '"""' in text or "'''" in text:
            evidence.append(
                Evidence(
                    type=EvidenceType.DOCUMENTATION,
                    description="Docstrings present in code",
                    source="code_analysis",
                    weight=0.7,
                )
            )

        return evidence

    def _explain_documentation(self, score: float) -> str:
        """Explain documentation score."""
        if score >= 70:
            return "Good documentation practices demonstrated"
        elif score >= 50:
            return "Some documentation present"
        else:
            return "Documentation could be improved"

    def _analyze_readability(self, text: str) -> float:
        """Analyze code readability."""
        score = 60.0

        lines = text.split("\n")
        meaningful_names = sum(
            1
            for line in lines
            if any(word in line.lower() for word in ["name", "value", "result", "data", "item"])
        )
        if meaningful_names > len(lines) / 10:
            score += 15

        return min(100.0, max(0.0, score))

    def _generate_readability_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for readability."""
        return [
            Evidence(
                type=EvidenceType.CODE_QUALITY,
                description="Code structure analyzed for readability",
                source="code_analysis",
                weight=0.6,
            )
        ]

    def _explain_readability(self, score: float) -> str:
        """Explain readability score."""
        if score >= 70:
            return "Code is readable and well-structured"
        elif score >= 55:
            return "Code readability is acceptable"
        else:
            return "Code readability could be improved"

    def _analyze_analytical_thinking(self, text: str) -> float:
        """Analyze analytical thinking."""
        score = 50.0
        text_lower = text.lower()

        if any(word in text_lower for word in ["analyze", "analysis", "break", "down", "step"]):
            score += 15
        if "logic" in text_lower or "reasoning" in text_lower:
            score += 10

        return min(100.0, max(0.0, score))

    def _generate_analytical_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for analytical thinking."""
        evidence = []
        text_lower = text.lower()

        if "analyze" in text_lower or "break" in text_lower:
            evidence.append(
                Evidence(
                    type=EvidenceType.CODE_QUALITY,
                    description="Shows analytical approach",
                    source="content_analysis",
                    weight=0.6,
                )
            )

        return evidence

    def _explain_analytical_thinking(self, score: float) -> str:
        """Explain analytical thinking score."""
        if score >= 70:
            return "Strong analytical thinking demonstrated"
        elif score >= 50:
            return "Good analytical approach"
        else:
            return "Analytical thinking could be more explicit"
