"""Creates a deliberately messy listings CSV so the pipeline has real work to do."""

import random
from pathlib import Path

import pandas as pd

random.seed(42)
CITIES = [
    ("Austin", "TX", 520_000),
    ("Denver", "CO", 610_000),
    ("Raleigh", "NC", 440_000),
    ("Boise", "ID", 480_000),
    ("Tampa", "FL", 390_000),
    ("Ashburn", "VA", 700_000),
]
STREETS = ["Oak St", "Maple Ave", "Pine Rd", "Cedar Ln", "Elm Dr", "Lake View Ct"]

rows = []
for i in range(300):
    city, state, base = random.choice(CITIES)
    sqft = random.randint(700, 3800)
    price = int(base * (sqft / 1800) * random.uniform(0.7, 1.3))
    rows.append(
        {
            "listing_id": f"L{i:04d}",
            "address": f"  {random.randint(10, 9999)} {random.choice(STREETS).lower()} ",
            "city": city.lower() if i % 7 == 0 else city,
            "state": state.lower() if i % 11 == 0 else state,
            "price": f"${price:,}",
            "beds": random.randint(1, 6),
            "baths": random.choice([1, 1.5, 2, 2.5, 3]),
            "sqft": sqft if i % 13 else None,
        }
    )

df = pd.DataFrame(rows)
df = pd.concat([df, df.sample(12, random_state=1)], ignore_index=True)  # duplicates
df.loc[5, "price"] = None
Path("data/raw").mkdir(parents=True, exist_ok=True)
df.to_csv("data/raw/listings.csv", index=False)
print(f"Wrote {len(df)} rows")
