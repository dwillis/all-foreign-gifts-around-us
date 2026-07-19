"""Deduplicate per-document extraction JSON into a single combined file."""

import json
from collections import OrderedDict
from pathlib import Path

# Fields that don't identify "the same gift" and so are excluded from the
# dedup key: `disposition` can change between reporting years (a gift is
# "Pending Transfer to NARA" one year, "Transferred to NARA" the next), and
# the source_* fields just record which Federal Register notice(s) a gift
# was reported in, which can legitimately differ across otherwise-identical
# re-reported entries.
NON_IDENTITY_FIELDS = {"disposition", "source_document_number", "source_document_url"}


def combine_json_files(directory: str) -> list[dict]:
    combined_data = []
    seen: dict[tuple, dict] = {}

    for file_path in sorted(Path(directory).glob("*.json")):
        data = json.loads(file_path.read_text(), object_pairs_hook=OrderedDict)
        for item in data:
            item_key = tuple((k, v) for k, v in item.items() if k not in NON_IDENTITY_FIELDS)
            doc_number = item.pop("source_document_number", None)
            doc_url = item.pop("source_document_url", None)

            if item_key not in seen:
                item["disposition"] = [item["disposition"]] if "disposition" in item else []
                item["source_documents"] = [doc_number] if doc_number else []
                item["source_urls"] = [doc_url] if doc_url else []
                combined_data.append(item)
                seen[item_key] = item
            else:
                existing = seen[item_key]
                if "disposition" in item:
                    new_disposition = item["disposition"]
                    if not isinstance(new_disposition, list):
                        new_disposition = [new_disposition]
                    existing["disposition"].extend(new_disposition)
                if doc_number and doc_number not in existing["source_documents"]:
                    existing["source_documents"].append(doc_number)
                if doc_url and doc_url not in existing["source_urls"]:
                    existing["source_urls"].append(doc_url)

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
