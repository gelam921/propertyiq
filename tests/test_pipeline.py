from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from propertyiq.processing.base import Transformer
from propertyiq.processing.pipeline import Pipeline, PipelineObserver, PipelineRun
from propertyiq.processing.quality import NotNullRule, QualityReport, RangeRule, UniqueRule
from propertyiq.processing.transformers import (
    AddressStandardizer,
    Deduplicator,
    DerivedMetrics,
    PriceNormalizer,
)


def make_run(**overrides):
    base = {
        "pipeline": "p",
        "input_name": "raw",
        "output_name": "clean",
        "steps": ["a"],
        "rows_in": 3,
        "rows_out": 2,
        "data": pd.DataFrame({"a": [1, 2]}),
        "finished_at": "2026-01-01T00:00:00+00:00",
    }
    return PipelineRun(**{**base, **overrides})


def test_run_stores_its_fields():
    run = make_run()
    assert run.pipeline == "p"
    assert (run.input_name, run.output_name) == ("raw", "clean")
    assert run.steps == ["a"]
    assert (run.rows_in, run.rows_out) == (3, 2)
    assert len(run.data) == 2


def test_run_record_is_frozen():
    run = make_run()
    with pytest.raises(FrozenInstanceError):
        run.rows_in = 99


class Spy(Transformer):
    def __init__(self, label, log):
        self.name = label
        self.log = log

    def transform(self, df):
        self.log.append(self.name)
        return df


def test_steps_run_in_order():
    log = []
    pipe = Pipeline("p", "raw", "clean", [Spy("a", log), Spy("b", log), Spy("c", log)])
    pipe.run(pd.DataFrame({"x": [1]}))
    assert log == ["a", "b", "c"]


def test_pipeline_run_record_has_the_facts():
    df = pd.DataFrame({"a": [1, 1, 2]})
    run = Pipeline("p", "raw", "clean", [Deduplicator(subset=["a"])]).run(df)
    assert isinstance(run, PipelineRun)
    assert run.pipeline == "p"
    assert (run.input_name, run.output_name) == ("raw", "clean")
    assert run.steps == ["deduplicator"]
    assert (run.rows_in, run.rows_out) == (3, 2)
    assert isinstance(run.finished_at, str)


def test_empty_pipeline_passes_data_through():
    df = pd.DataFrame({"a": [1, 2]})
    run = Pipeline("p", "raw", "clean", []).run(df)
    assert run.steps == []
    assert run.rows_in == run.rows_out == 2


def test_input_dataframe_is_not_modified():
    df = pd.DataFrame({"price": ["$1,000"]})
    Pipeline("p", "raw", "clean", [PriceNormalizer()]).run(df)
    assert df["price"].iloc[0] == "$1,000"


def test_full_cleaning_chain():
    df = pd.DataFrame(
        {
            "address": [" 1 main st ", "1 MAIN ST"],
            "city": ["austin", "Austin"],
            "state": ["tx", "TX"],
            "price": ["$300,000", "$300,000"],
            "sqft": [1000, 1000],
        }
    )
    pipe = Pipeline(
        "listings",
        "raw",
        "clean",
        [
            PriceNormalizer(),
            AddressStandardizer(),
            Deduplicator(subset=["address", "city", "state"]),
            DerivedMetrics(),
        ],
    )
    run = pipe.run(df)
    assert run.rows_out == 1
    assert run.data["price_per_sqft"].iloc[0] == 300.0
    assert run.steps == [
        "price_normalizer",
        "address_standardizer",
        "deduplicator",
        "derived_metrics",
    ]


def test_run_without_rules_has_a_perfect_report():
    run = Pipeline("p", "raw", "clean", []).run(pd.DataFrame({"a": [1]}))
    assert isinstance(run.quality, QualityReport)
    assert run.quality.score == 100.0
    assert run.quality.results == []


def test_run_validates_the_cleaned_output_not_the_input():
    df = pd.DataFrame({"id": [1, 1, 2]})
    pipe = Pipeline("p", "raw", "clean", [Deduplicator(subset=["id"])], rules=[UniqueRule(["id"])])
    run = pipe.run(df)
    assert run.quality.passed is True  # duplicates were removed before the check
    assert run.quality.dataset == "clean"
    assert run.quality.rows == 2


def test_run_report_records_failures():
    df = pd.DataFrame({"price": [100.0, None]})
    pipe = Pipeline(
        "p",
        "raw",
        "clean",
        [],
        rules=[NotNullRule(["price"]), RangeRule("price", min_value=0)],
    )
    run = pipe.run(df)
    assert run.quality.score == 50.0
    assert len(run.quality.failures) == 1
    assert run.quality.failures[0].failed_rows == 1


class Recorder(PipelineObserver):
    def __init__(self):
        self.runs = []

    def on_run_complete(self, run):
        self.runs.append(run)


def test_observer_is_abstract():
    with pytest.raises(TypeError):
        PipelineObserver()


def test_observer_receives_the_run():
    rec = Recorder()
    pipe = Pipeline("p", "raw", "clean", [], observers=[rec])
    run = pipe.run(pd.DataFrame({"a": [1]}))
    assert len(rec.runs) == 1
    assert rec.runs[0] is run


def test_every_observer_is_told():
    first, second = Recorder(), Recorder()
    Pipeline("p", "raw", "clean", [], observers=[first, second]).run(pd.DataFrame({"a": [1]}))
    assert len(first.runs) == 1
    assert len(second.runs) == 1


def test_observer_sees_the_quality_report():
    rec = Recorder()
    Pipeline("p", "raw", "clean", [], observers=[rec]).run(pd.DataFrame({"a": [1]}))
    assert rec.runs[0].quality.score == 100.0
