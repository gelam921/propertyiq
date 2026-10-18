import json

import pytest

from propertyiq.ingestion.base import BaseSource, SchemaError
from propertyiq.ingestion.json_source import JSONSource

RECORDS = [
    {"address": "1 Main St", "city": "Austin", "state": "TX", "price": "$300,000"},
    {"address": "2 Oak Ave", "city": "Denver", "state": "CO", "price": "$500,000"},
]


def write(tmp_path, data):
    path = tmp_path / "listings.json"
    path.write_text(json.dumps(data))
    return path


def test_is_a_base_source():
    assert issubclass(JSONSource, BaseSource)


def test_reads_records_into_a_dataframe(tmp_path):
    df = JSONSource("raw", write(tmp_path, RECORDS)).run()
    assert len(df) == 2
    assert list(df.columns) == ["address", "city", "state", "price"]
    assert df["city"].tolist() == ["Austin", "Denver"]


def test_column_map_renames_provider_fields(tmp_path):
    records = [{"street": "1 Main St", "city": "Austin", "state": "TX", "price": "$1"}]
    df = JSONSource("raw", write(tmp_path, records), column_map={"street": "address"}).run()
    assert "address" in df.columns
    assert "street" not in df.columns


def test_missing_required_columns_raise_schema_error(tmp_path):
    with pytest.raises(SchemaError):
        JSONSource("raw", write(tmp_path, [{"foo": 1}])).run()


def test_top_level_must_be_a_list(tmp_path):
    with pytest.raises(ValueError):
        JSONSource("raw", write(tmp_path, {"address": "x"})).run()


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        JSONSource("raw", tmp_path / "nope.json").run()


def test_repr_uses_the_class_name(tmp_path):
    assert repr(JSONSource("raw", "x.json")) == "JSONSource(name='raw')"