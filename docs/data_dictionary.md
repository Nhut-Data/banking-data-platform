# Data Dictionary

TODO (Day 2): điền schema thật của 6 entity (accounts, branches, cards,
customers, loans, merchants) + transactions, sau khi explore data xong.

## Ghi chú nguồn dữ liệu

- accounts, branches, cards, customers, loans, merchants: tồn tại ở CẢ
  CSV (data/raw/*.csv) lẫn SQLite (cùng tên table). Đã chạy
  scripts/compare_csv_sqlite.py để xác nhận data có trùng lặp không.
  -> Quyết định: CSV là source of truth cho batch, SQLite (transactions)
     là source duy nhất cho streaming. Xem docs/decisions/004-csv-as-source-of-truth.md.
     
transactions   : transaction_id, account_id, merchant_id, amount_usd, transaction_date  [1,000,000 rows]
accounts       : account_id, customer_id, account_type, balance_usd, open_date          [75,000 rows]
customers      : customer_id, first_name, last_name, email, city, credit_score, created_at [50,000 rows]
cards          : card_id, account_id, card_type, expiration_date                        [100,000 rows]
loans          : loan_id, customer_id, loan_amount, interest_rate, start_date           [30,000 rows]
merchants      : merchant_id, merchant_name, city                                       [5,000 rows]
branches       : branch_id, branch_name, manager_name, city(NULL), country(NULL)        [500 rows]