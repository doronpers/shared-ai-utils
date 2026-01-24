# Shared AI Utils

Shared utilities for AI-assisted development tools. This package provides reusable components extracted and consolidated from multiple repositories to eliminate duplication and ensure consistency across projects.

## 🆕 New Features (January 2026)

### 🚀 Unified Onboarding System
Interactive onboarding that helps users find the right tool and guides setup:
- Intent detection questionnaire
- Repository-specific setup wizards
- Setup verification and progress tracking
- **CLI:** `shared-ai-utils onboard` or `sono onboard`

### 🔧 Error Recovery Framework
Automatic recovery steps for common errors:
- 10+ error patterns with actionable recovery steps
- Contextual help system
- Unified error formatting (CLI/API/Web)
- **Integrated into:** sono-eval, feedback-loop

### 📚 Documentation Hub
Unified documentation search across all repositories:
- Cross-repo documentation indexing
- Context-aware documentation loading
- Relevance-based search ranking
- **CLI:** `shared-ai-utils docs "query"`

See `UX_IMPLEMENTATION_SUMMARY.md` for complete details.

---

## Installation

```bash
# Basic installation
pip install shared-ai-utils

# With LLM providers (Anthropic, OpenAI, Gemini)
pip install shared-ai-utils[llm]

# With MemU integration for semantic search
pip install shared-ai-utils[memu]

# All optional dependencies
pip install shared-ai-utils[all]

# Development dependencies
pip install shared-ai-utils[dev]
```

## Components

### LLM Providers

Unified async-first LLM provider interface with automatic fallback and token tracking.

**Features:**
- Async-first API with synchronous wrappers
- Automatic fallback between providers
- Token usage tracking
- Structured output support (JSON schema)
- Streaming support
- Provider availability detection

**Example:**
```python
from shared_ai_utils.llm import LLMManager

manager = LLMManager(preferred_provider="anthropic")
response = await manager.generate(
    system_prompt="You are a helpful assistant.",
    user_prompt="Explain async/await in Python",
    max_tokens=500
)
print(f"Response: {response.text}")
print(f"Tokens used: {response.tokens_used}")
```

**Available Providers:**
- `AnthropicProvider` - Claude models
- `OpenAIProvider` - GPT models
- `GeminiProvider` - Google Gemini models
- `HTTPProvider` - Custom HTTP endpoints

### Configuration System

Type-safe configuration with YAML support, environment variables, and preset management.

**Features:**
- Pydantic `BaseSettings` for type safety and validation
- YAML config file support with auto-loading
- Environment variable auto-loading (`.env` files)
- Dot-notation key access
- Preset system (8 predefined + custom presets)

**Example:**
```python
from shared_ai_utils.config import ConfigBase, ConfigManager, PresetManager

class MyConfig(ConfigBase):
    api_key: str
    debug: bool = False
    max_retries: int = 3

# Load from YAML or environment
config_manager = ConfigManager(config_path="~/.config/myapp/config.yaml")
config = config_manager.load(MyConfig)

# Use presets
preset = PresetManager.get_preset("development")
config_manager.apply_preset(preset)
```

**Predefined Presets:**
- `quick_test` - Minimal config for quick testing
- `development` - Development environment settings
- `testing` - Test environment configuration
- `staging` - Staging environment settings
- `production` - Production-ready configuration
- `high_performance` - Optimized for performance
- `low_resource` - Minimal resource usage
- `ml_development` - ML/AI development settings

### Assessment Engine

Evidence-based multi-path assessment system for explainable evaluation.

**Features:**
- Multi-path evaluation (Technical, Design, Collaboration, Problem-Solving, Communication)
- Evidence-based scoring with confidence levels
- Natural language explanations
- Extensible framework for ML integration
- Micro-motive tracking

**Example:**
```python
from shared_ai_utils.assessment import AssessmentEngine, AssessmentInput

engine = AssessmentEngine(enable_explanations=True)
input_data = AssessmentInput(
    candidate_id="dev-123",
    code_samples=["..."],
    test_results={...},
    collaboration_notes=["..."]
)
result = await engine.assess(input_data)

print(f"Overall Score: {result.overall_score}")
print(f"Confidence: {result.confidence}")
for path_score in result.path_scores:
    print(f"{path_score.path}: {path_score.score}")
```

### FastAPI Utilities

Production-ready FastAPI middleware and utilities for consistent API patterns.

**Features:**
- Request ID middleware for request tracing
- CORS validation with production safety checks
- Standardized error handling with custom error codes
- Health check endpoint utilities
- Request/response models

**Example:**
```python
from fastapi import FastAPI
from shared_ai_utils.api import (
    RequestIDMiddleware,
    create_cors_middleware,
    create_health_router,
    create_error_response
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Configure CORS
cors_config = create_cors_middleware(
    allowed_origins=["https://example.com"],
    app_env="production"
)
app.add_middleware(CORSMiddleware, **cors_config)

# Add health check
health_router = create_health_router(version="1.0.0")
app.include_router(health_router)

# Use standardized errors
@app.get("/api/data")
async def get_data():
    try:
        # ... your logic
        pass
    except ValueError as e:
        raise create_error_response(
            error_code="INVALID_INPUT",
            message=str(e),
            status_code=400
        )
```

### Pattern Management

Pattern library system with versioning, effectiveness tracking, and semantic search.

**Features:**
- CRUD operations for patterns
- Pattern versioning and archiving
- Effectiveness tracking
- MemU integration for semantic search
- Pattern recommendations

**Example:**
```python
from shared_ai_utils.patterns import PatternManager

manager = PatternManager(pattern_library_path="patterns.json")

# Add a pattern
pattern = manager.add_pattern(
    name="async-error-handling",
    description="Proper async error handling pattern",
    good_example="async def fetch_data(): ...",
    bad_example="def fetch_data(): ...",
    tags=["async", "error-handling", "python"]
)

# Search patterns
suggestions = manager.suggest_patterns("error handling in async code")
for pattern in suggestions:
    print(f"{pattern['name']}: {pattern['description']}")
```

### CLI Framework

Rich terminal utilities and interactive wizards for command-line applications.

**Features:**
- Rich table formatting with colors
- Interactive setup wizards
- Command structure helpers
- Output formatting utilities
- Progress indicators

**Example:**
```python
from shared_ai_utils.cli import print_table, print_success, SetupWizard

# Print formatted table
data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 87}
]
print_table(data, title="Assessment Results")

# Interactive wizard
wizard = SetupWizard()
wizard.add_step("api_key", "Enter your API key", required=True)
wizard.add_step("debug", "Enable debug mode?", input_type="boolean")
results = wizard.run()
```

## Documentation

- **[API Reference](API_REFERENCE.md)** - Comprehensive API documentation with detailed examples for all components
- **[Migration Guide](MIGRATION_GUIDE.md)** - Step-by-step guide for adopting shared-ai-utils in your repository

For quick reference, see the component examples in the [Components](#components) section above.

## Testing

The package includes comprehensive unit and integration tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=shared_ai_utils --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

## Contributing

When adding new components:

1. Follow the existing module structure
2. Add comprehensive type hints
3. Include docstrings for all public APIs
4. Write unit tests with >80% coverage
5. Update this README with examples

## Dependencies

**Core:**
- `pydantic>=2.0.0` - Type validation
- `pydantic-settings>=2.1.0` - Settings management
- `pyyaml>=6.0.0` - YAML support
- `python-dotenv>=1.0.0` - Environment variable loading
- `click>=8.0.0` - CLI framework
- `rich>=13.0.0` - Rich terminal output
- `httpx>=0.24.0` - HTTP client
- `fastapi>=0.100.0` - Web framework
- `uvicorn>=0.23.0` - ASGI server

**Optional:**
- `anthropic>=0.18.0` - Anthropic API
- `openai>=1.0.0` - OpenAI API
- `google-generativeai>=0.3.0` - Google Gemini API
- `memu-py>=0.1.0` - MemU semantic search

## License

MIT License

## Related Projects

This package consolidates functionality from:
- `feedback-loop` - Pattern management and MemU integration
- `council-ai` - LLM provider abstraction and CLI framework
- `sono-eval` - Assessment engine and FastAPI utilities
- `tex-assist-coding` - Documentation patterns
