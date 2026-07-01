"""Blank donor details for gifts received by anonymous agency employees."""

import json
from pathlib import Path


def anonymize(path: str = "data/interim/enriched.json") -> int:
    file_path = Path(path)
    data = json.loads(file_path.read_text())

    changed = 0
    for item in data:
        if item.get("name_and_title") == "An Agency Employee":
            item["donor_name"] = ""
            item["donor_title"] = ""
            item["donor_country"] = ""
            changed += 1

    if changed:
        file_path.write_text(json.dumps(data, indent=2))

    return changed
