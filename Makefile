.PHONY: up down init airflow streaming all logs test lint

# Core services only (postgres, redis, kafka, kafka-ui)
up:
	docker compose up -d

down:
	docker compose down

# Init Airflow DB + user (chạy 1 lần sau docker compose down -v)
init:
	docker compose --profile airflow up airflow-init

# Core + Airflow
airflow:
	docker compose --profile airflow up -d

# Core + Streaming (producer + consumer)
streaming:
	docker compose --profile streaming up -d

# Tất cả
all:
	docker compose --profile airflow --profile streaming up -d

logs:
	docker compose logs -f

test:
	uv run pytest tests/

lint:
	uv run ruff check src/ tests/
