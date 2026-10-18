import pandas as pd

from propertyiq.analytics.base import Analyzer


class MedianPriceByCity(Analyzer):
    title = "Median price by city"

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        summary = df.groupby(["city", "state"]).agg(
            listings=("price", "size"),
            median_price=("price", "median"),
            median_price_per_sqft=("price_per_sqft", "median"),
        )
        summary = summary.reset_index()
        summary = summary.round(2)
        summary = summary.sort_values("median_price", ascending=False)
        return summary.reset_index(drop=True)
