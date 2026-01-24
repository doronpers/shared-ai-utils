"""
Documentation Hub Core

Main hub for unified documentation across all repositories.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DocResult:
    """A documentation search result."""

    title: str
    path: str
    repo: str
    excerpt: str
    relevance_score: float
    doc_type: str  # "guide", "api", "troubleshooting", etc.

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "path": self.path,
            "repo": self.repo,
            "excerpt": self.excerpt,
            "relevance_score": self.relevance_score,
            "doc_type": self.doc_type,
        }


@dataclass
class DocIndex:
    """Searchable index of documentation."""

    docs: List[Dict[str, str]]  # List of doc metadata
    repo_paths: Dict[str, Path]  # Map repo names to paths


class DocumentationHub:
    """Unified documentation hub for all repos."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize documentation hub.

        Args:
            workspace_root: Root directory containing repositories
        """
        if workspace_root:
            self.workspace_root = Path(workspace_root)
        else:
            # Try to detect workspace root
            self.workspace_root = self._detect_workspace_root()

        self.repo_paths = self._discover_repos()
        self.index: Optional[DocIndex] = None

    def _detect_workspace_root(self) -> Path:
        """Detect workspace root directory.

        Returns:
            Path to workspace root
        """
        # Common workspace patterns
        current = Path.cwd()

        # Check if we're in a known repo
        for parent in [current] + list(current.parents):
            if (parent / "sono-platform").exists() or (parent / "sono-eval").exists():
                return parent

        # Default to current directory
        return current

    def _discover_repos(self) -> Dict[str, Path]:
        """Discover repositories in workspace.

        Returns:
            Dictionary mapping repo names to paths
        """
        repos: Dict[str, Path] = {}

        # Common repo names
        repo_names = [
            "sono-platform",
            "sono-eval",
            "feedback-loop",
            "council-ai",
            "sonotheia-examples",
            "shared-ai-utils",
        ]

        for repo_name in repo_names:
            repo_path = self.workspace_root / repo_name
            if repo_path.exists() and repo_path.is_dir():
                repos[repo_name] = repo_path

        return repos

    def _build_index(self) -> DocIndex:
        """Build searchable index of documentation.

        Returns:
            DocIndex with all documentation
        """
        from shared_ai_utils.docs.indexer import DocIndexer

        indexer = DocIndexer()
        docs: List[Dict[str, str]] = []

        for repo_name, repo_path in self.repo_paths.items():
            repo_docs = indexer.index_repo(repo_path, repo_name)
            docs.extend(repo_docs)

        return DocIndex(docs=docs, repo_paths=self.repo_paths)

    def search(
        self, query: str, context: Optional[Dict] = None, limit: int = 10
    ) -> List[DocResult]:
        """Search documentation across all repos.

        Args:
            query: Search query
            context: Optional context for filtering
            limit: Maximum number of results

        Returns:
            List of DocResult objects sorted by relevance
        """
        if not self.index:
            self.index = self._build_index()

        query_lower = query.lower()
        results: List[DocResult] = []

        for doc in self.index.docs:
            # Simple keyword matching (can be enhanced with semantic search)
            title = doc.get("title", "").lower()
            content = doc.get("content", "").lower()
            path = doc.get("path", "").lower()

            # Calculate relevance score
            score = 0.0

            if query_lower in title:
                score += 10.0
            if query_lower in content:
                score += 5.0
            if query_lower in path:
                score += 3.0

            # Word matching
            query_words = query_lower.split()
            for word in query_words:
                if word in title:
                    score += 2.0
                if word in content:
                    score += 1.0

            if score > 0:
                results.append(
                    DocResult(
                        title=doc.get("title", "Untitled"),
                        path=doc.get("path", ""),
                        repo=doc.get("repo", "unknown"),
                        excerpt=doc.get("excerpt", "")[:200],
                        relevance_score=score,
                        doc_type=doc.get("type", "guide"),
                    )
                )

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Apply context filtering if provided
        if context:
            results = self._filter_by_context(results, context)

        return results[:limit]

    def _filter_by_context(
        self, results: List[DocResult], context: Dict
    ) -> List[DocResult]:
        """Filter results by context.

        Args:
            results: Search results
            context: Context for filtering

        Returns:
            Filtered results
        """
        # Filter by repo if specified
        if "repo" in context:
            results = [r for r in results if r.repo == context["repo"]]

        # Filter by doc type if specified
        if "doc_type" in context:
            results = [
                r for r in results if r.doc_type == context["doc_type"]
            ]

        return results

    def get_contextual_docs(
        self, context: Dict[str, Any]
    ) -> List[DocResult]:
        """Get docs relevant to current user context.

        Args:
            context: User context (error, task, etc.)

        Returns:
            List of relevant DocResult objects
        """
        from shared_ai_utils.docs.contextual_loader import ContextualDocLoader

        loader = ContextualDocLoader(self)
        return loader.get_docs_for_context(context)
