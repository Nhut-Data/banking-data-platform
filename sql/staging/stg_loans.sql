CREATE OR REPLACE TABLE `${project}.staging.stg_loans` AS
SELECT
    loan_id,
    customer_id,
    ROUND(loan_amount, 2)               AS loan_amount,
    ROUND(interest_rate, 4)             AS interest_rate,
    SAFE.PARSE_DATE('%Y-%m-%d', start_date) AS start_date,
    _ingested_at
FROM `${project}.raw.loans`
WHERE loan_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND loan_amount > 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY loan_id ORDER BY _ingested_at DESC) = 1;
