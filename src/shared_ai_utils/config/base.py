"""
Base Configuration Class

Pydantic BaseSettings-based configuration that can be extended by applications.
"""

import os
from pathlib import Path
from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Auto-load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    # Try multiple common locations
    from ..utils.paths import get_workspace_config_dir

    env_paths_to_try = [
        Path.cwd() / ".env",  # Current working directory
        get_workspace_config_dir("shared-ai-utils") / ".env",  # Workspace config
        Path.home() / ".shared-ai-utils" / ".env",  # Legacy fallback
    ]

    for env_path in env_paths_to_try:
        if env_path.exists():
            # Check if any API key env vars are placeholders - if so, override them
            api_key_vars = [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GEMINI_API_KEY",
                "AI_GATEWAY_API_KEY",
            ]
            has_placeholder = False
            for var in api_key_vars:
                existing_val = os.environ.get(var, "")
                if existing_val and (
                    "your-" in existing_val.lower() or "here" in existing_val.lower()
                ):
                    has_placeholder = True
                    break

            # Override placeholders or use override=False to preserve real env vars
            load_dotenv(env_path, override=has_placeholder)
            break
    # Also try loading from current directory as fallback
    load_dotenv(override=False)
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


class ConfigBase(BaseSettings):
    """Base configuration class using Pydantic BaseSettings.

    Applications should extend this class to add their specific configuration fields.

    Example:
        class MyConfig(ConfigBase):
            api_key: str = Field(default="", alias="API_KEY")
            debug: bool = Field(default=False, alias="DEBUG")

        config = MyConfig()
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "api.provider")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        parts = key.split(".")
        value = self

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
        parts = key.split(".")
        obj = self

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
