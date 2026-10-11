from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from propertyiq.processing.quality import NotNullRule, Rule, RuleResult


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
    assert result.failed_rows == 2          # rows 1 and 2, even though row 1 has two gaps


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