"""Pattern checks for code quality assessment.

This module provides pattern violation detection based on feedback-loop patterns
and best practices for AI-assisted development.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class PatternViolation:
    """Structured pattern violation record."""

    pattern: str
    line: int
    code: str
    description: str
    severity: str
    confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Serialize violation to a dictionary for metadata."""
        return {
            "pattern": self.pattern,
            "line": self.line,
            "code": self.code,
            "description": self.description,
            "severity": self.severity,
            "confidence": self.confidence,
        }


PatternRule = Dict[str, str]


# Default pattern rules based on feedback-loop's 9 core patterns
DEFAULT_PATTERN_RULES: Dict[str, PatternRule] = {
    "numpy_json_serialization": {
        "regex": r"json\.dumps\([^)]*np\.|json\.dumps\([^)]*numpy",
        "description": "NumPy types in JSON serialization (use .item() or .tolist())",
        "severity": "high",
    },
    "numpy_nan_inf": {
        "regex": r"np\.(isnan|isinf)\([^)]*\)\s*(?!if|and|or)",
        "description": "NumPy NaN/Inf not checked before JSON serialization",
        "severity": "high",
    },
    "bounds_checking": {
        "regex": r"\w+\[0\](?!\s+if\s+\w+)",
        "description": "List access without bounds checking",
        "severity": "medium",
    },
    "specific_exceptions": {
        "regex": r"except\s*:",
        "description": "Bare except clause (should catch specific exceptions)",
        "severity": "medium",
    },
    "structured_logging": {
        "regex": r"\bprint\s*\(",
        "description": "Using print instead of logging",
        "severity": "low",
    },
    "temp_file_handling": {
        "regex": r"tempfile\.mktemp\(",
        "description": "Using deprecated mktemp function (use mkstemp or NamedTemporaryFile)",
        "severity": "high",
    },
    "large_file_loading": {
        "regex": r"\.read\(\)(?!\s*#\s*chunk)",
        "description": "Loading entire file into memory (consider streaming for large files)",
        "severity": "low",
    },
    "fastapi_streaming": {
        "regex": r"await\s+\w+\.read\(\)(?!\s*#\s*chunk)",
        "description": "FastAPI upload loaded entirely into memory (consider streaming)",
        "severity": "medium",
    },
    "metadata_logic": {
        "regex": r"if\s+['\"].*['\"]\s+in\s+\w+\.lower\(\)",
        "description": "String matching for business logic (consider metadata-based approach)",
        "severity": "low",
    },
}


def detect_pattern_violations(
    code: str, rules: Optional[Dict[str, PatternRule]] = None
) -> List[PatternViolation]:
    """Detect pattern violations in code using regex rules.

    Args:
        code: The code to analyze
        rules: Optional custom rules (defaults to DEFAULT_PATTERN_RULES)

    Returns:
        List of pattern violations found
    """
    rules = rules or DEFAULT_PATTERN_RULES
    violations: List[PatternViolation] = []

    for line_num, line in enumerate(code.split("\n"), 1):
        for pattern_name, pattern_info in rules.items():
            if re.search(pattern_info["regex"], line):
                violations.append(
                    PatternViolation(
                        pattern=pattern_name,
                        line=line_num,
                        code=line.strip(),
                        description=pattern_info["description"],
                        severity=pattern_info["severity"],
                        confidence=0.8,
                    )
                )

    return violations


def calculate_pattern_penalty(
    violations: Iterable[PatternViolation],
    severity_weights: Dict[str, float],
    max_penalty: float,
) -> float:
    """Calculate a capped penalty score based on unique pattern violations.

    Args:
        violations: Iterable of pattern violations
        severity_weights: Dictionary mapping severity to penalty weight
        max_penalty: Maximum penalty that can be applied

    Returns:
        Calculated penalty score (capped at max_penalty)
    """
    total_penalty = 0.0
    seen: set[str] = set()

    for violation in violations:
        if violation.pattern in seen:
            continue
        seen.add(violation.pattern)
        total_penalty += severity_weights.get(violation.severity, 0.0)

    return min(total_penalty, max_penalty)


def violations_to_metadata(violations: List[PatternViolation]) -> List[Dict[str, Any]]:
    """Convert violations to metadata format for storage.

    Args:
        violations: List of pattern violations

    Returns:
        List of violation dictionaries
    """
    return [v.to_dict() for v in violations]
