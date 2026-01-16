"""
Pattern Manager

Manages pattern library with CRUD operations, versioning, and effectiveness tracking.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PatternManager:
    """Manages pattern library with CRUD operations and archiving."""

    def __init__(
        self,
        pattern_library_path: str = "patterns.json",
        use_memory: bool = False,
        memory_service: Optional[Any] = None,
    ):
        """Initialize the pattern manager.

        Args:
            pattern_library_path: Path to the pattern library JSON file
            use_memory: Whether to enable MemU integration
            memory_service: Optional memory service instance
        """
        # Validate path to prevent path traversal
        if ".." in Path(pattern_library_path).parts:
            raise ValueError(f"Path traversal detected in: {pattern_library_path}")

        resolved_path = Path(pattern_library_path).resolve()
        self.pattern_library_path = str(resolved_path)

        self.patterns: List[Dict[str, Any]] = []
        self.changelog: List[Dict[str, Any]] = []

        # Memory integration
        self.use_memory = use_memory
        self.memory = memory_service

        # Try to load existing patterns
        if os.path.exists(self.pattern_library_path):
            self.load_patterns()
        else:
            logger.debug(
                f"Pattern library not found at {self.pattern_library_path}, will create new"
            )

    def load_patterns(self) -> None:
        """Load patterns from JSON file."""
        try:
            with open(self.pattern_library_path, "r") as f:
                data = json.load(f)
                self.patterns = data.get("patterns", [])
                self.changelog = data.get("changelog", [])
            logger.debug(
                f"Loaded {len(self.patterns)} patterns from {self.pattern_library_path}"
            )
        except (json.JSONDecodeError, IOError) as e:
            logger.debug(f"Failed to load patterns: {e}")
            self.patterns = []
            self.changelog = []

    def save_patterns(self) -> None:
        """Save patterns to JSON file."""
        try:
            data = {
                "patterns": self.patterns,
                "changelog": self.changelog,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.pattern_library_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(
                f"Saved {len(self.patterns)} patterns to {self.pattern_library_path}"
            )
        except IOError as e:
            logger.error(
                f"Failed to save patterns to {self.pattern_library_path}: {e}",
                exc_info=True,
            )
            raise

    def add_pattern(
        self,
        name: str,
        description: str,
        good_example: str,
        bad_example: Optional[str] = None,
        severity: str = "medium",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Add a new pattern.

        Args:
            name: Pattern name/identifier
            description: Pattern description
            good_example: Good code example
            bad_example: Bad code example (optional)
            severity: Severity level (low, medium, high)
            tags: Optional list of tags

        Returns:
            Created pattern dictionary
        """
        pattern = {
            "pattern_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "good_example": good_example,
            "bad_example": bad_example or "",
            "severity": severity,
            "tags": tags or [],
            "occurrence_frequency": 0,
            "effectiveness_score": 0.5,
            "created_at": datetime.now().isoformat(),
            "last_occurrence": None,
        }

        self.patterns.append(pattern)
        self._add_changelog_entry("added", name)
        logger.info(f"Added pattern: {name}")

        return pattern

    def update_pattern(
        self,
        pattern_id: str,
        description: Optional[str] = None,
        good_example: Optional[str] = None,
        bad_example: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing pattern.

        Args:
            pattern_id: Pattern ID to update
            description: New description (optional)
            good_example: New good example (optional)
            bad_example: New bad example (optional)
            severity: New severity (optional)

        Returns:
            Updated pattern or None if not found
        """
        pattern = self._find_pattern_by_id(pattern_id)
        if not pattern:
            return None

        if description is not None:
            pattern["description"] = description
        if good_example is not None:
            pattern["good_example"] = good_example
        if bad_example is not None:
            pattern["bad_example"] = bad_example
        if severity is not None:
            pattern["severity"] = severity

        self._add_changelog_entry("updated", pattern["name"])
        logger.info(f"Updated pattern: {pattern['name']}")

        return pattern

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern.

        Args:
            pattern_id: Pattern ID to remove

        Returns:
            True if removed, False if not found
        """
        pattern = self._find_pattern_by_id(pattern_id)
        if not pattern:
            return False

        self.patterns.remove(pattern)
        self._add_changelog_entry("removed", pattern["name"])
        logger.info(f"Removed pattern: {pattern['name']}")

        return True

    def archive_pattern(self, pattern_id: str) -> bool:
        """Archive a pattern (mark as archived, don't delete).

        Args:
            pattern_id: Pattern ID to archive

        Returns:
            True if archived, False if not found
        """
        pattern = self._find_pattern_by_id(pattern_id)
        if not pattern:
            return False

        pattern["archived"] = True
        pattern["archived_at"] = datetime.now().isoformat()
        self._add_changelog_entry("archived", pattern["name"])
        logger.info(f"Archived pattern: {pattern['name']}")

        return True

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a pattern by ID.

        Args:
            pattern_id: Pattern ID

        Returns:
            Pattern dictionary or None
        """
        return self._find_pattern_by_id(pattern_id)

    def list_patterns(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        """List all patterns.

        Args:
            include_archived: Include archived patterns

        Returns:
            List of pattern dictionaries
        """
        if include_archived:
            return self.patterns.copy()
        return [p for p in self.patterns if not p.get("archived", False)]

    def suggest_patterns(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest patterns based on context.

        Args:
            context: Development context
            limit: Maximum number of suggestions

        Returns:
            List of suggested patterns
        """
        # Simple keyword-based suggestion (can be enhanced with semantic search)
        context_lower = context.lower()
        suggestions = []

        for pattern in self.patterns:
            if pattern.get("archived", False):
                continue

            name = pattern.get("name", "").lower()
            description = pattern.get("description", "").lower()
            tags = [tag.lower() for tag in pattern.get("tags", [])]

            # Simple matching
            if (
                any(word in name for word in context_lower.split())
                or any(word in description for word in context_lower.split())
                or any(tag in context_lower for tag in tags)
            ):
                suggestions.append(pattern)

            if len(suggestions) >= limit:
                break

        return suggestions

    def get_pattern_effectiveness(self, pattern_id: str) -> Optional[float]:
        """Get effectiveness score for a pattern.

        Args:
            pattern_id: Pattern ID

        Returns:
            Effectiveness score (0.0-1.0) or None
        """
        pattern = self._find_pattern_by_id(pattern_id)
        if not pattern:
            return None
        return pattern.get("effectiveness_score", 0.5)

    def update_pattern_effectiveness(
        self, pattern_id: str, score: float
    ) -> bool:
        """Update effectiveness score for a pattern.

        Args:
            pattern_id: Pattern ID
            score: New effectiveness score (0.0-1.0)

        Returns:
            True if updated, False if not found
        """
        pattern = self._find_pattern_by_id(pattern_id)
        if not pattern:
            return False

        pattern["effectiveness_score"] = max(0.0, min(1.0, score))
        pattern["last_occurrence"] = datetime.now().isoformat()
        pattern["occurrence_frequency"] = pattern.get("occurrence_frequency", 0) + 1

        return True

    def _find_pattern_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Find pattern by ID."""
        for pattern in self.patterns:
            if pattern.get("pattern_id") == pattern_id:
                return pattern
        return None

    def _find_pattern_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find pattern by name."""
        for pattern in self.patterns:
            if pattern.get("name") == name:
                return pattern
        return None

    def _add_changelog_entry(self, action: str, pattern_name: str) -> None:
        """Add entry to changelog."""
        self.changelog.append(
            {
                "action": action,
                "pattern_name": pattern_name,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def sync_patterns_to_memory(self) -> int:
        """Sync all patterns to MemU memory.

        Returns:
            Number of patterns successfully synced
        """
        if not self.memory:
            logger.debug("Memory service not enabled")
            return 0

        synced_count = 0
        for pattern in self.patterns:
            if await self.memory.memorize_pattern(pattern):
                synced_count += 1

        logger.info(f"Synced {synced_count}/{len(self.patterns)} patterns to memory")
        return synced_count
