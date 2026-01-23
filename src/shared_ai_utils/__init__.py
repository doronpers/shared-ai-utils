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
    RateLimiter,
    RateLimitMiddleware,
    RequestIDMiddleware,
    RequestResponseLoggingMiddleware,
    WebSocketManager,
    create_api_key_auth,
    create_cors_middleware,
    create_error_response,
    create_health_router,
    create_rate_limit_middleware,
    websocket_endpoint,
)
from shared_ai_utils.assessment import (
    AssessmentEngine,
    AssessmentInput,
    AssessmentResult,
    CouncilAdapter,
    Evidence,
    EvidenceType,
    HeuristicScorer,
    HeuristicScorerConfig,
    MicroMotive,
    MicroMotiveScorer,
    MotiveType,
    PathScore,
    PathType,
    PatternViolation,
    ScoringMetric,
    calculate_pattern_penalty,
    detect_pattern_violations,
    extract_text_content,
    violations_to_metadata,
)
from shared_ai_utils.cli import (
    BaseCLI,
    SetupWizard,
    Wizard,
    WizardStep,
    docs,
    format_score,
    onboard,
    print_error,
    print_info,
    print_json,
    print_success,
    print_table,
    print_warning,
)
from shared_ai_utils.docs import (
    ContextualDocLoader,
    DocIndex,
    DocIndexer,
    DocResult,
    DocumentationHub,
)
from shared_ai_utils.errors import (
    ContextualHelp,
    ErrorRecovery,
    HelpResponse,
    RecoveryStep,
    UnifiedErrorFormatter,
)
from shared_ai_utils.onboarding import (
    IntentDetector,
    IntentResult,
    SetupVerifier,
    UnifiedOnboarding,
    VerificationResult,
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
from shared_ai_utils.insights import InsightsEngine, MetricsAnalyzerProtocol
from shared_ai_utils.analytics import (
    create_assessment_dashboard_config,
    create_pattern_dashboard_config,
    create_sensor_dashboard_config,
    create_unified_dashboard_config,
)
from shared_ai_utils.integrations import (
    FeedbackLoopAssessmentIntegration,
    SonoEvalPatternIntegration,
    SonoPlatformReviewer,
)
from shared_ai_utils.metrics import (
    MetricsCollector,
    MetricType,
    get_metric_categories,
)

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
    "SonoPlatformConfigAdapter",
    "SonoEvalConfigAdapter",
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
    "HeuristicScorer",
    "MicroMotiveScorer",
    "CouncilAdapter",
    "HeuristicScorerConfig",
    "PatternViolation",
    "detect_pattern_violations",
    "calculate_pattern_penalty",
    "violations_to_metadata",
    "extract_text_content",
    # API
    "RequestIDMiddleware",
    "RequestResponseLoggingMiddleware",
    "create_cors_middleware",
    "RateLimiter",
    "RateLimitMiddleware",
    "create_rate_limit_middleware",
    "create_api_key_auth",
    "verify_api_key",
    "get_api_key_from_request",
    "hash_api_key",
    "WebSocketManager",
    "websocket_endpoint",
    "ErrorCode",
    "ErrorResponse",
    "create_error_response",
    "HealthResponse",
    "create_health_router",
    # Error Recovery
    "ErrorRecovery",
    "RecoveryStep",
    "ContextualHelp",
    "HelpResponse",
    "UnifiedErrorFormatter",
    # Patterns
    "PatternManager",
    "PatternMemory",
    # CLI
    "BaseCLI",
    "AssessmentCLI",
    "SensorCLI",
    "PatternCLI",
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
    "onboard",
    "docs",
    # Documentation
    "DocumentationHub",
    "DocIndexer",
    "DocIndex",
    "DocResult",
    "ContextualDocLoader",
    # Onboarding
    "UnifiedOnboarding",
    "IntentDetector",
    "IntentResult",
    "SetupVerifier",
    "VerificationResult",
    # Insights
    "InsightsEngine",
    "MetricsAnalyzerProtocol",
    # Metrics
    "MetricsCollector",
    "MetricType",
    "get_metric_categories",
    # Integrations
    "SonoPlatformReviewer",
    "SonoEvalPatternIntegration",
    "FeedbackLoopAssessmentIntegration",
    # Analytics
    "create_unified_dashboard_config",
    "create_assessment_dashboard_config",
    "create_sensor_dashboard_config",
    "create_pattern_dashboard_config",
]
