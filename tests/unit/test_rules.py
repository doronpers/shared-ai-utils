"""Tests for rules builder."""

import tempfile
from pathlib import Path

import pytest

from shared_ai_utils.rules.builder import RuleBuilder, HEADER


class TestRuleBuilder:
    """Test RuleBuilder."""

    def test_builder_initialization(self):
        """Test RuleBuilder initialization."""
        builder = RuleBuilder()
        assert builder.rules_dir is not None
        assert builder.rules_dir.exists()

    def test_builder_initialization_with_custom_dir(self):
        """Test RuleBuilder with custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = RuleBuilder(rules_dir=tmpdir)
            assert builder.rules_dir == Path(tmpdir)

    def test_build_with_existing_rules(self):
        """Test building rules with existing rule files."""
        builder = RuleBuilder()
        content = builder.build()
        
        # Should include header
        assert HEADER in content
        # Should be a non-empty string
        assert len(content) > len(HEADER)

    def test_build_with_missing_rules(self):
        """Test building rules with missing rule files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = RuleBuilder(rules_dir=tmpdir)
            content = builder.build()
            
            # Should still include header even if no rules
            assert HEADER in content

    def test_write_to_file(self):
        """Test writing rules to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            builder = RuleBuilder()
            builder.write_to_file(str(output_path))
            
            assert output_path.exists()
            content = output_path.read_text()
            assert HEADER in content
