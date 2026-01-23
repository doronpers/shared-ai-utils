"""CLI extensions for domain-specific commands.

Provides standardized CLI extensions for:
- Assessment CLI (sono-eval)
- Sensor CLI (sono-platform)
- Pattern CLI (feedback-loop)
"""

import click
from typing import Any, Callable, Dict, List, Optional

from shared_ai_utils.cli.base import BaseCLI
from shared_ai_utils.cli.rich_utils import print_table, print_success


class AssessmentCLI(BaseCLI):
    """CLI extension for assessment operations (sono-eval)."""

    def __init__(self):
        """Initialize assessment CLI."""
        super().__init__("assessment", "1.0.0")

    def add_assess_command(
        self,
        group: click.Group,
        assess_func: Callable[[str, Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Add assessment command.

        Args:
            group: Click group
            assess_func: Function that performs assessment
        """
        @group.command("assess")
        @click.argument("candidate_id")
        @click.option("--file", type=click.Path(exists=True), help="File to assess")
        @click.option("--paths", multiple=True, help="Assessment paths to evaluate")
        @click.option("--format", type=click.Choice(["table", "json"]), default="table")
        def assess_cmd(candidate_id: str, file: Optional[str], paths: tuple, format: str):
            """Assess a candidate submission."""
            # Implementation would call assess_func
            pass


class SensorCLI(BaseCLI):
    """CLI extension for sensor operations (sono-platform)."""

    def __init__(self):
        """Initialize sensor CLI."""
        super().__init__("sensor", "1.0.0")

    def add_analyze_command(
        self,
        group: click.Group,
        analyze_func: Callable[[str, str], Dict[str, Any]],
    ) -> None:
        """Add sensor analysis command.

        Args:
            group: Click group
            analyze_func: Function that performs sensor analysis
        """
        @group.command("analyze")
        @click.argument("sensor_name")
        @click.argument("audio_file", type=click.Path(exists=True))
        @click.option("--format", type=click.Choice(["table", "json"]), default="table")
        def analyze_cmd(sensor_name: str, audio_file: str, format: str):
            """Analyze audio with a sensor."""
            # Implementation would call analyze_func
            pass


class PatternCLI(BaseCLI):
    """CLI extension for pattern operations (feedback-loop)."""

    def __init__(self):
        """Initialize pattern CLI."""
        super().__init__("pattern", "1.0.0")

    def add_check_command(
        self,
        group: click.Group,
        check_func: Callable[[str], List[Dict[str, Any]]],
    ) -> None:
        """Add pattern check command.

        Args:
            group: Click group
            check_func: Function that checks for pattern violations
        """
        @group.command("check")
        @click.argument("file", type=click.Path(exists=True))
        @click.option("--format", type=click.Choice(["table", "json"]), default="table")
        def check_cmd(file: str, format: str):
            """Check code for pattern violations."""
            violations = check_func(file)
            if format == "json":
                import json
                click.echo(json.dumps([v.to_dict() if hasattr(v, "to_dict") else v for v in violations], indent=2))
            else:
                print_table(violations, title="Pattern Violations")
