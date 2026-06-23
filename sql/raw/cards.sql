CREATE OR REPLACE TABLE `${project}.raw.cards` (
    card_id             STRING      NOT NULL,
    account_id          STRING      NOT NULL,
    card_type           STRING,
    expiration_date     STRING,
    _ingested_at        TIMESTAMP   NOT NULL
);
