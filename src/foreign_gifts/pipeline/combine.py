"""Deduplicate per-document extraction JSON into a single combined file."""

import json
from collections import OrderedDict
from pathlib import Path


def combine_json_files(directory: str) -> list[dict]:
    combined_data = []
    seen: dict[tuple, dict] = {}

    for file_path in sorted(Path(directory).glob("*.json")):
        data = json.loads(file_path.read_text(), object_pairs_hook=OrderedDict)
        for item in data:
            item_key = tuple((k, v) for k, v in item.items() if k != "disposition")
            if item_key not in seen:
                item["disposition"] = [item["disposition"]] if "disposition" in item else []
                combined_data.append(item)
                seen[item_key] = item
            else:
                existing = seen[item_key]
                if "disposition" in item:
                    new_disposition = item["disposition"]
                    if not isinstance(new_disposition, list):
                        new_disposition = [new_disposition]
                    existing["disposition"].extend(new_disposition)

    return combined_data


def combine(
    input_dir: str = "data/interim/extracted",
    output_path: str = "data/interim/combined.json",
) -> str:
    combined = combine_json_files(input_dir)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(combined, indent=2))
    return str(out)
