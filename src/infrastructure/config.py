"""
Config tập trung - đọc từ .env bằng pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gcp_project_id: str
    google_application_credentials: str
    bq_location: str = "asia-southeast1"
    bq_dataset_raw: str = "raw"
    bq_dataset_staging: str = "staging"
    bq_dataset_warehouse: str = "warehouse"
    bq_dataset_marts: str = "marts"


settings = Settings()
