CREATE OR REPLACE TABLE `${project}.raw.transactions` (
    transaction_id      STRING      NOT NULL,
    account_id          STRING      NOT NULL,
    merchant_id         STRING      NOT NULL,
    amount_usd          FLOAT64,
    transaction_date    TIMESTAMP,
    _ingested_at        TIMESTAMP   NOT NULL
)
PARTITION BY DATE(transaction_date)
CLUSTER BY account_id, merchant_id;
