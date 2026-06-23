CREATE OR REPLACE TABLE `${project}.staging.stg_accounts` AS
SELECT
    account_id,
    customer_id,
    UPPER(TRIM(account_type))           AS account_type,
    ROUND(balance_usd, 2)               AS balance_usd,
    SAFE.PARSE_DATE('%Y-%m-%d', open_date) AS open_date,
    _ingested_at
FROM `${project}.raw.accounts`
WHERE account_id IS NOT NULL
  AND customer_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY _ingested_at DESC) = 1;
