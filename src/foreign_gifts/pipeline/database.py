"""Build the committed gifts.db / gifts.csv / gifts.json artifacts."""

import csv
import json
from pathlib import Path

import sqlite_utils

from foreign_gifts.officeholders import resolve_recipient_name
from foreign_gifts.standardize import canonicalize_country, canonicalize_disposition, normalize_date

FTS_COLUMNS = ["gift_description", "foreign_donor", "name_and_title", "recipient_name"]

# A handful of notices include "gifts received in previous years" catch-up
# entries reaching back decades; the dataset is scoped to 2005 onward.
MIN_YEAR = "2005"

SCHEMA = {
    "id": int,
    "name_and_title": str,
    "gift_description": str,
    "received": str,
    "received_precision": str,
    "estimated_value": float,
    "disposition": str,
    "disposition_raw": str,
    "foreign_donor": str,
    "circumstances": str,
    "donor_name": str,
    "donor_title": str,
    "donor_country": str,
    "donor_country_raw": str,
    "donor_country_iso3": str,
    "donor_entity_type": str,
    "recipient_name": str,
    "recipient_name_raw": str,
    "recipient_name_source": str,
    "recipient_title": str,
    "source_documents": str,
    "source_urls": str,
}


def _parse_value(raw) -> float | None:
    """Parse an estimated_value string into a float, or None if unparseable.

    Some early records recorded a range ("1000-1500") or vague phrase
    ("Unknown", "In appraisal process", "Over $500") instead of a number;
    ranges resolve to their low end, vague phrases resolve to None.
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        return float(raw)

    text = raw.strip()
    lower = text.lower()
    if lower in ("unknown", "") or lower.startswith("over") or lower.startswith("in appraisal"):
        return None

    for sep in ("-", " to "):
        if sep in text:
            text = text.split(sep)[0]
            break

    try:
        return float(text.replace(",", "").replace("$", ""))
    except ValueError:
        return None


def _keep_record(record: dict) -> bool:
    """Drop records received before MIN_YEAR; keep records with an unknown date."""
    year = (record.get("received") or "")[:4]
    return not (year.isdigit() and year < MIN_YEAR)


def _collapse_disposition(disposition_field) -> tuple[str, str]:
    """Return (chosen, raw) from a disposition value.

    `disposition_field` is a list when it comes straight from combine.py
    (one entry per Federal Register document the gift appeared in, since a
    gift can be "Pending Transfer to NARA" one year and "Transferred to
    NARA" the next) or a single string for already-built rows. `raw` joins
    every distinct value seen, for transparency alongside the canonicalized
    value.
    """
    if isinstance(disposition_field, list):
        values = [d for d in disposition_field if d]
        raw = "; ".join(dict.fromkeys(values)) if values else "N/A"
        chosen = next((d for d in disposition_field if d == "Transferred to NARA"), values[0] if values else "N/A")
    else:
        chosen = disposition_field or "N/A"
        raw = chosen
    return chosen, raw


def _resolve_donor_fields(record: dict) -> tuple[str, str, str | None]:
    """Return (donor_name, donor_title, donor_country_raw).

    Corrects a known mis-slot where a country/organization name ended up in
    donor_name instead of donor_country (observed for Saudi Arabia and
    Iraq). Unlike the original patch, this never blanks an existing
    donor_country just because donor_name is empty, which made the earlier
    version unsafe to run twice over the same data.
    """
    donor_name = record.get("donor_name") or ""
    donor_title = record.get("donor_title") or ""
    donor_country_raw = record.get("donor_country") or None

    if donor_name in ("Kingdom of Saudi Arabia", "Republic of Iraq"):
        donor_country_raw, donor_name, donor_title = donor_name, donor_title, ""

    return donor_name, donor_title, donor_country_raw


def _flatten_sources(record: dict) -> tuple[str | None, str | None]:
    """Flatten source_documents/source_urls (lists combine.py builds when a
    gift is reported across multiple Federal Register notices) into
    comma-separated strings, or None when no provenance was captured (true
    for all rows extracted before this field existed)."""
    docs = record.get("source_documents") or []
    urls = record.get("source_urls") or []
    return (", ".join(docs) or None, ", ".join(urls) or None)


def _build_row(record: dict, idx: int) -> dict:
    donor_name, donor_title, donor_country_raw = _resolve_donor_fields(record)
    country_info = canonicalize_country(donor_country_raw)

    disposition_chosen, disposition_raw = _collapse_disposition(record.get("disposition"))

    received_raw = record.get("received", "")
    received, received_precision = normalize_date(received_raw)

    recipient_name_raw = record.get("recipient_name", "")
    recipient_name, recipient_name_source = resolve_recipient_name(
        name_and_title=record.get("name_and_title", ""),
        recipient_name=recipient_name_raw,
        received_date=received,
        received_precision=received_precision,
    )

    source_documents, source_urls = _flatten_sources(record)

    return {
        "id": idx,
        "name_and_title": record.get("name_and_title", ""),
        "gift_description": record.get("gift_description", ""),
        "received": received,
        "received_precision": received_precision,
        "estimated_value": _parse_value(record.get("estimated_value")),
        "disposition": canonicalize_disposition(disposition_chosen),
        "disposition_raw": disposition_raw,
        "foreign_donor": record.get("foreign_donor", ""),
        "circumstances": record.get("circumstances", ""),
        "donor_name": donor_name,
        "donor_title": donor_title,
        "donor_country": country_info["country"],
        "donor_country_raw": donor_country_raw,
        "donor_country_iso3": country_info["country_iso3"],
        "donor_entity_type": country_info["entity_type"],
        "recipient_name": recipient_name,
        "recipient_name_raw": recipient_name_raw,
        "recipient_name_source": recipient_name_source,
        "recipient_title": record.get("recipient_title", ""),
        "source_documents": source_documents,
        "source_urls": source_urls,
    }


def _compute_stats(rows: list[dict]) -> dict:
    countries = {r["donor_country"] for r in rows if r["donor_country"] and r["donor_entity_type"] == "country"}
    years = sorted({r["received"][:4] for r in rows if r["received"]})
    return {
        "total_gifts": len(rows),
        "min_year": years[0] if years else None,
        "max_year": years[-1] if years else None,
        "donor_countries": len(countries),
    }


def _update_site_metadata(metadata_path: str, stats: dict) -> None:
    """Refresh the Datasette Lite metadata description with current stats,
    so it never drifts from the actual data the way a hand-edited number
    would."""
    path = Path(metadata_path)
    if not path.exists():
        return
    metadata = json.loads(path.read_text())
    if stats["min_year"] and stats["max_year"]:
        year_range = f"{stats['min_year']}-{stats['max_year']}"
    else:
        year_range = "unknown"
    metadata["description"] = (
        "Tangible gifts given to U.S. federal employees by foreign governments, "
        f"extracted from Federal Register notices (calendar years {year_range})."
    )
    path.write_text(json.dumps(metadata, indent=2) + "\n")


def build_database(
    input_path: str = "data/interim/enriched.json",
    db_path: str = "data/gifts.db",
    csv_path: str = "data/gifts.csv",
    json_path: str = "data/gifts.json",
    stats_path: str = "data/stats.json",
    metadata_path: str = "site/metadata.json",
) -> str:
    records = [r for r in json.loads(Path(input_path).read_text()) if _keep_record(r)]
    rows = [_build_row(record, idx) for idx, record in enumerate(records, start=1)]

    db = sqlite_utils.Database(db_path)
    if db["gifts"].exists():
        if db["gifts"].detect_fts():
            db["gifts"].disable_fts()
        db["gifts"].drop()
    table = db["gifts"]
    table.create(SCHEMA, pk="id")
    table.insert_all(rows, pk="id")
    table.enable_fts(FTS_COLUMNS, create_triggers=True, replace=True)

    for out_path in (Path(csv_path).parent, Path(json_path).parent):
        out_path.mkdir(parents=True, exist_ok=True)

    Path(json_path).write_text(json.dumps(rows, indent=2))
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(SCHEMA.keys()))
        writer.writeheader()
        writer.writerows(rows)

    stats = _compute_stats(rows)
    Path(stats_path).parent.mkdir(parents=True, exist_ok=True)
    Path(stats_path).write_text(json.dumps(stats, indent=2))
    _update_site_metadata(metadata_path, stats)

    return db_path
