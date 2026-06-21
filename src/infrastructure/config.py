"""
Config tập trung - đọc từ .env bằng pydantic-settings.
TODO (Day 4): implement đầy đủ, hiện tại chỉ là khung.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gcp_project_id: str
    bq_location: str = "asia-southeast1"
    bq_dataset_raw: str = "raw"
    bq_dataset_staging: str = "staging"
    bq_dataset_warehouse: str = "warehouse"
    bq_dataset_marts: str = "marts"

    class Config:
        env_file = ".env"


# settings = Settings()  # TODO: uncomment khi đã có .env thật
