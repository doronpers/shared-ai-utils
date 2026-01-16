"""
Rich Terminal Utilities

Formatting utilities for rich terminal output.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

console = Console()


def print_table(
    data: List[Dict[str, Any]],
    title: Optional[str] = None,
    show_header: bool = True,
    header_style: str = "bold cyan",
) -> None:
    """Print data as a Rich table.

    Args:
        data: List of dictionaries to display
        title: Optional table title
        show_header: Show column headers
        header_style: Header style
    """
    if not data:
        console.print("[dim]No data to display[/dim]")
        return

    # Get column names from first row
    columns = list(data[0].keys())

    table = Table(show_header=show_header, title=title)
    for col in columns:
        table.add_column(col, header_style=header_style)

    for row in data:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    console.print(table)


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message in red."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_json(data: Any, indent: int = 2) -> None:
    """Print data as formatted JSON.

    Args:
        data: Data to print (will be converted to JSON)
        indent: JSON indentation
    """
    import json

    json_str = json.dumps(data, indent=indent, default=str)
    console.print(f"[dim]{json_str}[/dim]")


def format_score(score: float, thresholds: Optional[Dict[str, float]] = None) -> str:
    """Format score with color coding.

    Args:
        score: Score value (0-100)
        thresholds: Optional thresholds dict with 'good' and 'poor' keys

    Returns:
        Formatted score string with color
    """
    if thresholds is None:
        thresholds = {"good": 75.0, "poor": 60.0}

    if score >= thresholds.get("good", 75.0):
        color = "green"
    elif score >= thresholds.get("poor", 60.0):
        color = "yellow"
    else:
        color = "red"

    return f"[{color}]{score:.1f}[/{color}]"
