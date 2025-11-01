# Makefile for NeuroInsight Development

.PHONY: help build up down logs clean test lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

clean: ## Stop services and remove volumes
	docker-compose down -v

restart: down up ## Restart all services

status: ## Show status of all services
	docker-compose ps

test-backend: ## Run backend tests
	docker-compose exec backend pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

lint-backend: ## Lint backend code
	docker-compose exec backend black --check backend/
	docker-compose exec backend flake8 backend/

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

format-backend: ## Format backend code
	docker-compose exec backend black backend/

db-shell: ## Open database shell
	docker-compose exec db psql -U neuroinsight

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

backend-shell: ## Open backend container shell
	docker-compose exec backend bash

worker-shell: ## Open worker container shell
	docker-compose exec worker bash

dev: ## Start in development mode with hot-reload
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

init: ## Initialize project (first time setup)
	cp .env.example .env
	docker-compose build
	docker-compose up -d
	@echo "Waiting for services to start..."
	sleep 10
	@echo "Setup complete! Access the application at http://localhost:5173"

