from propertyiq.ingestion.csv_source import CSVSource
from propertyiq.processing.pipeline import Pipeline
from propertyiq.processing.transformers import (
    PriceNormalizer, AddressStandardizer, Deduplicator, DerivedMetrics)
raw = CSVSource("raw_listings", "data/raw/listings.csv").run()
pipe = Pipeline("listings_pipeline", "raw_listings", "listings_clean",
                [PriceNormalizer(), AddressStandardizer(),
                 Deduplicator(["address", "city", "state"]), DerivedMetrics()])
run = pipe.run(raw)
print(run.rows_in, run.rows_out, run.steps)
