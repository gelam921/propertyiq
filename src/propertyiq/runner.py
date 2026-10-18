from pathlib import Path

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.observer import CatalogObserver
from propertyiq.catalog.profiler import profile_dataframe
from propertyiq.ingestion.csv_source import CSVSource
from propertyiq.processing.pipeline import Pipeline, PipelineRun
from propertyiq.processing.quality import NotNullRule, RangeRule, UniqueRule
from propertyiq.processing.transformers import (
    AddressStandardizer,
    Deduplicator,
    DerivedMetrics,
    PriceNormalizer,
)
from propertyiq.storage.sqlite_repo import SQLiteRepository


def run_listings(csv_path: Path, db_path: Path, catalog_path: Path) -> PipelineRun:
    raw = CSVSource("raw_listings", str(csv_path)).run()

    catalog = Catalog.load(catalog_path)
    catalog.register(profile_dataframe("raw_listings", raw, f"Raw data from {csv_path}", ["raw"]))

    pipe = Pipeline(
        "listings_pipeline",
        "raw_listings",
        "listings_clean",
        [
            PriceNormalizer(),
            AddressStandardizer(),
            Deduplicator(["address", "city", "state"]),
            DerivedMetrics(),
        ],
        rules=[
            NotNullRule(["address", "price"]),
            RangeRule("price", min_value=10_000, max_value=50_000_000),
            UniqueRule(["listing_id"]),
        ],
        observers=[CatalogObserver(catalog, catalog_path)],
    )

    run = pipe.run(raw)

    repo = SQLiteRepository(db_path)
    repo.save("raw_listings", raw)
    repo.save(run.output_name, run.data)

    return run
