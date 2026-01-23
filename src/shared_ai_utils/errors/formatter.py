"""
Unified Error Formatter

Formats errors consistently across CLI, API, and web interfaces.
"""

from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel


class UnifiedErrorFormatter:
    """Formats errors for different output formats."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize formatter.

        Args:
            console: Optional Rich console for CLI formatting
        """
        self.console = console or Console()

    def format(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        format_type: str = "cli",
    ) -> Any:
        """Format error for different output types.

        Args:
            error_type: Type of error
            message: Error message
            context: Additional context
            format_type: Output format ("cli", "api", "web")

        Returns:
            Formatted error (string for CLI, dict for API/web)
        """
        if format_type == "cli":
            return self._format_cli(error_type, message, context)
        elif format_type == "api":
            return self._format_api(error_type, message, context)
        elif format_type == "web":
            return self._format_web(error_type, message, context)
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    def _format_cli(
        self, error_type: str, message: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Format error for CLI output.

        Args:
            error_type: Type of error
            message: Error message
            context: Additional context

        Returns:
            Formatted string
        """
        from rich.panel import Panel

        error_text = f"[red]{message}[/red]"

        if context:
            context_text = "\n".join(
                f"  • {k}: [cyan]{v}[/cyan]" for k, v in context.items()
            )
            error_text += f"\n\n[bold]Context:[/bold]\n{context_text}"

        panel = Panel(
            error_text,
            title=f"[bold red]❌ {error_type}[/bold red]",
            border_style="red",
        )

        return str(panel)

    def _format_api(
        self, error_type: str, message: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format error for API response.

        Args:
            error_type: Type of error
            message: Error message
            context: Additional context

        Returns:
            Dictionary for JSON response
        """
        response: Dict[str, Any] = {
            "error": True,
            "error_type": error_type,
            "message": message,
        }

        if context:
            response["context"] = context

        return response

    def _format_web(
        self, error_type: str, message: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format error for web UI.

        Args:
            error_type: Type of error
            message: Error message
            context: Additional context

        Returns:
            Dictionary for web UI
        """
        return {
            "type": error_type,
            "message": message,
            "context": context or {},
            "severity": self._determine_severity(error_type),
        }

    def _determine_severity(self, error_type: str) -> str:
        """Determine error severity.

        Args:
            error_type: Type of error

        Returns:
            Severity level ("error", "warning", "info")
        """
        critical_errors = [
            "FileNotFoundError",
            "PermissionError",
            "ConnectionError",
            "ImportError",
        ]

        if error_type in critical_errors:
            return "error"
        elif "Warning" in error_type or "warning" in error_type.lower():
            return "warning"
        else:
            return "info"
