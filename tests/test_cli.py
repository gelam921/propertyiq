from typer.testing import CliRunner

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.entries import ColumnEntry, DatasetEntry
from propertyiq.cli.main import app

runner = CliRunner()


def saved_catalog(tmp_path):
    cols = [ColumnEntry("price", "float64", 0.0, 10, ["1.0"])]
    catalog = Catalog()
    catalog.register(DatasetEntry("raw", 312, cols, "ts", tags=["raw"]))
    catalog.register(DatasetEntry("clean", 300, cols, "ts", tags=["clean"], quality_score=66.7))
    catalog.lineage.add("raw", "clean", ["step1"])
    path = tmp_path / "c.json"
    catalog.save(path)
    return str(path)


def run(*args):
    return runner.invoke(app, list(args))


def test_list_shows_every_dataset_in_name_order(tmp_path):
    result = run("catalog", "list", "--catalog", saved_catalog(tmp_path))
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    assert lines[0].startswith("clean")
    assert "66.7" in lines[0]
    assert lines[1].startswith("raw")


def test_list_on_missing_file_says_empty(tmp_path):
    result = run("catalog", "list", "--catalog", str(tmp_path / "nope.json"))
    assert result.exit_code == 0
    assert "empty" in result.stdout.lower()


def test_search_finds_matching_datasets(tmp_path):
    result = run("catalog", "search", "clean", "--catalog", saved_catalog(tmp_path))
    assert result.exit_code == 0
    assert result.stdout.startswith("clean")
    assert "raw" not in result.stdout


def test_search_with_no_match(tmp_path):
    result = run("catalog", "search", "zzz", "--catalog", saved_catalog(tmp_path))
    assert result.exit_code == 0
    assert "no matches" in result.stdout.lower()


def test_lineage_shows_upstream(tmp_path):
    result = run("catalog", "lineage", "clean", "--catalog", saved_catalog(tmp_path))
    lines = result.stdout.splitlines()
    assert lines[0].endswith("raw")
    assert lines[1].endswith("-")


def test_lineage_shows_downstream(tmp_path):
    result = run("catalog", "lineage", "raw", "--catalog", saved_catalog(tmp_path))
    lines = result.stdout.splitlines()
    assert lines[0].endswith("-")
    assert lines[1].endswith("clean")


def test_lineage_unknown_dataset_fails(tmp_path):
    result = run("catalog", "lineage", "nope", "--catalog", saved_catalog(tmp_path))
    assert result.exit_code == 1


def run_args(listings_csv, tmp_path):
    return [
        "--csv",
        str(listings_csv),
        "--db",
        str(tmp_path / "w.db"),
        "--catalog",
        str(tmp_path / "c.json"),
    ]


def test_run_command_prints_a_summary(listings_csv, tmp_path):
    result = run("run", *run_args(listings_csv, tmp_path))
    assert result.exit_code == 0
    assert "3 rows in" in result.stdout
    assert "2 rows out" in result.stdout
    assert "100.0" in result.stdout


def test_run_command_fills_the_catalog(listings_csv, tmp_path):
    run("run", *run_args(listings_csv, tmp_path))
    result = run("catalog", "list", "--catalog", str(tmp_path / "c.json"))
    assert "listings_clean" in result.stdout
    assert "raw_listings" in result.stdout


def test_run_command_with_missing_csv_fails(tmp_path):
    result = run(
        "run",
        "--csv",
        str(tmp_path / "nope.csv"),
        "--db",
        str(tmp_path / "w.db"),
        "--catalog",
        str(tmp_path / "c.json"),
    )
    assert result.exit_code == 1


def test_report_prints_the_analysis(listings_csv, tmp_path):
    run("run", *run_args(listings_csv, tmp_path))
    result = run("report", "--db", str(tmp_path / "w.db"))
    assert result.exit_code == 0
    assert "Median price by city" in result.stdout
    assert result.stdout.index("Denver") < result.stdout.index("Austin")


def test_report_on_unknown_dataset_fails(tmp_path):
    result = run("report", "--db", str(tmp_path / "w.db"))
    assert result.exit_code == 1
