"""
Base CLI Utilities

Common CLI patterns and helpers.
"""

import click
from typing import Any, Dict, Optional


class BaseCLI:
    """Base class for CLI applications."""

    def __init__(self, name: str, version: str = "0.1.0"):
        """Initialize base CLI.

        Args:
            name: Application name
            version: Application version
        """
        self.name = name
        self.version = version

    def create_group(self, help_text: str = "") -> click.Group:
        """Create a Click group.

        Args:
            help_text: Help text for the group

        Returns:
            Click group
        """
        @click.group()
        @click.version_option(version=self.version, prog_name=self.name)
        def cli():
            """CLI group."""
            pass

        cli.help = help_text
        return cli

    def create_command(
        self,
        name: str,
        help_text: str,
        func: callable,
        options: Optional[Dict[str, Any]] = None,
    ) -> click.Command:
        """Create a Click command.

        Args:
            name: Command name
            help_text: Help text
            func: Command function
            options: Optional dictionary of options

        Returns:
            Click command
        """
        @click.command(name=name, help=help_text)
        def command(*args, **kwargs):
            return func(*args, **kwargs)

        # Add options if provided
        if options:
            for opt_name, opt_config in options.items():
                command = click.option(
                    f"--{opt_name}",
                    **opt_config
                )(command)

        return command
