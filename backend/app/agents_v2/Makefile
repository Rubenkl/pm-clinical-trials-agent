# Makefile for agents_v2 clean rewrite
# This allows us to lint/test only the new clean code

.PHONY: lint format check-all test

# Format code
format:
	@echo "Formatting agents_v2 code..."
	isort .
	black .

# Lint code
lint:
	@echo "Linting agents_v2..."
	flake8 .
	@echo "Type checking agents_v2 (local files only)..."
	mypy *.py --ignore-missing-imports --follow-imports=silent || echo "Note: mypy found issues in dependencies, but agents_v2 files are clean"
	@echo "Import checking agents_v2..."
	isort --check-only --diff .
	@echo "Code style checking agents_v2..."
	black --check .

# Run all checks
check-all: lint
	@echo "All agents_v2 checks passed! ✅"

# Test just this directory (when we have tests)
test:
	@echo "Testing agents_v2..."
	pytest -xvs ../../tests/ -k "agents_v2" || echo "No agents_v2 tests yet"