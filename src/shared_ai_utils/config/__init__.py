"""
Configuration Management

Type-safe configuration with YAML support, presets, and environment variable loading.
"""

from shared_ai_utils.config.adapters import (
    SonoEvalConfigAdapter,
    SonoPlatformConfigAdapter,
)
from shared_ai_utils.config.base import ConfigBase
from shared_ai_utils.config.presets import (
    PresetManager,
    get_preset,
    list_presets,
)
from shared_ai_utils.config.yaml import ConfigManager, load_config, save_config

__all__ = [
    "ConfigBase",
    "ConfigManager",
    "load_config",
    "save_config",
    "PresetManager",
    "get_preset",
    "list_presets",
    "SonoPlatformConfigAdapter",
    "SonoEvalConfigAdapter",
]
