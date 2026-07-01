"""Unified CLI for the Foreign Gifts Tracker: analysis, search, export, and
the extraction pipeline that rebuilds data/gifts.db from Federal Register PDFs.
"""

import json
from pathlib import Path

import click
import sqlite_utils

from foreign_gifts.analysis.analyzer import GiftsAnalyzer
from foreign_gifts.analysis.classifier import GiftClassifier

try:
    from foreign_gifts.analysis.visualizer import GiftsVisualizer, HAS_MATPLOTLIB
except ImportError:
    HAS_MATPLOTLIB = False

DEFAULT_DB = "data/gifts.db"


@click.group()
@click.option("--database", default=DEFAULT_DB, show_default=True, help="Path to SQLite database")
@click.pass_context
def cli(ctx, database):
    """Foreign Gifts Tracker — analyze foreign gifts to U.S. officials."""
    ctx.ensure_object(dict)
    ctx.obj["database"] = database


@cli.command()
@click.option("--output", help="Output file path")
@click.pass_context
def analyze(ctx, output):
    """Generate a comprehensive analysis report."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    report = analyzer.generate_report(output)
    if output:
        click.echo(f"Report saved to {output}")
    else:
        click.echo(report)


@cli.command()
@click.option("--keyword", help="Search in gift description")
@click.option("--country", help="Filter by donor country")
@click.option("--recipient", help="Filter by recipient name")
@click.option("--min-value", type=float, help="Minimum value")
@click.option("--max-value", type=float, help="Maximum value")
@click.option("--year", help="Filter by year")
@click.option("--limit", type=int, default=10, show_default=True, help="Max results")
@click.pass_context
def search(ctx, keyword, country, recipient, min_value, max_value, year, limit):
    """Search for gifts."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    results = analyzer.search_gifts(
        keyword=keyword,
        country=country,
        recipient=recipient,
        min_value=min_value,
        max_value=max_value,
        year=year,
    )

    click.echo(f"Found {len(results)} matching gifts:\n")
    for i, gift in enumerate(results[:limit], 1):
        click.echo(f"{i}. {gift['gift_description'][:80]}")
        click.echo(f"   From: {gift['donor_name']} ({gift['donor_country']})")
        click.echo(f"   To: {gift['recipient_name']}")
        if gift["estimated_value"]:
            click.echo(f"   Value: ${gift['estimated_value']:,.2f}")
        click.echo(f"   Date: {gift['received']}\n")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show summary statistics."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    s = analyzer.get_summary_statistics()

    click.echo("\n" + "=" * 60)
    click.echo("FOREIGN GIFTS SUMMARY STATISTICS")
    click.echo("=" * 60)
    click.echo(f"\nTotal Gifts: {s['total_gifts']:,}")
    click.echo(
        f"Gifts with Value Data: {s['gifts_with_value']:,} "
        f"({s['gifts_with_value'] / s['total_gifts'] * 100:.1f}%)"
    )
    if s["total_value"]:
        click.echo(f"\nTotal Value: ${s['total_value']:,.2f}")
        click.echo(f"Average Value: ${s['average_value']:,.2f}")
        click.echo(f"Min Value: ${s['min_value']:,.2f}")
        click.echo(f"Max Value: ${s['max_value']:,.2f}")
    click.echo(f"\nUnique Donor Countries: {s['unique_countries']}")
    click.echo(f"Unique Recipients: {s['unique_recipients']}\n")


@cli.command("top-countries")
@click.option("--limit", type=int, default=10, show_default=True)
@click.pass_context
def top_countries(ctx, limit):
    """Show top donor countries."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    countries = analyzer.get_top_donor_countries(limit)

    click.echo(f"\nTop {limit} Donor Countries:")
    click.echo("=" * 70)
    click.echo(f"{'Rank':<6} {'Country':<30} {'Gifts':<10} {'Total Value':<15}")
    click.echo("-" * 70)
    for i, c in enumerate(countries, 1):
        value_str = f"${c['total_value']:,.2f}" if c["total_value"] else "N/A"
        click.echo(f"{i:<6} {c['country']:<30} {c['gift_count']:<10} {value_str:<15}")


@cli.command("top-recipients")
@click.option("--limit", type=int, default=10, show_default=True)
@click.pass_context
def top_recipients(ctx, limit):
    """Show top gift recipients."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    recipients = analyzer.get_top_recipients(limit)

    click.echo(f"\nTop {limit} Gift Recipients:")
    click.echo("=" * 80)
    click.echo(f"{'Rank':<6} {'Name':<35} {'Gifts':<10} {'Total Value':<15}")
    click.echo("-" * 80)
    for i, r in enumerate(recipients, 1):
        value_str = f"${r['total_value']:,.2f}" if r["total_value"] else "N/A"
        click.echo(f"{i:<6} {r['name']:<35} {r['gift_count']:<10} {value_str:<15}")


@cli.command()
@click.option("--limit", type=int, default=10, show_default=True)
@click.pass_context
def valuable(ctx, limit):
    """Show the most valuable gifts."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    gifts = analyzer.get_most_valuable_gifts(limit)

    click.echo(f"\n{limit} Most Valuable Gifts:")
    click.echo("=" * 80)
    for i, gift in enumerate(gifts, 1):
        click.echo(f"\n{i}. ${gift['estimated_value']:,.2f}")
        click.echo(f"   Description: {gift['gift_description']}")
        click.echo(f"   From: {gift['donor_name']} ({gift['donor_country']})")
        click.echo(f"   To: {gift['recipient_name']}")
        click.echo(f"   Date: {gift['received']}")


@cli.command()
@click.pass_context
def categories(ctx):
    """Show gift categories."""
    analyzer = GiftsAnalyzer(ctx.obj["database"])
    cats = analyzer.get_gift_categories()

    click.echo("\nGift Categories:")
    click.echo("=" * 50)
    click.echo(f"{'Category':<25} {'Count':<10}")
    click.echo("-" * 50)
    for category, count in cats.items():
        click.echo(f"{category.capitalize():<25} {count:<10}")


@cli.command()
@click.argument("description")
def classify(description):
    """Classify a gift description."""
    classifier = GiftClassifier()
    result = classifier.classify(description)
    materials = classifier.extract_materials(description)
    ceremonial = classifier.is_ceremonial(description)

    click.echo(f"\nClassification for: {description}")
    click.echo("=" * 80)
    click.echo(f"Category: {result['category_name']}")
    if result["subcategory"]:
        click.echo(f"Subcategory: {result['subcategory']}")
    click.echo(f"Confidence: {result['confidence']:.1%}")
    if materials:
        click.echo(f"Materials Detected: {', '.join(materials)}")
    if ceremonial:
        click.echo("Type: Ceremonial/Formal")


@cli.command()
@click.option("--format", "fmt", type=click.Choice(["csv", "json", "jsonl"]), default="csv", show_default=True)
@click.option("--output", required=True, help="Output file path")
@click.pass_context
def export(ctx, fmt, output):
    """Export data to CSV, JSON, or JSON Lines."""
    db = sqlite_utils.Database(ctx.obj["database"])
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        with open(output_path, "w") as f:
            db["gifts"].rows_where(order_by="id").write_csv(f)
    elif fmt == "json":
        output_path.write_text(json.dumps(list(db["gifts"].rows), indent=2))
    elif fmt == "jsonl":
        with open(output_path, "w") as f:
            for row in db["gifts"].rows:
                f.write(json.dumps(row) + "\n")

    click.echo(f"Exported to {fmt.upper()}: {output_path}")


@cli.command()
@click.option(
    "--type", "viz_type",
    type=click.Choice(["all", "dashboard", "countries", "values", "timeline", "recipients"]),
    default="dashboard", show_default=True,
)
@click.pass_context
def visualize(ctx, viz_type):
    """Create matplotlib visualizations."""
    if not HAS_MATPLOTLIB:
        raise click.ClickException("matplotlib is required for visualization. Install with: uv sync --group dev")

    visualizer = GiftsVisualizer(ctx.obj["database"])
    plots = {
        "dashboard": visualizer.create_dashboard,
        "countries": visualizer.plot_top_donor_countries,
        "values": visualizer.plot_value_distribution,
        "timeline": visualizer.plot_gifts_over_time,
        "recipients": visualizer.plot_recipient_analysis,
    }
    for t in (plots.keys() if viz_type == "all" else [viz_type]):
        path = plots[t]()
        click.echo(f"{t.capitalize()} saved to {path}")


# ---------------------------------------------------------------------------
# Pipeline: fetch -> download -> extract -> combine -> enrich -> anonymize ->
# build-db. Every model-calling stage takes --model, resolved through the
# `llm` library (Anthropic and Ollama both work — see llm_client.py).
# ---------------------------------------------------------------------------

@cli.group()
def pipeline():
    """Rebuild the dataset from Federal Register PDFs."""


@pipeline.command("fetch")
@click.option("--output", default="data/raw/federal_register.json", show_default=True)
def pipeline_fetch(output):
    """Fetch Federal Register document metadata."""
    from foreign_gifts.pipeline.fetch import save_documents

    path = save_documents(output)
    click.echo(f"Saved metadata to {path}")


@pipeline.command("download")
@click.option("--metadata", default="data/raw/federal_register.json", show_default=True)
@click.option("--pdf-dir", default="data/raw/pdfs", show_default=True)
def pipeline_download(metadata, pdf_dir):
    """Download Federal Register PDFs."""
    from foreign_gifts.pipeline.pdfs import download_pdfs

    downloaded = download_pdfs(metadata, pdf_dir)
    click.echo(f"Downloaded {len(downloaded)} new PDF(s)")


@pipeline.command("extract")
@click.argument("pdf_path")
@click.option("--output-dir", default="data/interim/extracted", show_default=True)
@click.option("--model", default=None, help="llm model ID (default: GIFTS_MODEL env or claude-haiku-4.5)")
@click.option("--overwrite", is_flag=True, help="Re-process and overwrite existing JSON output")
def pipeline_extract(pdf_path, output_dir, model, overwrite):
    """Extract gift records from a Federal Register PDF or directory of PDFs."""
    from foreign_gifts.pipeline.extract import extract_directory_or_file

    total = extract_directory_or_file(pdf_path, output_dir, model, overwrite)
    click.echo(f"Total records extracted: {total}")


@pipeline.command("combine")
@click.option("--input-dir", default="data/interim/extracted", show_default=True)
@click.option("--output", default="data/interim/combined.json", show_default=True)
def pipeline_combine(input_dir, output):
    """Deduplicate and merge per-document extraction files."""
    from foreign_gifts.pipeline.combine import combine

    path = combine(input_dir, output)
    click.echo(f"Combined data written to {path}")


@pipeline.command("enrich")
@click.option("--input", "input_path", default="data/interim/combined.json", show_default=True)
@click.option("--output", default="data/interim/enriched.json", show_default=True)
@click.option("--model", default=None, help="llm model ID (default: GIFTS_MODEL env or claude-haiku-4.5)")
def pipeline_enrich(input_path, output, model):
    """Extract donor and recipient names/titles/countries via LLM."""
    from foreign_gifts.pipeline.enrich import enrich

    path = enrich(input_path, output, model)
    click.echo(f"Enriched data written to {path}")


@pipeline.command("anonymize")
@click.option("--input", "input_path", default="data/interim/enriched.json", show_default=True)
def pipeline_anonymize(input_path):
    """Blank donor details for anonymous agency-employee recipients."""
    from foreign_gifts.pipeline.anonymize import anonymize

    changed = anonymize(input_path)
    click.echo(f"Anonymized {changed} record(s)")


@pipeline.command("build-db")
@click.option("--input", "input_path", default="data/interim/enriched.json", show_default=True)
@click.option("--db", "db_path", default=DEFAULT_DB, show_default=True)
@click.option("--csv", "csv_path", default="data/gifts.csv", show_default=True)
@click.option("--json", "json_path", default="data/gifts.json", show_default=True)
def pipeline_build_db(input_path, db_path, csv_path, json_path):
    """Build gifts.db, gifts.csv, and gifts.json from enriched records."""
    from foreign_gifts.pipeline.database import build_database

    path = build_database(input_path, db_path, csv_path, json_path)
    click.echo(f"Database built at {path}")


@pipeline.command("all")
@click.option("--model", default=None, help="llm model ID for extraction and enrichment")
def pipeline_all(model):
    """Run the full pipeline end to end: fetch, download, extract, combine, enrich, anonymize, build-db."""
    from foreign_gifts.pipeline.anonymize import anonymize
    from foreign_gifts.pipeline.combine import combine
    from foreign_gifts.pipeline.database import build_database
    from foreign_gifts.pipeline.enrich import enrich
    from foreign_gifts.pipeline.extract import extract_directory_or_file
    from foreign_gifts.pipeline.fetch import save_documents
    from foreign_gifts.pipeline.pdfs import download_pdfs

    click.echo("1/7 Fetching Federal Register metadata...")
    save_documents()
    click.echo("2/7 Downloading and converting PDFs...")
    download_pdfs()
    click.echo("3/7 Extracting gift records...")
    extract_directory_or_file("data/raw/pdfs", "data/interim/extracted", model)
    click.echo("4/7 Combining and deduplicating...")
    combine()
    click.echo("5/7 Enriching donor/recipient details...")
    enrich(model_id=model)
    click.echo("6/7 Anonymizing agency employees...")
    anonymize()
    click.echo("7/7 Building database and exports...")
    build_database()
    click.echo("Done.")


if __name__ == "__main__":
    cli()
