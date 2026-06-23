CREATE OR REPLACE TABLE `${project}.staging.stg_merchants` AS
SELECT
    merchant_id,
    TRIM(merchant_name)                 AS merchant_name,
    INITCAP(TRIM(city))                 AS city,
    _ingested_at
FROM `${project}.raw.merchants`
WHERE merchant_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY _ingested_at DESC) = 1;
