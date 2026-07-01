# Workflow Guide

This guide explains how to rebuild the dataset from Federal Register PDFs using `uv run gifts pipeline`.

## Overview

```
fetch -> download -> extract -> combine -> enrich -> anonymize -> build-db
```

| Stage | Reads | Writes | Calls an LLM? |
|-------|-------|--------|----------------|
| `fetch` | Federal Register API | `data/raw/federal_register.json` | No |
| `download` | `data/raw/federal_register.json` | `data/raw/pdfs/*.pdf` | No |
| `extract` | `data/raw/pdfs/*.pdf` | `data/interim/extracted/*.json` | Yes, for new PDFs only |
| `combine` | `data/interim/extracted/*.json` | `data/interim/combined.json` | No |
| `enrich` | `data/interim/combined.json` | `data/interim/enriched.json` | Yes, for new/failed records only |
| `anonymize` | `data/interim/enriched.json` | (modifies in place) | No |
| `build-db` | `data/interim/enriched.json` | `data/gifts.db`, `data/gifts.csv`, `data/gifts.json` | No |

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

Queries the Federal Register API for "Gifts to Federal Employees from Foreign Government Sources" notices from the State Department.

### 2. Download PDFs

```bash
uv run gifts pipeline download
```

Skips any PDF already present in `data/raw/pdfs/`.

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

Merges every file in `data/interim/extracted/` into one list, deduplicating on all fields except `disposition` and merging `disposition` values into an array for records that appear in more than one notice (a gift can be reported as "Pending Transfer to NARA" one year and "Transferred to NARA" the next).

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

Writes `data/gifts.db` (with FTS5 full-text search enabled on the description/name/donor fields), `data/gifts.csv`, and `data/gifts.json`.

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
