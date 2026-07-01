import json

import foreign_gifts.pipeline.enrich as enrich_module
from foreign_gifts.pipeline.enrich import enrich

RECORD_A = {
    "name_and_title": "The Honorable Jane Doe, Secretary of State",
    "gift_description": "Vase",
    "received": "2020-01-01",
    "estimated_value": "500.00",
    "disposition": ["Transferred to NARA"],
    "foreign_donor": "His Excellency John Smith, Prime Minister of Testland",
    "circumstances": "Non-acceptance would cause embarrassment to donor and U.S. Government",
}

RECORD_B = {**RECORD_A, "gift_description": "Sword"}


class FakeResponse:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class FakeModel:
    def __init__(self):
        self.calls = 0

    def prompt(self, prompt, system=None, schema=None):
        self.calls += 1
        if schema is not None and schema.__name__ == "DonorDetails":
            payload = {"donor_name": "John Smith", "donor_title": "Prime Minister", "donor_country": "Testland"}
        else:
            payload = {"recipient_name": "Jane Doe", "recipient_title": "Secretary of State"}
        return FakeResponse(json.dumps(payload))


def _patch_model(monkeypatch, fake_model):
    monkeypatch.setattr(enrich_module, "get_model", lambda model_id=None: fake_model)


def test_enrich_calls_llm_for_every_record_on_first_run(tmp_path, monkeypatch):
    fake_model = FakeModel()
    _patch_model(monkeypatch, fake_model)

    input_path = tmp_path / "combined.json"
    output_path = tmp_path / "enriched.json"
    input_path.write_text(json.dumps([RECORD_A, RECORD_B]))

    enrich(str(input_path), str(output_path))

    assert fake_model.calls == 4  # 2 records x (donor + recipient)
    enriched = json.loads(output_path.read_text())
    assert enriched[0]["donor_name"] == "John Smith"
    assert enriched[0]["recipient_name"] == "Jane Doe"


def test_enrich_skips_previously_enriched_records(tmp_path, monkeypatch):
    fake_model = FakeModel()
    _patch_model(monkeypatch, fake_model)

    input_path = tmp_path / "combined.json"
    output_path = tmp_path / "enriched.json"
    input_path.write_text(json.dumps([RECORD_A, RECORD_B]))
    enrich(str(input_path), str(output_path))
    assert fake_model.calls == 4

    record_c = {**RECORD_A, "gift_description": "Painting"}
    input_path.write_text(json.dumps([RECORD_A, RECORD_B, record_c]))
    enrich(str(input_path), str(output_path))

    assert fake_model.calls == 6  # only record_c's donor + recipient calls were made
    enriched = json.loads(output_path.read_text())
    assert len(enriched) == 3
    assert all(r["donor_name"] == "John Smith" for r in enriched)


def test_enrich_retries_previously_failed_records(tmp_path, monkeypatch):
    output_path = tmp_path / "enriched.json"
    input_path = tmp_path / "combined.json"
    input_path.write_text(json.dumps([RECORD_A]))

    # A previous run that failed left empty strings for donor/recipient fields.
    failed_previous = [{**RECORD_A, "donor_name": "", "donor_title": "", "donor_country": "",
                         "recipient_name": "", "recipient_title": ""}]
    output_path.write_text(json.dumps(failed_previous))

    fake_model = FakeModel()
    _patch_model(monkeypatch, fake_model)

    enrich(str(input_path), str(output_path))

    assert fake_model.calls == 2  # retried instead of reusing the empty failure result
    enriched = json.loads(output_path.read_text())
    assert enriched[0]["donor_name"] == "John Smith"
