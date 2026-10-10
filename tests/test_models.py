from dataclasses import FrozenInstanceError

import pytest

from propertyiq.models import Property


def make(**overrides):
    base = dict(
        listing_id="L1", address="123 Main St", city="Austin", state="TX", price=450_000
    )
    return Property(**{**base, **overrides})

def test_price_per_sqft():
    assert make(sqft=1500).price_per_sqft == 300.0

def test_price_per_sqft_missing_or_zero_sqft():
    assert make().price_per_sqft is None
    assert make(sqft=0).price_per_sqft is None

def test_is_immutable():
    p = make()
    with pytest.raises(FrozenInstanceError):
        p.price = 1

def test_str():
    assert str(make()) == "123 Main St, Austin, TX ($450,000)"