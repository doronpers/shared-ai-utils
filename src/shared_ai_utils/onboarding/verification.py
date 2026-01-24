"""
Setup Verification System

Verifies that repository setup is complete and functional.
"""

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


@dataclass
class VerificationCheck:
    """A single verification check."""

    name: str
    status: str  # "pass", "fail", "warning", "skip"
    message: str
    suggestion: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of setup verification."""

    repo_name: str
    overall_status: str  # "pass", "fail", "partial"
    checks: List[VerificationCheck]
    next_steps: List[str]


class SetupVerifier:
    """Verify repository setup completion."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize verifier.

        Args:
            console: Optional Rich console for output
        """
        self.console = console or Console()

    async def verify_repo(
        self, repo_name: str, repo_path: Optional[Path] = None
    ) -> VerificationResult:
        """Verify setup for a repository.

        Args:
            repo_name: Name of repository
            repo_path: Optional path to repository

        Returns:
            VerificationResult with check results
        """
        checks: List[VerificationCheck] = []

        # Common checks
        checks.extend(await self._check_python_version())
        checks.extend(await self._check_dependencies(repo_name, repo_path))
        checks.extend(await self._check_configuration(repo_name, repo_path))

        # Repository-specific checks
        if repo_name == "sono-eval":
            checks.extend(await self._check_sono_eval(repo_path))
        elif repo_name == "feedback-loop":
            checks.extend(await self._check_feedback_loop(repo_path))
        elif repo_name == "council-ai":
            checks.extend(await self._check_council_ai(repo_path))
        elif repo_name == "sono-platform":
            checks.extend(await self._check_sono_platform(repo_path))

        # Determine overall status
        failed = [c for c in checks if c.status == "fail"]
        warnings = [c for c in checks if c.status == "warning"]

        if failed:
            overall_status = "fail"
        elif warnings:
            overall_status = "partial"
        else:
            overall_status = "pass"

        # Generate next steps
        next_steps = self._generate_next_steps(checks, overall_status)

        return VerificationResult(
            repo_name=repo_name,
            overall_status=overall_status,
            checks=checks,
            next_steps=next_steps,
        )

    async def _check_python_version(self) -> List[VerificationCheck]:
        """Check Python version."""
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            return [
                VerificationCheck(
                    name="Python Version",
                    status="pass",
                    message=f"Python {version.major}.{version.minor}.{version.micro}",
                )
            ]
        else:
            return [
                VerificationCheck(
                    name="Python Version",
                    status="fail",
                    message=f"Python {version.major}.{version.minor} (requires 3.9+)",
                    suggestion="Upgrade Python to 3.9 or higher",
                )
            ]

    async def _check_dependencies(
        self, repo_name: str, repo_path: Optional[Path]
    ) -> List[VerificationCheck]:
        """Check if dependencies are installed."""
        checks: List[VerificationCheck] = []

        # Try importing key packages
        try:
            import click
            checks.append(
                VerificationCheck(
                    name="Click (CLI framework)",
                    status="pass",
                    message="Installed",
                )
            )
        except ImportError:
            checks.append(
                VerificationCheck(
                    name="Click (CLI framework)",
                    status="fail",
                    message="Not installed",
                    suggestion="Run: pip install click",
                )
            )

        try:
            import rich
            checks.append(
                VerificationCheck(
                    name="Rich (terminal formatting)",
                    status="pass",
                    message="Installed",
                )
            )
        except ImportError:
            checks.append(
                VerificationCheck(
                    name="Rich (terminal formatting)",
                    status="fail",
                    message="Not installed",
                    suggestion="Run: pip install rich",
                )
            )

        return checks

    async def _check_configuration(
        self, repo_name: str, repo_path: Optional[Path]
    ) -> List[VerificationCheck]:
        """Check configuration files."""
        checks: List[VerificationCheck] = []

        if not repo_path:
            return checks

        # Check for .env file
        env_file = repo_path / ".env"
        if env_file.exists():
            checks.append(
                VerificationCheck(
                    name="Environment Configuration",
                    status="pass",
                    message=".env file found",
                )
            )
        else:
            env_example = repo_path / ".env.example"
            if env_example.exists():
                checks.append(
                    VerificationCheck(
                        name="Environment Configuration",
                        status="warning",
                        message=".env file not found",
                        suggestion=f"Copy {env_example} to .env and configure",
                    )
                )

        return checks

    async def _check_sono_eval(
        self, repo_path: Optional[Path]
    ) -> List[VerificationCheck]:
        """Check sono-eval specific setup."""
        checks: List[VerificationCheck] = []

        # Check if Docker is available (for sono-eval)
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                checks.append(
                    VerificationCheck(
                        name="Docker",
                        status="pass",
                        message="Docker available",
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        name="Docker",
                        status="warning",
                        message="Docker not available",
                        suggestion="Install Docker for containerized deployment",
                    )
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks.append(
                VerificationCheck(
                    name="Docker",
                    status="warning",
                    message="Docker not found",
                    suggestion="Optional: Install Docker for easier deployment",
                )
            )

        return checks

    async def _check_feedback_loop(
        self, repo_path: Optional[Path]
    ) -> List[VerificationCheck]:
        """Check feedback-loop specific setup."""
        checks: List[VerificationCheck] = []

        # Check if feedback-loop CLI is available
        try:
            result = subprocess.run(
                ["feedback-loop", "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                checks.append(
                    VerificationCheck(
                        name="Feedback Loop CLI",
                        status="pass",
                        message="CLI installed and working",
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        name="Feedback Loop CLI",
                        status="warning",
                        message="CLI may not be properly installed",
                        suggestion="Run: pip install -e .",
                    )
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks.append(
                VerificationCheck(
                    name="Feedback Loop CLI",
                    status="warning",
                    message="CLI not in PATH",
                    suggestion="Install with: pip install -e .",
                )
            )

        return checks

    async def _check_council_ai(
        self, repo_path: Optional[Path]
    ) -> List[VerificationCheck]:
        """Check council-ai specific setup."""
        checks: List[VerificationCheck] = []

        # Check for API key configuration
        import os

        has_api_key = any(
            key in os.environ
            for key in [
                "ANTHROPIC_API_KEY",
                "OPENAI_API_KEY",
                "GEMINI_API_KEY",
            ]
        )

        if has_api_key:
            checks.append(
                VerificationCheck(
                    name="API Key Configuration",
                    status="pass",
                    message="API key found in environment",
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    name="API Key Configuration",
                    status="warning",
                    message="No API key found",
                    suggestion="Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or use LM Studio",
                )
            )

        return checks

    async def _check_sono_platform(
        self, repo_path: Optional[Path]
    ) -> List[VerificationCheck]:
        """Check sono-platform specific setup."""
        checks: List[VerificationCheck] = []

        # Check for Docker Compose (sono-platform uses it)
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                checks.append(
                    VerificationCheck(
                        name="Docker Compose",
                        status="pass",
                        message="Docker Compose available",
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        name="Docker Compose",
                        status="warning",
                        message="Docker Compose not available",
                        suggestion="Install Docker Compose for full platform setup",
                    )
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks.append(
                VerificationCheck(
                    name="Docker Compose",
                    status="warning",
                    message="Docker Compose not found",
                    suggestion="Optional: Install for containerized deployment",
                )
            )

        return checks

    def _generate_next_steps(
        self, checks: List[VerificationCheck], overall_status: str
    ) -> List[str]:
        """Generate next steps based on verification results.

        Args:
            checks: List of verification checks
            overall_status: Overall verification status

        Returns:
            List of next step messages
        """
        next_steps: List[str] = []

        if overall_status == "pass":
            next_steps.append("✅ Setup complete! You're ready to start using the tool.")
            next_steps.append("Run the tool's main command to get started.")
        elif overall_status == "partial":
            next_steps.append("⚠️ Setup mostly complete, but some optional items need attention.")
            failed_checks = [c for c in checks if c.status == "fail"]
            if failed_checks:
                next_steps.append(f"Fix {len(failed_checks)} critical issue(s) first.")
        else:
            next_steps.append("❌ Setup incomplete. Please address the issues above.")
            failed_checks = [c for c in checks if c.status == "fail"]
            if failed_checks:
                next_steps.append(f"Start with: {failed_checks[0].suggestion}")

        return next_steps

    def display_results(self, result: VerificationResult) -> None:
        """Display verification results.

        Args:
            result: Verification result to display
        """
        self.console.print(f"\n[bold]Verification Results for {result.repo_name}[/bold]\n")

        # Create results table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Message", style="white")
        table.add_column("Suggestion", style="dim")

        for check in result.checks:
            status_icon = {
                "pass": "[green]✓[/green]",
                "fail": "[red]✗[/red]",
                "warning": "[yellow]⚠[/yellow]",
                "skip": "[dim]-[/dim]",
            }.get(check.status, "")

            table.add_row(
                check.name,
                status_icon,
                check.message,
                check.suggestion or "",
            )

        self.console.print(table)

        # Show next steps
        if result.next_steps:
            self.console.print("\n[bold]Next Steps:[/bold]")
            for step in result.next_steps:
                self.console.print(f"  {step}")
