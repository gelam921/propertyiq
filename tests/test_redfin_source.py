import pytest

from propertyiq.ingestion.base import BaseSource, SchemaError
from propertyiq.ingestion.csv_source import CSVSource
from propertyiq.ingestion.redfin_source import RedfinSource
from propertyiq.processing.pipeline import Pipeline
from propertyiq.processing.transformers import (
    AddressStandardizer,
    Deduplicator,
    DerivedMetrics,
    PriceNormalizer,
)

HEADER = (
    "SALE TYPE,ADDRESS,CITY,STATE OR PROVINCE,ZIP OR POSTAL CODE,"
    "PRICE,BEDS,BATHS,SQUARE FEET,MLS#\n"
)
ROWS = (
    "MLS Listing,1 Main St,Austin,TX,78701,300000,3,2.0,1000,A1\n"
    "MLS Listing,2 Oak Ave,Denver,CO,80202,500000,4,3.0,,A2\n"
)


@pytest.fixture
def redfin_csv(tmp_path):
    path = tmp_path / "redfin.csv"
    path.write_text(HEADER + ROWS)
    return path


def test_is_a_csv_source_and_a_base_source():
    assert issubclass(RedfinSource, CSVSource)
    assert issubclass(RedfinSource, BaseSource)


def test_renames_redfin_columns(redfin_csv):
    df = RedfinSource("raw", redfin_csv).run()
    assert {"address", "city", "state", "price", "beds", "baths", "sqft", "listing_id"} <= set(
        df.columns
    )
    assert "ADDRESS" not in df.columns


def test_keeps_unmapped_columns(redfin_csv):
    df = RedfinSource("raw", redfin_csv).run()
    assert "ZIP OR POSTAL CODE" in df.columns


def test_values_come_through(redfin_csv):
    df = RedfinSource("raw", redfin_csv).run()
    assert df["city"].tolist() == ["Austin", "Denver"]
    assert df["sqft"].iloc[0] == 1000
    assert df["sqft"].isna().iloc[1]


def test_missing_required_columns_raise_schema_error(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("foo,bar\n1,2\n")
    with pytest.raises(SchemaError):
        RedfinSource("raw", path).run()


def test_feeds_the_existing_pipeline(redfin_csv):
    raw = RedfinSource("raw", redfin_csv).run()
    pipeline = Pipeline(
        "p", "raw", "clean",
        [
            PriceNormalizer(),
            AddressStandardizer(),
            Deduplicator(["address", "city", "state"]),
            DerivedMetrics(),
        ],
    )
    run = pipeline.run(raw)
    assert run.rows_out == 2
    assert run.data["price_per_sqft"].iloc[0] == 300.0
    assert run.data["price_per_sqft"].isna().iloc[1]


def test_repr_uses_the_class_name():
    assert repr(RedfinSource("raw", "x.csv")) == "RedfinSource(name='raw')"