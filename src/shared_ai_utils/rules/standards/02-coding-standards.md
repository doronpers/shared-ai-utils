## 2. Coding Standards (The "Gold Standard")

* **Python**:
  * **Formatter**: `black` (line-length: 100)
  * **Linter**: `ruff` (Select: E, F, I, N, W, B). Imports must be sorted (`I`).
  * **Typing**: `mypy` required for all new code.
  * **Style**: Use `snake_case` for functions and variables, `PascalCase` for classes.
* **Frontend**:
  * **Framework**: React 18 + MUI 5
  * **Style**: Use `camelCase` for JavaScript variables and functions, `PascalCase` for components.
* **Structure**:
  * **src-layout**: All code lives in `src/<package_name>/`.
  * **No Root Scripts**: Scripts belong in `scripts/` or `bin/`.
* **Configuration**: `backend/config/settings.yaml` is the SINGLE source of truth for application configuration.
