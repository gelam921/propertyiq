from dataclasses import dataclass

from propertyiq.catalog.entries import DatasetEntry


@dataclass(frozen=True)
class LineageEdge:
    source: str
    target: str
    steps: tuple[str, ...]


class LineageGraph:
    def __init__(self) -> None:
        self._edges: dict[str, DatasetEntry] = []

    def add(self, source, target, steps: list[str]) -> None:
        if source == target:
            raise ValueError(f"A dataset cannot feed itself: {source!r}")
        edge = LineageEdge(source, target, tuple(steps))
        self._edges = [e for e in self._edges if not (e.source == source and e.target == target )]
        self._edges.append(edge)

    def edges(self) -> list[LineageEdge]:
        return self._edges.copy()

    def upstream(self, name: str) -> set[str]:
        found = set()
        to_check = [name]
        while to_check:
            current = to_check.pop()
            for parent_link in self._edges:
                if parent_link.target == current and parent_link.source not in found:
                    found.add(parent_link.source)
                    to_check.append(parent_link.source)
        return found
    def downstream(self, name: str) -> set[str]:
        found = set()
        to_check = [name]
        while to_check:
            current = to_check.pop()
            for parent_link in self._edges:
                if parent_link.source == current and parent_link.target not in found:
                    found.add(parent_link.target)
                    to_check.append(parent_link.target)
        return found

    def to_list(self) -> list[dict]:
        items = []
        for edge in self._edges:
            items.append({"source": edge.source, "target": edge.target, "steps": list(edge.steps)})
        return items

    @classmethod
    def from_list(cls, items: list[dict]) -> "LineageGraph":
        graph = cls()
        for item in items:
            graph.add(item["source"], item["target"], item["steps"])
        return graph