"""Base abstractions for data ingestion sources."""

from abc import ABC, abstractmethod

import pandas as pd


class SchemaError(ValueError):
    """Custom exception raised when a DataFrame does not match the required schema"""


class BaseSource(ABC):
    """Common interface for all ingestion sources."""

    required_columns: tuple[str, ...] = ()

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def fetch(self):
        """Fetch data from the source."""
        raise NotImplementedError

    def to_frame(self, raw):
        if isinstance(raw, pd.DataFrame):
            return raw
        return pd.DataFrame(raw)

    def validate_schema(self, df):
        missing_columns = [col for col in self.required_columns if col not in df.columns]

        if missing_columns:
            raise SchemaError(
                f"Schema validation failed. Missing required columns: {missing_columns}"
            )

    def run(self):
        raw_data = self.fetch()
        df = self.to_frame(raw_data)
        self.validate_schema(df)
        return df

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"
