CREATE OR REPLACE TABLE `${project}.warehouse.dim_customer` AS
SELECT
    customer_id,
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name)  AS full_name,
    email,
    city,
    credit_score,
    CASE
        WHEN credit_score >= 750 THEN 'Excellent'
        WHEN credit_score >= 700 THEN 'Good'
        WHEN credit_score >= 650 THEN 'Fair'
        ELSE 'Poor'
    END                                 AS credit_score_band,
    created_at,
    _ingested_at                        AS _loaded_at
FROM `${project}.staging.stg_customers`;
