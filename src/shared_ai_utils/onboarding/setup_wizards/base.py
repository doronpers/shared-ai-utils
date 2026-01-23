"""
Base Setup Wizard

Abstract base class for repository-specific setup wizards.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console

from shared_ai_utils.cli import print_info, print_success, print_warning


@dataclass
class SetupStep:
    """A single setup step."""

    name: str
    description: str
    required: bool = True
    completed: bool = False
    error: Optional[str] = None


@dataclass
class SetupResult:
    """Result of setup wizard execution."""

    success: bool
    steps_completed: List[str]
    steps_failed: List[str]
    errors: List[str]
    next_steps: List[str]


class BaseSetupWizard(ABC):
    """Base class for repository-specific setup wizards."""

    def __init__(self, repo_name: str, console: Optional[Console] = None):
        """Initialize setup wizard.

        Args:
            repo_name: Name of repository
            console: Optional Rich console for output
        """
        self.repo_name = repo_name
        self.console = console or Console()
        self.steps: List[SetupStep] = []

    @abstractmethod
    def get_setup_steps(self) -> List[SetupStep]:
        """Get list of setup steps for this repository.

        Returns:
            List of SetupStep objects
        """
        pass

    async def run(self, repo_path: Optional[Path] = None) -> SetupResult:
        """Run the setup wizard.

        Args:
            repo_path: Optional path to repository

        Returns:
            SetupResult with completion status
        """
        self.steps = self.get_setup_steps()

        self._show_welcome()

        completed_steps: List[str] = []
        failed_steps: List[str] = []
        errors: List[str] = []

        for step in self.steps:
            self.console.print(f"\n[bold cyan]Step: {step.name}[/bold cyan]")
            self.console.print(f"[dim]{step.description}[/dim]\n")

            try:
                success = await self._execute_step(step, repo_path)
                if success:
                    step.completed = True
                    completed_steps.append(step.name)
                    print_success(f"✓ {step.name} completed")
                else:
                    step.error = "Step execution failed"
                    if step.required:
                        failed_steps.append(step.name)
                        errors.append(f"{step.name}: {step.error}")
                        print_warning(f"⚠ {step.name} failed (required)")
                        break  # Stop on first required failure
                    else:
                        print_warning(f"⚠ {step.name} skipped (optional)")
            except Exception as e:
                step.error = str(e)
                if step.required:
                    failed_steps.append(step.name)
                    errors.append(f"{step.name}: {e}")
                    print_warning(f"✗ {step.name} failed: {e}")
                    break
                else:
                    print_warning(f"⚠ {step.name} failed (optional): {e}")

        # Generate next steps
        next_steps = self._generate_next_steps(completed_steps, failed_steps)

        success = len(failed_steps) == 0

        return SetupResult(
            success=success,
            steps_completed=completed_steps,
            steps_failed=failed_steps,
            errors=errors,
            next_steps=next_steps,
        )

    @abstractmethod
    async def _execute_step(self, step: SetupStep, repo_path: Optional[Path]) -> bool:
        """Execute a single setup step.

        Args:
            step: Setup step to execute
            repo_path: Optional path to repository

        Returns:
            True if step completed successfully, False otherwise
        """
        pass

    def _show_welcome(self) -> None:
        """Show welcome message."""
        from rich.panel import Panel

        welcome_text = f"""
[bold]Setting up {self.repo_name}[/bold]

This wizard will guide you through the setup process.
You can skip optional steps if needed.
        """
        panel = Panel(welcome_text.strip(), border_style="cyan", title="🚀 Setup Wizard")
        self.console.print(panel)

    def _generate_next_steps(
        self, completed: List[str], failed: List[str]
    ) -> List[str]:
        """Generate next steps based on setup results.

        Args:
            completed: List of completed step names
            failed: List of failed step names

        Returns:
            List of next step messages
        """
        next_steps: List[str] = []

        if not failed:
            next_steps.append(f"✅ {self.repo_name} setup complete!")
            next_steps.append("You can now start using the tool.")
        else:
            next_steps.append(f"⚠️ Setup incomplete. {len(failed)} step(s) failed.")
            next_steps.append("Please review the errors above and try again.")

        return next_steps


def get_wizard_for_repo(repo_name: str) -> BaseSetupWizard:
    """Get appropriate wizard for a repository.

    Args:
        repo_name: Name of repository

    Returns:
        BaseSetupWizard instance

    Raises:
        ValueError: If repo_name is not recognized
    """
    # For now, return a generic wizard
    # Repository-specific wizards can be added later
    from shared_ai_utils.onboarding.setup_wizards.generic import GenericSetupWizard

    return GenericSetupWizard(repo_name)
