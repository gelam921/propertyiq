from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from propertyiq.processing.base import Transformer
from propertyiq.processing.quality import QualityReport, Rule, Validator


@dataclass(frozen=True)
class PipelineRun:
    pipeline: str
    input_name: str
    output_name: str
    steps: list[str]
    rows_in: int
    rows_out: int
    data: pd.DataFrame
    finished_at: str
    quality: QualityReport | None = None


class PipelineObserver(ABC):
    """Anything that wants to hear about finished pipeline runs."""

    @abstractmethod
    def on_run_complete(self, run: PipelineRun) -> None:
        raise NotImplementedError


class Pipeline:
    def __init__(
        self,
        name,
        input_name,
        output_name,
        transformers: list[Transformer],
        rules: list[Rule] | None = None,
        observers: list[PipelineObserver] | None = None,
    ):
        self.name = name
        self.input_name = input_name
        self.output_name = output_name
        self.transformers = transformers
        self.validator = Validator(rules or [])
        self.observers = observers or []

    def run(self, df) -> PipelineRun:
        out = df
        for transformer in self.transformers:
            out = transformer.transform(out)
        quality = self.validator.run(self.output_name, out)
        result = PipelineRun(
            pipeline=self.name,
            input_name=self.input_name,
            output_name=self.output_name,
            steps=[transformer.name for transformer in self.transformers],
            rows_in=len(df),
            rows_out=len(out),
            data=out,
            finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            quality=quality,
        )
        for observers in self.observers:
            observers.on_run_complete(result)
        return result
