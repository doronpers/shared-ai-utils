---
description: Pre-task instructions for all agents working on shared-ai-utils
---

# Before Starting Any Task

Before making ANY changes, read the `CONTRIBUTING.md` file in the repository root.

```bash
cat CONTRIBUTING.md
```

This file contains critical instructions including:

1. Coding standards (black, type hints)
2. Project structure
3. Development workflows
4. Testing requirements

## Verification

After completing your task, run the pre-commit checklist:

```bash
# Format code
black src/

# Check YAML (if applicable)
yamllint .

# Run all pre-commit hooks (final check, if configured)
pre-commit run --all-files
```

**CRITICAL**: See `.agent/workflows/pre-commit-checklist.md` for detailed requirements to prevent commit failures.
