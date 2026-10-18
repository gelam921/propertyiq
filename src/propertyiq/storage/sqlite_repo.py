import re
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from propertyiq.storage.base import Repository


class SQLiteRepository(Repository):
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _validate_name(self, name: str) -> None:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"Invalid dataset name: {name!r}")

    def save(self, name: str, df: pd.DataFrame) -> None:
        self._validate_name(name)
        with closing(sqlite3.connect(self.db_path)) as conn:
            df.to_sql(name, conn, if_exists="replace", index=False)

    def list_datasets(self) -> list[str]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            return sorted(row[0] for row in rows)

    def load(self, name: str) -> pd.DataFrame:
        self._validate_name(name)
        if name not in self.list_datasets():
            raise KeyError(f"Dataset {name!r} not found")
        with closing(sqlite3.connect(self.db_path)) as conn:
            sql = f'SELECT * FROM "{name}"'
            return pd.read_sql_query(sql, conn)
