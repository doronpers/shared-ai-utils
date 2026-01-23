"""Heuristic-based scorer for assessment engine."""

import logging
from typing import Any, Dict, List, Optional

from shared_ai_utils.assessment.helpers import extract_text_content
from shared_ai_utils.assessment.models import (
    AssessmentInput,
    Evidence,
    EvidenceType,
    PathType,
    ScoringMetric,
)
from shared_ai_utils.assessment.pattern_checks import (
    PatternViolation,
    calculate_pattern_penalty,
)

logger = logging.getLogger(__name__)


class HeuristicScorerConfig:
    """Configuration for heuristic scorer."""

    def __init__(
        self,
        pattern_checks_enabled: bool = True,
        pattern_penalty_low: float = 1.0,
        pattern_penalty_medium: float = 3.0,
        pattern_penalty_high: float = 5.0,
        pattern_penalty_max: float = 15.0,
    ):
        self.pattern_checks_enabled = pattern_checks_enabled
        self.pattern_penalty_low = pattern_penalty_low
        self.pattern_penalty_medium = pattern_penalty_medium
        self.pattern_penalty_high = pattern_penalty_high
        self.pattern_penalty_max = pattern_penalty_max


class HeuristicScorer:
    """Handles heuristic-based scoring for different assessment paths."""

    def __init__(self, config: Optional[HeuristicScorerConfig] = None):
        """Initialize heuristic scorer.

        Args:
            config: Optional configuration (uses defaults if None)
        """
        self.config = config or HeuristicScorerConfig()
        self.pattern_penalty_weights = {
            "low": self.config.pattern_penalty_low,
            "medium": self.config.pattern_penalty_medium,
            "high": self.config.pattern_penalty_high,
            "critical": self.config.pattern_penalty_high,
        }
        self.pattern_penalty_max = self.config.pattern_penalty_max

    def generate_metrics_for_path(
        self,
        path: PathType,
        input_data: AssessmentInput,
        pattern_violations: Optional[List[PatternViolation]] = None,
    ) -> List[ScoringMetric]:
        """Generate scoring metrics for a specific path."""
        metrics = []
        content = input_data.content
        submission_text = extract_text_content(content)

        if path == PathType.TECHNICAL:
            metrics.extend(self._analyze_technical(submission_text, pattern_violations))
        elif path == PathType.DESIGN:
            metrics.extend(self._analyze_design(submission_text))
        elif path == PathType.COLLABORATION:
            metrics.extend(self._analyze_collaboration(submission_text, content))
        elif path == PathType.PROBLEM_SOLVING:
            metrics.extend(self._analyze_problem_solving_path(submission_text))

        return metrics

    def identify_micro_motives(
        self, path: PathType, input_data: AssessmentInput
    ) -> List:
        """HeuristicScorer doesn't identify micro-motives (use MicroMotiveScorer)."""
        return []

    def _analyze_technical(
        self, text: str, pattern_violations: Optional[List[PatternViolation]]
    ) -> List[ScoringMetric]:
        """Analyze technical path."""
        metrics = []

        # Code Quality
        code_score = self._analyze_code_quality(text, pattern_violations)
        code_evidence = self._generate_code_quality_evidence(text, pattern_violations)
        violation_count = len(pattern_violations or [])

        metrics.append(
            ScoringMetric(
                name="Code Quality",
                category="technical",
                score=code_score,
                weight=0.3,
                evidence=code_evidence,
                explanation=self._explain_code_quality(code_score, violation_count),
                confidence=0.85,
            )
        )

        # Problem Solving
        ps_score = self._analyze_problem_solving(text)
        metrics.append(
            ScoringMetric(
                name="Problem Solving",
                category="technical",
                score=ps_score,
                weight=0.3,
                evidence=self._generate_problem_solving_evidence(text),
                explanation=self._explain_problem_solving(ps_score),
                confidence=0.8,
            )
        )

        # Testing
        test_score = self._analyze_testing(text)
        metrics.append(
            ScoringMetric(
                name="Testing",
                category="technical",
                score=test_score,
                weight=0.2,
                evidence=self._generate_testing_evidence(text),
                explanation=self._explain_testing(test_score),
                confidence=0.75,
            )
        )

        return metrics

    def _analyze_design(self, text: str) -> List[ScoringMetric]:
        """Analyze design path."""
        metrics = []

        # Architecture
        arch_score = self._analyze_architecture(text)
        metrics.append(
            ScoringMetric(
                name="Architecture",
                category="design",
                score=arch_score,
                weight=0.4,
                evidence=self._generate_architecture_evidence(text),
                explanation=self._explain_architecture(arch_score),
                confidence=0.8,
            )
        )

        # Design Thinking
        dt_score = self._analyze_design_thinking(text)
        metrics.append(
            ScoringMetric(
                name="Design Thinking",
                category="design",
                score=dt_score,
                weight=0.3,
                evidence=self._generate_design_thinking_evidence(text),
                explanation=self._explain_design_thinking(dt_score),
                confidence=0.75,
            )
        )

        return metrics

    def _analyze_collaboration(self, text: str, content: Dict[str, Any]) -> List[ScoringMetric]:
        """Analyze collaboration path."""
        metrics = []

        # Documentation
        doc_score = self._analyze_documentation(text)
        metrics.append(
            ScoringMetric(
                name="Documentation",
                category="collaboration",
                score=doc_score,
                weight=0.3,
                evidence=self._generate_documentation_evidence(text),
                explanation=self._explain_documentation(doc_score),
                confidence=0.8,
            )
        )

        # Readability
        read_score = self._analyze_readability(text)
        metrics.append(
            ScoringMetric(
                name="Code Readability",
                category="collaboration",
                score=read_score,
                weight=0.35,
                evidence=self._generate_readability_evidence(text),
                explanation=self._explain_readability(read_score),
                confidence=0.85,
            )
        )

        return metrics

    def _analyze_problem_solving_path(self, text: str) -> List[ScoringMetric]:
        """Analyze problem solving path."""
        metrics = []

        # Analytical Thinking
        anal_score = self._analyze_analytical_thinking(text)
        metrics.append(
            ScoringMetric(
                name="Analytical Thinking",
                category="problem_solving",
                score=anal_score,
                weight=0.3,
                evidence=self._generate_analytical_evidence(text),
                explanation=self._explain_analytical_thinking(anal_score),
                confidence=0.8,
            )
        )

        return metrics

    # Analysis implementation methods

    def _analyze_code_quality(
        self, text: str, pattern_violations: Optional[List[PatternViolation]] = None
    ) -> float:
        """Analyze code quality with pattern violation penalties."""
        score = 50.0
        text_lower = text.lower()
        lines = text.split("\n")
        non_empty_lines = [
            line.strip() for line in lines if line.strip() and not line.strip().startswith("#")
        ]

        if "def " in text or "function " in text or "class " in text:
            score += 10
        if "import " in text or "from " in text:
            score += 5

        logic_density = len(non_empty_lines) / max(len(lines), 1)
        if logic_density > 0.7:
            score += 8
        elif logic_density > 0.5:
            score += 5

        if "try:" in text or "except" in text or "error" in text_lower:
            score += 10
        if "test" in text_lower or "assert" in text_lower:
            score += 10

        if text.count("print(") > 5:
            score -= 5
        if "todo" in text_lower or "fixme" in text_lower:
            score -= 3

        # Apply pattern violation penalty
        if pattern_violations and self.config.pattern_checks_enabled:
            score -= calculate_pattern_penalty(
                pattern_violations,
                self.pattern_penalty_weights,
                self.pattern_penalty_max,
            )

        return min(100.0, max(0.0, score))

    def _generate_code_quality_evidence(
        self, text: str, pattern_violations: Optional[List[PatternViolation]] = None
    ) -> List[Evidence]:
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
        if pattern_violations and self.config.pattern_checks_enabled:
            weights = {"critical": 1.0, "high": 0.9, "medium": 0.7, "low": 0.5}
            for violation in pattern_violations[:10]:
                evidence.append(
                    Evidence(
                        type=EvidenceType.CODE_QUALITY,
                        description=f"Pattern violation: {violation.pattern} - {violation.description}",
                        source="pattern_checks",
                        weight=weights.get(violation.severity, 0.6),
                        metadata=violation.to_dict(),
                    )
                )
        return evidence

    def _explain_code_quality(self, score: float, violation_count: int = 0) -> str:
        """Explain code quality score."""
        pattern_note = ""
        if violation_count > 0 and self.config.pattern_checks_enabled:
            pattern_note = (
                f" Pattern checks flagged {violation_count} potential issue"
                f"{'s' if violation_count != 1 else ''}."
            )
        if score >= 80:
            return "Code demonstrates strong quality with good structure and practices" + pattern_note
        elif score >= 60:
            return "Code shows solid fundamentals with room for improvement" + pattern_note
        else:
            return "Code quality could be enhanced with better structure and practices" + pattern_note

    def _analyze_problem_solving(self, text: str) -> float:
        """Analyze problem-solving approach."""
        score = 50.0
        text_lower = text.lower()
        if any(w in text_lower for w in ["algorithm", "complexity", "optimize", "efficient"]):
            score += 15
        if any(w in text_lower for w in ["loop", "iterate", "recursion"]):
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
        if "test" in text.lower():
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
        return "Architecture could be more structured"

    def _analyze_design_thinking(self, text: str) -> float:
        """Analyze design thinking."""
        score = 50.0
        text_lower = text.lower()
        if any(w in text_lower for w in ["consider", "think", "approach", "design"]):
            score += 15
        if "alternative" in text_lower or "option" in text_lower:
            score += 10
        return min(100.0, max(0.0, score))

    def _generate_design_thinking_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for design thinking."""
        evidence = []
        if "consider" in text.lower() or "think" in text.lower():
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
        return "Design thinking could be more explicit"

    def _analyze_documentation(self, text: str) -> float:
        """Analyze documentation quality."""
        score = 40.0
        comment_ratio = text.count("#") + text.count("//") + text.count("/*")
        if comment_ratio > len(text) / 50:
            score += 20
        if '"""' in text or "'''" in text:
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
        return "Documentation could be improved"

    def _analyze_readability(self, text: str) -> float:
        """Analyze code readability."""
        score = 60.0
        lines = text.split("\n")
        meaningful_names = sum(
            1
            for line in lines
            if any(w in line.lower() for w in ["name", "value", "result", "data", "item"])
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
        return "Code readability could be improved"

    def _analyze_analytical_thinking(self, text: str) -> float:
        """Analyze analytical thinking."""
        score = 50.0
        text_lower = text.lower()
        if any(w in text_lower for w in ["analyze", "analysis", "break", "down", "step"]):
            score += 15
        if "logic" in text_lower or "reasoning" in text_lower:
            score += 10
        return min(100.0, max(0.0, score))

    def _generate_analytical_evidence(self, text: str) -> List[Evidence]:
        """Generate evidence for analytical thinking."""
        evidence = []
        if "analyze" in text.lower() or "break" in text.lower():
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
        return "Analytical thinking could be more explicit"
