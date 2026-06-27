CREATE OR REPLACE TABLE `${project}.marts.customer_360` AS
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.city,
    c.credit_score,
    c.credit_score_band,
    c.created_at,

    -- Account metrics
    COUNT(DISTINCT a.account_id)                    AS total_accounts,
    ROUND(SUM(a.balance_usd), 2)                    AS total_balance_usd,
    ROUND(AVG(a.balance_usd), 2)                    AS avg_balance_usd,

    -- Loan metrics
    COUNT(DISTINCT l.loan_id)                       AS total_loans,
    ROUND(SUM(l.loan_amount), 2)                    AS total_loan_amount,
    ROUND(AVG(l.interest_rate), 4)                  AS avg_interest_rate,

    -- Card metrics
    COUNT(DISTINCT cd.card_id)                      AS total_cards,
    COUNTIF(cd.is_expired = FALSE)                  AS active_cards,

    -- Transaction metrics
    COUNT(DISTINCT f.transaction_id)                AS total_transactions,
    ROUND(SUM(f.amount_usd), 2)                     AS total_spent_usd,
    ROUND(AVG(f.amount_usd), 2)                     AS avg_transaction_usd,
    MAX(f.transaction_date)                         AS last_transaction_at

FROM `${project}.warehouse.dim_customer` c
LEFT JOIN `${project}.warehouse.dim_account`     a  ON c.customer_id = a.customer_id
LEFT JOIN `${project}.warehouse.dim_loan`        l  ON c.customer_id = l.customer_id
LEFT JOIN `${project}.warehouse.dim_card`        cd ON a.account_id  = cd.account_id
LEFT JOIN `${project}.warehouse.fact_transaction` f ON a.account_id  = f.account_id
GROUP BY
    c.customer_id, c.full_name, c.email, c.city,
    c.credit_score, c.credit_score_band, c.created_at;
