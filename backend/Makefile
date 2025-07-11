.PHONY: help install lint format test test-cov check-all clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make lint      - Run all linters (flake8, mypy, isort check, black check)"
	@echo "  make format    - Auto-format code with black and isort"
	@echo "  make test      - Run tests"
	@echo "  make test-cov  - Run tests with coverage"
	@echo "  make check-all - Run all checks (lint + test)"
	@echo "  make clean     - Clean up generated files"

install:
	pip install -r requirements.txt

lint:
	@echo "Running flake8..."
	flake8 app tests
	@echo "\nRunning mypy..."
	mypy app
	@echo "\nChecking import sorting with isort..."
	isort --check-only --diff app tests
	@echo "\nChecking code formatting with black..."
	black --check app tests
	@echo "\nAll linting checks passed! ✅"

format:
	@echo "Formatting imports with isort..."
	isort app tests
	@echo "\nFormatting code with black..."
	black app tests
	@echo "\nCode formatted! ✨"

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing -v

check-all: lint test
	@echo "\nAll checks passed! 🎉"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage