# api-starter Makefile
# Author: Ck.epsilon
#
# Usage:
#   make setup    # Install dependencies + pre-commit hooks
#   make dev      # Start dev server with hot reload
#   make test     # Run tests with coverage
#   make lint     # Check code quality
#   make clean    # Remove cache and build artifacts

.PHONY: setup dev test lint clean docker-up docker-down

PYTHON := python
UVICORN := uvicorn

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pre-commit pytest pytest-asyncio pytest-cov httpx
	pre-commit install

dev:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

lint:
	ruff check app/ tests/
	mypy app/ --ignore-missing-imports

format:
	ruff format app/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -delete

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v
