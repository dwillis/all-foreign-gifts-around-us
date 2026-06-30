"""
Extract gift records from Federal Register PDFs using NaturalPDF + llm library.

Pipeline per page:
  1. Find and exclude the Federal Register running header
  2. Extract clean text from the content region below the header
  3. OCR fallback for scanned / image-only pages
  4. Skip pages with no gift-record content (preamble, other notices)
  5. LLM extraction of all gift records on the page via Pydantic schema
  6. Write JSON array compatible with combine_json.py

Usage:
    uv run python src/extractors/natural_pdf_extractor.py pdfs/2024-03129.pdf
    uv run python src/extractors/natural_pdf_extractor.py pdfs/ --overwrite
    uv run python src/extractors/natural_pdf_extractor.py pdfs/ --model claude-3-5-sonnet-20241022

API key:
    Set ANTHROPIC_API_KEY in your environment, or run: uv run llm keys set anthropic
    Note: the existing CLAUDE_API_KEY env var is NOT used here — use ANTHROPIC_API_KEY.
    To list available models: uv run llm models
"""

import argparse
import json
import sys
from pathlib import Path

import llm
from natural_pdf import PDF
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class GiftRecord(BaseModel):
    name_and_title: str
    gift_description: str
    received: str
    estimated_value: str
    disposition: str
    foreign_donor: str
    circumstances: str


class GiftRecordList(BaseModel):
    gifts: list[GiftRecord]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are extracting foreign gift records from a U.S. Federal Register notice. "
    "Extract ALL tangible gifts and gifts of travel regardless of recipient title. "
    "Dates must be in yyyy-mm-dd format. "
    "estimated_value must be a numeric dollar amount only — no dollar sign, no commas (e.g. '1200.00'). "
    "If a field is absent from the text, use an empty string. "
    "Skip preamble, legal boilerplate, and non-gift content. "
    "Return only actual gift records."
)

# Markers that distinguish gift-data pages from preamble / other notices
GIFT_MARKERS = ["Rec'd", "Est. Value", "Disposition", "Excellency", "Majesty", "Honorable"]

# Run `uv run llm models` to see all available IDs. Aliases and full
# anthropic/ prefixed IDs both work, e.g. claude-haiku-4.5, claude-sonnet-4.6
DEFAULT_MODEL = "claude-haiku-4.5"


# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------

def extract_page_text(page) -> str:
    """
    Extract text from a page, stripping the Federal Register running header.

    The running header ('Federal Register / Vol. XX ...') appears at the top of
    every page. We find it and extract text only from the region below it.
    """
    fr_header = page.find('text:contains("Federal Register")')

    if fr_header:
        text = fr_header.below().extract_text() or ""
    else:
        text = page.extract_text() or ""

    # OCR fallback: scanned or image-only pages produce very short text
    if len(text.strip()) < 50:
        page.apply_ocr()
        fr_header = page.find('text:contains("Federal Register")')
        if fr_header:
            text = fr_header.below().extract_text() or ""
        else:
            text = page.extract_text() or ""

    return text


def has_gift_content(text: str) -> bool:
    """Return True if the page likely contains gift records (not just preamble)."""
    return any(marker in text for marker in GIFT_MARKERS)


# ---------------------------------------------------------------------------
# LLM extraction
# ---------------------------------------------------------------------------

def parse_gifts_from_text(text: str, model) -> list[dict]:
    """
    Use LLM to extract gift records from page text.

    Tries structured schema extraction first; falls back to prompting for a
    raw JSON array if the model doesn't support schema= or returns an error.
    """
    prompt = f"Extract all foreign gift records from this Federal Register page:\n\n{text}"

    # Primary: structured Pydantic schema
    try:
        response = model.prompt(prompt, system=SYSTEM_PROMPT, schema=GiftRecordList)
        data = json.loads(response.text())
        gifts = data.get("gifts", [])
        if isinstance(gifts, list):
            return gifts
    except Exception as primary_err:
        print(f"    [schema extraction failed: {primary_err}; trying fallback]", file=sys.stderr)

    # Fallback: ask for a raw JSON array
    fallback_prompt = (
        prompt
        + "\n\nReturn a JSON array. Each element must have exactly these keys: "
        "name_and_title, gift_description, received, estimated_value, "
        "disposition, foreign_donor, circumstances."
    )
    try:
        response = model.prompt(fallback_prompt, system=SYSTEM_PROMPT)
        raw = response.text().strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except Exception as fallback_err:
        print(f"    [fallback extraction failed: {fallback_err}]", file=sys.stderr)

    return []


# ---------------------------------------------------------------------------
# Main extraction logic
# ---------------------------------------------------------------------------

def extract_from_pdf(pdf_path: str, model_id: str) -> list[dict]:
    """Open a PDF and extract all gift records across all pages."""
    model = llm.get_model(model_id)
    all_records: list[dict] = []

    pdf = PDF(pdf_path)
    try:
        for page in pdf.pages:
            text = extract_page_text(page)
            if not has_gift_content(text):
                continue

            records = parse_gifts_from_text(text, model)
            all_records.extend(records)

            page_num = getattr(page, "page_number", "?")
            print(f"  page {page_num}: {len(records)} record(s)", file=sys.stderr)
    finally:
        pdf.close()

    return all_records


def process_pdf(pdf_path: str, output_path: str, model_id: str) -> int:
    """Extract gifts from pdf_path and write JSON to output_path. Returns count."""
    print(f"Processing {Path(pdf_path).name} ...")
    records = extract_from_pdf(pdf_path, model_id)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(records, f, indent=4)
    print(f"  → {len(records)} records written to {output_path}")
    return len(records)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract foreign gift records from Federal Register PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run python src/extractors/natural_pdf_extractor.py pdfs/2024-03129.pdf\n"
            "  uv run python src/extractors/natural_pdf_extractor.py pdfs/ --output-dir json\n"
            "  uv run python src/extractors/natural_pdf_extractor.py pdfs/ --overwrite\n"
            "\n"
            "List available models:  uv run llm models\n"
            "Set API key (ANTHROPIC_API_KEY):  uv run llm keys set anthropic\n"
        ),
    )
    parser.add_argument("pdf", help="PDF file or directory of PDFs")
    parser.add_argument(
        "--output-dir",
        default="json",
        help="Output directory for JSON files (default: json/)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"LLM model ID (default: {DEFAULT_MODEL}). Run 'uv run llm models' to list options. e.g. claude-haiku-4.5, claude-sonnet-4.6",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-process and overwrite existing JSON output files",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    output_dir = Path(args.output_dir)

    if pdf_path.is_dir():
        pdfs = sorted(pdf_path.glob("*.pdf"))
    elif pdf_path.is_file():
        pdfs = [pdf_path]
    else:
        print(f"Error: {pdf_path} is not a file or directory", file=sys.stderr)
        sys.exit(1)

    if not pdfs:
        print(f"No PDF files found at {pdf_path}", file=sys.stderr)
        sys.exit(1)

    total = 0
    for pdf in pdfs:
        out = output_dir / f"{pdf.stem}.json"
        if out.exists() and not args.overwrite:
            print(f"Skipping {pdf.name} (output exists; use --overwrite to force)")
            continue
        total += process_pdf(str(pdf), str(out), model_id=args.model)

    print(f"\nTotal records extracted: {total}")


if __name__ == "__main__":
    main()
