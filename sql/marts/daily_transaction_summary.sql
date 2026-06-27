CREATE OR REPLACE TABLE `${project}.marts.daily_transaction_summary` AS
SELECT
    DATE(transaction_date)              AS transaction_date,
    COUNT(*)                            AS total_transactions,
    COUNT(DISTINCT account_id)          AS unique_accounts,
    COUNT(DISTINCT merchant_id)         AS unique_merchants,
    ROUND(SUM(amount_usd), 2)           AS total_amount_usd,
    ROUND(AVG(amount_usd), 2)           AS avg_amount_usd,
    ROUND(MIN(amount_usd), 2)           AS min_amount_usd,
    ROUND(MAX(amount_usd), 2)           AS max_amount_usd,
    ROUND(STDDEV(amount_usd), 2)        AS stddev_amount_usd
FROM `${project}.warehouse.fact_transaction`
GROUP BY 1
ORDER BY 1 DESC;
