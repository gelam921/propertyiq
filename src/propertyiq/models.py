from dataclasses import dataclass


@dataclass(frozen=True)
class Property:
    listing_id: str
    address: str
    city: str
    state: str
    price: float
    beds: int | None = None
    baths: float | None = None
    sqft: float | None = None

    @property
    def price_per_sqft(self) -> float | None:
        if not self.sqft:
            return None
        return round(self.price/self.sqft, ndigits=2)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} (${self.price:,.0f})"