import pandas as pd
import pytest

from propertyiq.ingestion.base import BaseSource, SchemaError
from propertyiq.ingestion.csv_source import CSVSource


def test_base_source_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseSource("x")


def test_subclass_must_implement_fetch():
    class Incomplete(BaseSource):
        pass

    with pytest.raises(TypeError):
        Incomplete("x")


def test_run_calls_steps_in_order():
    calls = []

    class Spy(BaseSource):
        def fetch(self):
            calls.append("fetch")
            return [{"a": 1}]

        def to_frame(self, raw):
            calls.append("to_frame")
            return super().to_frame(raw)

        def validate_schema(self, df):
            calls.append("validate")

    Spy("spy").run()
    assert calls == ["fetch", "to_frame", "validate"]


def test_csv_source_reads_file(tmp_path):
    f = tmp_path / "l.csv"
    f.write_text("address,city,state,price\n1 Main St,Austin,TX,100\n")
    df = CSVSource("raw", str(f)).run()
    assert len(df) == 1


def test_csv_column_map_renames(tmp_path):
    f = tmp_path / "l.csv"
    f.write_text("Street,city,state,price\n1 Main St,Austin,TX,100\n")
    df = CSVSource("raw", str(f), column_map={"Street": "address"}).run()
    assert "address" in df.columns


def test_missing_columns_raise_schema_error(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("foo,bar\n1,2\n")
    with pytest.raises(SchemaError):
        CSVSource("bad", str(f)).run()


def test_repr():
    assert "raw" in repr(CSVSource("raw", "x.csv"))