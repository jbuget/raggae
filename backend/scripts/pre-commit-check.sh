#!/bin/bash
set -e

echo "Running tests..."
pytest

echo "Formatting code..."
ruff format src/ tests/

echo "Linting..."
ruff check src/ tests/

echo "Type checking..."
mypy src/

echo "All checks passed!"
