"""
Generic Setup Wizard

A generic setup wizard that works for any repository.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

from shared_ai_utils.onboarding.setup_wizards.base import (
    BaseSetupWizard,
    SetupResult,
    SetupStep,
)


class GenericSetupWizard(BaseSetupWizard):
    """Generic setup wizard for any repository."""

    async def get_setup_steps(self) -> list[SetupStep]:
        """Get generic setup steps."""
        return [
            SetupStep(
                name="Check Python Version",
                description="Verify Python 3.9+ is installed",
                required=True,
            ),
            SetupStep(
                name="Check Dependencies",
                description="Verify required packages are available",
                required=True,
            ),
            SetupStep(
                name="Create Configuration",
                description="Set up configuration files",
                required=False,
            ),
            SetupStep(
                name="Verify Installation",
                description="Test that the tool works",
                required=False,
            ),
        ]

    async def _execute_step(
        self, step: SetupStep, repo_path: Optional[Path]
    ) -> bool:
        """Execute a generic setup step."""
        if step.name == "Check Python Version":
            return await self._check_python_version()
        elif step.name == "Check Dependencies":
            return await self._check_dependencies()
        elif step.name == "Create Configuration":
            return await self._create_configuration(repo_path)
        elif step.name == "Verify Installation":
            return await self._verify_installation()
        else:
            return False

    async def _check_python_version(self) -> bool:
        """Check Python version."""
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            self.console.print(f"[green]✓[/green] Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.console.print(
                f"[red]✗[/red] Python {version.major}.{version.minor} (requires 3.9+)"
            )
            return False

    async def _check_dependencies(self) -> bool:
        """Check if basic dependencies are installed."""
        missing = []

        try:
            import click
        except ImportError:
            missing.append("click")

        try:
            import rich
        except ImportError:
            missing.append("rich")

        if missing:
            self.console.print(f"[yellow]Missing dependencies: {', '.join(missing)}[/yellow]")
            if Confirm.ask("Install missing dependencies?", default=True):
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install"] + missing,
                        check=True,
                    )
                    self.console.print("[green]✓[/green] Dependencies installed")
                    return True
                except subprocess.CalledProcessError:
                    self.console.print("[red]✗[/red] Failed to install dependencies")
                    return False
            else:
                return False

        self.console.print("[green]✓[/green] All dependencies available")
        return True

    async def _create_configuration(self, repo_path: Optional[Path]) -> bool:
        """Create configuration files."""
        if not repo_path:
            return True  # Skip if no repo path

        env_file = repo_path / ".env"
        env_example = repo_path / ".env.example"

        if env_file.exists():
            self.console.print("[green]✓[/green] .env file already exists")
            return True

        if env_example.exists():
            if Confirm.ask("Create .env file from .env.example?", default=True):
                try:
                    import shutil

                    shutil.copy(env_example, env_file)
                    self.console.print("[green]✓[/green] Created .env file")
                    self.console.print("[yellow]⚠[/yellow] Remember to configure your .env file")
                    return True
                except Exception as e:
                    self.console.print(f"[red]✗[/red] Failed to create .env: {e}")
                    return False
            else:
                return True  # User skipped
        else:
            self.console.print("[dim]No .env.example found, skipping[/dim]")
            return True

    async def _verify_installation(self) -> bool:
        """Verify installation works."""
        # Generic verification - just check imports
        try:
            import click
            import rich
            self.console.print("[green]✓[/green] Basic installation verified")
            return True
        except ImportError as e:
            self.console.print(f"[red]✗[/red] Verification failed: {e}")
            return False
