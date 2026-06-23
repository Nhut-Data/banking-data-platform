CREATE TABLE IF NOT EXISTS raw_transactions (
    transaction_id      TEXT        PRIMARY KEY,
    account_id          TEXT        NOT NULL,
    merchant_id         TEXT        NOT NULL,
    amount_usd          NUMERIC(12, 2),
    transaction_date    TIMESTAMPTZ NOT NULL,
    ingested_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed           BOOLEAN     NOT NULL DEFAULT FALSE,
    kafka_partition     INTEGER,
    kafka_offset        BIGINT
);

CREATE INDEX IF NOT EXISTS idx_raw_txn_processed
    ON raw_transactions (processed)
    WHERE processed = FALSE;

CREATE INDEX IF NOT EXISTS idx_raw_txn_ingested_at
    ON raw_transactions (ingested_at);
