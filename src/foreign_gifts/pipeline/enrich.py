"""Enrich combined gift records with structured donor/recipient details via LLM.

Incremental: a record is skipped and its previous result reused if
`output_path` already has a matching record with that detail filled in, so
re-running this stage after new PDFs are extracted only calls the LLM for
genuinely new records (or ones that failed to extract last time).
"""

import json
from pathlib import Path

from foreign_gifts.llm_client import get_model
from foreign_gifts.models import DonorDetails, RecipientDetails

DONOR_SYSTEM_PROMPT = (
    "Extract the donor name (without honorifics), title, and country from the "
    "provided foreign_donor string."
)
RECIPIENT_SYSTEM_PROMPT = (
    "Extract the recipient name (without honorifics) and title from the "
    "provided name_and_title string."
)

# Fields that identify the same underlying gift across pipeline runs
# (everything combine.py dedupes on except `disposition`, which can grow).
IDENTITY_FIELDS = [
    "name_and_title",
    "gift_description",
    "received",
    "estimated_value",
    "foreign_donor",
    "circumstances",
]


def _identity_key(record: dict) -> tuple:
    return tuple(record.get(field) for field in IDENTITY_FIELDS)


def _load_previous(output_path: str) -> dict[tuple, dict]:
    path = Path(output_path)
    if not path.exists():
        return {}
    try:
        previous = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return {_identity_key(r): r for r in previous}


def extract_donor_details(foreign_donor: str, model) -> dict:
    response = model.prompt(foreign_donor, system=DONOR_SYSTEM_PROMPT, schema=DonorDetails)
    return json.loads(response.text())


def extract_recipient_details(name_and_title: str, model) -> dict:
    response = model.prompt(name_and_title, system=RECIPIENT_SYSTEM_PROMPT, schema=RecipientDetails)
    return json.loads(response.text())


def enrich(
    input_path: str = "data/interim/combined.json",
    output_path: str = "data/interim/enriched.json",
    model_id: str | None = None,
) -> str:
    records = json.loads(Path(input_path).read_text())
    previous = _load_previous(output_path)

    model = None
    donor_calls = 0
    recipient_calls = 0

    def resolved_model():
        nonlocal model
        if model is None:
            model = get_model(model_id)
        return model

    for record in records:
        prior = previous.get(_identity_key(record))

        foreign_donor = record.get("foreign_donor")
        if foreign_donor:
            if prior and (prior.get("donor_name") or prior.get("donor_title") or prior.get("donor_country")):
                record["donor_name"] = prior.get("donor_name", "")
                record["donor_title"] = prior.get("donor_title", "")
                record["donor_country"] = prior.get("donor_country", "")
            else:
                donor_calls += 1
                try:
                    record.update(extract_donor_details(foreign_donor, resolved_model()))
                except Exception as e:
                    print(f"  [donor extraction failed for {foreign_donor!r}: {e}]")
                    record.setdefault("donor_name", "")
                    record.setdefault("donor_title", "")
                    record.setdefault("donor_country", "")

        name_and_title = record.get("name_and_title")
        if name_and_title:
            if prior and (prior.get("recipient_name") or prior.get("recipient_title")):
                record["recipient_name"] = prior.get("recipient_name", "")
                record["recipient_title"] = prior.get("recipient_title", "")
            else:
                recipient_calls += 1
                try:
                    record.update(extract_recipient_details(name_and_title, resolved_model()))
                except Exception as e:
                    print(f"  [recipient extraction failed for {name_and_title!r}: {e}]")
                    record.setdefault("recipient_name", "")
                    record.setdefault("recipient_title", "")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Enrich: {donor_calls} donor + {recipient_calls} recipient LLM call(s); the rest reused from {output_path}")
    return str(out)
