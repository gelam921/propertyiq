from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColumnEntry:
    name: str
    dtype: str
    null_rate: float
    distinct_count: int
    samples: list[str]


@dataclass(frozen=True)
class DatasetEntry:
    name: str
    row_count: int
    columns: list[ColumnEntry]
    updated_at: str
    description: str = ""
    owner: str = "data-team"
    tags: list[str] = field(default_factory=list)
    quality_score: float | None = None