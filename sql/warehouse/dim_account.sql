CREATE OR REPLACE TABLE `${project}.warehouse.dim_account` AS
SELECT
    a.account_id,
    a.customer_id,
    a.account_type,
    a.balance_usd,
    CASE
        WHEN a.balance_usd >= 100000 THEN 'High'
        WHEN a.balance_usd >= 10000  THEN 'Medium'
        ELSE 'Low'
    END                                 AS balance_band,
    a.open_date,
    a._ingested_at                      AS _loaded_at
FROM `${project}.staging.stg_accounts` a;
