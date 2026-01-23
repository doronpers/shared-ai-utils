"""
Intent Detection System

Helps users determine which repository/tool best fits their needs through
interactive questioning.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from shared_ai_utils.cli import print_table, print_info


@dataclass
class IntentResult:
    """Result of intent detection."""

    recommended_repos: List[str]
    confidence: float
    reasoning: str


class IntentDetector:
    """Detect user intent and recommend appropriate tools."""

    QUESTIONS = [
        {
            "question": "What is your primary goal?",
            "options": [
                ("voice", "Voice authentication and deepfake detection"),
                ("assessment", "Code assessment and developer evaluation"),
                ("patterns", "Learn from code patterns and improve quality"),
                ("advisory", "AI advisory and multi-perspective decision-making"),
                ("integration", "Integrate voice detection into my application"),
            ],
            "recommendations": {
                "voice": ["sono-platform", "sonotheia-examples"],
                "assessment": ["sono-eval"],
                "patterns": ["feedback-loop"],
                "advisory": ["council-ai"],
                "integration": ["sonotheia-examples", "shared-ai-utils"],
            },
        },
        {
            "question": "What is your experience level?",
            "options": [
                ("beginner", "New to the ecosystem, need guidance"),
                ("intermediate", "Familiar with similar tools"),
                ("advanced", "Experienced developer, want full control"),
            ],
            "recommendations": {
                "beginner": ["sono-eval", "council-ai"],  # Easier onboarding
                "intermediate": ["feedback-loop", "sono-platform"],
                "advanced": ["sono-platform", "shared-ai-utils"],
            },
        },
        {
            "question": "What is your preferred interface?",
            "options": [
                ("cli", "Command-line interface"),
                ("web", "Web application"),
                ("api", "REST API integration"),
                ("library", "Python library/SDK"),
            ],
            "recommendations": {
                "cli": ["sono-eval", "feedback-loop", "council-ai"],
                "web": ["council-ai", "sono-platform"],
                "api": ["sono-eval", "sono-platform", "sonotheia-examples"],
                "library": ["shared-ai-utils"],
            },
        },
    ]

    def __init__(self, console: Optional[Console] = None):
        """Initialize intent detector.

        Args:
            console: Optional Rich console for output
        """
        self.console = console or Console()

    async def detect_intent(self, skip_questions: bool = False) -> IntentResult:
        """Detect user intent through interactive questions.

        Args:
            skip_questions: If True, return default recommendations

        Returns:
            IntentResult with recommended repositories
        """
        if skip_questions:
            return IntentResult(
                recommended_repos=["shared-ai-utils"],
                confidence=0.5,
                reasoning="Default recommendation (questions skipped)",
            )

        self._show_welcome()

        answers: Dict[str, str] = {}
        repo_scores: Dict[str, int] = {}

        # Ask questions
        for question_data in self.QUESTIONS:
            question = question_data["question"]
            options = question_data["options"]
            recommendations = question_data["recommendations"]

            # Display question
            self.console.print(f"\n[bold cyan]{question}[/bold cyan]\n")

            # Show options
            for i, (key, description) in enumerate(options, 1):
                self.console.print(f"  {i}. {description}")

            # Get answer
            while True:
                try:
                    choice = Prompt.ask(
                        "\nEnter your choice",
                        choices=[str(i) for i in range(1, len(options) + 1)],
                        default="1",
                    )
                    selected_key = options[int(choice) - 1][0]
                    answers[question] = selected_key

                    # Score repositories
                    for repo in recommendations.get(selected_key, []):
                        repo_scores[repo] = repo_scores.get(repo, 0) + 1

                    break
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Cancelled[/yellow]")
                    return IntentResult(
                        recommended_repos=[],
                        confidence=0.0,
                        reasoning="User cancelled",
                    )

        # Determine recommendations
        if not repo_scores:
            recommended_repos = ["shared-ai-utils"]
            confidence = 0.3
        else:
            # Sort by score
            sorted_repos = sorted(
                repo_scores.items(), key=lambda x: x[1], reverse=True
            )
            recommended_repos = [repo for repo, _ in sorted_repos[:3]]
            confidence = min(sorted_repos[0][1] / len(self.QUESTIONS), 1.0)

        reasoning = self._generate_reasoning(answers, recommended_repos)

        return IntentResult(
            recommended_repos=recommended_repos,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _show_welcome(self) -> None:
        """Show welcome message."""
        welcome_text = """
[bold]Welcome to the Sonotheia Ecosystem![/bold]

I'll ask you a few questions to help you find the right tool for your needs.
This will take less than a minute.
        """
        panel = Panel(welcome_text.strip(), border_style="cyan", title="🎯 Intent Detection")
        self.console.print(panel)

    def _generate_reasoning(
        self, answers: Dict[str, str], recommended_repos: List[str]
    ) -> str:
        """Generate human-readable reasoning for recommendations.

        Args:
            answers: User's answers to questions
            recommended_repos: Recommended repositories

        Returns:
            Reasoning text
        """
        if not recommended_repos:
            return "No specific recommendations based on your answers."

        repo_descriptions = {
            "sono-platform": "Voice authentication and deepfake detection platform",
            "sono-eval": "Code assessment and developer evaluation system",
            "feedback-loop": "Pattern learning and code quality improvement",
            "council-ai": "AI advisory council for multi-perspective decisions",
            "sonotheia-examples": "Integration examples and evaluation framework",
            "shared-ai-utils": "Shared utilities and components library",
        }

        descriptions = [
            f"• {repo}: {repo_descriptions.get(repo, 'Tool in the ecosystem')}"
            for repo in recommended_repos
        ]

        return "Based on your answers:\n" + "\n".join(descriptions)
