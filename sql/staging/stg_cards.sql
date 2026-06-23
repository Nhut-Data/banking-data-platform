CREATE OR REPLACE TABLE `${project}.staging.stg_cards` AS
SELECT
    card_id,
    account_id,
    UPPER(TRIM(card_type))              AS card_type,
    SAFE.PARSE_DATE('%Y-%m-%d', expiration_date) AS expiration_date,
    _ingested_at
FROM `${project}.raw.cards`
WHERE card_id IS NOT NULL
  AND account_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY _ingested_at DESC) = 1;
