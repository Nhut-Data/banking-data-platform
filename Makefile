.PHONY: up down logs test lint

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	uv run pytest tests/

lint:
	uv run ruff check src/ tests/
