# Migration Guide: Adopting shared-ai-utils

**Last Updated**: 2026-01-24

This guide helps you migrate your repository to use shared-ai-utils components, based on successful migrations from council-ai and other repositories.

---

## Table of Contents

- [Overview](#overview)
- [Migration Checklist](#migration-checklist)
- [LLM Provider Migration](#llm-provider-migration)
- [Configuration Migration](#configuration-migration)
- [Pattern Management Migration](#pattern-management-migration)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Testing Your Migration](#testing-your-migration)

---

## Overview

shared-ai-utils consolidates common functionality across multiple repositories:

- **LLM Providers**: Unified interface for Anthropic, OpenAI, Gemini, and custom HTTP endpoints
- **Configuration**: Type-safe YAML/environment variable management with presets
- **Pattern Management**: Pattern library with versioning and semantic search
- **FastAPI Utilities**: Production-ready middleware and error handling
- **Assessment Engine**: Multi-path evaluation system
- **CLI Framework**: Rich terminal utilities and wizards

### Benefits of Migration

- **Reduced Duplication**: Single source of truth for common functionality
- **Consistency**: Same patterns across all repositories
- **Maintainability**: Bug fixes and improvements benefit all repositories
- **Type Safety**: Pydantic-based validation and type hints
- **Better Testing**: Shared test infrastructure

---

## Migration Checklist

- [ ] Add shared-ai-utils as dependency
- [ ] Migrate LLM provider code (if applicable)
- [ ] Migrate configuration management (if applicable)
- [ ] Update imports throughout codebase
- [ ] Update tests to use new interfaces
- [ ] Verify backward compatibility
- [ ] Update documentation
- [ ] Run full test suite

---

## LLM Provider Migration

### Before (Custom Implementation)

```python
# Old code
from anthropic import Anthropic
from openai import OpenAI

class LLMService:
    def __init__(self, provider="anthropic"):
        if provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate(self, prompt: str):
        if self.provider == "anthropic":
            response = await self.client.messages.create(...)
        elif self.provider == "openai":
            response = await self.client.chat.completions.create(...)
        return response.content
```

### After (Using shared-ai-utils)

```python
# New code
from shared_ai_utils.llm import LLMManager

# Initialize once
llm_manager = LLMManager(preferred_provider="anthropic")

# Use unified interface
response = await llm_manager.generate(
    user_prompt=prompt,
    max_tokens=500
)
print(response.text)
```

### Step-by-Step Migration

1. **Add dependency** to `pyproject.toml`:

```toml
[project]
dependencies = [
    "shared-ai-utils[llm]>=0.1.0",
]
```

2. **Replace provider initialization**:

```python
# Old
from your_app.providers import CustomLLMProvider
provider = CustomLLMProvider(api_key="...")

# New
from shared_ai_utils.llm import LLMManager
manager = LLMManager(preferred_provider="anthropic")
```

3. **Update method calls**:

```python
# Old
result = await provider.complete(prompt, max_tokens=100)

# New
response = await manager.generate(
    user_prompt=prompt,
    max_tokens=100
)
result = response.text
```

4. **Handle response objects**:

```python
# Old response might be a string
text = result

# New response is LLMResponse object
text = response.text
tokens = response.tokens_used
provider_used = response.provider
```

### Maintaining Backward Compatibility

If you need to maintain the old interface temporarily:

```python
from shared_ai_utils.llm import LLMManager

class LegacyLLMService:
    """Wrapper to maintain old interface"""
    
    def __init__(self, provider="anthropic"):
        self.manager = LLMManager(preferred_provider=provider)
        self.provider = provider
    
    async def generate(self, prompt: str):
        response = await self.manager.generate(user_prompt=prompt)
        return response.text  # Return string for compatibility
```

---

## Configuration Migration

### Before (Custom Config)

```python
# Old code
import yaml
import os
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.data = yaml.safe_load(f)
        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith("APP_"):
                self.data[key[4:].lower()] = value
    
    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.data
        for k in keys:
            value = value.get(k, {})
        return value if value else default
```

### After (Using shared-ai-utils)

```python
# New code
from shared_ai_utils.config import ConfigBase, ConfigManager
from pydantic import Field

class AppConfig(ConfigBase):
    api_key: str = Field(..., description="API key")
    debug: bool = Field(default=False)
    max_retries: int = Field(default=3, ge=1, le=10)

# Load configuration
config_manager = ConfigManager(config_path="config.yaml")
config = config_manager.load(AppConfig)

# Access with type safety
print(config.api_key)  # Type-checked
print(config.debug)    # Type-checked
```

### Step-by-Step Migration

1. **Define your config class**:

```python
from shared_ai_utils.config import ConfigBase
from pydantic import Field

class MyAppConfig(ConfigBase):
    # Required fields
    api_key: str
    
    # Optional fields with defaults
    debug: bool = False
    timeout: float = 30.0
    
    # Validated fields
    max_retries: int = Field(default=3, ge=1, le=10)
```

2. **Update config loading**:

```python
# Old
config = load_config("config.yaml")

# New
from shared_ai_utils.config import ConfigManager
config_manager = ConfigManager("config.yaml")
config = config_manager.load(MyAppConfig)
```

3. **Update config access**:

```python
# Old (dict access)
api_key = config["api"]["key"]
debug = config.get("debug", False)

# New (attribute access with type safety)
api_key = config.api_key
debug = config.debug
```

4. **Handle nested config**:

```python
# For nested config, use dot notation in ConfigManager
nested_value = config_manager.get("api.provider.key")

# Or define nested Pydantic models
class ProviderConfig(ConfigBase):
    key: str
    model: str

class AppConfig(ConfigBase):
    api: ProviderConfig
```

### Preserving YAML Structure

Your existing YAML files will work without changes:

```yaml
# config.yaml (works as-is)
api_key: "your-key"
debug: false
max_retries: 3
timeout: 30.0
```

Environment variables still override YAML values:

```bash
# .env or environment
API_KEY=production-key
DEBUG=true
```

---

## Pattern Management Migration

### Before (Custom Pattern Storage)

```python
# Old code
import json

class PatternLibrary:
    def __init__(self, file_path: str):
        with open(file_path) as f:
            self.patterns = json.load(f)
    
    def add_pattern(self, name: str, description: str, example: str):
        self.patterns[name] = {
            "description": description,
            "example": example
        }
        self.save()
    
    def search(self, query: str):
        # Simple text search
        return [p for p in self.patterns.values() 
                if query.lower() in p["description"].lower()]
```

### After (Using shared-ai-utils)

```python
# New code
from shared_ai_utils.patterns import PatternManager

manager = PatternManager(pattern_library_path="patterns.json")

# Add pattern with versioning
pattern = manager.add_pattern(
    name="async-error-handling",
    description="Proper async error handling",
    good_example="...",
    bad_example="...",
    tags=["async", "python"]
)

# Semantic search
suggestions = manager.suggest_patterns("error handling")
```

### Step-by-Step Migration

1. **Install with pattern support**:

```toml
[project]
dependencies = [
    "shared-ai-utils[patterns]>=0.1.0",
]
```

2. **Migrate pattern storage**:

```python
# Old
patterns = load_patterns("patterns.json")

# New
from shared_ai_utils.patterns import PatternManager
manager = PatternManager("patterns.json")
```

3. **Update pattern operations**:

```python
# Old
add_pattern(name, description, example)

# New
manager.add_pattern(
    name=name,
    description=description,
    good_example=example,
    tags=["python"]
)
```

---

## Common Issues and Solutions

### Issue 1: Import Errors

**Problem**: `ImportError: cannot import name 'LLMManager'`

**Solution**: Ensure shared-ai-utils is installed with the correct extras:

```bash
pip install "shared-ai-utils[llm]>=0.1.0"
```

### Issue 2: Configuration Validation Errors

**Problem**: `ValidationError` when loading config

**Solution**: Check that your config class matches your YAML structure:

```python
# Ensure field names match YAML keys (case-sensitive)
class Config(ConfigBase):
    api_key: str  # Matches "api_key" in YAML, not "apiKey"
```

### Issue 3: Provider Fallback Not Working

**Problem**: Falls back immediately instead of trying preferred provider

**Solution**: Check API keys are set correctly:

```python
# Verify API keys are available
import os
print(os.getenv("ANTHROPIC_API_KEY"))  # Should not be None

# Or check provider availability
from shared_ai_utils.llm import LLMManager
manager = LLMManager(preferred_provider="anthropic")
available = manager.check_provider_availability("anthropic")
```

### Issue 4: Type Errors with Config

**Problem**: `AttributeError` or type errors accessing config

**Solution**: Use Pydantic models, not dict access:

```python
# Wrong
value = config["key"]  # Dict access doesn't work

# Right
value = config.key  # Attribute access with type checking
```

### Issue 5: Pattern Search Returns Empty

**Problem**: `suggest_patterns()` returns no results

**Solution**: Ensure MemU is configured (optional but recommended):

```bash
pip install "shared-ai-utils[memu]>=0.1.0"
```

Or use tag-based search as fallback:

```python
# Fallback to tag search
patterns = manager.search_by_tags(["python", "async"])
```

---

## Testing Your Migration

### Unit Tests

```python
import pytest
from shared_ai_utils.llm import LLMManager
from shared_ai_utils.config import ConfigManager, ConfigBase

class TestConfig(ConfigBase):
    api_key: str
    debug: bool = False

def test_config_loading():
    config_manager = ConfigManager("test_config.yaml")
    config = config_manager.load(TestConfig)
    assert config.api_key is not None
    assert isinstance(config.debug, bool)

@pytest.mark.asyncio
async def test_llm_generation():
    manager = LLMManager(preferred_provider="anthropic")
    response = await manager.generate(
        user_prompt="Test",
        max_tokens=10
    )
    assert response.text is not None
    assert response.tokens_used > 0
```

### Integration Tests

```python
def test_migration_backward_compatibility():
    """Test that old code still works with adapter"""
    from your_app.legacy import LegacyLLMService
    
    service = LegacyLLMService(provider="anthropic")
    result = await service.generate("test")
    
    # Should return string (old interface)
    assert isinstance(result, str)
    assert len(result) > 0
```

### Smoke Tests

```bash
# Test CLI commands still work
python -m your_app.cli --help

# Test API endpoints
curl http://localhost:8000/health

# Test configuration loading
python -c "from your_app.config import load_config; print(load_config())"
```

---

## Real-World Example: council-ai Migration

Council-AI successfully migrated to shared-ai-utils. Here's what changed:

### Files Modified

1. **`pyproject.toml`**: Added shared-ai-utils dependency
2. **`src/council_ai/providers/__init__.py`**: Replaced custom providers with shared-ai-utils
3. **`src/council_ai/core/council.py`**: Updated to use LLMManager
4. **`src/council_ai/core/config.py`**: Replaced with ConfigManager

### Key Changes

```python
# Before
from council_ai.providers import AnthropicProvider, OpenAIProvider
provider = AnthropicProvider(api_key="...")

# After
from shared_ai_utils.llm import LLMManager
manager = LLMManager(preferred_provider="anthropic")
```

### Migration Timeline

- **Day 1**: Add dependency, create adapter layer
- **Day 2**: Migrate LLM provider code
- **Day 3**: Migrate configuration management
- **Day 4**: Update tests, verify compatibility
- **Day 5**: Remove old code, update documentation

### Lessons Learned

1. **Start with adapter layer** to maintain backward compatibility
2. **Migrate incrementally** - one module at a time
3. **Keep old code** until migration is fully tested
4. **Update tests first** to catch breaking changes early

---

## Next Steps

After migration:

1. **Update documentation** to reflect new dependencies
2. **Remove old code** once migration is verified
3. **Update CI/CD** to test with shared-ai-utils
4. **Share feedback** with the shared-ai-utils maintainers

---

## Getting Help

- **Documentation**: See [README.md](README.md) and [API_REFERENCE.md](API_REFERENCE.md)
- **Issues**: Report problems on the shared-ai-utils repository
- **Examples**: Check council-ai for a complete migration example

---

**Note**: This guide is based on the council-ai migration experience. Your migration may vary based on your specific use case.
