"""
Interactive Wizards

Framework for creating interactive setup wizards and multi-step flows.
"""

from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


class WizardStep:
    """Represents a single step in a wizard."""

    def __init__(
        self,
        name: str,
        prompt: str,
        validator: Optional[Callable[[str], Any]] = None,
        default: Optional[str] = None,
        choices: Optional[List[str]] = None,
        password: bool = False,
    ):
        """Initialize wizard step.

        Args:
            name: Step identifier
            prompt: Prompt text
            validator: Optional validation function
            default: Default value
            choices: Optional list of choices
            password: Whether input should be hidden (password)
        """
        self.name = name
        self.prompt = prompt
        self.validator = validator
        self.default = default
        self.choices = choices
        self.password = password
        self.value: Optional[Any] = None

    def execute(self) -> Any:
        """Execute the step and get user input."""
        if self.choices:
            self.value = Prompt.ask(
                self.prompt, choices=self.choices, default=self.default
            )
        elif self.password:
            self.value = Prompt.ask(self.prompt, password=True)
        else:
            self.value = Prompt.ask(self.prompt, default=self.default)

        if self.validator:
            self.value = self.validator(self.value)

        return self.value


class Wizard:
    """Base class for interactive wizards."""

    def __init__(self, title: str, description: str = ""):
        """Initialize wizard.

        Args:
            title: Wizard title
            description: Wizard description
        """
        self.title = title
        self.description = description
        self.steps: List[WizardStep] = []
        self.results: Dict[str, Any] = {}

    def add_step(
        self,
        name: str,
        prompt: str,
        validator: Optional[Callable[[str], Any]] = None,
        default: Optional[str] = None,
        choices: Optional[List[str]] = None,
        password: bool = False,
    ) -> "Wizard":
        """Add a step to the wizard.

        Args:
            name: Step identifier
            prompt: Prompt text
            validator: Optional validation function
            default: Default value
            choices: Optional list of choices
            password: Whether input should be hidden

        Returns:
            Self for chaining
        """
        step = WizardStep(name, prompt, validator, default, choices, password)
        self.steps.append(step)
        return self

    def run(self) -> Dict[str, Any]:
        """Run the wizard and collect results.

        Returns:
            Dictionary of step name -> value
        """
        console.print(
            Panel(
                f"[bold]{self.title}[/bold]\n\n{self.description}",
                title="Wizard",
                border_style="blue",
            )
        )

        for step in self.steps:
            value = step.execute()
            self.results[step.name] = value

        return self.results


class SetupWizard(Wizard):
    """Setup wizard for first-time configuration."""

    def __init__(self):
        """Initialize setup wizard."""
        super().__init__(
            "Setup Wizard",
            "This wizard will help you configure the application.",
        )

    def add_provider_step(self, providers: List[str], default: str = "openai") -> "SetupWizard":
        """Add provider selection step."""
        self.add_step(
            "provider",
            "Which provider would you like to use?",
            choices=providers,
            default=default,
        )
        return self

    def add_api_key_step(self, provider: str) -> "SetupWizard":
        """Add API key configuration step."""
        console.print(f"\n[dim]You can get an API key from:[/dim]")
        if provider == "anthropic":
            console.print("  https://console.anthropic.com/")
        elif provider == "openai":
            console.print("  https://platform.openai.com/api-keys")
        elif provider == "gemini":
            console.print("  https://ai.google.dev/")

        if Confirm.ask("Do you have an API key to configure now?", default=True):
            self.add_step(
                f"{provider}_api_key",
                f"{provider.capitalize()} API key",
                password=True,
            )
        return self

    def add_confirmation_step(self) -> "SetupWizard":
        """Add final confirmation step."""
        self.add_step(
            "confirm",
            "Save this configuration?",
            validator=lambda x: Confirm.ask("Save configuration?", default=True),
        )
        return self
