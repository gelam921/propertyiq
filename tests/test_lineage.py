import json
from dataclasses import FrozenInstanceError

import pytest

from propertyiq.catalog.lineage import LineageEdge, LineageGraph


def test_edge_is_frozen():
    edge = LineageEdge("a", "b", ("x",))
    with pytest.raises(FrozenInstanceError):
        edge.source = "c"


def test_add_records_an_edge():
    graph = LineageGraph()
    graph.add("raw", "clean", ["step1", "step2"])
    assert graph.edges() == [LineageEdge("raw", "clean", ("step1", "step2"))]


def test_add_same_pair_replaces_the_edge():
    graph = LineageGraph()
    graph.add("raw", "clean", ["old"])
    graph.add("raw", "clean", ["new"])
    assert len(graph.edges()) == 1
    assert graph.edges()[0].steps == ("new",)


def test_add_rejects_a_dataset_feeding_itself():
    with pytest.raises(ValueError):
        LineageGraph().add("a", "a", [])


def test_upstream_direct():
    graph = LineageGraph()
    graph.add("raw", "clean", [])
    assert graph.upstream("clean") == {"raw"}


def test_upstream_is_transitive():
    graph = LineageGraph()
    graph.add("a", "b", [])
    graph.add("b", "c", [])
    assert graph.upstream("c") == {"a", "b"}


def test_downstream_is_transitive():
    graph = LineageGraph()
    graph.add("a", "b", [])
    graph.add("b", "c", [])
    assert graph.downstream("a") == {"b", "c"}


def test_branching_graph():
    graph = LineageGraph()
    graph.add("a", "b", [])
    graph.add("a", "c", [])
    graph.add("b", "d", [])
    graph.add("c", "d", [])
    assert graph.upstream("d") == {"a", "b", "c"}
    assert graph.downstream("a") == {"b", "c", "d"}


def test_unknown_dataset_has_no_lineage():
    graph = LineageGraph()
    graph.add("a", "b", [])
    assert graph.upstream("zzz") == set()
    assert graph.downstream("zzz") == set()


def test_a_loop_in_the_data_does_not_hang():
    graph = LineageGraph()
    graph.add("a", "b", [])
    graph.add("b", "a", [])
    assert "b" in graph.upstream("a")


def test_to_list_is_plain_data():
    graph = LineageGraph()
    graph.add("a", "b", ["x", "y"])
    assert graph.to_list() == [{"source": "a", "target": "b", "steps": ["x", "y"]}]


def test_from_list_round_trip():
    graph = LineageGraph()
    graph.add("a", "b", ["x"])
    graph.add("b", "c", [])
    rebuilt = LineageGraph.from_list(graph.to_list())
    assert rebuilt.edges() == graph.edges()


def test_survives_json_text():
    graph = LineageGraph()
    graph.add("a", "b", [])
    graph.add("b", "c", [])
    rebuilt = LineageGraph.from_list(json.loads(json.dumps(graph.to_list())))
    assert rebuilt.upstream("c") == {"a", "b"}
