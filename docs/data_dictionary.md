# Data Dictionary

TODO (Day 2): điền schema thật của 6 entity (accounts, branches, cards,
customers, loans, merchants) + transactions, sau khi explore data xong.

## Ghi chú nguồn dữ liệu

- accounts, branches, cards, customers, loans, merchants: tồn tại ở CẢ
  CSV (data/raw/*.csv) lẫn SQLite (cùng tên table). Đã chạy
  scripts/compare_csv_sqlite.py để xác nhận data có trùng lặp không.
  -> Quyết định: CSV là source of truth cho batch, SQLite (transactions)
     là source duy nhất cho streaming. Xem docs/decisions/004-csv-as-source-of-truth.md.
