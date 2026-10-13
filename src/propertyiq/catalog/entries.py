from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ColumnEntry:
    name: str
    dtype: str
    null_rate: float
    distinct_count: int
    samples: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ColumnEntry":
        return cls(
            name=data["name"],
            dtype=data["dtype"],
            null_rate=data["null_rate"],
            distinct_count=data["distinct_count"],
            samples=data["samples"]
        )


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

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DatasetEntry":
        columns = [ColumnEntry.from_dict(c) for c in data["columns"]]
        return cls(
            name=data["name"],
            row_count=data["row_count"],
            columns=columns,
            updated_at=data["updated_at"],
            description=data["description"],
            owner=data["owner"],
            tags=data["tags"],
            quality_score=data["quality_score"]
        )