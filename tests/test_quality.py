from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from propertyiq.processing.quality import (
    NotNullRule,
    QualityReport,
    RangeRule,
    Rule,
    RuleResult,
    UniqueRule,
    Validator,
)


def test_rule_is_abstract():
    with pytest.raises(TypeError):
        Rule()


def test_rule_result_is_frozen():
    result = RuleResult("r", True, 0)
    with pytest.raises(FrozenInstanceError):
        result.passed = False


def test_not_null_passes_on_complete_data():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    result = NotNullRule(["a", "b"]).check(df)
    assert result.passed is True
    assert result.failed_rows == 0


def test_not_null_counts_rows_not_cells():
    df = pd.DataFrame({"a": [1, None, None], "b": ["x", None, "z"]})
    result = NotNullRule(["a", "b"]).check(df)
    assert result.passed is False
    assert result.failed_rows == 2  # rows 1 and 2, even though row 1 has two gaps


def test_not_null_only_checks_listed_columns():
    df = pd.DataFrame({"a": [1, 2], "b": [None, None]})
    assert NotNullRule(["a"]).check(df).passed is True


def test_not_null_returns_plain_python_types():
    df = pd.DataFrame({"a": [None]})
    result = NotNullRule(["a"]).check(df)
    assert type(result.failed_rows) is int
    assert type(result.passed) is bool


def test_check_does_not_modify_input():
    df = pd.DataFrame({"a": [1, None]})
    NotNullRule(["a"]).check(df)
    assert len(df) == 2 and df["a"].isna().sum() == 1


def test_range_passes_when_all_values_in_range():
    df = pd.DataFrame({"price": [100.0, 500.0, 1000.0]})
    result = RangeRule("price", min_value=100, max_value=1000).check(df)
    assert result.passed is True
    assert result.failed_rows == 0


def test_range_counts_values_below_min_and_above_max():
    df = pd.DataFrame({"price": [5.0, 100.0, 2000.0]})
    result = RangeRule("price", min_value=10, max_value=1000).check(df)
    assert result.failed_rows == 2


def test_range_ignores_missing_values():
    df = pd.DataFrame({"price": [100.0, None]})
    result = RangeRule("price", min_value=10, max_value=1000).check(df)
    assert result.passed is True


def test_range_with_only_one_bound():
    df = pd.DataFrame({"price": [-5.0, 5.0, 5000.0]})
    assert RangeRule("price", min_value=0).check(df).failed_rows == 1
    assert RangeRule("price", max_value=1000).check(df).failed_rows == 1


def test_range_zero_is_a_real_bound():
    df = pd.DataFrame({"price": [-1.0, 0.0, 1.0]})
    assert RangeRule("price", min_value=0).check(df).failed_rows == 1


def test_range_returns_plain_python_types():
    result = RangeRule("price", min_value=0).check(pd.DataFrame({"price": [-1.0]}))
    assert type(result.failed_rows) is int
    assert type(result.passed) is bool


def test_unique_passes_when_keys_are_unique():
    df = pd.DataFrame({"id": [1, 2, 3]})
    assert UniqueRule(["id"]).check(df).passed is True


def test_unique_counts_extra_copies():
    df = pd.DataFrame({"id": [1, 1, 1, 2]})
    result = UniqueRule(["id"]).check(df)
    assert result.passed is False
    assert result.failed_rows == 2


def test_unique_composite_key():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "y", "x"]})
    assert UniqueRule(["a", "b"]).check(df).passed is True
    assert UniqueRule(["a"]).check(df).failed_rows == 1


def test_unique_returns_plain_python_types():
    result = UniqueRule(["id"]).check(pd.DataFrame({"id": [1, 1]}))
    assert type(result.failed_rows) is int
    assert type(result.passed) is bool


def make_report(*passed_flags):
    results = [RuleResult(f"r{i}", ok, 0 if ok else 1) for i, ok in enumerate(passed_flags)]
    return QualityReport("ds", 10, results)


def test_score_is_percentage_of_rules_passed():
    assert make_report(True, True, False, False).score == 50.0
    assert make_report(True, True, True).score == 100.0
    assert make_report(False).score == 0.0


def test_score_rounds_to_one_decimal():
    assert make_report(True, False, False).score == 33.3


def test_score_with_no_rules_is_100():
    assert make_report().score == 100.0


def test_passed_only_when_every_rule_passes():
    assert make_report(True, True).passed is True
    assert make_report(True, False).passed is False
    assert make_report().passed is True


def test_failures_lists_only_failed_results():
    report = make_report(True, False, True, False)
    assert [r.rule for r in report.failures] == ["r1", "r3"]


def test_report_is_frozen():
    with pytest.raises(FrozenInstanceError):
        make_report(True).rows = 5


def test_validator_runs_every_rule():
    df = pd.DataFrame({"id": [1, 1], "price": [5.0, None]})
    validator = Validator(
        [
            NotNullRule(["price"]),
            UniqueRule(["id"]),
            RangeRule("price", min_value=0),
        ]
    )
    report = validator.run("ds", df)
    assert report.dataset == "ds"
    assert report.rows == 2
    assert len(report.results) == 3
    assert report.score == 33.3  # only the range rule passes


def test_validator_with_no_rules():
    report = Validator([]).run("ds", pd.DataFrame({"a": [1]}))
    assert report.score == 100.0
    assert report.results == []
