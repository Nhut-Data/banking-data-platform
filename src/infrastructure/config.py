from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # GCP
    gcp_project_id: str
    google_application_credentials: str
    bq_location: str = "asia-southeast1"
    bq_dataset_raw: str = "raw"
    bq_dataset_staging: str = "staging"
    bq_dataset_warehouse: str = "warehouse"
    bq_dataset_marts: str = "marts"

    # PostgreSQL banking buffer
    banking_db_host: str = "localhost"
    banking_db_port: int = 5432
    banking_db_name: str = "banking_db"
    banking_db_user: str = "airflow"
    banking_db_password: str = "airflow"

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_transactions: str = "transactions.events"
    kafka_topic_dlq: str = "transactions.dlq"

    # SQLite
    sqlite_db_path: str = "data/raw/sqlite/bank_sqlite.db"

    @property
    def banking_db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.banking_db_user}:{self.banking_db_password}"
            f"@{self.banking_db_host}:{self.banking_db_port}/{self.banking_db_name}"
        )


settings = Settings()
