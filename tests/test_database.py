import json

from foreign_gifts.pipeline.database import build_database

RECORD = {
    "name_and_title": "President",
    "gift_description": "Model ship",
    "received": "2005-03-09",
    "estimated_value": "425.00",
    "disposition": ["Pending Transfer to General Services Administration", "Transferred to GSA"],
    "foreign_donor": "His Excellency Traian Basescu, President of Romania",
    "circumstances": "Non-acceptance would cause embarrassment to donor and U.S. Government.",
    "donor_name": "Traian Basescu",
    "donor_title": "President",
    "donor_country": "Romania",
    "recipient_name": "Joseph R. Biden Jr.",
    "recipient_title": "President",
}


def _build(tmp_path, records):
    input_path = tmp_path / "enriched.json"
    input_path.write_text(json.dumps(records))
    build_database(
        input_path=str(input_path),
        db_path=str(tmp_path / "gifts.db"),
        csv_path=str(tmp_path / "gifts.csv"),
        json_path=str(tmp_path / "gifts.json"),
        stats_path=str(tmp_path / "stats.json"),
        metadata_path=str(tmp_path / "does-not-exist.json"),
    )
    return json.loads((tmp_path / "gifts.json").read_text())


def test_build_database_fixes_officeholder_misattribution(tmp_path):
    rows = _build(tmp_path, [RECORD])
    row = rows[0]
    assert row["recipient_name"] == "George W. Bush"
    assert row["recipient_name_raw"] == "Joseph R. Biden Jr."
    assert row["recipient_name_source"] == "date-resolved"


def test_build_database_canonicalizes_country_and_disposition(tmp_path):
    rows = _build(tmp_path, [RECORD])
    row = rows[0]
    assert row["donor_country"] == "Romania"
    assert row["donor_country_iso3"] == "ROU"
    assert row["donor_entity_type"] == "country"
    assert row["disposition"] == "Pending Transfer to GSA"
    assert "Pending Transfer to General Services Administration" in row["disposition_raw"]


def test_build_database_normalizes_missing_dates_to_null(tmp_path):
    record = {**RECORD, "received": "Unknown"}
    rows = _build(tmp_path, [record])
    row = rows[0]
    assert row["received"] is None
    assert row["received_precision"] == "unknown"


def test_build_database_writes_stats_file(tmp_path):
    _build(tmp_path, [RECORD])
    stats = json.loads((tmp_path / "stats.json").read_text())
    assert stats["total_gifts"] == 1
    assert stats["min_year"] == "2005"
    assert stats["max_year"] == "2005"
    assert stats["donor_countries"] == 1


def test_build_database_saudi_iraq_mis_slot_fix_is_idempotent(tmp_path):
    record = {**RECORD, "donor_name": "Kingdom of Saudi Arabia", "donor_title": "", "donor_country": None}
    rows = _build(tmp_path, [record])
    assert rows[0]["donor_country"] == "Saudi Arabia"

    # Re-running build_database on its own already-standardized output must
    # not blank out the country a second time.
    rows_again = _build(tmp_path, rows)
    assert rows_again[0]["donor_country"] == "Saudi Arabia"
