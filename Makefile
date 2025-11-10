.PHONY: help test test-unit test-integration test-property test-all lint format type-check security clean coverage mutation-test install install-dev

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

# Testing
test:  ## Run all fast tests (unit + property)
	pytest tests/unit tests/property -v

test-unit:  ## Run unit tests only
	pytest tests/unit -v --cov=. --cov-report=term-missing

test-integration:  ## Run integration tests
	pytest tests/integration -v --slow

test-property:  ## Run property-based tests
	pytest tests/property -v

test-all:  ## Run ALL tests (unit + integration + property)
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-fast:  ## Run only fast tests (for quick feedback)
	pytest tests/unit -v -k "not slow"

test-watch:  ## Run tests in watch mode (requires pytest-watch)
	pytest-watch -- tests/unit -v

# Code Quality
lint:  ## Run all linters
	@echo "Running flake8..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
	@echo "\nRunning pylint..."
	pylint --rcfile=.pylintrc *.py providers/ || true

format:  ## Format code with black and isort
	@echo "Formatting with black..."
	black .
	@echo "\nSorting imports with isort..."
	isort .

format-check:  ## Check if code is formatted correctly
	@echo "Checking format with black..."
	black --check --diff .
	@echo "\nChecking imports with isort..."
	isort --check-only --diff .

type-check:  ## Run type checker (mypy)
	mypy --ignore-missing-imports --strict-optional .

# Security
security:  ## Run security checks
	@echo "Running bandit..."
	bandit -r . -f screen || true
	@echo "\nRunning safety..."
	safety check || true

# Coverage
coverage:  ## Generate coverage report
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
	@echo "\nCoverage report generated in htmlcov/index.html"

coverage-report:  ## Open coverage report in browser
	python -m webbrowser htmlcov/index.html

# Mutation Testing (for test quality)
mutation-test:  ## Run mutation testing to verify test quality
	mutmut run --paths-to-mutate=validation.py,rate_limiter.py,logging_config.py,exceptions.py

mutation-results:  ## Show mutation testing results
	mutmut results

# Pre-commit checks (run before committing)
pre-commit: format-check lint type-check test-unit security  ## Run all pre-commit checks
	@echo "\n✅ All pre-commit checks passed!"

# CI simulation (what runs in GitHub Actions)
ci: format-check lint type-check test-all security  ## Run full CI pipeline locally
	@echo "\n✅ CI pipeline simulation complete!"

# Cleanup
clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ .eggs/

# TDD Workflow
tdd-red:  ## Step 1: Write a failing test (RED)
	@echo "📝 Write a failing test first!"
	@echo "Example:"
	@echo "  def test_new_feature():"
	@echo "      result = new_feature()"
	@echo "      assert result == expected"

tdd-green:  ## Step 2: Make the test pass (GREEN)
	@echo "✅ Write minimal code to pass the test!"
	pytest tests/unit -v --lf  # Run last failed test

tdd-refactor:  ## Step 3: Refactor code (REFACTOR)
	@echo "🔧 Refactor while keeping tests green!"
	pytest tests/unit -v && make lint && make type-check

tdd:  ## Run full TDD cycle
	@echo "🔴 RED: Write failing test"
	@echo "🟢 GREEN: Make it pass"
	@echo "🔵 REFACTOR: Improve code"
	@echo ""
	@echo "Run: make tdd-green after writing test"
	@echo "Run: make tdd-refactor after passing test"

# Documentation
docs:  ## Build documentation
	sphinx-build -b html docs/ docs/_build/

docs-serve:  ## Serve documentation locally
	python -m http.server --directory docs/_build 8000

# Quick checks
quick:  ## Quick validation (format + fast tests)
	make format-check && pytest tests/unit -v -k "not slow" --maxfail=1

# Detailed help for TDD workflow
tdd-help:  ## Show detailed TDD workflow help
	@echo "=========================================="
	@echo "       TDD Workflow Guide"
	@echo "=========================================="
	@echo ""
	@echo "1. RED Phase - Write Failing Test:"
	@echo "   - Write test that describes desired behavior"
	@echo "   - Run: pytest tests/unit/test_<module>.py::test_<feature> -v"
	@echo "   - Test should FAIL (this is good!)"
	@echo ""
	@echo "2. GREEN Phase - Make Test Pass:"
	@echo "   - Write minimal code to pass the test"
	@echo "   - Run: make tdd-green"
	@echo "   - Test should PASS (but code may be ugly)"
	@echo ""
	@echo "3. REFACTOR Phase - Improve Code:"
	@echo "   - Clean up code while tests stay green"
	@echo "   - Run: make tdd-refactor"
	@echo "   - Tests stay green, code improves"
	@echo ""
	@echo "4. Before Commit:"
	@echo "   - Run: make pre-commit"
	@echo "   - All checks should pass"
	@echo ""
	@echo "Example workflow:"
	@echo "  1. vim tests/unit/test_validation.py  # Write failing test"
	@echo "  2. pytest -k test_new_feature -v      # Verify it fails"
	@echo "  3. vim validation.py                  # Implement feature"
	@echo "  4. make tdd-green                     # Verify it passes"
	@echo "  5. make tdd-refactor                  # Clean up code"
	@echo "  6. make pre-commit                    # Final checks"
	@echo "  7. git commit -m 'feat: add feature'"
	@echo ""

# Docker support (if needed)
docker-test:  ## Run tests in Docker
	docker run --rm -v $(PWD):/app -w /app python:3.11 bash -c "pip install -r requirements-dev.txt && make test"
