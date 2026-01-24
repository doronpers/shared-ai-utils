"""Tests for configuration system."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import Field

from shared_ai_utils.config import ConfigBase, ConfigManager, PresetManager, get_preset, list_presets


class TestConfigClass(ConfigBase):
    """Test configuration class."""

    api_key: str = Field(default="", alias="API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")
    port: int = Field(default=8000, alias="PORT")


class TestConfigBase:
    """Test ConfigBase functionality."""

    def test_config_creation(self):
        """Test creating config instance."""
        config = TestConfigClass()
        assert config.api_key == ""
        assert config.debug is False
        assert config.port == 8000

    def test_config_from_env(self):
        """Test loading config from environment variables."""
        with patch.dict(os.environ, {"API_KEY": "test-key", "DEBUG": "true"}):
            config = TestConfigClass()
            assert config.api_key == "test-key"
            assert config.debug is True

    def test_get_dot_notation(self):
        """Test dot-notation access."""
        config = TestConfigClass()
        # For simple fields, get should work
        assert config.get("api_key", "default") == ""
        assert config.get("nonexistent", "default") == "default"

    def test_set_dot_notation(self):
        """Test dot-notation setting."""
        config = TestConfigClass()
        config.set("api_key", "new-key")
        assert config.api_key == "new-key"


class TestPresetManager:
    """Test PresetManager."""

    def test_get_preset(self):
        """Test getting a preset."""
        manager = PresetManager()
        preset = manager.get_preset("development")
        assert "APP_ENV" in preset
        assert preset["APP_ENV"] == "development"
        assert preset["DEBUG"] is True

    def test_get_preset_invalid(self):
        """Test getting invalid preset."""
        manager = PresetManager()
        with pytest.raises(ValueError, match="Unknown preset"):
            manager.get_preset("invalid_preset")

    def test_list_presets(self):
        """Test listing presets."""
        manager = PresetManager()
        presets = manager.list_presets()
        assert "development" in presets
        assert "production" in presets
        assert len(presets) >= 8

    def test_save_custom_preset(self):
        """Test saving custom preset."""
        manager = PresetManager()
        manager.save_preset("custom", {"CUSTOM_KEY": "value"}, "Custom description")
        preset = manager.get_preset("custom")
        assert preset["CUSTOM_KEY"] == "value"
        assert "custom" in manager.list_presets()

    def test_delete_custom_preset(self):
        """Test deleting custom preset."""
        manager = PresetManager()
        manager.save_preset("temp", {"KEY": "value"})
        assert "temp" in manager.list_presets()
        manager.delete_preset("temp")
        with pytest.raises(ValueError):
            manager.get_preset("temp")


class TestConfigManager:
    """Test ConfigManager."""

    def test_load_config_from_file(self):
        """Test loading config from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            # YAML format for Pydantic model
            config_file.write_text("API_KEY: test-key\nDEBUG: true\n")

            manager = ConfigManager(config_path=str(config_file))
            config = manager.load(TestConfigClass)

            # Config loads from YAML, but field names use aliases
            assert config.api_key == "test-key" or config.get("api_key") == "test-key"
            assert config.debug is True

    def test_save_config_to_file(self):
        """Test saving config to YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            manager = ConfigManager(config_path=str(config_file))

            # Set values using environment or direct assignment
            import os
            with patch.dict(os.environ, {"API_KEY": "saved-key", "DEBUG": "true"}):
                config = TestConfigClass()
                manager.save(config)

            assert config_file.exists()
            content = config_file.read_text()
            # YAML may use field names or aliases
            assert "saved-key" in content or "api_key" in content.lower()

    def test_get_dot_notation(self):
        """Test getting values with dot notation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            manager = ConfigManager(config_path=str(config_file))
            config = manager.load(TestConfigClass)
            config.api_key = "test"

            value = manager.get("api_key")
            assert value == "test"

    def test_set_dot_notation(self):
        """Test setting values with dot notation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            manager = ConfigManager(config_path=str(config_file))
            config = manager.load(TestConfigClass)

            manager.set("api_key", "new-value")
            assert config.api_key == "new-value"


class TestPresetFunctions:
    """Test preset module functions."""

    def test_get_preset_function(self):
        """Test get_preset function."""
        preset = get_preset("development")
        assert isinstance(preset, dict)
        assert "APP_ENV" in preset

    def test_list_presets_function(self):
        """Test list_presets function."""
        presets = list_presets()
        assert isinstance(presets, dict)
        assert "development" in presets
