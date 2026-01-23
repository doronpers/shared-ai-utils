"""
Documentation Indexer

Indexes markdown documentation files from repositories.
"""

import re
from pathlib import Path
from typing import Dict, List


class DocIndexer:
    """Index documentation files."""

    DOC_PATTERNS = [
        "**/*.md",
        "**/README.md",
        "**/documentation/**/*.md",
        "**/docs/**/*.md",
    ]

    def index_repo(self, repo_path: Path, repo_name: str) -> List[Dict[str, str]]:
        """Index all documentation in a repository.

        Args:
            repo_path: Path to repository
            repo_name: Name of repository

        Returns:
            List of document metadata dictionaries
        """
        docs: List[Dict[str, str]] = []

        # Find all markdown files
        for pattern in self.DOC_PATTERNS:
            for doc_path in repo_path.glob(pattern):
                if doc_path.is_file():
                    doc_meta = self._index_file(doc_path, repo_path, repo_name)
                    if doc_meta:
                        docs.append(doc_meta)

        return docs

    def _index_file(
        self, doc_path: Path, repo_path: Path, repo_name: str
    ) -> Dict[str, str]:
        """Index a single documentation file.

        Args:
            doc_path: Path to documentation file
            repo_path: Repository root path
            repo_name: Repository name

        Returns:
            Document metadata dictionary
        """
        try:
            content = doc_path.read_text(encoding="utf-8")

            # Extract title (first # heading)
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else doc_path.stem

            # Extract excerpt (first paragraph or first 200 chars)
            excerpt = self._extract_excerpt(content)

            # Determine doc type
            doc_type = self._determine_doc_type(doc_path, content)

            # Relative path from repo root
            rel_path = doc_path.relative_to(repo_path)

            return {
                "title": title,
                "path": str(rel_path),
                "repo": repo_name,
                "content": content,
                "excerpt": excerpt,
                "type": doc_type,
            }
        except Exception:
            # Skip files that can't be read
            return {}

    def _extract_excerpt(self, content: str, max_length: int = 200) -> str:
        """Extract excerpt from content.

        Args:
            content: File content
            max_length: Maximum excerpt length

        Returns:
            Excerpt text
        """
        # Remove code blocks
        content = re.sub(r"```[\s\S]*?```", "", content)
        # Remove inline code
        content = re.sub(r"`[^`]+`", "", content)
        # Remove markdown links
        content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)

        # Get first paragraph
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 20:
                if len(line) > max_length:
                    return line[:max_length] + "..."
                return line

        # Fallback: first 200 chars
        return content[:max_length] + "..." if len(content) > max_length else content

    def _determine_doc_type(self, doc_path: Path, content: str) -> str:
        """Determine documentation type.

        Args:
            doc_path: Path to file
            content: File content

        Returns:
            Document type string
        """
        path_str = str(doc_path).lower()
        content_lower = content.lower()

        if "api" in path_str or "api" in content_lower[:500]:
            return "api"
        elif "troubleshoot" in path_str or "troubleshoot" in content_lower[:500]:
            return "troubleshooting"
        elif "quickstart" in path_str or "getting started" in content_lower[:500]:
            return "quickstart"
        elif "guide" in path_str:
            return "guide"
        elif "readme" in path_str:
            return "readme"
        else:
            return "guide"
