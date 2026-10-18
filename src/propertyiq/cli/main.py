from pathlib import Path

import typer

from propertyiq.catalog.catalog import Catalog
from propertyiq.catalog.entries import DatasetEntry

app = typer.Typer(help="PropertyIQ: real estate analytics with a built-in data catalog.")
catalog_app = typer.Typer(help="Browse the data catalog.")
app.add_typer(catalog_app, name="catalog")

DEFAULT_CATALOG = Path("data/catalog.json")

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

if __name__ == "__main__":
    app()