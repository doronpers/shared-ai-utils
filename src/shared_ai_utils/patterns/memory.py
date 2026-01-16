"""
Pattern Memory Integration

MemU integration for semantic pattern storage and retrieval.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PatternMemory:
    """
    MemU integration for semantic pattern storage and retrieval.

    Provides intelligent memory layer that enables:
    - Semantic pattern retrieval (query by concept, not just name)
    - Self-evolving patterns (patterns improve based on usage)
    - Cross-project learning (share patterns across projects)
    - Multimodal memory (code, logs, tests, reviews)
    - Intelligent recommendations (context-aware suggestions)
    """

    def __init__(
        self,
        storage_type: str = "inmemory",
        openai_api_key: Optional[str] = None,
        db_url: Optional[str] = None,
    ):
        """Initialize MemU service.

        Args:
            storage_type: Storage backend ("inmemory" or "postgres")
            openai_api_key: OpenAI API key for embeddings (optional)
            db_url: PostgreSQL connection string (only for postgres storage)
        """
        self.storage_type = storage_type
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.db_url = db_url
        self._memory = None
        self._initialized = False
        self._memu_available = False

        # Try to import MemU
        try:
            import memu  # noqa: F401
            self._memu_available = True
            logger.info("MemU library loaded successfully")
        except ImportError:
            self._memu_available = False
            logger.warning(
                "MemU library not available. Install with: pip install memu-py"
            )

    async def initialize(self) -> bool:
        """Initialize MemU service.

        Returns:
            True if initialized successfully
        """
        if not self._memu_available:
            return False

        if self._initialized:
            return True

        try:
            import memu

            # Initialize MemU based on storage type
            if self.storage_type == "postgres":
                if not self.db_url:
                    logger.error("PostgreSQL storage requires db_url")
                    return False
                self._memory = memu.MemU(
                    storage_type="postgres",
                    db_url=self.db_url,
                    openai_api_key=self.openai_api_key,
                )
            else:
                # In-memory storage (default)
                self._memory = memu.MemU(
                    storage_type="inmemory",
                    openai_api_key=self.openai_api_key,
                )

            await self._memory.initialize()
            self._initialized = True
            logger.info(f"MemU initialized with storage: {self.storage_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MemU: {e}")
            return False

    def is_available(self) -> bool:
        """Check if MemU is available and initialized.

        Returns:
            True if MemU is available and ready to use
        """
        return self._memu_available and self._initialized

    async def _ensure_initialized(self) -> bool:
        """Ensure MemU is initialized."""
        if not self._initialized:
            return await self.initialize()
        return True

    async def memorize_pattern(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store a pattern in MemU memory.

        Args:
            pattern: Pattern dictionary with fields:
                - name: Pattern identifier
                - description: Pattern description
                - good_example: Good code example
                - bad_example: Bad code example (optional)
                - tags: Optional list of tags

        Returns:
            Response from MemU or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            # Prepare resource for MemU
            resource = {
                "type": "pattern",
                "content": self._format_pattern_content(pattern),
                "metadata": {
                    "pattern_name": pattern.get("name", "unknown"),
                    "pattern_id": pattern.get("pattern_id", ""),
                    "severity": pattern.get("severity", "medium"),
                    "occurrence_frequency": pattern.get("occurrence_frequency", 0),
                    "effectiveness_score": pattern.get("effectiveness_score", 0.5),
                    "timestamp": datetime.now().isoformat(),
                    "source": "shared-ai-utils",
                },
                "tags": self._extract_tags(pattern),
            }

            # Store in MemU
            response = await self._memory.memorize(resource)
            logger.debug(f"Stored pattern '{pattern.get('name')}' in MemU")
            return response

        except Exception as e:
            logger.error(f"Failed to memorize pattern: {e}")
            return None

    async def retrieve_patterns(
        self, query: str, method: str = "rag", limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Retrieve patterns using semantic search.

        Args:
            query: Natural language query
            method: Retrieval method ("rag" for fast, "llm" for deep)
            limit: Maximum number of results

        Returns:
            Dictionary with retrieved patterns or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            # Query MemU with semantic search
            if method == "rag":
                response = await self._memory.retrieve_rag(
                    query=query, limit=limit, filters={"type": "pattern"}
                )
            elif method == "llm":
                response = await self._memory.retrieve_llm(
                    query=query, limit=limit, filters={"type": "pattern"}
                )
            else:
                raise ValueError(f"Unsupported retrieval method: {method}")

            logger.debug(
                f"Retrieved {len(response.get('results', []))} patterns for query: {query}"
            )
            return response

        except Exception as e:
            logger.error(f"Failed to retrieve patterns: {e}")
            return None

    async def recommend_patterns(
        self, context: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get pattern recommendations for current context.

        Args:
            context: Current development context
            limit: Maximum number of recommendations

        Returns:
            List of recommended patterns
        """
        if not await self._ensure_initialized():
            return []

        try:
            # Use RAG retrieval for recommendations
            response = await self.retrieve_patterns(context, method="rag", limit=limit)
            if response and "results" in response:
                return response["results"]
            return []

        except Exception as e:
            logger.error(f"Failed to get pattern recommendations: {e}")
            return []

    def _format_pattern_content(self, pattern: Dict[str, Any]) -> str:
        """Format pattern content for MemU storage."""
        parts = [
            f"Pattern: {pattern.get('name', 'unknown')}",
            f"Description: {pattern.get('description', '')}",
        ]

        if pattern.get("good_example"):
            parts.append(f"Good Example:\n{pattern['good_example']}")

        if pattern.get("bad_example"):
            parts.append(f"Bad Example:\n{pattern['bad_example']}")

        return "\n\n".join(parts)

    def _extract_tags(self, pattern: Dict[str, Any]) -> List[str]:
        """Extract tags from pattern."""
        tags = pattern.get("tags", [])
        if pattern.get("severity"):
            tags.append(f"severity:{pattern['severity']}")
        return tags
