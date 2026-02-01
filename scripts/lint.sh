#!/bin/bash
# Linting script (like npm run lint)

echo "🔍 Running Ruff linter..."
.venv/bin/ruff check . --statistics

echo ""
echo "💡 To auto-fix issues, run: ./scripts/lint-fix.sh"
