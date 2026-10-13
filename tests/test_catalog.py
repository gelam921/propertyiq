from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from propertyiq.catalog.entries import DatasetEntry
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