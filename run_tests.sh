#!/bin/bash

# Test runner script for the High School Management System

echo "🧪 Running High School Management System Tests"
echo "=============================================="

# Run all tests with verbose output
echo "📋 Running all tests..."
python -m pytest tests/ -v

echo ""
echo "📊 Running tests with coverage..."
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Test run complete!"
echo "📁 HTML coverage report available in htmlcov/index.html"