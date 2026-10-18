import pandas as pd
import pytest

from propertyiq.analytics.analyzers import MedianPriceByCity
from propertyiq.analytics.base import Analyzer


def sample():
    return pd.DataFrame({
        "city": ["A", "A", "B"],
        "state": ["X", "X", "Y"],
        "price": [100.0, 300.0, 500.0],
        "price_per_sqft": [1.0, 3.0, None],
    })


def test_analyzer_is_abstract():
    with pytest.raises(TypeError):
        Analyzer()


def test_has_a_title():
    assert MedianPriceByCity().title != "analysis"


def test_output_columns():
    out = MedianPriceByCity().analyze(sample())
    assert list(out.columns) == [
        "city", "state", "listings", "median_price", "median_price_per_sqft",
    ]


def test_values_per_city():
    out = MedianPriceByCity().analyze(sample()).set_index("city")
    assert out.loc["A", "listings"] == 2
    assert out.loc["A", "median_price"] == 200.0
    assert out.loc["A", "median_price_per_sqft"] == 2.0


def test_missing_price_per_sqft_stays_missing():
    out = MedianPriceByCity().analyze(sample()).set_index("city")
    assert pd.isna(out.loc["B", "median_price_per_sqft"])


def test_most_expensive_city_first():
    out = MedianPriceByCity().analyze(sample())
    assert out["city"].tolist() == ["B", "A"]


def test_index_is_reset():
    out = MedianPriceByCity().analyze(sample())
    assert out.index.tolist() == [0, 1]


def test_same_city_name_in_two_states_stays_separate():
    df = pd.DataFrame({
        "city": ["Springfield", "Springfield"],
        "state": ["IL", "MO"],
        "price": [100.0, 200.0],
        "price_per_sqft": [1.0, 2.0],
    })
    assert len(MedianPriceByCity().analyze(df)) == 2


def test_does_not_modify_input():
    df = sample()
    MedianPriceByCity().analyze(df)
    assert list(df.columns) == ["city", "state", "price", "price_per_sqft"]
    assert len(df) == 3