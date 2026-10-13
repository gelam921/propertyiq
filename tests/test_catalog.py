from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.entries import ColumnEntry, DatasetEntry
from propertyiq.catalog.profiler import profile_dataframe


def test_entries_are_frozen():
    entry = DatasetEntry("t", 0, [], "2026-01-01T00:00:00+00:00")
    with pytest.raises(FrozenInstanceError):
        entry.row_count = 5


def test_default_tags_are_not_shared():
    a = DatasetEntry("a", 0, [], "ts")
    b = DatasetEntry("b", 0, [], "ts")
    assert a.tags == []
    assert a.tags is not b.tags


def test_profile_dataset_facts():
    df = pd.DataFrame({"city": ["a", "b", None, "a"], "price": [1.0, 2.0, 3.0, 4.0]})
    entry = profile_dataframe("t", df, description="demo", tags=["raw"], quality_score=66.7)
    assert (entry.name, entry.row_count) == ("t", 4)
    assert [c.name for c in entry.columns] == ["city", "price"]
    assert entry.description == "demo"
    assert entry.tags == ["raw"]
    assert entry.quality_score == 66.7
    assert isinstance(entry.updated_at, str)


def test_profile_column_facts():
    df = pd.DataFrame({"city": ["a", "b", None, "a"], "price": [1.0, 2.0, 3.0, 4.0]})
    city, price = profile_dataframe("t", df).columns
    assert city.null_rate == 0.25
    assert city.distinct_count == 2
    assert price.null_rate == 0.0
    assert price.dtype == "float64"


def test_profile_samples_are_short_strings():
    df = pd.DataFrame({"n": [1, 2, 3, 4, 5]})
    assert profile_dataframe("t", df).columns[0].samples == ["1", "2", "3"]


def test_profile_samples_skip_missing_values():
    df = pd.DataFrame({"a": [None, "x"]})
    assert profile_dataframe("t", df).columns[0].samples == ["x"]


def test_profile_empty_dataframe():
    entry = profile_dataframe("t", pd.DataFrame({"a": []}))
    col = entry.columns[0]
    assert entry.row_count == 0
    assert col.null_rate == 0.0
    assert col.distinct_count == 0
    assert col.samples == []


def test_profile_returns_plain_python_types():
    entry = profile_dataframe("t", pd.DataFrame({"a": [1, None]}))
    col = entry.columns[0]
    assert type(entry.row_count) is int
    assert type(col.dtype) is str
    assert type(col.null_rate) is float
    assert type(col.distinct_count) is int
    assert all(type(s) is str for s in col.samples)


def test_profile_defaults():
    entry = profile_dataframe("t", pd.DataFrame({"a": [1]}))
    assert entry.description == ""
    assert entry.tags == []
    assert entry.quality_score is None


def test_profile_does_not_modify_input():
    df = pd.DataFrame({"a": [1, None]})
    profile_dataframe("t", df)
    assert len(df) == 2
    assert df["a"].isna().sum() == 1


def make_entry(name, description="", tags=None, columns=()):
    cols = [ColumnEntry(c, "object", 0.0, 1, []) for c in columns]
    return DatasetEntry(
        name, 0, cols, "2026-01-01T00:00:00+00:00",
        description=description, tags=tags or [],
    )


def test_register_and_get():
    catalog = Catalog()
    entry = make_entry("a")
    catalog.register(entry)
    assert catalog.get("a") is entry


def test_get_missing_raises_key_error():
    with pytest.raises(KeyError):
        Catalog().get("nope")


def test_register_replaces_entry_with_same_name():
    catalog = Catalog()
    catalog.register(make_entry("a", description="old"))
    catalog.register(make_entry("a", description="new"))
    assert len(catalog) == 1
    assert catalog.get("a").description == "new"


def test_len_and_contains():
    catalog = Catalog()
    assert len(catalog) == 0
    catalog.register(make_entry("a"))
    assert len(catalog) == 1
    assert "a" in catalog
    assert "b" not in catalog


def test_names_are_sorted():
    catalog = Catalog()
    catalog.register(make_entry("b"))
    catalog.register(make_entry("a"))
    assert catalog.names() == ["a", "b"]


def test_search_by_name():
    catalog = Catalog()
    catalog.register(make_entry("listings_clean"))
    catalog.register(make_entry("other"))
    assert [e.name for e in catalog.search("listings")] == ["listings_clean"]


def test_search_by_description():
    catalog = Catalog()
    catalog.register(make_entry("a", description="Cleaned home listings"))
    catalog.register(make_entry("b"))
    assert [e.name for e in catalog.search("home")] == ["a"]


def test_search_by_tag():
    catalog = Catalog()
    catalog.register(make_entry("a", tags=["raw"]))
    catalog.register(make_entry("b", tags=["clean"]))
    assert [e.name for e in catalog.search("raw")] == ["a"]


def test_search_by_column_name():
    catalog = Catalog()
    catalog.register(make_entry("a", columns=["price"]))
    catalog.register(make_entry("b", columns=["city"]))
    assert [e.name for e in catalog.search("price")] == ["a"]


def test_search_is_case_insensitive():
    catalog = Catalog()
    catalog.register(make_entry("Listings"))
    assert len(catalog.search("LISTINGS")) == 1


def test_search_no_match_returns_empty_list():
    catalog = Catalog()
    catalog.register(make_entry("a"))
    assert catalog.search("zzz") == []


def test_search_results_are_sorted_by_name():
    catalog = Catalog()
    catalog.register(make_entry("b", tags=["x"]))
    catalog.register(make_entry("a", tags=["x"]))
    assert [e.name for e in catalog.search("x")] == ["a", "b"]


def test_search_returns_each_entry_once():
    catalog = Catalog()
    catalog.register(
        make_entry("price_data", description="price", tags=["price"], columns=["price"])
    )
    assert len(catalog.search("price")) == 1