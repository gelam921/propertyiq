import pandas as pd

from propertyiq.processing.base import Transformer


class PriceNormalizer(Transformer):
    name = "price_normalizer"

    def __init__(self, column: str = "price") -> None:
        self.column = column

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        price_normalized = df.copy()

        cleaned = price_normalized[self.column].astype(str).str.replace(r"[$,\s]", "", regex=True)
        price_normalized[self.column] = pd.to_numeric(cleaned, errors="coerce")

        return price_normalized


class AddressStandardizer(Transformer):
    name = "address_standardizer"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        address_cleaned = df.copy()

        for col in ["address", "city"]:
            if col in address_cleaned.columns:
                address_cleaned[col] = address_cleaned[col].str.strip().str.title()

        if "state" in address_cleaned.columns:
            address_cleaned["state"] = address_cleaned["state"].str.strip().str.upper()

        return address_cleaned


class Deduplicator(Transformer):
    name = "deduplicator"

    def __init__(self, subset: list[str]) -> None:
        self.subset = subset

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates(subset=self.subset, keep="first").reset_index(drop=True)


class DerivedMetrics(Transformer):
    name = "derived_metrics"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        sqft = pd.to_numeric(df["sqft"], errors="coerce")
        sqft = sqft.where(sqft > 0)
        df["price_per_sqft"] = (df["price"] / sqft).round(2)
        return df
