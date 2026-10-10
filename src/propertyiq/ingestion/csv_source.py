import pandas as pd

from propertyiq.ingestion.base import BaseSource


class CSVSource(BaseSource):
    required_columns = ("address", "city", "state", "price")

    def __init__(self, name, path, column_map=None):
        super().__init__(name)
        self.path = path
        self.column_map = {} if column_map is None else column_map

    def fetch(self):
        return pd.read_csv(self.path)

    def to_frame(self, raw):
        df = pd.DataFrame(raw)
        return df.rename(columns=self.column_map)