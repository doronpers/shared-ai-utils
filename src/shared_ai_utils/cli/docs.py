"""
Documentation Hub CLI Command

Unified documentation search and discovery.
"""

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from shared_ai_utils.docs import DocumentationHub


@click.command("docs")
@click.argument("query", required=False)
@click.option("--context", help="Current context (error, task, repo)")
@click.option("--format", type=click.Choice(["table", "json"]), default="table")
@click.option("--limit", default=10, help="Maximum number of results")
def docs(query: Optional[str], context: Optional[str], format: str, limit: int):
    """📚 Unified documentation hub.

    Search documentation across all Sonotheia ecosystem repositories.

    Examples:

      \b
      # Search documentation
      shared-ai-utils docs "error handling"

      \b
      # Search with context
      shared-ai-utils docs --context "error=ValidationError"

      \b
      # Get docs for specific repo
      shared-ai-utils docs --context "repo=sono-eval"

      \b
      # JSON output
      shared-ai-utils docs "quickstart" --format json
    """
    console = Console()

    try:
        hub = DocumentationHub()

        if query:
            # Parse context if provided
            context_dict = {}
            if context:
                # Simple parsing: key=value format
                if "=" in context:
                    key, value = context.split("=", 1)
                    context_dict[key] = value

            results = hub.search(query, context=context_dict if context_dict else None, limit=limit)

            if format == "json":
                output = json.dumps([r.to_dict() for r in results], indent=2)
                console.print(output)
            else:
                # Table format
                if results:
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Title", style="cyan")
                    table.add_column("Repo", style="yellow")
                    table.add_column("Path", style="dim")
                    table.add_column("Relevance", style="green")

                    for result in results:
                        table.add_row(
                            result.title[:50],
                            result.repo,
                            result.path[:40],
                            f"{result.relevance_score:.1f}",
                        )

                    console.print(table)
                    console.print(f"\n[dim]Found {len(results)} result(s)[/dim]")
                else:
                    console.print("[yellow]No documentation found[/yellow]")
                    console.print("[dim]Try a different search query[/dim]")

        else:
            # Show documentation index
            console.print("[bold]Documentation Hub[/bold]\n")
            console.print("Available repositories:")
            for repo_name, repo_path in hub.repo_paths.items():
                console.print(f"  • [cyan]{repo_name}[/cyan] - {repo_path}")

            console.print("\n[dim]Use 'docs <query>' to search documentation[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    return 0
