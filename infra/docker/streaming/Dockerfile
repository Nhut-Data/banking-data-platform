FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY src/ ./src/
COPY data/ ./data/
COPY sql/ ./sql/

ENV PYTHONPATH=/app