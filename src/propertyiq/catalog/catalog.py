import json
from pathlib import Path

from propertyiq.catalog.entries import DatasetEntry
from propertyiq.catalog.lineage import LineageGraph


class Catalog:
    def __init__(self) -> None:
        self._entries: dict[str, DatasetEntry] = {}
        self.lineage = LineageGraph()

    def register(self, entry: DatasetEntry) -> None:
        self._entries[entry.name] = entry

    def get(self, name: str) -> DatasetEntry:
        if name not in self._entries:
            raise KeyError(f"Dataset {name!r} not found")
        return self._entries[name]

    def names(self) -> list[str]:
        return sorted(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, name: object) -> bool:
        return name in self._entries

    def search(self, term: str) -> list[DatasetEntry]:
        term = term.lower()
        matches = []
        for name in self.names():
            entry = self._entries[name]
            texts = [entry.name, entry.description]
            for tag in entry.tags:
                texts.extend(entry.tags)
            for column in entry.columns:
                texts.extend(column.name for column in entry.columns)
            for text in texts:
                if term in text.lower():
                    matches.append(entry)
                    break
        return matches

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        items = []
        for name in self.names():
            items.append(self._entries[name].to_dict())
        data = {"entries": items, "lineage": self.lineage.to_list()}
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Catalog":
        path = Path(path)
        catalog = cls()
        if not path.exists():
            return catalog
        data = json.loads(path.read_text())
        for item in data["entries"]:
            catalog.register(DatasetEntry.from_dict(item))
            catalog.lineage = LineageGraph.from_list(data.get("lineage", []))
        return catalog
