# infra/docker/streaming/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir \
    faker \
    kafka-python \
    pydantic \
    pydantic-settings \
    python-dotenv \
    sqlalchemy \
    psycopg2-binary

COPY src/ ./src/
COPY data/ ./data/

ENV PYTHONPATH=/app