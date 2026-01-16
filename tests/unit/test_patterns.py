"""Tests for pattern management."""

import json
import tempfile
from pathlib import Path

import pytest

from shared_ai_utils.patterns import PatternManager, PatternMemory


class TestPatternManager:
    """Test PatternManager."""

    @pytest.fixture
    def temp_file(self):
        """Create temporary pattern file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            yield f.name
        Path(f.name).unlink(missing_ok=True)

    def test_pattern_manager_initialization(self, temp_file):
        """Test pattern manager initialization."""
        manager = PatternManager(pattern_library_path=temp_file)
        assert manager.patterns == []
        assert manager.changelog == []

    def test_add_pattern(self, temp_file):
        """Test adding a pattern."""
        manager = PatternManager(pattern_library_path=temp_file)
        pattern = manager.add_pattern(
            name="test_pattern",
            description="Test description",
            good_example="def good(): pass",
            bad_example="def bad(): pass",
        )

        assert pattern["name"] == "test_pattern"
        assert "pattern_id" in pattern
        assert len(manager.patterns) == 1

    def test_save_and_load_patterns(self, temp_file):
        """Test saving and loading patterns."""
        manager = PatternManager(pattern_library_path=temp_file)
        manager.add_pattern(
            name="test_pattern",
            description="Test",
            good_example="def good(): pass",
        )
        manager.save_patterns()

        # Create new manager and load
        manager2 = PatternManager(pattern_library_path=temp_file)
        manager2.load_patterns()

        assert len(manager2.patterns) == 1
        assert manager2.patterns[0]["name"] == "test_pattern"

    def test_update_pattern(self, temp_file):
        """Test updating a pattern."""
        manager = PatternManager(pattern_library_path=temp_file)
        pattern = manager.add_pattern(
            name="test_pattern",
            description="Old description",
            good_example="def good(): pass",
        )

        updated = manager.update_pattern(
            pattern["pattern_id"], description="New description"
        )

        assert updated["description"] == "New description"
        assert updated["pattern_id"] == pattern["pattern_id"]

    def test_remove_pattern(self, temp_file):
        """Test removing a pattern."""
        manager = PatternManager(pattern_library_path=temp_file)
        pattern = manager.add_pattern(
            name="test_pattern",
            description="Test",
            good_example="def good(): pass",
        )

        result = manager.remove_pattern(pattern["pattern_id"])
        assert result is True
        assert len(manager.patterns) == 0

    def test_archive_pattern(self, temp_file):
        """Test archiving a pattern."""
        manager = PatternManager(pattern_library_path=temp_file)
        pattern = manager.add_pattern(
            name="test_pattern",
            description="Test",
            good_example="def good(): pass",
        )

        result = manager.archive_pattern(pattern["pattern_id"])
        assert result is True
        assert pattern["archived"] is True
        assert "archived_at" in pattern

    def test_suggest_patterns(self, temp_file):
        """Test pattern suggestions."""
        manager = PatternManager(pattern_library_path=temp_file)
        manager.add_pattern(
            name="api_pattern",
            description="API endpoint pattern",
            good_example="def endpoint(): pass",
            tags=["api", "endpoint"],
        )

        suggestions = manager.suggest_patterns("API endpoint", limit=5)
        assert len(suggestions) > 0
        assert suggestions[0]["name"] == "api_pattern"

    def test_get_pattern_effectiveness(self, temp_file):
        """Test getting pattern effectiveness."""
        manager = PatternManager(pattern_library_path=temp_file)
        pattern = manager.add_pattern(
            name="test_pattern",
            description="Test",
            good_example="def good(): pass",
        )

        effectiveness = manager.get_pattern_effectiveness(pattern["pattern_id"])
        assert effectiveness == 0.5  # Default

    def test_update_pattern_effectiveness(self, temp_file):
        """Test updating pattern effectiveness."""
        manager = PatternManager(pattern_library_path=temp_file)
        pattern = manager.add_pattern(
            name="test_pattern",
            description="Test",
            good_example="def good(): pass",
        )

        result = manager.update_pattern_effectiveness(pattern["pattern_id"], 0.8)
        assert result is True
        assert pattern["effectiveness_score"] == 0.8
        assert pattern["occurrence_frequency"] == 1


class TestPatternMemory:
    """Test PatternMemory."""

    def test_pattern_memory_initialization(self):
        """Test pattern memory initialization."""
        memory = PatternMemory(storage_type="inmemory")
        assert memory.storage_type == "inmemory"
        assert memory.is_available() is False  # Not initialized yet

    def test_pattern_memory_without_memu(self):
        """Test pattern memory without memu-py installed."""
        memory = PatternMemory()
        # Should not raise error even if memu-py not installed
        assert memory._memu_available is False

    @pytest.mark.asyncio
    async def test_memorize_pattern_without_memu(self):
        """Test memorizing pattern without MemU."""
        memory = PatternMemory()
        result = await memory.memorize_pattern(
            {
                "name": "test",
                "description": "Test pattern",
                "good_example": "def good(): pass",
            }
        )
        # Should return None if MemU not available
        assert result is None

    @pytest.mark.asyncio
    async def test_retrieve_patterns_without_memu(self):
        """Test retrieving patterns without MemU."""
        memory = PatternMemory()
        result = await memory.retrieve_patterns("test query")
        # Should return None if MemU not available
        assert result is None
