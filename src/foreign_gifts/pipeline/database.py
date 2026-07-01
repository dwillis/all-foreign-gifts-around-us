"""Build the committed gifts.db / gifts.csv / gifts.json artifacts."""

import csv
import json
from pathlib import Path

import sqlite_utils

FTS_COLUMNS = ["gift_description", "foreign_donor", "name_and_title", "recipient_name"]

# A handful of notices include "gifts received in previous years" catch-up
# entries reaching back decades; the dataset is scoped to 2005 onward.
MIN_YEAR = "2005"

SCHEMA = {
    "id": int,
    "name_and_title": str,
    "gift_description": str,
    "received": str,
    "estimated_value": float,
    "disposition": str,
    "foreign_donor": str,
    "circumstances": str,
    "donor_name": str,
    "donor_title": str,
    "donor_country": str,
    "recipient_name": str,
    "recipient_title": str,
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


def _build_row(record: dict, idx: int) -> dict:
    disposition = record.get("disposition") or ["N/A"]
    if isinstance(disposition, list):
        disposition = next(
            (d for d in disposition if d == "Transferred to NARA"),
            disposition[0] if disposition else "N/A",
        )

    donor_name = record.get("donor_name") or ""
    donor_title = record.get("donor_title") or ""
    donor_country = record.get("donor_country") or None

    if donor_name in ("Kingdom of Saudi Arabia", "Republic of Iraq"):
        donor_country, donor_name, donor_title = donor_name, donor_title, None
    elif donor_name == "":
        donor_country = None

    return {
        "id": idx,
        "name_and_title": record.get("name_and_title", ""),
        "gift_description": record.get("gift_description", ""),
        "received": record.get("received", ""),
        "estimated_value": _parse_value(record.get("estimated_value")),
        "disposition": disposition,
        "foreign_donor": record.get("foreign_donor", ""),
        "circumstances": record.get("circumstances", ""),
        "donor_name": donor_name,
        "donor_title": donor_title,
        "donor_country": donor_country,
        "recipient_name": record.get("recipient_name", ""),
        "recipient_title": record.get("recipient_title", ""),
    }


def build_database(
    input_path: str = "data/interim/enriched.json",
    db_path: str = "data/gifts.db",
    csv_path: str = "data/gifts.csv",
    json_path: str = "data/gifts.json",
) -> str:
    records = [r for r in json.loads(Path(input_path).read_text()) if _keep_record(r)]
    rows = [_build_row(record, idx) for idx, record in enumerate(records, start=1)]

    db = sqlite_utils.Database(db_path)
    table = db["gifts"]
    table.create(SCHEMA, pk="id", if_not_exists=True)
    table.insert_all(rows, pk="id", replace=True, truncate=True)
    table.enable_fts(FTS_COLUMNS, create_triggers=True, replace=True)

    for out_path in (Path(csv_path).parent, Path(json_path).parent):
        out_path.mkdir(parents=True, exist_ok=True)

    Path(json_path).write_text(json.dumps(rows, indent=2))
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(SCHEMA.keys()))
        writer.writeheader()
        writer.writerows(rows)

    return db_path
