import pandas as pd

def describe_sqlite_tables(con):
    """
    SQLite データベース内の全テーブルについて、
    テーブル名と列名・型の一覧を表示する。
    """
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table'",
        con
    )["name"]

    for t in tables:
        print(f"\n[{t}]")
        print(
            pd.read_sql(
                f"PRAGMA table_info('{t}')",
                con
            )[["name", "type"]]
        )
