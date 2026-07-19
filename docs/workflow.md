# Workflow Guide

This guide explains how to rebuild the dataset from Federal Register PDFs using `uv run gifts pipeline`.

## Overview

```
fetch -> download -> extract -> combine -> enrich -> anonymize -> build-db
```

| Stage | Reads | Writes | Calls an LLM? |
|-------|-------|--------|----------------|
| `fetch` | Federal Register API (all pages) | `data/raw/federal_register.json` | No |
| `download` | `data/raw/federal_register.json` | `data/raw/pdfs/*.pdf`, `data/raw/pdf_index.json` | No |
| `extract` | `data/raw/pdfs/*.pdf`, `data/raw/pdf_index.json` | `data/interim/extracted/*.json` | Yes, for new PDFs only |
| `combine` | `data/interim/extracted/*.json` | `data/interim/combined.json` | No |
| `enrich` | `data/interim/combined.json` | `data/interim/enriched.json` | Yes, for new/failed records only |
| `anonymize` | `data/interim/enriched.json` | (modifies in place) | No |
| `build-db` | `data/interim/enriched.json` | `data/gifts.db`, `data/gifts.csv`, `data/gifts.json`, `data/stats.json`, `site/metadata.json` (description only) | No |

Everything under `data/raw/` and `data/interim/` is gitignored and fully regenerable; only the three files `build-db` produces are committed.

## Running the whole pipeline

```bash
uv run gifts pipeline all --model claude-haiku-4.5
```

## Running stage by stage

### 1. Fetch document metadata

```bash
uv run gifts pipeline fetch
```

Queries the Federal Register API for "Gifts to Federal Employees from Foreign Government Sources" notices from the State Department, walking every page of results (not just the first).

### 2. Download PDFs

```bash
uv run gifts pipeline download
```

Skips any PDF already present in `data/raw/pdfs/`. Also (re)writes `data/raw/pdf_index.json`, mapping each PDF filename to its Federal Register document number and notice URL, so `extract` can stamp provenance onto the records it pulls from that PDF.

### 3. Extract gift records

```bash
uv run gifts pipeline extract data/raw/pdfs --model claude-haiku-4.5
```

For each page: find and strip the Federal Register running header, OCR if the page has almost no extractable text, skip pages without gift-record markers ("Rec'd", "Est. Value", "Excellency", etc.), then ask the model to extract all gift records on the page against the `GiftRecordList` schema (`src/foreign_gifts/models.py`). You can also point this at a single PDF: `uv run gifts pipeline extract data/raw/pdfs/2024-03129.pdf`.

Pass `--overwrite` to re-process PDFs that already have output JSON.

### 4. Combine and deduplicate

```bash
uv run gifts pipeline combine
```

Merges every file in `data/interim/extracted/` into one list, deduplicating on all fields except `disposition` and the `source_*` fields. `disposition` merges into an array for records that appear in more than one notice (a gift can be reported as "Pending Transfer to NARA" one year and "Transferred to NARA" the next); `source_document_number`/`source_document_url` similarly accumulate into `source_documents`/`source_urls` arrays.

### 5. Enrich donor and recipient details

```bash
uv run gifts pipeline enrich --model claude-haiku-4.5
```

Asks the model to split `foreign_donor` into `donor_name` / `donor_title` / `donor_country`, and `name_and_title` into `recipient_name` / `recipient_title`.

This step is incremental: it compares each record against the existing `data/interim/enriched.json` and reuses the prior result for anything already successfully enriched, only calling the LLM for new records or ones that failed last time. Delete `data/interim/enriched.json` first if you want to force a full re-enrichment.

### 6. Anonymize agency employees

```bash
uv run gifts pipeline anonymize
```

Blanks `donor_name`, `donor_title`, and `donor_country` wherever the recipient is listed as "An Agency Employee," to avoid identifying that person via their gift's donor.

### 7. Build the database and exports

```bash
uv run gifts pipeline build-db
```

Writes `data/gifts.db` (with FTS5 full-text search enabled on the description/name/donor fields), `data/gifts.csv`, and `data/gifts.json`. Also standardizes several fields, always keeping the original text alongside the standardized value:

- `received` / `received_precision`: unifies every "missing date" spelling (`""`, `"Unknown"`, `"unknown"`, ranges, etc.) to a single `null` + `"unknown"` precision, and flags partial (`"year"`/`"month"`) or ranged (`"range"`) dates.
- `disposition` / `disposition_raw`: maps free text to a small controlled vocabulary (`src/foreign_gifts/standardize.py::canonicalize_disposition`) — e.g. every "Pending transfer to GSA/General Services Administration" variant collapses to one value.
- `donor_country` / `donor_country_raw` / `donor_country_iso3` / `donor_entity_type`: canonicalizes country name variants (`canonicalize_country`), rolls subnational entities (Dubai, Bavaria, ...) up to their parent country, and flags international organizations separately.
- `recipient_name` / `recipient_name_raw` / `recipient_name_source`: when the source text names no one at all (a bare "President", "Vice President", or "First Lady"), resolves the actual officeholder from `received` via `src/foreign_gifts/officeholders.py` instead of trusting whatever the LLM guessed. This fixes real historical rows in the shipped dataset — e.g. 2005 Bush-era gifts that had been misattributed to "Joseph R. Biden Jr." because that's who was president when enrichment ran, not who actually received the gift.

`build-db` also writes `data/stats.json` (total gifts, year range, distinct donor country count) and refreshes the `description` field in `site/metadata.json`, so neither the landing page nor the Datasette Lite metadata can drift out of sync with the actual data the way hand-edited numbers did before.

You can re-run standardization alone, without any new LLM calls, by pointing `build-db` at the already-built `data/gifts.json` instead of `data/interim/enriched.json`:

```bash
uv run gifts pipeline build-db --input data/gifts.json
```

Only do this from a copy of `data/gifts.json` that still has the *original* raw values in its `donor_country`/`disposition`/`recipient_name` fields (e.g. right after `git checkout` from before a standardization change) — running it a second time straight from its own already-standardized output will still produce correct canonical values, but the `_raw` columns will capture the already-standardized text instead of the true original, losing the audit trail.

## Analyzing the result

```bash
uv run gifts stats
uv run gifts search --keyword painting --country France
uv run datasette data/gifts.db -m site/metadata.json
```

See [Analysis Features](analysis_features.md) for the full command and API reference.

## Best Practices

1. **Cost management**: `extract` and `enrich` are the only stages that call an LLM. Test on a single PDF (`gifts pipeline extract data/raw/pdfs/<file>.pdf`) before running the full directory.
2. **Quality checks**: spot-check a sample of extracted records against the source PDF, especially for scanned/OCR'd pages.
3. **Re-running**: `extract` skips PDFs that already have output JSON unless you pass `--overwrite`; the other stages simply overwrite their output each run.

## Troubleshooting

### LLM extraction errors

`extract` falls back to a plain JSON-array prompt if schema-based extraction fails, and logs both failures to stderr. If a page consistently fails, check the OCR'd text quality or try a stronger model with `--model`.

### JSON parsing errors

Check the stderr output from `extract`/`enrich` for `[schema extraction failed: ...]` or `[fallback extraction failed: ...]` messages, which include the underlying error.

### Database errors

`build-db` expects the shape produced by `enrich` (`GiftRecord` fields plus `donor_name`/`donor_title`/`donor_country`/`recipient_name`/`recipient_title`). If it errors, check `data/interim/enriched.json` for missing fields.
