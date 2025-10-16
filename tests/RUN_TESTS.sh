#!/bin/bash
# Test Runner Script for Telegram Bot
# Usage: ./tests/RUN_TESTS.sh [options]

set -e

echo "🧪 Telegram Bot Test Suite"
echo "======================================"
echo ""

# Navigate to project root
cd "/Users/parmeetsingh/Documents/dbaas/facebook try"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing test dependencies..."
    pip install -r tests/requirements-test.txt
fi

# Parse command line arguments
MODE=${1:-"all"}

case $MODE in
    "unit")
        echo "🔬 Running Unit Tests Only..."
        pytest tests/unit/ -v --tb=short
        ;;
    "integration")
        echo "🔗 Running Integration Tests Only..."
        pytest tests/integration/ -v --tb=short
        ;;
    "coverage")
        echo "📊 Running Tests with Coverage..."
        pytest --cov=app --cov-report=html --cov-report=term-missing tests/ -v
        echo ""
        echo "✅ Coverage report generated: htmlcov/index.html"
        ;;
    "quick")
        echo "⚡ Running Quick Tests (no slow tests)..."
        pytest -m "not slow" tests/ -v --tb=short
        ;;
    "failed")
        echo "🔄 Re-running Failed Tests..."
        pytest --lf -v --tb=short tests/
        ;;
    "all")
        echo "🎯 Running All Tests..."
        pytest tests/ -v --tb=short
        ;;
    *)
        echo "❌ Unknown mode: $MODE"
        echo ""
        echo "Available modes:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run only unit tests"
        echo "  integration  - Run only integration tests"
        echo "  coverage     - Run with coverage report"
        echo "  quick        - Run without slow tests"
        echo "  failed       - Re-run only failed tests"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "✅ Test run complete!"

