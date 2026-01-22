## 1. Operational Guardrails

* **Config**: `pyproject.toml` is the source of truth for tooling. `settings.yaml` (or equivalent) for app config.
* **Audio**: Float32 mono 16kHz numpy arrays only.
* **Dependencies**: Lock versions. Do not upgrade without explicit instruction. Use pragmatic dependency management - avoid unnecessary dependencies, but framework dependencies (e.g., FastAPI for API modules) are acceptable when appropriate.

### Dependency Tiers

Minimize dependencies while allowing appropriate framework usage:

* **Core Modules** (sensors, VAD, JSON utils): `numpy` + `pydantic` only
* **CLI Modules**: Core + `Rich`, `Click` (interactive formatting)
* **API/Assessment Modules**: Core + `FastAPI`, `textstat`, lightweight analysis libraries
* **Avoid**: Vendor-specific SDKs, heavy ML frameworks (TensorFlow/PyTorch), libraries with C extensions (unless critical)

**Guideline**: Core contracts remain dependency-free. API-specific modules may include framework dependencies when they provide clear net gain over manual implementation.
