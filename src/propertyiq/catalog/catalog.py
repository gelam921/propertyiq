
from propertyiq.catalog.entries import DatasetEntry


class Catalog:

    def __init__(self) -> None:
        self._entries: dict[str, DatasetEntry] = {}

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
                texts.append(tag)
            for column in entry.columns:
                texts.append(column.name)
            for text in texts:
                if term in text.lower():
                    matches.append(entry)
                    break
        return matches
