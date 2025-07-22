#!/bin/bash
set -e

echo "🔍 Checking Python 3.11+..."
if ! python3 --version | grep -q "3.11"; then
  echo "❌ Python 3.11+ is required."
  exit 1
fi

echo "✅ Python version: $(python3 --version)"

echo "🔍 Checking for Poetry..."
if ! command -v poetry &>/dev/null; then
  echo "📦 Installing Poetry..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
else
  echo "✅ Poetry is installed: $(poetry --version)"
fi

echo "📦 Installing dependencies..."
poetry install

echo "✅ Setup complete. Use 'poetry shell' to activate environment."
