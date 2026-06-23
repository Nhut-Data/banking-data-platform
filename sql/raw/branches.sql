CREATE OR REPLACE TABLE `${project}.raw.branches` (
    branch_id       STRING      NOT NULL,
    branch_name     STRING,
    manager_name    STRING,
    city            STRING,
    country         STRING,
    _ingested_at    TIMESTAMP   NOT NULL
);
