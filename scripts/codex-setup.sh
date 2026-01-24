#!/usr/bin/env bash
# Codex environment setup script for shared-ai-utils
# This script runs automatically when Codex creates or resumes a container

set -e

echo "🔧 Shared AI Utils - Codex Environment Setup"
echo "============================================="
echo ""

# Change to workspace directory
cd /workspace/shared-ai-utils || cd "$(dirname "$0")/.." || exit 1

echo "📦 Installing/upgrading pip..."
python3 -m pip install --upgrade pip --quiet

echo "📦 Installing shared-ai-utils with dev dependencies..."
# Install in editable mode with dev extras (includes pytest, black, ruff, mypy)
pip install -e ".[dev]" --quiet

# Install pre-commit hooks (optional - don't fail if it's not critical)
echo "🔧 Setting up pre-commit hooks..."
pre-commit install || echo "⚠️  Pre-commit install skipped (non-critical)"

# Verify installation
echo "✅ Verifying installation..."
python3 -c "import shared_ai_utils; print('✓ shared-ai-utils installed')" || echo "⚠️  Version check skipped"

# Quick sanity check - run a fast test subset (don't fail setup on test failures)
echo "🧪 Running quick sanity check..."
pytest -q --co -q > /dev/null 2>&1 && echo "✓ Test discovery successful" || echo "⚠️  Test discovery check skipped"

echo ""
echo "✅ Setup complete! Environment ready for shared-ai-utils development and testing."
echo ""
echo "Quick commands:"
echo "  pytest                    # Run all tests"
echo "  black src/                 # Format code"
echo "  ruff check src/            # Lint code"
echo "  mypy src/                  # Type check"
echo "  pre-commit run --all-files # Run all pre-commit hooks"
echo ""
