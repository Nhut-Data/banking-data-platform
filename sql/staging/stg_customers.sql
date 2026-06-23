CREATE OR REPLACE TABLE `${project}.staging.stg_customers` AS
SELECT
    customer_id,
    INITCAP(TRIM(first_name))           AS first_name,
    INITCAP(TRIM(last_name))            AS last_name,
    LOWER(TRIM(email))                  AS email,
    INITCAP(TRIM(city))                 AS city,
    credit_score,
    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', created_at) AS created_at,
    _ingested_at
FROM `${project}.raw.customers`
WHERE customer_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY _ingested_at DESC) = 1;
