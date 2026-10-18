import pandas as pd

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.observer import CatalogObserver
from propertyiq.processing.pipeline import Pipeline
from propertyiq.processing.quality import NotNullRule, RangeRule
from propertyiq.processing.transformers import PriceNormalizer


def make_pipeline(catalog, path=None):
    return Pipeline(
        "listings",
        "raw",
        "clean",
        [PriceNormalizer()],
        rules=[NotNullRule(["price"]), RangeRule("price", min_value=0)],
        observers=[CatalogObserver(catalog, path)],
    )


def sample_data():
    return pd.DataFrame({"price": ["$1,000", None]})


def test_run_registers_the_output_dataset():
    catalog = Catalog()
    make_pipeline(catalog).run(sample_data())
    entry = catalog.get("clean")
    assert entry.row_count == 2
    assert entry.quality_score == 50.0
    assert entry.tags == ["clean"]
    assert "listings" in entry.description


def test_run_records_lineage():
    catalog = Catalog()
    make_pipeline(catalog).run(sample_data())
    assert catalog.lineage.upstream("clean") == {"raw"}
    assert catalog.lineage.edges()[0].steps == ("price_normalizer",)


def test_rerunning_does_not_duplicate():
    catalog = Catalog()
    pipe = make_pipeline(catalog)
    pipe.run(sample_data())
    pipe.run(sample_data())
    assert len(catalog) == 1
    assert len(catalog.lineage.edges()) == 1


def test_saves_when_given_a_path(tmp_path):
    path = tmp_path / "catalog.json"
    make_pipeline(Catalog(), path).run(sample_data())
    loaded = Catalog.load(path)
    assert loaded.names() == ["clean"]
    assert loaded.lineage.upstream("clean") == {"raw"}


def test_works_without_rules():
    catalog = Catalog()
    pipe = Pipeline("p", "raw", "clean", [], observers=[CatalogObserver(catalog)])
    pipe.run(pd.DataFrame({"a": [1]}))
    assert catalog.get("clean").quality_score == 100.0
