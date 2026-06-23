CREATE OR REPLACE TABLE `${project}.raw.accounts` (
    account_id      STRING      NOT NULL,
    customer_id     STRING      NOT NULL,
    account_type    STRING,
    balance_usd     FLOAT64,
    open_date       STRING,
    _ingested_at    TIMESTAMP   NOT NULL
);
