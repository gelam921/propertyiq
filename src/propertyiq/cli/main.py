from pathlib import Path

import typer

from propertyiq.analytics.analyzers import MedianPriceByCity
from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.entries import DatasetEntry
from propertyiq.runner import run_listings
from propertyiq.storage.sqlite_repo import SQLiteRepository

app = typer.Typer(help="PropertyIQ: real estate analytics with a built-in data catalog.")
catalog_app = typer.Typer(help="Browse the data catalog.")
app.add_typer(catalog_app, name="catalog")

DEFAULT_CATALOG = Path("data/catalog.json")
DEFAULT_CSV = Path("data/raw/listings.csv")
DEFAULT_DB = Path("data/warehouse.db")


def _describe(entry: DatasetEntry) -> str:
    return f"{entry.name}  rows={entry.row_count}  quality={entry.quality_score}"


@catalog_app.command("list")
def list_datasets(catalog: Path = DEFAULT_CATALOG) -> None:
    cat = Catalog.load(catalog)
    if len(cat) == 0:
        typer.echo("Catalog is empty.")
        return
    for name in cat.names():
        typer.echo(_describe(cat.get(name)))


@catalog_app.command("search")
def search_datasets(term: str, catalog: Path = DEFAULT_CATALOG) -> None:
    cat = Catalog.load(catalog)
    matches = cat.search(term)
    if not matches:
        typer.echo("No matches.")
        return
    for entry in matches:
        typer.echo(_describe(entry))


@catalog_app.command("lineage")
def lineage_datasets(name: str, catalog: Path = DEFAULT_CATALOG) -> None:
    cat = Catalog.load(catalog)
    if name not in cat:
        typer.echo(f"Unknown dataset: {name}", err=True)
        raise typer.Exit(code=1)
    upstream = sorted(cat.lineage.upstream(name))
    downstream = sorted(cat.lineage.downstream(name))
    typer.echo(f"Upstream:   {','.join(upstream) or '-'}")
    typer.echo(f"Downstream: {','.join(downstream) or '-'}")


@app.command("run")
def run_pipeline(
    csv: Path = DEFAULT_CSV,
    db: Path = DEFAULT_DB,
    catalog: Path = DEFAULT_CATALOG,
) -> None:
    try:
        result = run_listings(csv, db, catalog)
    except FileNotFoundError:
        typer.echo(f"File not found: {csv}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"{result.rows_in} rows in, {result.rows_out} rows out")
    if result.quality:
        typer.echo(f"Quality score: {result.quality.score}%")
        for failure in result.quality.failures:
            typer.echo(f" FAIL ({failure.failed_rows} rows): {failure.rule}")


@app.command("report")
def report(dataset: str = "listings_clean", db: Path = DEFAULT_DB) -> None:
    try:
        df = SQLiteRepository(db).load(dataset)
        analyzer = MedianPriceByCity()
        typer.echo(analyzer.title)
        typer.echo(analyzer.analyze(df).to_string(index=False))
    except KeyError:
        typer.echo(f"Dataset not found: {dataset} (run 'propertyiq run' first)", err=True)
        raise typer.Exit(code=1)

    if __name__ == "__main__":
        app()
