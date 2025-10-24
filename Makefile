# Root Makefile for School Match AI
# Orchestrates both backend and frontend development

.PHONY: help install dev dev-backend dev-frontend test test-backend test-frontend lint format clean setup db-migrate

# Default target
help:
	@echo "School Match AI - Development Commands"
	@echo "======================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup            Complete project setup (install deps, run migrations)"
	@echo "  make dev              Start both backend and frontend in parallel"
	@echo ""
	@echo "Development:"
	@echo "  make dev-backend      Start backend server only"
	@echo "  make dev-frontend     Start frontend dev server only"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate       Run database migrations"
	@echo "  make db-reset         Reset database (backend only)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests (backend + frontend)"
	@echo "  make test-backend     Run backend tests"
	@echo "  make test-frontend    Run frontend tests"
	@echo "  make test-e2e         Run end-to-end tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linters on both projects"
	@echo "  make format           Format code in both projects"
	@echo "  make type-check       Run type checks on both projects"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install dependencies for both projects"
	@echo "  make install-backend  Install backend dependencies"
	@echo "  make install-frontend Install frontend dependencies"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Clean all generated files"
	@echo ""
	@echo "Individual Project Commands:"
	@echo "  cd backend && make help    Show backend-specific commands"
	@echo "  cd frontend && npm run     Show frontend-specific commands"

# Setup
setup: install db-migrate
	@echo "✓ Setup complete! Run 'make dev' to start development"

install: install-backend install-frontend
	@echo "✓ All dependencies installed"

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && $(MAKE) install

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development servers
dev:
	@echo "Starting both backend and frontend..."
	@echo "Backend will be available at: http://localhost:8000"
	@echo "Frontend will be available at: http://localhost:5173"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@echo ""
	@trap 'kill 0' SIGINT; \
		$(MAKE) dev-backend & \
		$(MAKE) dev-frontend & \
		wait

dev-backend:
	@echo "Starting backend server..."
	cd backend && $(MAKE) dev

dev-frontend:
	@echo "Starting frontend dev server..."
	cd frontend && npm run dev

# Database
db-migrate:
	@echo "Running database migrations..."
	cd backend && $(MAKE) migrate

db-reset:
	@echo "Resetting database..."
	cd backend && $(MAKE) db-reset

# Testing
test: test-backend test-frontend
	@echo "✓ All tests passed"

test-backend:
	@echo "Running backend tests..."
	cd backend && $(MAKE) test

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test

test-e2e:
	@echo "Running end-to-end tests..."
	@echo "→ Backend E2E tests..."
	cd backend && $(MAKE) test-e2e
	@echo "→ Frontend E2E tests..."
	cd frontend && npm run test:e2e

test-cov:
	@echo "Running tests with coverage..."
	cd backend && $(MAKE) test-cov
	cd frontend && npm run test:coverage

# Code quality
lint: lint-backend lint-frontend
	@echo "✓ Linting complete"

lint-backend:
	@echo "Linting backend..."
	cd backend && $(MAKE) lint

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && npm run lint:check

format: format-backend format-frontend
	@echo "✓ Formatting complete"

format-backend:
	@echo "Formatting backend..."
	cd backend && $(MAKE) format

format-frontend:
	@echo "Formatting frontend..."
	cd frontend && npm run format

type-check: type-check-backend type-check-frontend
	@echo "✓ Type checking complete"

type-check-backend:
	@echo "Type checking backend..."
	cd backend && $(MAKE) type-check

type-check-frontend:
	@echo "Type checking frontend..."
	cd frontend && npm run type-check

# Build
build: build-backend build-frontend
	@echo "✓ Build complete"

build-backend:
	@echo "Building backend..."
	@echo "Note: Python apps don't need a build step"

build-frontend:
	@echo "Building frontend..."
	cd frontend && npm run build

# Cleanup
clean: clean-backend clean-frontend
	@echo "✓ Cleanup complete"

clean-backend:
	@echo "Cleaning backend..."
	cd backend && $(MAKE) clean

clean-frontend:
	@echo "Cleaning frontend..."
	cd frontend && npm run clean
	cd frontend && rm -rf node_modules

# Docker (for future use)
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Note: Implement documentation generation"

# Version info
version:
	@echo "School Match AI"
	@echo "Backend: Python $(shell python --version 2>&1 | cut -d' ' -f2)"
	@echo "Frontend: Node $(shell node --version)"
	@echo "npm: $(shell npm --version)"

