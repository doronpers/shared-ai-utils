## 3. Common Pitfalls & Anti-Patterns

### Code Duplication

* **Duplicate Logic**: Do not copy-paste LLM handling or Config loading. Use `shared-ai-utils`.
* **Custom Providers**: Never implement custom LLM provider logic. Use `shared-ai-utils.LLMManager`.

### Error Handling

* **Silent Failures**: Never `except Exception: pass`. Log the error or re-raise.
* **Bare Except**: Use specific exception types: `except (TypeError, ValueError) as e:`

### Architecture

* **Global State**: Minimize module-level globals. Use dependency injection.
* **Magic Numbers**: Extract constants to a config or constants file.

### Environment & Tooling

* **Virtual Environments**: Always use `.venv` (not `venv`). Check for duplicates before creating new ones.
* **Pre-commit Hooks**: When updating Python versions, ensure pre-commit tool versions support it (e.g., `black 26.1.0+` for Python 3.13).
* **Version Conflicts**: If pre-commit fails with "invalid target-version", update the tool in `.pre-commit-config.yaml`, not `pyproject.toml`.
* **Bypassing Hooks**: Use `--no-verify` only for structural migrations, not to hide code quality issues.
* **IDE Setup**: Enable "Format on Save" and configure linter to use `.pre-commit-config.yaml` (see AGENT_KNOWLEDGE_BASE.md).
* **Bulk Operations**: Use `git diff --stat` to audit changes, then run `python3 -m compileall .` before committing (see AGENT_KNOWLEDGE_BASE.md).

### Import Management

* **Circular Imports**: Use Protocol pattern (typing.Protocol) for dependency-free interfaces.
* **Import Order**: Run `ruff check --fix` or `isort` to auto-fix import sorting issues.
