CREATE OR REPLACE TABLE `${project}.warehouse.dim_branch` AS
SELECT
    branch_id,
    branch_name,
    manager_name,
    city,
    country,
    _ingested_at                        AS _loaded_at
FROM `${project}.staging.stg_branches`;
