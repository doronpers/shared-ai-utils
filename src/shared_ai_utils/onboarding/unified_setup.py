"""
Unified Onboarding System

Main orchestrator for unified onboarding across all Sonotheia ecosystem repositories.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from shared_ai_utils.onboarding.intent_detector import IntentDetector, IntentResult
from shared_ai_utils.onboarding.setup_wizards.base import BaseSetupWizard, get_wizard_for_repo
from shared_ai_utils.onboarding.verification import SetupVerifier, VerificationResult


class UnifiedOnboarding:
    """Unified onboarding for Sonotheia ecosystem."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize unified onboarding.

        Args:
            console: Optional Rich console for output
        """
        self.console = console or Console()
        self.intent_detector = IntentDetector(console=self.console)
        self.verifier = SetupVerifier(console=self.console)
        self.progress_file = Path.home() / ".sonotheia" / "onboarding_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

    async def run(
        self,
        repo: Optional[str] = None,
        skip_questions: bool = False,
        repo_path: Optional[Path] = None,
    ) -> Dict:
        """Run unified onboarding flow.

        Args:
            repo: Optional repository name to skip intent detection
            skip_questions: Skip interactive questions
            repo_path: Optional path to repository

        Returns:
            Dictionary with onboarding results
        """
        # 1. Welcome
        self._show_welcome()

        # 2. Detect intent (if repo not specified)
        if not repo:
            intent_result = await self.intent_detector.detect_intent(
                skip_questions=skip_questions
            )

            if not intent_result.recommended_repos:
                self.console.print("[yellow]No repositories recommended. Exiting.[/yellow]")
                return {"success": False, "reason": "No recommendations"}

            # Show recommendations
            self._show_recommendations(intent_result)

            # Let user choose
            if len(intent_result.recommended_repos) == 1:
                repo = intent_result.recommended_repos[0]
                self.console.print(f"\n[green]Selected: {repo}[/green]")
            else:
                repo = self._select_repo(intent_result.recommended_repos)
        else:
            intent_result = None

        if not repo:
            self.console.print("[yellow]No repository selected. Exiting.[/yellow]")
            return {"success": False, "reason": "No selection"}

        # 3. Run setup wizard
        wizard = get_wizard_for_repo(repo)
        setup_result = await wizard.run(repo_path=repo_path)

        if not setup_result.success:
            self.console.print("\n[red]Setup incomplete. Please fix the errors above.[/red]")
            return {
                "success": False,
                "repo": repo,
                "setup_result": setup_result,
            }

        # 4. Verify setup
        verification = await self.verifier.verify_repo(repo, repo_path=repo_path)
        self.verifier.display_results(verification)

        # 5. Show next steps
        self._show_next_steps(repo, setup_result, verification)

        # Save progress
        self._save_progress(repo, setup_result, verification)

        return {
            "success": True,
            "repo": repo,
            "intent": intent_result,
            "setup_result": setup_result,
            "verification": verification,
        }

    def _show_welcome(self) -> None:
        """Show welcome message."""
        welcome_text = """
[bold]Welcome to the Sonotheia Ecosystem![/bold]

This onboarding system will help you:
  • Find the right tool for your needs
  • Set up your chosen repository
  • Verify everything works correctly

Let's get started!
        """
        panel = Panel(welcome_text.strip(), border_style="cyan", title="🎉 Welcome")
        self.console.print(panel)

    def _show_recommendations(self, intent_result: IntentResult) -> None:
        """Show recommended repositories.

        Args:
            intent_result: Intent detection result
        """
        self.console.print("\n[bold]Recommended Tools:[/bold]\n")
        self.console.print(intent_result.reasoning)
        self.console.print(f"\n[dim]Confidence: {intent_result.confidence:.0%}[/dim]")

    def _select_repo(self, recommended_repos: List[str]) -> Optional[str]:
        """Let user select a repository.

        Args:
            recommended_repos: List of recommended repository names

        Returns:
            Selected repository name or None
        """
        self.console.print("\n[bold]Select a repository to set up:[/bold]\n")

        repo_descriptions = {
            "sono-platform": "Voice authentication and deepfake detection",
            "sono-eval": "Code assessment and developer evaluation",
            "feedback-loop": "Pattern learning and code quality",
            "council-ai": "AI advisory and decision-making",
            "sonotheia-examples": "Integration examples and evaluation",
            "shared-ai-utils": "Shared utilities library",
        }

        for i, repo in enumerate(recommended_repos, 1):
            desc = repo_descriptions.get(repo, "Tool in the ecosystem")
            self.console.print(f"  {i}. [cyan]{repo}[/cyan] - {desc}")

        while True:
            try:
                choice = Prompt.ask(
                    "\nEnter your choice",
                    choices=[str(i) for i in range(1, len(recommended_repos) + 1)],
                    default="1",
                )
                return recommended_repos[int(choice) - 1]
            except KeyboardInterrupt:
                return None

    def _show_next_steps(
        self,
        repo: str,
        setup_result,
        verification: VerificationResult,
    ) -> None:
        """Show next steps after onboarding.

        Args:
            repo: Repository name
            setup_result: Setup wizard result
            verification: Verification result
        """
        self.console.print("\n[bold green]🎉 Onboarding Complete![/bold green]\n")

        # Show quick start commands
        quick_start = {
            "sono-eval": "sono-eval assess run --help",
            "feedback-loop": "feedback-loop --help",
            "council-ai": "council consult --help",
            "sono-platform": "See documentation for getting started",
            "sonotheia-examples": "See examples/README.md",
            "shared-ai-utils": "See README.md for usage examples",
        }

        command = quick_start.get(repo, "See repository README")
        self.console.print(f"[bold]Next Steps:[/bold]")
        self.console.print(f"  1. Try the tool: [cyan]{command}[/cyan]")
        self.console.print(f"  2. Read the documentation in the {repo} repository")
        self.console.print(f"  3. Explore examples and tutorials")

        if verification.overall_status != "pass":
            self.console.print(
                f"\n[yellow]⚠ Note: Some verification checks had warnings.[/yellow]"
            )
            self.console.print("You can address these later if needed.")

    def _save_progress(
        self, repo: str, setup_result, verification: VerificationResult
    ) -> None:
        """Save onboarding progress.

        Args:
            repo: Repository name
            setup_result: Setup wizard result
            verification: Verification result
        """
        progress = {
            "repo": repo,
            "completed": setup_result.success,
            "steps_completed": setup_result.steps_completed,
            "verification_status": verification.overall_status,
            "timestamp": str(Path(__file__).stat().st_mtime),  # Simple timestamp
        }

        try:
            with open(self.progress_file, "w") as f:
                json.dump(progress, f, indent=2)
        except Exception:
            pass  # Don't fail if we can't save progress
