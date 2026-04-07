# HumanOS — Makefile
# Quick commands for development

.PHONY: help setup install migrate run worker beat infra infra-down health test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## First-time setup (venv + deps + DNA + migrate)
	python scripts/setup.py

install: ## Install Python dependencies
	pip install -r requirements.txt

migrate: ## Run database migrations
	python manage.py migrate

makemigrations: ## Create new migrations
	python manage.py makemigrations

run: ## Start Django development server
	python manage.py runserver 0.0.0.0:8000

worker: ## Start Celery worker
	celery -A config worker -l info

beat: ## Start Celery beat scheduler
	celery -A config beat -l info

infra: ## Start infrastructure (PostgreSQL, Redis, ChromaDB)
	docker-compose up -d

infra-down: ## Stop infrastructure
	docker-compose down

infra-logs: ## Show infrastructure logs
	docker-compose logs -f

health: ## Check system health
	curl -s http://localhost:8000/health/ | python -m json.tool

test: ## Run tests
	pytest --cov=organs --cov=core -v

lint: ## Run linter
	ruff check core/ organs/

shell: ## Django shell (IPython)
	python manage.py shell_plus

superuser: ## Create Django superuser
	python manage.py createsuperuser

clean: ## Remove compiled Python files and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	rm -rf .pytest_cache htmlcov .coverage
