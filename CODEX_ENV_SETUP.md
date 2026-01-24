# Codex Environment Setup for shared-ai-utils

Complete configuration guide for setting up a Codex development environment for `shared-ai-utils`.

## Quick Configuration

### 1. Name & Description
- **Name**: `shared-ai-utils / dev + tests`
- **Description**: `Full shared-ai-utils dev env with dependencies, pytest, linting, and cross-repo testing.`

### 2. Container Image & Workspace
- **Container image**: `universal`
- **Workspace directory**: `/workspace/shared-ai-utils` (default)

### 3. Setup Script & Caching
- **Setup script (Manual)**: `/workspace/shared-ai-utils/scripts/codex-setup.sh`
- **Container Caching**: `On`
- **Maintenance script**: `pip install -e ".[dev]"`

### 4. Environment Variables
```
SHARED_AI_UTILS_ENV=codex
PYTHONUNBUFFERED=1
PYTHONUTF8=1
```

### 5. Secrets (API Keys)
- `OPENAI_API_KEY` - For OpenAI provider testing
- `ANTHROPIC_API_KEY` - For Anthropic provider testing
- `GEMINI_API_KEY` - For Google Gemini provider testing

### 6. Agent Internet Access
- **Agent internet access**: `On`
- **Domain allowlist**: Start with `Common dependencies`, then add:
  - `api.openai.com`
  - `api.anthropic.com`
  - `generativelanguage.googleapis.com`
  - `pypi.org`
  - `files.pythonhosted.org`
  - `github.com`
  - `raw.githubusercontent.com`
- **Allowed HTTP Methods**: `All methods`

## Special Considerations

### Cross-Repo Testing
- shared-ai-utils is used by multiple repos (council-ai, feedback-loop, sono-eval)
- Test compatibility with dependent repos
- Consider testing integration scenarios
