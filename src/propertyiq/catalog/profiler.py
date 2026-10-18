from datetime import datetime, timezone

import pandas as pd

from propertyiq.catalog.entries import ColumnEntry, DatasetEntry


def profile_dataframe(
    name: str,
    df: pd.DataFrame,
    description: str = "",
    tags: list[str] | None = None,
    quality_score: float | None = None,
) -> DatasetEntry:
    columns = [
        ColumnEntry(
            name=str(col),
            dtype=str(df[col].dtype),
            null_rate=float(df[col].isna().mean()) if len(df) else 0.0,
            distinct_count=int(df[col].nunique()),
            samples=[str(item) for item in df[col].dropna().unique()[:3]],
        )
        for col in df.columns
    ]
    return DatasetEntry(
        name=name,
        row_count=len(df),
        columns=columns,
        updated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        description=description,
        tags=tags or [],
        quality_score=quality_score,
    )
