.PHONY: help install venv clean test lint type-check run run-mqtt run-all docs migrate docker-build docker-up docker-down

VENV_NAME = .venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate

help:
	@echo "RFID Attendance System - Makefile commands"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install dependencies"
	@echo "  make venv         - Create virtual environment"
	@echo "  make run          - Run API server (requires .env with APP_KEY)"
	@echo "  make run-mqtt     - Run MQTT listener"
	@echo "  make run-all      - Run API and MQTT together"
	@echo ""
	@echo "Quality:"
	@echo "  make test         - Run pytest tests"
	@echo "  make lint         - Run pylint"
	@echo "  make type-check   - Run mypy type checking"
	@echo "  make clean        - Clean up cache and build files"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations (alembic upgrade head)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker compose (requires .env with APP_KEY)"
	@echo "  make docker-down  - Stop Docker services"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

venv:
	test -d $(VENV_NAME) || python -m venv $(VENV_NAME)
	@echo "Virtual environment created. Activate with: source $(VENV_NAME)/bin/activate"

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-mqtt:
	python -m src.mqtt_handler

run-all:
	@echo "Starting API and MQTT listener (use Ctrl+C to stop both)"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@(uvicorn main:app --reload --host 0.0.0.0 --port 8000 & \
	  python -m src.mqtt_handler & \
	  wait)

test:
	pytest -v

lint:
	pylint src/

type-check:
	mypy src/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

migrate:
	alembic upgrade head

docker-build:
	docker build -t karty-api .

docker-up:
	docker compose up --build

docker-down:
	docker compose down
