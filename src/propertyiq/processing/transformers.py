import pandas as pd

from propertyiq.processing.base import Transformer


class PriceNormalizer(Transformer):
    name = "price_normalizer"

    def __init__(self, column: str = "price") -> None:
        self.column = column

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        cleaned = out[self.column].astype(str).str.replace(r"[$,\s]", "", regex=True)
        out[self.column] = pd.to_numeric(cleaned, errors="coerce")

        return out


class AddressStandardizer(Transformer):
    name = "address_standardizer"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.copy()

        for col in ["address", "city"]:
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].str.strip().str.title()

        if "state" in cleaned.columns:
            cleaned["state"] = cleaned["state"].str.strip().str.upper()

        return cleaned
