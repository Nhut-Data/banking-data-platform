"""
FastAPI entrypoint — expose REST API đọc từ BigQuery warehouse/marts.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import customers_router, transactions_router

app = FastAPI(
    title="Banking Data Platform API",
    description="REST API đọc từ BigQuery warehouse",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(customers_router.router)
app.include_router(transactions_router.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}