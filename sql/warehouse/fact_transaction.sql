CREATE OR REPLACE TABLE `${project}.warehouse.fact_transaction`
PARTITION BY DATE(transaction_date)
CLUSTER BY account_id, merchant_id
AS
SELECT
    t.transaction_id,
    t.account_id,
    t.merchant_id,
    a.customer_id,
    t.amount_usd,
    t.transaction_date,
    EXTRACT(YEAR  FROM t.transaction_date) AS transaction_year,
    EXTRACT(MONTH FROM t.transaction_date) AS transaction_month,
    EXTRACT(DAY   FROM t.transaction_date) AS transaction_day,
    EXTRACT(HOUR  FROM t.transaction_date) AS transaction_hour,
    t._ingested_at                          AS _loaded_at
FROM `${project}.staging.stg_transactions` t
LEFT JOIN `${project}.warehouse.dim_account` a
    ON t.account_id = a.account_id;
