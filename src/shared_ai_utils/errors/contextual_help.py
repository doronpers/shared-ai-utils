"""
Contextual Help System

Provides contextual help based on error and user context.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class HelpResponse:
    """Response with contextual help."""

    title: str
    description: str
    steps: List[str]
    examples: List[str]
    doc_links: List[str]
    related_errors: List[str]


class ContextualHelp:
    """Provide contextual help based on error and user context."""

    HELP_DATABASE: Dict[str, Dict[str, Any]] = {
        "ValidationError": {
            "title": "Validation Error Help",
            "description": "The input data doesn't match the expected format.",
            "steps": [
                "Check the field format",
                "Verify required fields are present",
                "Ensure data types match expectations",
            ],
            "examples": [
                '{"candidate_id": "user123", "content": {"code": "..."}}',
            ],
            "doc_links": ["/docs/validation", "/docs/api-reference"],
            "related_errors": ["ValueError", "TypeError"],
        },
        "FileNotFoundError": {
            "title": "File Not Found Help",
            "description": "The specified file or path doesn't exist.",
            "steps": [
                "Verify the file path is correct",
                "Check current working directory",
                "Use absolute path if relative path fails",
            ],
            "examples": [
                "ls -la path/to/file",
                "pwd  # Check current directory",
            ],
            "doc_links": ["/docs/file-paths", "/docs/troubleshooting"],
            "related_errors": ["PermissionError", "IsADirectoryError"],
        },
        "ImportError": {
            "title": "Import Error Help",
            "description": "A required package or module is not available.",
            "steps": [
                "Install the missing package",
                "Check virtual environment is activated",
                "Verify Python path includes the module",
            ],
            "examples": [
                "pip install <package>",
                "python -m pip install <package>",
            ],
            "doc_links": ["/docs/installation", "/docs/dependencies"],
            "related_errors": ["ModuleNotFoundError"],
        },
    }

    def __init__(self):
        """Initialize contextual help system."""
        pass

    def get_help(
        self, error_type: str, context: Optional[Dict[str, Any]] = None
    ) -> HelpResponse:
        """Get contextual help for an error.

        Args:
            error_type: Type of error
            context: Additional context

        Returns:
            HelpResponse with help information
        """
        help_data = self.HELP_DATABASE.get(error_type, {})

        if not help_data:
            # Generic help
            return HelpResponse(
                title="Error Help",
                description=f"Help for {error_type}",
                steps=[
                    "Review the error message",
                    "Check documentation",
                    "Search for similar issues",
                ],
                examples=[],
                doc_links=["/docs/troubleshooting"],
                related_errors=[],
            )

        # Customize based on context
        steps = help_data.get("steps", [])
        if context:
            steps = self._customize_steps(steps, context)

        return HelpResponse(
            title=help_data.get("title", "Help"),
            description=help_data.get("description", ""),
            steps=steps,
            examples=help_data.get("examples", []),
            doc_links=help_data.get("doc_links", []),
            related_errors=help_data.get("related_errors", []),
        )

    def _customize_steps(
        self, steps: List[str], context: Dict[str, Any]
    ) -> List[str]:
        """Customize help steps based on context.

        Args:
            steps: Base help steps
            context: User context

        Returns:
            Customized steps
        """
        customized = []

        for step in steps:
            # Replace placeholders
            if "<package>" in step and "package" in context:
                step = step.replace("<package>", context["package"])
            if "<path>" in step and "path" in context:
                step = step.replace("<path>", str(context["path"]))

            customized.append(step)

        return customized
