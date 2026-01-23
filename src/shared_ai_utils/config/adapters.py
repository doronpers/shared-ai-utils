"""Configuration adapters for different repository formats.

Provides adapters to convert between different config formats:
- sono-platform settings.yaml format
- sono-eval config/ format
- Standard shared-ai-utils ConfigManager format
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class SonoPlatformConfigAdapter:
    """Adapter for sono-platform settings.yaml format."""

    @staticmethod
    def load_settings_yaml(settings_path: str) -> Dict[str, Any]:
        """Load sono-platform settings.yaml file.

        Args:
            settings_path: Path to settings.yaml file

        Returns:
            Dictionary of settings
        """
        path = Path(settings_path)
        if not path.exists():
            logger.warning(f"Settings file not found: {settings_path}")
            return {}

        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load settings.yaml: {e}")
            return {}

    @staticmethod
    def convert_to_shared_config(settings: Dict[str, Any]) -> Dict[str, Any]:
        """Convert sono-platform settings to shared-ai-utils config format.

        Args:
            settings: Sono-platform settings dictionary

        Returns:
            Shared-ai-utils config dictionary
        """
        # Map sono-platform settings to shared config
        shared_config = {}

        # Sensor settings
        if "sensors" in settings:
            shared_config["sensors"] = settings["sensors"]

        # API settings
        if "api" in settings:
            shared_config["api"] = settings["api"]

        # Assessment settings (if present)
        if "assessment" in settings:
            shared_config["assessment"] = settings["assessment"]

        # Pattern checks
        shared_config["pattern_checks_enabled"] = settings.get("pattern_checks_enabled", True)

        return shared_config

    @staticmethod
    def merge_with_shared_config(
        settings: Dict[str, Any], shared_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge shared-ai-utils config into sono-platform settings.

        Args:
            settings: Sono-platform settings
            shared_config: Shared-ai-utils config

        Returns:
            Merged configuration
        """
        merged = settings.copy()

        # Merge assessment settings
        if "assessment" in shared_config:
            merged.setdefault("assessment", {}).update(shared_config["assessment"])

        # Merge pattern checks
        if "pattern_checks_enabled" in shared_config:
            merged["pattern_checks_enabled"] = shared_config["pattern_checks_enabled"]

        return merged


class SonoEvalConfigAdapter:
    """Adapter for sono-eval config/ format."""

    @staticmethod
    def load_config_directory(config_dir: str) -> Dict[str, Any]:
        """Load sono-eval config from directory.

        Args:
            config_dir: Path to config directory

        Returns:
            Dictionary of configuration
        """
        config_path = Path(config_dir)
        if not config_path.exists():
            logger.warning(f"Config directory not found: {config_dir}")
            return {}

        config = {}
        # Look for common config files
        for config_file in ["config.yaml", "settings.yaml", "config.json"]:
            file_path = config_path / config_file
            if file_path.exists():
                try:
                    if config_file.endswith(".yaml") or config_file.endswith(".yml"):
                        with open(file_path, "r") as f:
                            config.update(yaml.safe_load(f) or {})
                    elif config_file.endswith(".json"):
                        import json

                        with open(file_path, "r") as f:
                            config.update(json.load(f) or {})
                except Exception as e:
                    logger.error(f"Failed to load {config_file}: {e}")

        return config

    @staticmethod
    def convert_to_shared_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert sono-eval config to shared-ai-utils format.

        Args:
            config: Sono-eval config dictionary

        Returns:
            Shared-ai-utils config dictionary
        """
        shared_config = {}

        # Assessment engine settings
        if "assessment_engine_version" in config:
            shared_config["assessment_engine_version"] = config["assessment_engine_version"]
        if "assessment_enable_explanations" in config:
            shared_config["assessment_enable_explanations"] = config[
                "assessment_enable_explanations"
            ]
        if "dark_horse_mode" in config:
            shared_config["dark_horse_enabled"] = config["dark_horse_mode"].lower() in (
                "enabled",
                "true",
                "1",
            )
        if "pattern_checks_enabled" in config:
            shared_config["pattern_checks_enabled"] = config["pattern_checks_enabled"]

        return shared_config
