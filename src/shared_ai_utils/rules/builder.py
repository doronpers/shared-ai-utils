"""
Rule Builder Module

Assembles monolithic AGENT_KNOWLEDGE_BASE.md from modular rule files.
"""

from pathlib import Path
from typing import List, Optional

# Standard header for the generated file
HEADER = """# Global Agent Knowledge Base & Instructional Set

This document is the **Single Source of Truth** for all AI agents (Claude, Cursor, Gemini, etc.) working on Sonotheia and related repositories. You MUST refer to this before and during your tasks.

> **License**: This document and the associated codebase are licensed under the [MIT License](LICENSE). When using or adapting code from this repository, include the original copyright notice. Third-party dependencies retain their original licenses.

> **NOTE**: This file is auto-generated from modular rules in `shared-ai-utils`. 
> DO NOT EDIT DIRECTLY. Update the source files in `shared-ai-utils/src/shared_ai_utils/rules/`.

---
"""


class RuleBuilder:
    """Builds the AGENT_KNOWLEDGE_BASE.md from modular rule files."""

    def __init__(self, rules_dir: Optional[str] = None):
        """Initialize RuleBuilder.

        Args:
            rules_dir: Path to rules directory. Defaults to current module path.
        """
        if rules_dir:
            self.rules_dir = Path(rules_dir)
        else:
            # Default to the directory where this file resides
            self.rules_dir = Path(__file__).parent

    def build(self) -> str:
        """Assemble all rule files into a single markdown string.

        Returns:
            The complete content of AGENT_KNOWLEDGE_BASE.md
        """
        content = [HEADER]
        
        # Define the order of sections explicitly to ensure consistency
        sections = [
            # Core Principles
            "core/00-prime-directives.md",
            "core/01-operational-guardrails.md",
            
            # Standards
            "standards/02-coding-standards.md",
            "guides/03-common-pitfalls.md",
            
            # Reference
            "guides/04-key-commands.md",
            "guides/05-key-paths.md",
            
            # Processes
            "standards/06-ai-assisted-development.md",
            "standards/07-documentation.md",
            "guides/08-reasoning-logs.md",
        ]

        for section_path in sections:
            full_path = self.rules_dir / section_path
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    file_content = f.read().strip()
                    content.append(file_content)
                    content.append("\n\n---\n")
            else:
                print(f"Warning: Rule file not found: {section_path}")

        return "\n".join(content)

    def write_to_file(self, output_path: str) -> None:
        """Write the built content to a file.

        Args:
            output_path: Destination path for the generated markdown file.
        """
        content = self.build()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully generated agent rules at: {output_path}")


if __name__ == "__main__":
    # Example usage when run directly
    builder = RuleBuilder()
    print(builder.build())
