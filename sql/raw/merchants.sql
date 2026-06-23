CREATE OR REPLACE TABLE `${project}.raw.merchants` (
    merchant_id     STRING      NOT NULL,
    merchant_name   STRING,
    city            STRING,
    _ingested_at    TIMESTAMP   NOT NULL
);
