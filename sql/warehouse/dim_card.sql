CREATE OR REPLACE TABLE `${project}.warehouse.dim_card` AS
SELECT
    card_id,
    account_id,
    card_type,
    expiration_date,
    CASE
        WHEN expiration_date < CURRENT_DATE() THEN TRUE
        ELSE FALSE
    END                                 AS is_expired,
    _ingested_at                        AS _loaded_at
FROM `${project}.staging.stg_cards`;
