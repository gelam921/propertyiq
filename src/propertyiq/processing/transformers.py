import pandas as pd

from propertyiq.processing.base import Transformer


class PriceNormalizer(Transformer):
    name = "price_normalizer"

    def __init__(self, column: float = "price") -> None:
        self.column = column

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        cleaned = out[self.column].astype(str).str.replace(r"[$,\s]", "", regex="True")
        out[self.column] = pd.to_numeric(cleaned, errors="coerce")
        return out