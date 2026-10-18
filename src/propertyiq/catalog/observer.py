from pathlib import Path

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.profiler import profile_dataframe
from propertyiq.processing.pipeline import PipelineObserver, PipelineRun


class CatalogObserver(PipelineObserver):
    def __init__(self, catalog: Catalog, path: str | Path | None = None) -> None:
        self.catalog = catalog
        self.path = path


    def on_run_complete(self, run: PipelineRun) -> None:
        entry = profile_dataframe(
            run.output_name,
            run.data,
            f"Output of pipeline {run.pipeline!r}",
            ["clean"],
            run.quality.score if run.quality else None
        )
        self.catalog.register(entry)
        self.catalog.lineage.add(run.input_name, run.output_name, run.steps)
        if self.path: 
            self.catalog.save(self.path)