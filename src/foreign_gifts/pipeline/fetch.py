"""Fetch Federal Register document metadata for foreign-gifts notices."""

import json
from pathlib import Path

import requests

BASE_URL = "https://www.federalregister.gov/api/v1/documents"
SEARCH_TERM = '"Gifts to Federal Employees from Foreign Government Sources"'
AGENCIES = ["state-department"]


def fetch_documents(term: str = SEARCH_TERM, agencies=AGENCIES, page: int = 1) -> dict:
    params = {"conditions[term]": term, "format": "json", "page": page}
    if agencies:
        params["conditions[agencies][]"] = agencies

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()


def save_documents(output_path: str = "data/raw/federal_register.json") -> str:
    data = fetch_documents()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    return str(out)
