import json

from foreign_gifts.pipeline.combine import combine_json_files

RECORD = {
    "name_and_title": "The Honorable Jane Doe, Secretary of State",
    "gift_description": "Vase",
    "received": "2020-01-01",
    "estimated_value": "500.00",
    "foreign_donor": "His Excellency John Smith, Prime Minister of Testland",
    "circumstances": "Non-acceptance would cause embarrassment to donor and U.S. Government",
}

UNIQUE_RECORD = {**RECORD, "gift_description": "Sword"}


def _write(path, records):
    path.write_text(json.dumps(records))


def test_duplicate_records_merge_dispositions(tmp_path):
    _write(tmp_path / "a.json", [{**RECORD, "disposition": "Pending Transfer to NARA"}])
    _write(tmp_path / "b.json", [{**RECORD, "disposition": "Transferred to NARA"}])

    combined = combine_json_files(str(tmp_path))

    assert len(combined) == 1
    assert combined[0]["disposition"] == ["Pending Transfer to NARA", "Transferred to NARA"]


def test_distinct_records_are_not_merged(tmp_path):
    _write(tmp_path / "a.json", [{**RECORD, "disposition": "Transferred to NARA"}])
    _write(tmp_path / "b.json", [{**UNIQUE_RECORD, "disposition": "Transferred to NARA"}])

    combined = combine_json_files(str(tmp_path))

    assert len(combined) == 2
    descriptions = {item["gift_description"] for item in combined}
    assert descriptions == {"Vase", "Sword"}


def test_record_without_disposition_gets_empty_list(tmp_path):
    _write(tmp_path / "a.json", [dict(RECORD)])

    combined = combine_json_files(str(tmp_path))

    assert combined[0]["disposition"] == []
