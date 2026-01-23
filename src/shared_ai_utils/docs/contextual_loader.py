"""
Contextual Documentation Loader

Loads documentation based on user context (errors, tasks, etc.).
"""

from typing import Any, Dict, List

from shared_ai_utils.docs.hub import DocResult, DocumentationHub


class ContextualDocLoader:
    """Load docs based on user context."""

    def __init__(self, hub: DocumentationHub):
        """Initialize contextual loader.

        Args:
            hub: DocumentationHub instance
        """
        self.hub = hub

    def get_docs_for_context(self, context: Dict[str, Any]) -> List[DocResult]:
        """Get docs relevant to user context.

        Args:
            context: User context dictionary

        Returns:
            List of relevant DocResult objects
        """
        if "error" in context:
            return self.get_docs_for_error(context["error"])

        if "task" in context:
            return self.get_docs_for_task(context["task"])

        if "repo" in context:
            return self.get_docs_for_repo(context["repo"])

        return []

    def get_docs_for_error(self, error: str) -> List[DocResult]:
        """Get docs relevant to an error.

        Args:
            error: Error type or message

        Returns:
            List of relevant DocResult objects
        """
        # Search for troubleshooting and error-related docs
        results = self.hub.search(
            f"error {error}",
            context={"doc_type": "troubleshooting"},
            limit=5,
        )

        # Also search for general troubleshooting
        if not results:
            results = self.hub.search("troubleshooting", limit=3)

        return results

    def get_docs_for_task(self, task: str) -> List[DocResult]:
        """Get docs for a specific task.

        Args:
            task: Task description

        Returns:
            List of relevant DocResult objects
        """
        return self.hub.search(task, limit=5)

    def get_docs_for_repo(self, repo: str) -> List[DocResult]:
        """Get docs for a specific repository.

        Args:
            repo: Repository name

        Returns:
            List of relevant DocResult objects
        """
        return self.hub.search("", context={"repo": repo}, limit=10)
