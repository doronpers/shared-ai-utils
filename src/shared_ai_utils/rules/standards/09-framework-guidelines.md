## 9. Framework Guidelines

To ensure consistency and maintainability across the workspace, adherence to these framework choices is **mandatory**.

### Frontend Stack

* **Core**: React 18+
* **UI Library**: Material UI (MUI) 5+
* **State**: Context API or Zustand (avoid Redux unless necessary)
* **Build**: Vite (preferred over CRA)

**Anti-Pattern**: Do not mix UI libraries (e.g., Tailwind + MUI) without explicit approval. Stick to the MUI system for theming and layout.

### Backend Stack

* **Framework**: FastAPI
* **Validation**: Pydantic v2 (Strict mode preferred)
* **ORM**: SQLAlchemy 2.0+ (Async)
* **Task Queue**: Celery or ARQ

### Testing

* **Unit/Integration**: Pytest
* **E2E**: Playwright
* **Mocking**: `unittest.mock` or `pytest-mock`
