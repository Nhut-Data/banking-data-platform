CREATE OR REPLACE TABLE `${project}.staging.stg_transactions`
PARTITION BY DATE(transaction_date)
CLUSTER BY account_id, merchant_id
AS
SELECT
    transaction_id,
    account_id,
    merchant_id,
    ROUND(amount_usd, 2)                AS amount_usd,
    transaction_date,
    _ingested_at
FROM `${project}.raw.transactions`
WHERE transaction_id IS NOT NULL
  AND account_id IS NOT NULL
  AND merchant_id IS NOT NULL
  AND amount_usd > 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY _ingested_at DESC) = 1;
