# Testing Guide - How to Run Tests

## Prerequisites

### 1. Install Testing Dependencies

```bash
cd "/Users/parmeetsingh/Documents/dbaas/facebook try"
pip install -r tests/requirements-test.txt
```

### 2. Verify Installation

```bash
pytest --version
# Should show: pytest 7.4.3
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest tests/

# With verbose output
pytest tests/ -v

# With detailed output
pytest tests/ -vv
```

### Run Specific Test Categories

```bash
# Only unit tests
pytest tests/unit/

# Only integration tests
pytest tests/integration/

# Only authentication tests
pytest tests/unit/test_authentication.py

# Only AI generation tests
pytest tests/unit/test_ai_generation.py
```

### Run Specific Test Functions

```bash
# Single test class
pytest tests/unit/test_authentication.py::TestTelegramAuth

# Single test method
pytest tests/unit/test_authentication.py::TestTelegramAuth::test_verify_login_success

# Match by name pattern
pytest tests/ -k "test_login"
pytest tests/ -k "authentication"
```

### Using Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"

# Run tests that don't require API
pytest -m "not requires_api"
```

## Test Output Options

### Verbose Modes

```bash
# Short output (default)
pytest tests/

# Verbose (shows test names)
pytest tests/ -v

# Very verbose (shows full test details)
pytest tests/ -vv

# Quiet (only show summary)
pytest tests/ -q
```

### Show Print Statements

```bash
# Show all print() output
pytest tests/ -s

# Show only for failed tests
pytest tests/ --tb=short
```

### Output Formatting

```bash
# Show only failed tests details
pytest tests/ --tb=short

# Show full traceback
pytest tests/ --tb=long

# No traceback
pytest tests/ --tb=no

# Show summary of all test outcomes
pytest tests/ -ra
```

## Code Coverage

### Generate Coverage Report

```bash
# Basic coverage
pytest --cov=app tests/

# Coverage with HTML report
pytest --cov=app --cov-report=html tests/

# View HTML report
open htmlcov/index.html

# Coverage with terminal report
pytest --cov=app --cov-report=term-missing tests/
```

### Coverage Options

```bash
# Only show missing lines
pytest --cov=app --cov-report=term-missing tests/

# Minimum coverage threshold (fail if below 80%)
pytest --cov=app --cov-fail-under=80 tests/

# Coverage for specific module
pytest --cov=app.services.telegram_bot_service tests/
```

## Filtering Tests

### By Status

```bash
# Run only failed tests from last run
pytest --lf tests/

# Run failed tests first, then others
pytest --ff tests/

# Stop on first failure
pytest -x tests/

# Stop after N failures
pytest --maxfail=3 tests/
```

### By Duration

```bash
# Show slowest 10 tests
pytest --durations=10 tests/

# Show all test durations
pytest --durations=0 tests/

# Timeout tests after 10 seconds
pytest --timeout=10 tests/
```

## Debugging Tests

### Interactive Debugging

```bash
# Drop into debugger on failure
pytest --pdb tests/

# Drop into debugger at start of each test
pytest --trace tests/
```

### Verbose Logging

```bash
# Show logging output
pytest --log-cli-level=INFO tests/

# Debug level logging
pytest --log-cli-level=DEBUG tests/
```

### Capture Control

```bash
# Disable output capture (see prints immediately)
pytest -s tests/

# Show captured output for failed tests
pytest --capture=no tests/
```

## Parallel Testing

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4 tests/

# Auto-detect number of CPUs
pytest -n auto tests/
```

## Test Selection Examples

### Example 1: Quick Unit Test Run

```bash
# Fast unit tests only, skip slow ones
pytest -m "unit and not slow" tests/ -v
```

### Example 2: Full Test Suite with Coverage

```bash
# Complete test run with HTML coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing tests/ -v
```

### Example 3: Integration Tests Only

```bash
# Run integration tests with verbose output
pytest -m integration tests/ -vv -s
```

### Example 4: Specific Feature Testing

```bash
# Test only authentication-related features
pytest tests/ -k "auth" -v

# Test only AI generation features
pytest tests/ -k "generation or ai" -v
```

## Continuous Testing

### Watch for Changes

```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw tests/
```

### Pre-commit Testing

```bash
# Run tests before each commit
# Add to .git/hooks/pre-commit:
#!/bin/bash
pytest tests/unit/ -v
```

## Test Results

### Generate Test Report

```bash
# JUnit XML report (for CI/CD)
pytest --junitxml=test-results.xml tests/

# HTML report
pip install pytest-html
pytest --html=test-report.html tests/
```

### View Test Summary

```bash
# Short summary
pytest tests/ -ra

# Full summary with all test details
pytest tests/ -rapP
```

## Environment-Specific Testing

### Mock Environment

```bash
# All tests use mocks (default)
pytest tests/
```

### With Real APIs (Use Sparingly)

```bash
# Run tests that require real API keys
# Make sure .env is configured
pytest -m requires_api tests/

# Skip tests that need APIs
pytest -m "not requires_api" tests/
```

## Troubleshooting

### Common Issues

**Issue: "No module named 'app'"**
```bash
# Solution: Run from project root
cd "/Users/parmeetsingh/Documents/dbaas/facebook try"
pytest tests/
```

**Issue: "Event loop is closed"**
```bash
# Solution: Install pytest-asyncio
pip install pytest-asyncio
```

**Issue: "Fixture not found"**
```bash
# Solution: Check conftest.py is in tests/ directory
ls tests/conftest.py
```

**Issue: "Import errors"**
```bash
# Solution: Ensure all __init__.py files exist
ls tests/__init__.py tests/unit/__init__.py
```

## Best Practices

### Before Pushing Code

```bash
# Run full test suite
pytest tests/ -v

# Check coverage
pytest --cov=app --cov-fail-under=80 tests/

# Run linting
flake8 app/ tests/

# Format code
black app/ tests/
```

### During Development

```bash
# Run only tests for current feature
pytest tests/ -k "my_feature" -v

# Watch mode for TDD
ptw tests/
```

### CI/CD Pipeline

```bash
# Full test run with all checks
pytest tests/ \
  --cov=app \
  --cov-fail-under=80 \
  --junitxml=test-results.xml \
  --html=test-report.html \
  -v
```

## Quick Reference Card

```bash
# Most Common Commands
pytest tests/                          # Run all tests
pytest tests/ -v                       # Verbose output
pytest tests/unit/                     # Unit tests only
pytest -m unit                         # Unit marker
pytest -k "auth"                       # Match by name
pytest --cov=app tests/                # With coverage
pytest --lf                            # Last failed
pytest -x                              # Stop on first fail
pytest -s                              # Show print output
pytest --pdb                           # Debug on failure

# Coverage
pytest --cov=app --cov-report=html tests/

# Markers
pytest -m unit                         # Unit tests
pytest -m integration                  # Integration tests
pytest -m "not slow"                   # Skip slow tests

# Specific Test
pytest tests/unit/test_auth.py::TestClass::test_method
```

## Test Development Workflow

1. **Write test** (TDD approach)
   ```bash
   # Create test file
   touch tests/unit/test_new_feature.py
   ```

2. **Run test** (should fail initially)
   ```bash
   pytest tests/unit/test_new_feature.py -v
   ```

3. **Implement feature**
   ```bash
   # Edit source code
   ```

4. **Run test again** (should pass)
   ```bash
   pytest tests/unit/test_new_feature.py -v
   ```

5. **Check coverage**
   ```bash
   pytest --cov=app.module tests/unit/test_new_feature.py
   ```

6. **Run full suite**
   ```bash
   pytest tests/ -v
   ```

---

## Summary

**Quick Start:**
```bash
pip install -r tests/requirements-test.txt
pytest tests/ -v
```

**Full Test Run:**
```bash
pytest --cov=app --cov-report=html tests/ -v
open htmlcov/index.html
```

**Fast Development:**
```bash
pytest tests/ -k "feature_name" -vv -s
```

Happy Testing! 🧪✨

