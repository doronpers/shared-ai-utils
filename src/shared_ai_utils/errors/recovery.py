"""
Error Recovery System

Generates actionable recovery steps for errors based on error type and context.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RecoveryStep:
    """A single recovery step."""

    description: str
    command: Optional[str] = None
    code_example: Optional[str] = None
    doc_link: Optional[str] = None
    verification: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "command": self.command,
            "code_example": self.code_example,
            "doc_link": self.doc_link,
            "verification": self.verification,
        }


class ErrorRecovery:
    """Generate recovery steps for errors."""

    RECOVERY_PATTERNS: Dict[str, List[RecoveryStep]] = {
        "ValidationError": [
            RecoveryStep(
                description="Check the field format and required fields",
                doc_link="/docs/validation",
            ),
            RecoveryStep(
                description="See example format",
                code_example='{"field": "example_value"}',
            ),
        ],
        "FileNotFoundError": [
            RecoveryStep(
                description="Verify file exists",
                command="ls -la <path>",
            ),
            RecoveryStep(
                description="Check current directory",
                command="pwd",
            ),
            RecoveryStep(
                description="Use absolute path or relative path from current directory",
            ),
        ],
        "PermissionError": [
            RecoveryStep(
                description="Check file permissions",
                command="ls -l <path>",
            ),
            RecoveryStep(
                description="Ensure you have read/write access",
            ),
            RecoveryStep(
                description="Try running with appropriate permissions",
            ),
        ],
        "ImportError": [
            RecoveryStep(
                description="Verify package is installed",
                command="pip list | grep <package>",
            ),
            RecoveryStep(
                description="Install missing package",
                command="pip install <package>",
            ),
            RecoveryStep(
                description="Check Python path and virtual environment",
            ),
        ],
        "ConnectionError": [
            RecoveryStep(
                description="Check network connectivity",
                command="ping <host>",
            ),
            RecoveryStep(
                description="Verify service is running",
            ),
            RecoveryStep(
                description="Check firewall and proxy settings",
            ),
        ],
        "TimeoutError": [
            RecoveryStep(
                description="Increase timeout value",
                code_example="timeout=60  # Increase from default",
            ),
            RecoveryStep(
                description="Check network connection",
            ),
            RecoveryStep(
                description="Verify service is responsive",
            ),
        ],
        "ValueError": [
            RecoveryStep(
                description="Check input value format",
            ),
            RecoveryStep(
                description="Verify value is within expected range",
            ),
            RecoveryStep(
                description="See documentation for valid values",
                doc_link="/docs/values",
            ),
        ],
        "KeyError": [
            RecoveryStep(
                description="Check that the key exists in the dictionary",
            ),
            RecoveryStep(
                description="Use .get() method with default value",
                code_example='value = data.get("key", "default")',
            ),
        ],
        "AttributeError": [
            RecoveryStep(
                description="Verify object has the attribute",
            ),
            RecoveryStep(
                description="Check object type and version",
            ),
            RecoveryStep(
                description="See API documentation for available attributes",
            ),
        ],
        "TypeError": [
            RecoveryStep(
                description="Check variable types match expected types",
            ),
            RecoveryStep(
                description="Add type conversion if needed",
                code_example="value = int(string_value)",
            ),
        ],
    }

    def __init__(self, error_type: str, context: Dict[str, Any]):
        """Initialize error recovery.

        Args:
            error_type: Type of error (exception class name)
            context: Additional context about the error
        """
        self.error_type = error_type
        self.context = context

    def get_steps(self) -> List[RecoveryStep]:
        """Get recovery steps for this error.

        Returns:
            List of RecoveryStep objects
        """
        # Get base steps for this error type
        steps = self.RECOVERY_PATTERNS.get(self.error_type, [])

        # Customize based on context
        steps = self._customize_steps(steps)

        # Add generic help if no specific steps
        if not steps:
            steps = [
                RecoveryStep(
                    description="Review error message for details",
                ),
                RecoveryStep(
                    description="Check documentation",
                    doc_link="/docs/troubleshooting",
                ),
                RecoveryStep(
                    description="Search for similar issues",
                ),
            ]

        return steps

    def _customize_steps(self, steps: List[RecoveryStep]) -> List[RecoveryStep]:
        """Customize steps based on context.

        Args:
            steps: Base recovery steps

        Returns:
            Customized recovery steps
        """
        customized = []

        for step in steps:
            # Replace placeholders in commands
            if step.command and "<path>" in step.command:
                path = self.context.get("path", "<path>")
                step = RecoveryStep(
                    description=step.description,
                    command=step.command.replace("<path>", str(path)),
                    code_example=step.code_example,
                    doc_link=step.doc_link,
                    verification=step.verification,
                )

            # Add context-specific suggestions
            if "file" in self.context:
                if "FileNotFoundError" in self.error_type:
                    customized.append(
                        RecoveryStep(
                            description=f"Verify file exists: {self.context['file']}",
                            command=f"ls -la {self.context['file']}",
                        )
                    )

            customized.append(step)

        return customized

    def format_cli(self) -> str:
        """Format recovery steps for CLI display.

        Returns:
            Formatted string
        """
        from rich.console import Console
        from rich.panel import Panel

        steps = self.get_steps()
        steps_text = "\n".join(
            f"{i+1}. {s.description}" for i, s in enumerate(steps)
        )

        console = Console()
        panel = Panel(steps_text, title="Recovery Steps", border_style="yellow")
        return str(panel)

    def get_suggestions(self) -> List[str]:
        """Get list of suggestion strings.

        Returns:
            List of suggestion strings
        """
        return [step.description for step in self.get_steps()]
