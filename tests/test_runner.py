import pytest

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.entries import DatasetEntry
from propertyiq.runner import run_listings
from propertyiq.storage.sqlite_repo import SQLiteRepository


def go(listings_csv, tmp_path):
    return run_listings(listings_csv, tmp_path / "w.db", tmp_path / "c.json")


def test_run_reports_what_happened(listings_csv, tmp_path):
    run = go(listings_csv, tmp_path)
    assert (run.rows_in, run.rows_out) == (3, 2)
    assert run.quality.score == 100.0


def test_both_datasets_are_in_the_catalog(listings_csv, tmp_path):
    go(listings_csv, tmp_path)
    assert Catalog.load(tmp_path / "c.json").names() == ["listings_clean", "raw_listings"]


def test_lineage_is_recorded(listings_csv, tmp_path):
    go(listings_csv, tmp_path)
    loaded = Catalog.load(tmp_path / "c.json")
    assert loaded.lineage.upstream("listings_clean") == {"raw_listings"}


def test_both_tables_are_saved(listings_csv, tmp_path):
    go(listings_csv, tmp_path)
    repo = SQLiteRepository(tmp_path / "w.db")
    assert repo.list_datasets() == ["listings_clean", "raw_listings"]
    assert len(repo.load("listings_clean")) == 2
    assert len(repo.load("raw_listings")) == 3


def test_rerunning_does_not_duplicate(listings_csv, tmp_path):
    go(listings_csv, tmp_path)
    go(listings_csv, tmp_path)
    loaded = Catalog.load(tmp_path / "c.json")
    assert len(loaded) == 2
    assert len(loaded.lineage.edges()) == 1


def test_other_datasets_in_the_catalog_survive(listings_csv, tmp_path):
    existing = Catalog()
    existing.register(DatasetEntry("other", 1, [], "ts"))
    existing.save(tmp_path / "c.json")
    go(listings_csv, tmp_path)
    assert "other" in Catalog.load(tmp_path / "c.json")


def test_missing_csv_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_listings(tmp_path / "nope.csv", tmp_path / "w.db", tmp_path / "c.json")
