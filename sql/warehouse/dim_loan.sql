CREATE OR REPLACE TABLE `${project}.warehouse.dim_loan` AS
SELECT
    loan_id,
    customer_id,
    loan_amount,
    interest_rate,
    start_date,
    CASE
        WHEN loan_amount >= 500000 THEN 'Large'
        WHEN loan_amount >= 100000 THEN 'Medium'
        ELSE 'Small'
    END                                 AS loan_size_band,
    _ingested_at                        AS _loaded_at
FROM `${project}.staging.stg_loans`;
