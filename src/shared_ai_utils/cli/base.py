"""
Base CLI Utilities

Common CLI patterns and helpers with standardized command structure.
"""

import click
from typing import Any, Callable, Dict, List, Optional


class BaseCLI:
    """Base class for CLI applications with standardized command patterns."""

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
        func: Callable,
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

    # Standardized command patterns

    def add_list_command(
        self,
        group: click.Group,
        name: str,
        list_func: Callable[[], List[Dict[str, Any]]],
        display_func: Optional[Callable[[Dict[str, Any]], str]] = None,
    ) -> None:
        """Add a standardized 'list' command.

        Args:
            group: Click group to add command to
            name: Resource name (e.g., 'sensors', 'patterns')
            list_func: Function that returns list of items
            display_func: Optional function to format each item for display
        """
        @group.command(name=f"list-{name}")
        @click.option("--format", type=click.Choice(["table", "json"]), default="table")
        def list_cmd(format: str):
            """List all {name}."""
            items = list_func()
            if format == "json":
                import json
                click.echo(json.dumps(items, indent=2))
            else:
                from shared_ai_utils.cli import print_table
                if display_func:
                    formatted = [display_func(item) for item in items]
                    print_table(formatted, title=name.title())
                else:
                    print_table(items, title=name.title())

    def add_show_command(
        self,
        group: click.Group,
        name: str,
        show_func: Callable[[str], Dict[str, Any]],
    ) -> None:
        """Add a standardized 'show' command.

        Args:
            group: Click group to add command to
            name: Resource name
            show_func: Function that takes ID and returns item details
        """
        @group.command(name=f"show-{name}")
        @click.argument("id")
        @click.option("--format", type=click.Choice(["table", "json"]), default="table")
        def show_cmd(id: str, format: str):
            """Show details for a specific {name}."""
            item = show_func(id)
            if format == "json":
                import json
                click.echo(json.dumps(item, indent=2))
            else:
                from shared_ai_utils.cli import print_table
                print_table([item], title=f"{name.title()} Details")

    def add_create_command(
        self,
        group: click.Group,
        name: str,
        create_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        required_fields: List[str],
    ) -> None:
        """Add a standardized 'create' command.

        Args:
            group: Click group to add command to
            name: Resource name
            create_func: Function that creates the resource
            required_fields: List of required field names
        """
        @group.command(name=f"create-{name}")
        def create_cmd(**kwargs):
            """Create a new {name}."""
            # Filter to only include required fields
            data = {k: v for k, v in kwargs.items() if k in required_fields and v is not None}
            result = create_func(data)
            from shared_ai_utils.cli import print_success
            print_success(f"Created {name}: {result.get('id', 'unknown')}")

    def add_update_command(
        self,
        group: click.Group,
        name: str,
        update_func: Callable[[str, Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Add a standardized 'update' command.

        Args:
            group: Click group to add command to
            name: Resource name
            update_func: Function that updates the resource
        """
        @group.command(name=f"update-{name}")
        @click.argument("id")
        def update_cmd(id: str, **kwargs):
            """Update a {name}."""
            data = {k: v for k, v in kwargs.items() if v is not None}
            result = update_func(id, data)
            from shared_ai_utils.cli import print_success
            print_success(f"Updated {name}: {id}")

    def add_delete_command(
        self,
        group: click.Group,
        name: str,
        delete_func: Callable[[str], bool],
    ) -> None:
        """Add a standardized 'delete' command.

        Args:
            group: Click group to add command to
            name: Resource name
            delete_func: Function that deletes the resource
        """
        @group.command(name=f"delete-{name}")
        @click.argument("id")
        @click.confirmation_option(prompt=f"Are you sure you want to delete {name}?")
        def delete_cmd(id: str):
            """Delete a {name}."""
            success = delete_func(id)
            if success:
                from shared_ai_utils.cli import print_success
                print_success(f"Deleted {name}: {id}")
            else:
                from shared_ai_utils.cli import print_error
                print_error(f"Failed to delete {name}: {id}")
