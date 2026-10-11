import pandas as pd
import pytest

from propertyiq.processing.base import Transformer
from propertyiq.processing.transformers import PriceNormalizer, AddressStandardizer


def test_transformer_is_abstract():
    with pytest.raises(TypeError):
        Transformer()


def test_price_normalizer_parses_strings():
    df = pd.DataFrame({"price": ["$450,000", " $1,200 ", None]})
    out = PriceNormalizer().transform(df)
    assert out["price"].iloc[0] == 450000
    assert out["price"].iloc[1] == 1200
    assert pd.isna(out["price"].iloc[2])


def test_price_normalizer_does_not_mutate_input():
    df = pd.DataFrame({"price": ["$1"]})
    PriceNormalizer().transform(df)
    assert df["price"].iloc[0] == "$1"


def test_price_normalizer_has_a_name():
    assert PriceNormalizer().name != "transformer"


def test_address_standardizer():
    df = pd.DataFrame({"address": ["  12 oak st "], "city": ["austin"], "state": [" tx"]})
    out = AddressStandardizer().transform(df)
    assert out.loc[0, "address"] == "12 Oak St"
    assert out.loc[0, "city"] == "Austin"
    assert out.loc[0, "state"] == "TX"


def test_address_standardizer_does_not_mutate_input():
    df = pd.DataFrame({"address": [" a "], "city": ["b"], "state": ["c"]})
    AddressStandardizer().transform(df)
    assert df.loc[0, "address"] == " a "


def test_address_standardizer_has_a_name():
    assert AddressStandardizer().name != "transformer"