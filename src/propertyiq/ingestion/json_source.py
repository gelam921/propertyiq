import json
from pathlib import Path

from propertyiq.ingestion.base import BaseSource


class JSONSource(BaseSource):
    required_columns = ("address", "city", "state", "price")

    def __init__(self, name, path, column_map=None):
        super().__init__(name)
        self.path = Path(path)
        self.column_map = {} if column_map is None else column_map

    def fetch(self):
        data = json.loads(self.path.read_text())
        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON list of records in {self.path}")  # noqa: TRY004
        return data

    def to_frame(self, raw):
        df = super().to_frame(raw)
        return df.rename(columns=self.column_map)