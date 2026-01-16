"""
Shared AI Utils

Shared utilities for AI-assisted development tools.
"""

__version__ = "0.1.0"

# Export main components
from shared_ai_utils.api import (
    ErrorCode,
    ErrorResponse,
    HealthResponse,
    RequestIDMiddleware,
    create_cors_middleware,
    create_error_response,
    create_health_router,
)
from shared_ai_utils.assessment import (
    AssessmentEngine,
    AssessmentInput,
    AssessmentResult,
    Evidence,
    EvidenceType,
    MicroMotive,
    MotiveType,
    PathScore,
    PathType,
    ScoringMetric,
)
from shared_ai_utils.cli import (
    BaseCLI,
    SetupWizard,
    Wizard,
    WizardStep,
    format_score,
    print_error,
    print_info,
    print_json,
    print_success,
    print_table,
    print_warning,
)
from shared_ai_utils.config import (
    ConfigBase,
    ConfigManager,
    PresetManager,
    get_preset,
    list_presets,
    load_config,
    save_config,
)
from shared_ai_utils.llm import (
    LLMManager,
    LLMProvider,
    LLMResponse,
    AnthropicProvider,
    GeminiProvider,
    HTTPProvider,
    OpenAIProvider,
    get_llm_manager,
)
from shared_ai_utils.patterns import PatternManager, PatternMemory

__all__ = [
    # Version
    "__version__",
    # LLM
    "LLMProvider",
    "LLMResponse",
    "LLMManager",
    "AnthropicProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "HTTPProvider",
    "get_llm_manager",
    # Config
    "ConfigBase",
    "ConfigManager",
    "PresetManager",
    "get_preset",
    "list_presets",
    "load_config",
    "save_config",
    # Assessment
    "AssessmentEngine",
    "AssessmentInput",
    "AssessmentResult",
    "PathScore",
    "ScoringMetric",
    "Evidence",
    "EvidenceType",
    "MicroMotive",
    "MotiveType",
    "PathType",
    # API
    "RequestIDMiddleware",
    "create_cors_middleware",
    "ErrorCode",
    "ErrorResponse",
    "create_error_response",
    "HealthResponse",
    "create_health_router",
    # Patterns
    "PatternManager",
    "PatternMemory",
    # CLI
    "BaseCLI",
    "print_table",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "print_json",
    "format_score",
    "Wizard",
    "WizardStep",
    "SetupWizard",
]
