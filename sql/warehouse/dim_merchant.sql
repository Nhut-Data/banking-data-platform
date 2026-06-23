CREATE OR REPLACE TABLE `${project}.warehouse.dim_merchant` AS
SELECT
    merchant_id,
    merchant_name,
    city,
    _ingested_at                        AS _loaded_at
FROM `${project}.staging.stg_merchants`;
