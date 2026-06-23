CREATE OR REPLACE TABLE `${project}.raw.loans` (
    loan_id         STRING      NOT NULL,
    customer_id     STRING      NOT NULL,
    loan_amount     FLOAT64,
    interest_rate   FLOAT64,
    start_date      STRING,
    _ingested_at    TIMESTAMP   NOT NULL
);
