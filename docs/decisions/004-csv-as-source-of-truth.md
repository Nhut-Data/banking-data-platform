# ADR 004: CSV là source of truth cho 6 entity tĩnh, SQLite chỉ dùng cho transactions

## Bối cảnh

Dataset có 6 entity (accounts, branches, cards, customers, loans, merchants)
tồn tại ở CẢ dạng CSV lẫn dạng table trong SQLite, cộng thêm 1 table
`transactions` chỉ có trong SQLite.

## Quyết định

- 6 entity tĩnh: dùng CSV làm nguồn batch extract duy nhất. KHÔNG extract
  6 table trùng tên này từ SQLite.
- transactions: dùng SQLite làm nguồn duy nhất, mô phỏng streaming qua
  Kafka (producer đọc SQLite -> Kafka -> consumer -> BigQuery).

## Lý do

- Tránh dual-sourcing cho cùng 1 entity gây nhầm lẫn "source of truth nào đúng".
- CSV tự nhiên fit với pattern batch/static data, không cần thêm logic đọc
  SQLite cho data không cần streaming.
- Đã verify bằng scripts/compare_csv_sqlite.py trước khi quyết định (xem kết quả
  trong docs/data_dictionary.md).

## Trade-off

- Nếu sau này phát hiện CSV và SQLite KHÔNG giống nhau (data lệch), cần quay
  lại quyết định này, có thể phải làm reconciliation logic giữa 2 nguồn.
