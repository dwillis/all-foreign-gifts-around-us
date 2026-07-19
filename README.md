# All Foreign Gifts Around Us

> Structured data and a browsable dataset of tangible gifts given to U.S. federal employees by foreign governments, extracted from Federal Register notices.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## Overview

The Federal Register is the official journal of the United States government, which publishes various notices, rules, and regulatory information. Among these publications are reports detailing gifts received by U.S. government officials from foreign sources. Some presidential administrations are [better than others](https://oversightdemocrats.house.gov/news/press-releases/oversight-democrats-release-evidence-showing-trump-first-family-failed-to) about reporting these gifts. The current minimum value of reportable gifts is [$480](https://www.gsa.gov/policy-regulations/policy/personal-property-policy-overview/special-programs/foreign-gifts).

This project uses [`llm`](https://llm.datasette.io/) to extract structured data from these unstructured Federal Register notices, via natural-pdf and any model `llm` supports — Claude (Anthropic) or a local model through Ollama. The result is a dataset you can query directly or browse online.

**[Browse the data →](site/index.html)** (or open `site/index.html` locally)

## Quick Start

This project uses [uv](https://docs.astral.sh/uv/) for dependency and script management.

```bash
git clone https://github.com/dwillis/all-foreign-gifts-around-us.git
cd all-foreign-gifts-around-us
uv sync
```

Query the data that's already committed to the repo:

```bash
uv run gifts stats
uv run gifts search --keyword painting --country France
uv run gifts top-countries --limit 20
```

Or browse it locally with [Datasette](https://datasette.io/):

```bash
uv run datasette data/gifts.db -m site/metadata.json
```

## Project Structure

```
all-foreign-gifts-around-us/
├── src/foreign_gifts/       # Python package
│   ├── cli.py                #   `gifts` command-line entry point
│   ├── models.py             #   Pydantic schemas for gift records
│   ├── llm_client.py         #   Resolves models through the `llm` library
│   ├── pipeline/              #   fetch -> download -> extract -> combine -> enrich -> anonymize -> build-db
│   └── analysis/               #   Statistics, classification, enrichment, visualization
├── data/
│   ├── gifts.db, gifts.csv, gifts.json  # Committed dataset
│   ├── raw/                  # Source PDFs (regenerated, gitignored)
│   └── interim/              # Intermediate extraction JSON (regenerated, gitignored)
├── site/                     # Static browse/filter site (Datasette Lite + GitHub Pages)
├── docs/                     # Setup and workflow guides
├── notebooks/                # Jupyter notebook for interactive analysis
└── tests/
```

## The Extraction Pipeline

Rebuilding the dataset from scratch runs through `uv run gifts pipeline <stage>`:

1. **`fetch`** — Query the Federal Register API for foreign-gifts notices.
2. **`download`** — Download the PDFs.
3. **`extract`** — Read each PDF with [natural-pdf](https://github.com/jsoma/natural-pdf), stripping headers and OCR'ing scanned pages, then extract gift records per page via an LLM using a Pydantic schema.
4. **`combine`** — Deduplicate records across documents and merge `disposition` values.
5. **`enrich`** — Use an LLM to split `foreign_donor` and `name_and_title` into structured donor/recipient name, title, and country.
6. **`anonymize`** — Blank donor details for anonymous "Agency Employee" recipients.
7. **`build-db`** — Write `data/gifts.db` (with full-text search enabled), `data/gifts.csv`, and `data/gifts.json`.

Or run the whole thing at once:

```bash
uv run gifts pipeline all --model claude-haiku-4.5
```

### Choosing a model

Every pipeline stage that calls an LLM goes through [`llm`](https://llm.datasette.io/), so any model `llm` knows about works via `--model`:

```bash
# Anthropic (default: claude-haiku-4.5)
uv run llm keys set anthropic
uv run gifts pipeline extract data/raw/pdfs --model claude-sonnet-4.6

# A local model via Ollama
ollama pull qwen3.5:397b-cloud
uv run gifts pipeline extract data/raw/pdfs --model qwen3.5:397b-cloud
```

Set `GIFTS_MODEL` to change the default without passing `--model` every time. Run `uv run llm models` to see everything installed.

## Keeping the Data Current

The Federal Register publishes new gift notices periodically, often with a one- to two-year reporting lag, so `data/gifts.db` is a point-in-time snapshot rather than a live feed. To pull in anything new:

```bash
uv run gifts pipeline all
git add data/gifts.db data/gifts.csv data/gifts.json data/stats.json site/metadata.json
git commit -m "Update dataset through <calendar year>"
git push
```

This is cheap to re-run: `fetch`/`download`/`extract` only touch notices and PDFs you don't already have (`extract` skips a PDF if its output JSON already exists), and `enrich` only sends *new* records to the LLM — it skips anything that already has `donor_name`/`recipient_name` filled in from a previous run. `combine` and `build-db` are pure local steps and always rebuild from everything on disk, so the output stays complete and deduplicated even though the LLM calls are incremental.

Because [`site/index.html`](site/index.html) and [`site/metadata.json`](site/metadata.json) point Datasette Lite straight at the committed `data/gifts.db` on GitHub Pages, pushing the rebuilt file *is* the site update — there's no separate deploy step. `build-db` also regenerates `data/stats.json` (which `site/index.html` fetches at page load to populate its stat boxes) and refreshes `site/metadata.json`'s `description` field, so there's no manual number-updating step left — just commit whatever `pipeline all` or `pipeline build-db` produces.

## Data Schema

| Field | Description |
|-------|-------------|
| `name_and_title` | Recipient's full name and title, as printed |
| `recipient_name` / `recipient_title` | Recipient name (honorifics removed) and title. When the source text names no one at all (a bare "President", "Vice President", or "First Lady"), `recipient_name` is resolved from officeholder tenure dates instead — see `recipient_name_source` |
| `recipient_name_raw` / `recipient_name_source` | The name as originally extracted, and `"date-resolved"` if it was overridden as above |
| `gift_description` | Description of the gift |
| `received` / `received_precision` | Date received (yyyy-mm-dd), `null` if unknown; precision is `"day"`, `"month"`, `"year"`, `"range"` (a reported date range; `received` is the start date), or `"unknown"` |
| `estimated_value` | Estimated value in USD |
| `disposition` / `disposition_raw` | What happened to the gift, standardized to a controlled vocabulary (e.g. "Transferred to NARA", "Pending Transfer to GSA", "Retained for Official Use"), alongside the original text |
| `foreign_donor` | Donor's full name, title, and country, as printed |
| `donor_name` / `donor_title` | Donor name and title |
| `donor_country` / `donor_country_raw` / `donor_country_iso3` / `donor_entity_type` | Donor country, canonicalized so spelling variants collapse to one value (with an ISO3 code where available), plus the original text and an `entity_type` of `"country"`, `"organization"` (UN, EU, ...), `"subnational"` (a city/region rolled up to its parent country), or `"unknown"` |
| `circumstances` | Stated reason the gift was accepted |
| `source_documents` / `source_urls` | Federal Register document number(s) and notice URL(s) the gift was reported in. Only populated for records extracted after this field was added, so it's blank for most of the historical dataset |

## Analysis Features

```bash
uv run gifts stats
uv run gifts search --keyword painting --country France
uv run gifts search --min-value 5000 --recipient Biden
uv run gifts top-countries --limit 20
uv run gifts top-recipients --limit 15
uv run gifts valuable --limit 10
uv run gifts categories
uv run gifts classify "Gold necklace with diamonds"
uv run gifts export --format csv --output out.csv
uv run gifts visualize --type dashboard   # requires: uv sync --group dev
```

Programmatically:

```python
from foreign_gifts.analysis.analyzer import GiftsAnalyzer
from foreign_gifts.analysis.classifier import GiftClassifier

analyzer = GiftsAnalyzer()  # defaults to data/gifts.db
stats = analyzer.get_summary_statistics()
top_countries = analyzer.get_top_donor_countries(limit=20)

classifier = GiftClassifier()
result = classifier.classify("Gold necklace with diamonds")
```

An interactive walkthrough of all of this lives in [`notebooks/gift_analysis.ipynb`](notebooks/gift_analysis.ipynb) (`uv run --group dev jupyter notebook notebooks/gift_analysis.ipynb`). See [docs/analysis_features.md](docs/analysis_features.md) for the full reference.

## Documentation

- [Setup Guide](docs/setup.md)
- [Workflow Guide](docs/workflow.md) — running the extraction pipeline stage by stage
- [Analysis Features](docs/analysis_features.md)
- [Contributing Guide](CONTRIBUTING.md)

## Caveats

- The dataset is scoped to gifts received in 2005 or later. A small number of notices include scattered "gifts received in previous years" catch-up entries reaching back to the 1970s; `build-db` drops these (see `MIN_YEAR` in `src/foreign_gifts/pipeline/database.py`).
- Reporting completeness varies by administration; a gap in a given year likely reflects a reporting delay, not an absence of gifts.
- Values recorded as ranges (e.g. "$1,000–$1,500") resolve to the low end; vague values ("Unknown", "In appraisal process") are left blank.
- Donor/recipient name, title, and country are parsed from free text by an LLM and may occasionally misparse unusual formatting.
- Country canonicalization (`src/foreign_gifts/standardize.py`) covers variant spellings actually observed in this dataset, not every country on earth; an unrecognized value passes through unchanged with no ISO3 code.
- Officeholder resolution (`src/foreign_gifts/officeholders.py`) only covers President, Vice President, First Lady, Secretary of State, and Secretary of Defense — the offices that actually appear as bare, nameless titles in the source text — and only resolves day-precision dates, to stay safely clear of inauguration-day transitions.
- `source_documents`/`source_urls` provenance is only captured for records extracted after that field was added to the pipeline; it's blank for the bulk of the historical dataset, whose extraction predates it.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details. The underlying data is a work of the U.S. Government and is in the public domain.

## Acknowledgments

- Data source: [Federal Register](https://www.federalregister.gov/)
- Built with [uv](https://docs.astral.sh/uv/), [llm](https://llm.datasette.io/), [natural-pdf](https://github.com/jsoma/natural-pdf), and [Datasette](https://datasette.io/)

---

**Note**: This project is for educational and transparency purposes. The data is publicly available from the Federal Register.
