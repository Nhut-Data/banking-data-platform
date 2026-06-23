"""
So sánh data giữa 6 file CSV (accounts, branches, cards, customers, loans,
merchants) và 6 table cùng tên trong SQLite, để xác nhận có phải data
trùng lặp hoàn toàn hay không trước khi quyết định nguồn nào là source
of truth cho từng domain.

Cách chạy:
    uv run python scripts/compare_csv_sqlite.py

Yêu cầu: đặt 6 file CSV vào data/raw/<domain>.csv và file SQLite vào
data/raw/banking.db (đổi SQLITE_PATH bên dưới nếu tên file khác).
"""
import sqlite3
from pathlib import Path

import pandas as pd

CSV_DIR = Path("data/raw/csv")
SQLITE_PATH = Path("data/raw/sqlite/bank_sqlite.db")
TABLES = ["accounts", "branches", "cards", "customers", "loans", "merchants"]


def compare_table(table: str, conn: sqlite3.Connection) -> None:
    csv_path = CSV_DIR / f"{table}.csv"
    if not csv_path.exists():
        print(f"[{table}] SKIP - không tìm thấy {csv_path}")
        return

    df_csv = pd.read_csv(csv_path)
    df_sqlite = pd.read_sql(f"SELECT * FROM {table}", conn)

    print(f"--- {table} ---")
    print(f"  CSV rows    : {len(df_csv)}")
    print(f"  SQLite rows : {len(df_sqlite)}")
    print(f"  CSV columns    : {list(df_csv.columns)}")
    print(f"  SQLite columns : {list(df_sqlite.columns)}")

    if set(df_csv.columns) != set(df_sqlite.columns):
        print("  -> Schema KHÁC NHAU, cần xem kỹ thủ công.\n")
        return

    sort_col = df_csv.columns[0]
    a = df_csv.sort_values(by=sort_col).reset_index(drop=True)
    b = df_sqlite[df_csv.columns].sort_values(by=sort_col).reset_index(drop=True)

    identical = a.equals(b)
    print(f"  -> Data giống hệt nhau: {identical}")

    if not identical and len(a) == len(b):
        diff_mask = (a != b).any(axis=1)
        n_diff_rows = diff_mask.sum()
        print(f"  -> Số dòng khác nhau: {n_diff_rows}/{len(a)}")
    print()


def main() -> None:
    if not SQLITE_PATH.exists():
        print(f"Không tìm thấy {SQLITE_PATH}, chỉnh lại SQLITE_PATH trong file này.")
        return

    conn = sqlite3.connect(SQLITE_PATH)
    for table in TABLES:
        compare_table(table, conn)
    conn.close()


if __name__ == "__main__":
    main()
