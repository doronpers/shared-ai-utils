"""
Onboarding CLI Command

Unified onboarding command for the Sonotheia ecosystem.
"""

import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from shared_ai_utils.onboarding import UnifiedOnboarding


@click.command("onboard")
@click.option(
    "--repo",
    help="Skip questionnaire, setup specific repository",
    type=click.Choice(
        [
            "sono-platform",
            "sono-eval",
            "feedback-loop",
            "council-ai",
            "sonotheia-examples",
            "shared-ai-utils",
        ]
    ),
)
@click.option(
    "--repo-path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to repository (if not in current directory)",
)
@click.option(
    "--skip-questions",
    is_flag=True,
    help="Skip interactive questions (use defaults)",
)
def onboard(repo: Optional[str], repo_path: Optional[Path], skip_questions: bool):
    """🚀 Unified onboarding for Sonotheia ecosystem.

    This command guides you through:
      • Finding the right tool for your needs
      • Setting up your chosen repository
      • Verifying everything works correctly

    Examples:

      \b
      # Interactive onboarding
      shared-ai-utils onboard

      \b
      # Setup specific repository
      shared-ai-utils onboard --repo sono-eval

      \b
      # Setup with custom path
      shared-ai-utils onboard --repo feedback-loop --repo-path /path/to/repo
    """
    console = Console()

    try:
        onboarding = UnifiedOnboarding(console=console)
        result = asyncio.run(
            onboarding.run(
                repo=repo,
                skip_questions=skip_questions,
                repo_path=repo_path,
            )
        )

        if result.get("success"):
            console.print("\n[bold green]✅ Onboarding completed successfully![/bold green]")
            return 0
        else:
            console.print("\n[yellow]⚠️ Onboarding incomplete[/yellow]")
            return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Onboarding cancelled by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Error during onboarding: {e}[/red]")
        return 1
