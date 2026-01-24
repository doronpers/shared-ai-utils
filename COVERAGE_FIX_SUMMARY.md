# Coverage Measurement Fix - shared-ai-utils

**Date:** 2026-01-23  
**Status:** ✅ Configuration Fixed | ⚠️ Code Errors Blocking Test Execution

---

## Problem

Coverage was showing 0% because it was tracking the installed package from site-packages instead of local source files in `src/shared_ai_utils/`.

---

## Solution Implemented

### 1. Added Coverage Configuration
Added `[tool.coverage.run]` section to `pyproject.toml`:
```toml
[tool.coverage.run]
source = ["src/shared_ai_utils"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/test_*.py",
    "*/conftest.py",
]
branch = true
```

### 2. Added Pytest Pythonpath
Added `pythonpath = ["src"]` to `[tool.pytest.ini_options]` to ensure tests can find local source.

### 3. Installed in Editable Mode
Installed package in editable mode: `pip install -e .`
- This ensures imports use local source when available
- Verified: `Editable project location: /Volumes/Treehorn/Gits/shared-ai-utils`

### 4. Fixed Code Errors
Fixed missing type imports:
- `src/shared_ai_utils/api/auth.py`: Added `Callable` to typing imports
- `src/shared_ai_utils/docs/hub.py`: Added `Any` to typing imports

---

## Verification

### Coverage Configuration
✅ Coverage is now tracking local source files:
- Files tracked: `src/shared_ai_utils/` (verified in coverage.json)
- Configuration: `source = ["src/shared_ai_utils"]` ✅
- Pythonpath: `["src"]` ✅

### Current Status
- ✅ **Coverage Configuration:** Fixed and working
- ✅ **Source Tracking:** Correctly tracking `src/shared_ai_utils/`
- ⚠️ **Test Execution:** Blocked by code errors (circular imports)
- ⚠️ **Coverage Percentage:** 0% (tests can't run due to code errors, not config issue)

---

## Remaining Issues

### Code Errors Blocking Tests
1. **Circular Import:** `shared_ai_utils.onboarding.intent_detector` → `shared_ai_utils.cli`
   - Error: `cannot import name 'print_table' from partially initialized module`
   - **Location:** `src/shared_ai_utils/onboarding/intent_detector.py:15`

2. **Test Failures:** 5 tests still failing (separate from coverage issue)
   - `test_config.py::TestConfigManager::test_load_config_from_file`
   - `test_llm_providers.py` (4 tests)

---

## Next Steps

### Immediate (To Get Coverage Working)
1. **Fix Circular Import**
   - Resolve `intent_detector.py` → `cli` circular dependency
   - Options: Move functions, use lazy imports, refactor structure

2. **Fix Remaining Code Errors**
   - Ensure all type imports are present
   - Fix any other import issues

### Once Tests Can Run
1. **Verify Coverage Measurement**
   - Run: `pytest tests/ --cov=src/shared_ai_utils --cov-report=term`
   - Should show actual coverage percentage (estimated 20-30%)

2. **Fix Test Failures**
   - Address 5 failing tests
   - Update tests to match current API

---

## Configuration Changes Made

### pyproject.toml
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]  # ADDED
# ... existing config ...

[tool.coverage.run]  # ADDED
source = ["src/shared_ai_utils"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/test_*.py",
    "*/conftest.py",
]
branch = true

[tool.coverage.report]  # ADDED
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

### Code Fixes
- `src/shared_ai_utils/api/auth.py`: Added `Callable` import
- `src/shared_ai_utils/docs/hub.py`: Added `Any` import

---

## Verification Commands

```bash
# Verify coverage tracks local source
cd /Volumes/Treehorn/Gits/shared-ai-utils
python -c "import json; data = json.load(open('coverage.json')); files = [f for f in data.get('files', {}).keys() if f.startswith('src/')]; print(f'Local files tracked: {len(files)}')"

# Once code errors fixed, run:
pytest tests/ --cov=src/shared_ai_utils --cov-report=term
# Should show actual coverage percentage
```

---

**Status:** ✅ Coverage configuration fixed. Code errors need resolution before tests can run and show accurate coverage.
