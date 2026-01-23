"""
Configuration Presets

Predefined configuration presets for common use cases.
"""

from typing import Any, Dict, Optional


# Standard presets from sono-eval
STANDARD_PRESETS = {
    "quick_test": {
        "APP_ENV": "development",
        "DEBUG": True,
        "LOG_LEVEL": "ERROR",  # Minimal logging
        "API_WORKERS": 1,
        "API_PORT": 8000,
    },
    "development": {
        "APP_ENV": "development",
        "DEBUG": True,
        "LOG_LEVEL": "INFO",
        "API_WORKERS": 2,
        "API_PORT": 8000,
    },
    "testing": {
        "APP_ENV": "testing",
        "DEBUG": False,
        "LOG_LEVEL": "WARNING",  # Less verbose in tests
        "API_WORKERS": 1,
        "API_PORT": 8001,  # Different port to avoid conflicts
    },
    "staging": {
        "APP_ENV": "staging",
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "API_WORKERS": 3,
        "API_PORT": 8000,
    },
    "production": {
        "APP_ENV": "production",
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "API_WORKERS": 4,
        "API_PORT": 8000,
    },
    "high_performance": {
        "APP_ENV": "production",
        "DEBUG": False,
        "LOG_LEVEL": "WARNING",  # Less logging overhead
        "API_WORKERS": 8,  # More workers
        "API_PORT": 8000,
    },
    "low_resource": {
        "APP_ENV": "development",
        "DEBUG": True,
        "LOG_LEVEL": "ERROR",
        "API_WORKERS": 1,
        "API_PORT": 8000,
    },
    "ml_development": {
        "APP_ENV": "development",
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",  # Verbose for ML debugging
        "API_WORKERS": 2,
        "API_PORT": 8000,
    },
    # Domain-specific presets
    "sono_platform_sensor": {
        "APP_ENV": "development",
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "PATTERN_CHECKS_ENABLED": True,
        "ASSESSMENT_ENABLED": True,
        "COUNCIL_DOMAIN": "sonotheia",
    },
    "sono_eval_assessment": {
        "APP_ENV": "development",
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "DARK_HORSE_MODE": "enabled",
        "PATTERN_CHECKS_ENABLED": True,
        "ASSESSMENT_ENABLE_EXPLANATIONS": True,
    },
    "feedback_loop_patterns": {
        "APP_ENV": "development",
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "PATTERN_LIBRARY_PATH": "patterns.json",
        "MEMORY_ENABLED": False,
    },
}

PRESET_DESCRIPTIONS = {
    "quick_test": "Fast setup for quick testing (minimal features, fast startup)",
    "development": "Full-featured development environment (all features enabled)",
    "testing": "Optimized for running tests (fast, minimal resources)",
    "staging": "Pre-production environment (production-like but with debugging)",
    "production": "Production-ready configuration (optimized, secure)",
    "high_performance": "Maximum performance (more workers, aggressive caching)",
    "low_resource": "Minimal resource usage (single worker, no ML models)",
    "ml_development": "ML model development and training (ML features enabled)",
    "sono_platform_sensor": "Sono-platform sensor development preset (pattern checks, assessment enabled)",
    "sono_eval_assessment": "Sono-eval assessment preset (Dark Horse mode, pattern checks, explanations)",
    "feedback_loop_patterns": "Feedback-loop pattern library preset (pattern management enabled)",
}


class PresetManager:
    """Manages configuration presets."""

    def __init__(self):
        """Initialize preset manager."""
        self.presets: Dict[str, Dict[str, Any]] = STANDARD_PRESETS.copy()
        self.custom_presets: Dict[str, Dict[str, Any]] = {}

    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """Get configuration preset values.

        Args:
            preset_name: Name of the preset

        Returns:
            Dictionary of configuration values to set as environment variables

        Raises:
            ValueError: If preset not found
        """
        if preset_name in self.presets:
            return self.presets[preset_name].copy()
        if preset_name in self.custom_presets:
            return self.custom_presets[preset_name].copy()

        available = ", ".join(list(self.presets.keys()) + list(self.custom_presets.keys()))
        raise ValueError(
            f"Unknown preset: '{preset_name}'. "
            f"Available presets: {available}\n\n"
            f"Preset descriptions:\n"
            + "\n".join(f"  - {k}: {v}" for k, v in PRESET_DESCRIPTIONS.items())
        )

    def list_presets(self) -> Dict[str, str]:
        """List all available configuration presets with descriptions.

        Returns:
            Dictionary mapping preset names to descriptions
        """
        result = PRESET_DESCRIPTIONS.copy()
        # Add custom presets
        for name in self.custom_presets:
            result[name] = f"Custom preset: {name}"
        return result

    def save_preset(self, name: str, values: Dict[str, Any], description: Optional[str] = None):
        """Save a custom preset.

        Args:
            name: Preset name
            values: Configuration values
            description: Optional description
        """
        self.custom_presets[name] = values.copy()
        if description:
            PRESET_DESCRIPTIONS[name] = description

    def delete_preset(self, name: str):
        """Delete a custom preset.

        Args:
            name: Preset name

        Raises:
            KeyError: If preset not found
        """
        if name not in self.custom_presets:
            raise KeyError(f"Custom preset '{name}' not found")
        del self.custom_presets[name]
        if name in PRESET_DESCRIPTIONS:
            del PRESET_DESCRIPTIONS[name]


# Global preset manager instance
_preset_manager: PresetManager = None


def get_preset(preset_name: str) -> Dict[str, Any]:
    """Get configuration preset values.

    Args:
        preset_name: Name of the preset

    Returns:
        Dictionary of configuration values
    """
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = PresetManager()
    return _preset_manager.get_preset(preset_name)


def list_presets() -> Dict[str, str]:
    """List all available configuration presets.

    Returns:
        Dictionary mapping preset names to descriptions
    """
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = PresetManager()
    return _preset_manager.list_presets()
