# Shared AI Utils - API Reference

**Last Updated**: 2026-01-24

This document provides comprehensive API reference documentation with detailed examples for all major components of shared-ai-utils.

---

## Table of Contents

- [LLM Module](#llm-module)
- [Configuration Module](#configuration-module)
- [Assessment Module](#assessment-module)
- [FastAPI Utilities](#fastapi-utilities)
- [Pattern Management](#pattern-management)
- [Error Handling](#error-handling)
- [CLI Framework](#cli-framework)

---

## LLM Module

### LLMManager

The `LLMManager` provides a unified interface for multiple LLM providers with automatic fallback.

#### Basic Usage

```python
from shared_ai_utils.llm import LLMManager

# Initialize with preferred provider
manager = LLMManager(preferred_provider="anthropic")

# Generate a response
response = await manager.generate(
    system_prompt="You are a helpful assistant.",
    user_prompt="Explain async/await in Python",
    max_tokens=500
)

print(f"Response: {response.text}")
print(f"Tokens used: {response.tokens_used}")
print(f"Provider used: {response.provider}")
```

#### Automatic Fallback

```python
# If Anthropic is unavailable, automatically falls back to OpenAI, then Gemini
manager = LLMManager(
    preferred_provider="anthropic",
    fallback_providers=["openai", "gemini"]
)

# Will try Anthropic first, then fallback if needed
response = await manager.generate(
    user_prompt="What is machine learning?",
    max_tokens=300
)
```

#### Structured Output

```python
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str
    age: int
    email: str

# Request structured JSON output
response = await manager.generate(
    user_prompt="Extract user information: John, 30, john@example.com",
    response_format=UserInfo,
    max_tokens=200
)

user = response.structured_output  # Returns UserInfo instance
print(f"Name: {user.name}, Age: {user.age}")
```

#### Streaming Responses

```python
async for chunk in manager.generate_stream(
    user_prompt="Write a short story about AI",
    max_tokens=1000
):
    print(chunk.text, end="", flush=True)
```

#### Custom Provider Configuration

```python
from shared_ai_utils.llm import LLMManager, AnthropicProvider

# Use specific model
manager = LLMManager(
    preferred_provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)

# Or configure provider directly
provider = AnthropicProvider(
    api_key="your-key",
    model="claude-3-opus-20240229",
    temperature=0.7,
    max_tokens=1000
)
manager = LLMManager(providers=[provider])
```

#### Error Handling

```python
from shared_ai_utils.llm import LLMError

try:
    response = await manager.generate(
        user_prompt="Test prompt",
        max_tokens=100
    )
except LLMError as e:
    print(f"LLM Error: {e.message}")
    print(f"Provider: {e.provider}")
    print(f"Retryable: {e.retryable}")
```

---

## Configuration Module

### ConfigManager

Type-safe configuration management with YAML and environment variable support.

#### Basic Configuration

```python
from shared_ai_utils.config import ConfigBase, ConfigManager
from pydantic import Field

class AppConfig(ConfigBase):
    api_key: str = Field(..., description="API key for external service")
    debug: bool = Field(default=False, description="Enable debug mode")
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout: float = Field(default=30.0, gt=0)

# Load from YAML file
config_manager = ConfigManager(config_path="~/.config/myapp/config.yaml")
config = config_manager.load(AppConfig)

print(f"API Key: {config.api_key[:10]}...")
print(f"Debug: {config.debug}")
```

#### Environment Variable Override

```python
# config.yaml
# api_key: "default-key"
# debug: false

# .env file or environment
# API_KEY=production-key
# DEBUG=true

# Environment variables override YAML values
config = config_manager.load(AppConfig)
assert config.api_key == "production-key"
assert config.debug == True
```

#### Dot Notation Access

```python
# Access nested config values
api_key = config_manager.get("api.provider.anthropic.key")
model = config_manager.get("api.provider.anthropic.model", default="claude-3-sonnet")

# Set values programmatically
config_manager.set("api.provider.anthropic.key", "new-key")
config_manager.save()  # Persist to YAML
```

#### Presets

```python
from shared_ai_utils.config import PresetManager

# Apply a preset
preset = PresetManager.get_preset("development")
config_manager.apply_preset(preset)

# List available presets
presets = PresetManager.list_presets()
for preset_name in presets:
    print(f"- {preset_name}")

# Create custom preset
custom_preset = {
    "debug": True,
    "max_retries": 5,
    "timeout": 60.0
}
PresetManager.save_preset("my_custom", custom_preset)
```

#### Configuration Validation

```python
from pydantic import ValidationError

try:
    config = config_manager.load(AppConfig)
except ValidationError as e:
    print("Configuration validation failed:")
    for error in e.errors():
        print(f"  {error['loc']}: {error['msg']}")
```

---

## Assessment Module

### AssessmentEngine

Evidence-based multi-path assessment system.

#### Basic Assessment

```python
from shared_ai_utils.assessment import AssessmentEngine, AssessmentInput

engine = AssessmentEngine(enable_explanations=True)

input_data = AssessmentInput(
    candidate_id="dev-123",
    content="def calculate_total(items): return sum(item.price for item in items)",
    paths=["technical", "design"]
)

result = await engine.assess(input_data)

print(f"Overall Score: {result.overall_score:.2f}")
print(f"Confidence: {result.confidence:.2f}")

for path_score in result.path_scores:
    print(f"{path_score.path}: {path_score.score:.2f}")
    print(f"  Evidence: {path_score.evidence}")
```

#### Multi-Path Assessment

```python
input_data = AssessmentInput(
    candidate_id="candidate-456",
    code_samples=["sample1.py", "sample2.py"],
    test_results={"coverage": 0.85, "tests_passing": 42},
    collaboration_notes=["Worked well in team", "Good code reviews"],
    paths=["technical", "design", "collaboration", "problem_solving", "communication"]
)

result = await engine.assess(input_data)

# Access individual path scores
technical_score = next(
    (ps for ps in result.path_scores if ps.path == "technical"),
    None
)
if technical_score:
    print(f"Technical: {technical_score.score}")
    print(f"Explanation: {technical_score.explanation}")
```

#### Custom Scorers

```python
from shared_ai_utils.assessment.scorers import BaseScorer

class CustomScorer(BaseScorer):
    async def score(self, input_data: AssessmentInput, path: str) -> float:
        # Custom scoring logic
        return 0.85

engine = AssessmentEngine(
    enable_explanations=True,
    custom_scorers={"custom_path": CustomScorer()}
)
```

---

## FastAPI Utilities

### Request ID Middleware

```python
from fastapi import FastAPI
from shared_ai_utils.api import RequestIDMiddleware

app = FastAPI()

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

@app.get("/api/data")
async def get_data(request: Request):
    # Access request ID
    request_id = request.state.request_id
    return {"request_id": request_id, "data": "..."}
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware
from shared_ai_utils.api import create_cors_middleware

# Production-safe CORS
cors_config = create_cors_middleware(
    allowed_origins=["https://example.com", "https://app.example.com"],
    app_env="production"
)
app.add_middleware(CORSMiddleware, **cors_config)

# Development CORS (with warnings)
cors_config = create_cors_middleware(
    allowed_origins=["*"],
    app_env="development"  # Will log warning about wildcard
)
```

### Health Check Router

```python
from shared_ai_utils.api import create_health_router

# Create health check router
health_router = create_health_router(
    version="1.0.0",
    service_name="my-api",
    checks={
        "database": lambda: check_database(),
        "cache": lambda: check_redis()
    }
)
app.include_router(health_router, prefix="/health")
```

### Standardized Error Responses

```python
from shared_ai_utils.api import create_error_response, ErrorCode
from fastapi import HTTPException

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    user = await fetch_user(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                error_code=ErrorCode.NOT_FOUND,
                message=f"User {user_id} not found",
                status_code=404
            )
        )
    return user
```

---

## Pattern Management

### PatternManager

Pattern library with versioning and semantic search.

#### Adding Patterns

```python
from shared_ai_utils.patterns import PatternManager

manager = PatternManager(pattern_library_path="patterns.json")

# Add a new pattern
pattern = manager.add_pattern(
    name="async-error-handling",
    description="Proper async error handling with try/except",
    good_example="""
    async def fetch_data():
        try:
            result = await api.get()
            return result
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
    """,
    bad_example="""
    async def fetch_data():
        result = await api.get()  # No error handling
        return result
    """,
    tags=["async", "error-handling", "python"],
    category="error-handling"
)

print(f"Pattern ID: {pattern.id}")
print(f"Version: {pattern.version}")
```

#### Searching Patterns

```python
# Semantic search
suggestions = manager.suggest_patterns("error handling in async code")
for pattern in suggestions:
    print(f"{pattern['name']}: {pattern['description']}")
    print(f"  Relevance: {pattern['relevance']:.2f}")

# Tag-based search
patterns = manager.search_by_tags(["async", "python"])
for pattern in patterns:
    print(f"- {pattern.name}")
```

#### Pattern Versioning

```python
# Update a pattern (creates new version)
updated = manager.update_pattern(
    pattern_id="async-error-handling",
    description="Updated description with more details",
    good_example="..."  # Updated example
)

# Archive old version
manager.archive_pattern("async-error-handling", version=1)

# Get pattern history
history = manager.get_pattern_history("async-error-handling")
for version in history:
    print(f"Version {version.version}: {version.description}")
```

---

## Error Handling

### Error Recovery Framework

```python
from shared_ai_utils.errors import ErrorRecovery, format_error

# Automatic error recovery
recovery = ErrorRecovery()

try:
    result = await some_operation()
except Exception as e:
    # Get recovery steps
    recovery_steps = recovery.get_recovery_steps(e)
    
    if recovery_steps:
        print("Recovery steps available:")
        for step in recovery_steps:
            print(f"  - {step.action}: {step.description}")
    else:
        # Format error for display
        formatted = format_error(e, context="API call")
        print(formatted)
```

### Contextual Help

```python
from shared_ai_utils.errors import get_contextual_help

# Get help based on error context
help_text = get_contextual_help(
    error_type=ValueError,
    context="config_loading",
    user_input="invalid-api-key"
)

print(help_text)
```

---

## CLI Framework

### Rich Output Utilities

```python
from shared_ai_utils.cli import print_table, print_success, print_error, print_warning

# Print formatted table
data = [
    {"name": "Alice", "score": 95, "status": "passed"},
    {"name": "Bob", "score": 87, "status": "passed"},
    {"name": "Charlie", "score": 72, "status": "needs_work"}
]
print_table(data, title="Assessment Results")

# Status messages
print_success("Operation completed successfully")
print_error("Failed to connect to API")
print_warning("Rate limit approaching")
```

### Interactive Wizards

```python
from shared_ai_utils.cli import SetupWizard

wizard = SetupWizard(title="API Configuration")

# Add steps
wizard.add_step(
    "api_key",
    "Enter your API key",
    required=True,
    input_type="password"
)
wizard.add_step(
    "provider",
    "Select provider",
    input_type="choice",
    choices=["anthropic", "openai", "gemini"]
)
wizard.add_step(
    "debug",
    "Enable debug mode?",
    input_type="boolean",
    default=False
)

# Run wizard
results = wizard.run()

print(f"API Key: {results['api_key'][:10]}...")
print(f"Provider: {results['provider']}")
print(f"Debug: {results['debug']}")
```

---

## Additional Examples

### Complete FastAPI Application

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from shared_ai_utils.api import (
    RequestIDMiddleware,
    create_cors_middleware,
    create_health_router,
    create_error_response,
    ErrorCode
)
from shared_ai_utils.llm import LLMManager
from shared_ai_utils.config import ConfigManager, ConfigBase

class AppConfig(ConfigBase):
    api_key: str
    debug: bool = False

# Load configuration
config_manager = ConfigManager("config.yaml")
config = config_manager.load(AppConfig)

# Initialize LLM manager
llm_manager = LLMManager(preferred_provider="anthropic")

# Create FastAPI app
app = FastAPI(title="My API", version="1.0.0")

# Add middleware
app.add_middleware(RequestIDMiddleware)
cors_config = create_cors_middleware(
    allowed_origins=["https://example.com"],
    app_env="production"
)
app.add_middleware(CORSMiddleware, **cors_config)

# Add health check
health_router = create_health_router(version="1.0.0")
app.include_router(health_router)

# API endpoint
@app.post("/api/chat")
async def chat(request: Request, message: str):
    try:
        response = await llm_manager.generate(
            user_prompt=message,
            max_tokens=500
        )
        return {
            "response": response.text,
            "tokens_used": response.tokens_used,
            "request_id": request.state.request_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message=str(e),
                status_code=500
            )
        )
```

---

## Error Codes

Common error codes from `shared_ai_utils.api.ErrorCode`:

- `VALIDATION_ERROR` - Input validation failed
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded
- `INTERNAL_ERROR` - Internal server error
- `SERVICE_UNAVAILABLE` - External service unavailable

---

## Best Practices

1. **Always use async/await** with LLM operations for better performance
2. **Handle errors gracefully** using the error recovery framework
3. **Use type hints** for configuration classes (Pydantic validation)
4. **Enable structured output** when you need consistent response formats
5. **Configure CORS properly** for production (never use wildcard in production)
6. **Use request IDs** for tracing requests across services
7. **Version your patterns** when updating pattern library entries

---

For more information, see the [README.md](README.md) or check the source code documentation.
