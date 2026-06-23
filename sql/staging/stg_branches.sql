CREATE OR REPLACE TABLE `${project}.staging.stg_branches` AS
SELECT
    branch_id,
    TRIM(branch_name)                   AS branch_name,
    INITCAP(TRIM(manager_name))         AS manager_name,
    NULLIF(TRIM(city), '')              AS city,
    NULLIF(TRIM(country), '')           AS country,
    _ingested_at
FROM `${project}.raw.branches`
WHERE branch_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY branch_id ORDER BY _ingested_at DESC) = 1;
