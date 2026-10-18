import pytest


@pytest.fixture
def listings_csv(tmp_path):
    path = tmp_path / "listings.csv"
    path.write_text(
        "listing_id,address,city,state,price,beds,baths,sqft\n"
        'L1, 1 main st ,austin,tx,"$300,000",3,2,1000\n'
        'L1, 1 main st ,Austin,TX,"$300,000",3,2,1000\n'
        'L2,2 oak ave,Denver,CO,"$500,000",4,3,\n'
    )
    return path
