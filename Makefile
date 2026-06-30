# Makefile - Convenient deployment commands

.PHONY: help install dev prod docker docker-build docker-push test lint security clean deploy-local deploy-aws deploy-gcloud

help:
	@echo "AI Tutor Platform - Make Commands"
	@echo "=================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development environment"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linters"
	@echo "  make security         - Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker           - Build and run Docker Compose"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-push      - Push to container registry"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-local     - Deploy locally (Docker)"
	@echo "  make deploy-aws       - Deploy to AWS ECS"
	@echo "  make deploy-gcloud    - Deploy to Google Cloud Run"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make prod             - Production checks"

install:
	pip install -e .
	pip install pytest pytest-cov ruff mypy bandit

dev:
	./scripts/start-dev.sh || ./scripts/start-dev.bat

test:
	pytest tests/ -v --cov=backend --cov-report=term-missing

lint:
	ruff check . --exclude=venv,build

security:
	bandit -r backend/ -f json -o bandit-report.json
	safety check

docker:
	docker-compose up -d

docker-build:
	docker-compose build

docker-push:
	docker-compose push

deploy-local: docker-build docker
	@echo "✅ Deployed locally"
	@echo "Frontend: http://localhost:8501"
	@echo "Backend: http://localhost:8000"

deploy-aws:
	@echo "Deploying to AWS..."
	chmod +x scripts/deploy-aws.sh
	./scripts/deploy-aws.sh

deploy-gcloud:
	@echo "Deploying to Google Cloud..."
	chmod +x scripts/deploy-gcloud.sh
	./scripts/deploy-gcloud.sh

prod: test lint security
	@echo "✅ All production checks passed"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -f bandit-report.json
	rm -rf build/ dist/ *.egg-info
