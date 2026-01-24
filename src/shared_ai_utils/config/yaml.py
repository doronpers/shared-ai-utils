"""
YAML Configuration File Support

Load and save configuration to YAML files with dot-notation access.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages loading and saving configuration from YAML files."""

    def __init__(self, config_path: Optional[str] = None, app_name: str = "shared-ai-utils"):
        """Initialize config manager.

        Args:
            config_path: Explicit path to config file (optional)
            app_name: Application name for default config directory
        """
        self.app_name = app_name
        if config_path:
            self.path = Path(config_path)
        else:
            # Import here to avoid circular dependency
            from ..utils.paths import get_workspace_config_dir

            options = [
                os.environ.get(f"{app_name.upper().replace('-', '_')}_CONFIG_DIR"),
                get_workspace_config_dir(app_name),
                Path.home() / ".config" / app_name,  # Legacy fallback
                Path("/tmp") / app_name,
            ]

            for option in options:
                if not option:
                    continue
                path = Path(option)
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.path = path / "config.yaml"
                    break
                except OSError:
                    continue
            else:
                # Fallback if no paths are writable
                self.path = Path("config.yaml")  # Dummy path

        self.config: Optional[BaseModel] = None

    def load(self, config_class: type[BaseModel]) -> BaseModel:
        """Load configuration from file.

        Args:
            config_class: Pydantic model class to load into

        Returns:
            Config instance
        """
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                # Create config instance, allowing YAML data to override defaults
                self.config = config_class(**data)
                logger.debug(f"Loaded config from {self.path}")
            except Exception as e:
                import sys

                print(f"Warning: Failed to load config from {self.path}: {e}", file=sys.stderr)
                self.config = config_class()
        else:
            self.config = config_class()

        return self.config

    def save(self, config: BaseModel) -> None:
        """Save configuration to file.

        Args:
            config: Config instance to save
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                yaml.dump(
                    config.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                )
            try:
                os.chmod(self.path, 0o600)  # Secure file permissions
            except OSError:
                pass
            logger.debug(f"Saved config to {self.path}")
        except OSError as e:
            logger.warning(f"Failed to save configuration to {self.path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "api.provider")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if self.config is None:
            return default

        parts = key.split(".")
        value = self.config

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "api.provider")
            value: Value to set

        Raises:
            KeyError: If key path is invalid
        """
        if self.config is None:
            raise ValueError("Config not loaded. Call load() first.")

        parts = key.split(".")
        obj = self.config

        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict):
                if part not in obj:
                    obj[part] = {}
                obj = obj[part]
            else:
                raise KeyError(f"Invalid config path: {key}")

        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        elif isinstance(obj, dict):
            obj[final_key] = value
        else:
            raise KeyError(f"Invalid config key: {key}")


def load_config(config_class: type[BaseModel], path: Optional[str] = None, app_name: str = "shared-ai-utils") -> BaseModel:
    """Load configuration from YAML file.

    Args:
        config_class: Pydantic model class to load into
        path: Optional path to config file
        app_name: Application name for default config directory

    Returns:
        Config instance
    """
    manager = ConfigManager(path, app_name)
    return manager.load(config_class)


def save_config(config: BaseModel, path: Optional[str] = None, app_name: str = "shared-ai-utils") -> None:
    """Save configuration to YAML file.

    Args:
        config: Config instance to save
        path: Optional path to config file
        app_name: Application name for default config directory
    """
    manager = ConfigManager(path, app_name)
    manager.save(config)
