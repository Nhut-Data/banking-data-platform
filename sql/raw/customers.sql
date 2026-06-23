CREATE OR REPLACE TABLE `${project}.raw.customers` (
    customer_id     STRING      NOT NULL,
    first_name      STRING,
    last_name       STRING,
    email           STRING,
    city            STRING,
    credit_score    INT64,
    created_at      STRING,
    _ingested_at    TIMESTAMP   NOT NULL
);
