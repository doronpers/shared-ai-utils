# Security Policy

## Supported Versions

Currently, shared-ai-utils is in **alpha** (version 0.1.0). Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@sonotheia.com**

When reporting a vulnerability, please include:

1. **Type of vulnerability** (e.g., XSS, SQL injection, dependency vulnerability, etc.)
2. **Full paths** of affected source files
3. **Location** of the affected code (tag/branch/commit)
4. **Step-by-step instructions** to reproduce the issue
5. **Proof-of-concept or exploit code** (if possible)
6. **Impact** of the vulnerability
7. **Suggested fix** (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: Next release cycle

## Security Best Practices

### API Key Management

**CRITICAL: Never commit API keys to version control**

1. **Use environment variables only**

   ```bash
   export ANTHROPIC_API_KEY='your-key'
   export OPENAI_API_KEY='your-key'
   export GEMINI_API_KEY='your-key'
   ```

2. **Secure storage**
   - Use secret management tools (AWS Secrets Manager, HashiCorp Vault, etc.)
   - For local development, use `.env` files (ensure `.gitignore` includes them)
   - For CI/CD, use encrypted secrets

3. **Key rotation**
   - Rotate API keys every 90 days
   - Immediately rotate if compromised
   - Use different keys for dev/staging/prod

### Dependency Security

**Regular Updates**: Check for vulnerabilities

```bash
# Install safety
pip install safety

# Check dependencies
safety check

# Or use pip-audit
pip install pip-audit
pip-audit
```

**Known Issues**:

- Review `pyproject.toml` regularly
- Update dependencies with security patches
- Use `dependabot` for automated alerts

### Secret Management

**NEVER commit**:

- API keys
- Passwords
- Private keys
- `.env` files
- Database credentials

**Use**:

- Environment variables
- Secret management services (AWS Secrets Manager, HashiCorp Vault)
- `.env.example` for documentation (without real values)

### Input Validation

All user inputs should be validated using Pydantic models:

```python
from pydantic import BaseModel, Field, validator

class ConfigInput(BaseModel):
    api_key: str = Field(..., min_length=1)

    @validator('api_key')
    def validate_api_key(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('api_key must be alphanumeric')
        return v
```

### Logging and Monitoring

**Do Log**:

- Authentication attempts
- Authorization failures
- Input validation failures
- System errors

**Don't Log**:

- Passwords
- API keys
- Personal identifiable information (PII)
- Session tokens

```python
# GOOD
logger.info(f"API request for endpoint: {endpoint}")

# BAD
logger.info(f"API request with key: {api_key}")
```

## Security Features

### Built-in Protections

1. **Input validation**: Pydantic models for type safety
2. **API key isolation**: Keys never logged or exposed
3. **Error handling**: Graceful degradation without exposing internals
4. **Type safety**: Comprehensive type hints

### Secure Defaults

- LLM features require explicit API key setup
- No telemetry or data collection without consent
- Local-first operation by default
- Minimal network exposure

## Security Checklist

Before deploying to production:

- [ ] API keys stored securely (not in code)
- [ ] Different keys for dev/staging/prod
- [ ] Dependencies updated and scanned
- [ ] `.env` files in `.gitignore`
- [ ] Security policies reviewed with team
- [ ] Monitoring and alerting configured
- [ ] Access controls implemented
- [ ] Audit logging enabled (if required)

## Security Resources

### Tools

- **Safety**: Dependency vulnerability scanner
- **pip-audit**: Python package vulnerability auditor
- **Bandit**: Python security linter
- **Trivy**: Container vulnerability scanner

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Pydantic Security](https://docs.pydantic.dev/latest/concepts/security/)

## Contact

For security concerns, contact: **security@sonotheia.com**

For general issues: <https://github.com/doronpers/shared-ai-utils/issues>

---

**Last Updated**: January 2026
**Version**: 0.1.0
