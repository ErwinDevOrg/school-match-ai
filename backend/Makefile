# Backend Makefile for School Match AI
# Provides convenient commands for development, testing, and deployment

.PHONY: help install dev test test-unit test-integration test-e2e test-cov lint format type-check migrate migrate-create clean db-reset db-seed shell

# Default target
help:
	@echo "Backend Development Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies"
	@echo "  make db-reset         Reset database (drop all tables and recreate)"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start development server with auto-reload"
	@echo "  make shell            Open Python shell with app context"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Run database migrations"
	@echo "  make migrate-create   Create a new migration (use MSG='description')"
	@echo "  make db-seed          Seed database with sample data"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-e2e         Run end-to-end tests only"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linters (flake8, mypy)"
	@echo "  make format           Format code with black and isort"
	@echo "  make type-check       Run type checking with mypy"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove generated files and caches"

# Installation
install:
	@echo "Installing backend dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "✓ Dependencies installed"

# Development server
dev:
	@echo "Starting development server with auto-reload..."
	python -m uvicorn src.main:app --reload --reload-delay 0.25 --log-level info --host 0.0.0.0 --port 8000

# Python shell
shell:
	@echo "Opening Python shell with app context..."
	python -i -c "from src.main import app; from src.database import get_session; print('App and get_session imported')"

# Database migrations
migrate:
	@echo "Running database migrations..."
	alembic upgrade head
	@echo "✓ Migrations complete"

migrate-create:
	@echo "Creating new migration: $(MSG)"
	@test -n "$(MSG)" || (echo "Error: MSG is required. Use: make migrate-create MSG='description'" && exit 1)
	alembic revision --autogenerate -m "$(MSG)"
	@echo "✓ Migration created"

db-reset:
	@echo "Resetting database..."
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f app.db; \
		alembic upgrade head; \
		echo "✓ Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

db-seed:
	@echo "Seeding database with sample data..."
	@echo "Note: Implement seed script in scripts/seed_db.py"
	# python scripts/seed_db.py
	@echo "✓ Database seeded"

# Testing
test:
	@echo "Running all tests..."
	pytest -v

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration -v

test-e2e:
	@echo "Running end-to-end tests..."
	pytest tests/e2e -v

test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term
	@echo "✓ Coverage report generated in htmlcov/"

# Code quality
lint:
	@echo "Running linters..."
	@echo "→ flake8..."
	flake8 src tests
	@echo "→ mypy..."
	mypy src
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	@echo "→ black..."
	black src tests
	@echo "→ isort..."
	isort src tests
	@echo "✓ Formatting complete"

type-check:
	@echo "Running type checks..."
	mypy src
	@echo "✓ Type checking complete"

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "✓ Cleanup complete"

