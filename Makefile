.PHONY: help install dev test clean docker-up docker-down docker-logs format lint

help:
	@echo "FlintBloom Development Commands"
	@echo "================================"
	@echo "install       - Install backend dependencies"
	@echo "dev           - Run backend in development mode"
	@echo "test          - Run tests"
	@echo "test-cov      - Run tests with coverage"
	@echo "format        - Format code with black and isort"
	@echo "lint          - Lint code with flake8 and mypy"
	@echo "clean         - Clean up temporary files"
	@echo "docker-up     - Start all services with Docker"
	@echo "docker-down   - Stop all Docker services"
	@echo "docker-logs   - View Docker logs"
	@echo "frontend-dev  - Run frontend development server"
	@echo "frontend-build - Build frontend for production"

install:
	cd backend && pip install -r requirements.txt

install-dev:
	cd backend && pip install -r requirements.txt -r requirements-dev.txt

dev:
	cd backend && python -m app.main

test:
	cd backend && pytest -v

test-cov:
	cd backend && pytest --cov=app --cov-report=html --cov-report=term

format:
	cd backend && black app/ && isort app/

lint:
	cd backend && flake8 app/ && mypy app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf backend/htmlcov
	rm -rf backend/.coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

docker-restart:
	docker-compose restart backend

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# Database commands
db-migrate:
	cd backend && alembic upgrade head

db-rollback:
	cd backend && alembic downgrade -1

db-reset:
	docker-compose down -v
	docker-compose up -d

# Quick start
quickstart:
	@echo "Starting FlintBloom..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "FlintBloom is ready!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
