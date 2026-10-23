from propertyiq.ingestion.csv_source import CSVSource


class RedfinSource(CSVSource):

    def __init__(self, name, path):
        REDFIN_COLUMNS = {"ADDRESS": "address", "CITY": "city", "STATE OR PROVINCE": "state", "PRICE": "price", "BEDS": "beds", "BATHS": "baths", "SQUARE FEET": "sqft", "MLS#": "listing_id"}
        super().__init__(name, path, column_map=REDFIN_COLUMNS)