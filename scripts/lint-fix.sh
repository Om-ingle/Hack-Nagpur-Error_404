#!/bin/bash
# Auto-fix linting issues (like npm run lint:fix)

echo "🔧 Auto-fixing linting issues..."
.venv/bin/ruff check . --fix

echo ""
echo "🎨 Formatting code with Ruff..."
.venv/bin/ruff format .

echo ""
echo "✅ Done! Run ./scripts/lint.sh to verify"
