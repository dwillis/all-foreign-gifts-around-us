"""Extract gift records from Federal Register PDFs using natural-pdf + llm.

Pipeline per page:
  1. Find and exclude the Federal Register running header
  2. Extract clean text from the content region below the header
  3. OCR fallback for scanned / image-only pages
  4. Skip pages with no gift-record content (preamble, other notices)
  5. LLM extraction of all gift records on the page via a Pydantic schema
"""

import json
import sys
from pathlib import Path

from natural_pdf import PDF

from foreign_gifts.llm_client import get_model
from foreign_gifts.models import GiftRecordList

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


def extract_page_text(page) -> str:
    """Extract text from a page, stripping the Federal Register running header."""
    fr_header = page.find('text:contains("Federal Register")')
    text = fr_header.below().extract_text() if fr_header else page.extract_text()
    text = text or ""

    # OCR fallback: scanned or image-only pages produce very short text
    if len(text.strip()) < 50:
        page.apply_ocr()
        fr_header = page.find('text:contains("Federal Register")')
        text = fr_header.below().extract_text() if fr_header else page.extract_text()
        text = text or ""

    return text


def has_gift_content(text: str) -> bool:
    """Return True if the page likely contains gift records (not just preamble)."""
    return any(marker in text for marker in GIFT_MARKERS)


def parse_gifts_from_text(text: str, model) -> list[dict]:
    """Use the LLM to extract gift records from page text.

    Tries structured schema extraction first; falls back to prompting for a
    raw JSON array if the model doesn't support schema= or returns an error.
    """
    prompt = f"Extract all foreign gift records from this Federal Register page:\n\n{text}"

    try:
        response = model.prompt(prompt, system=SYSTEM_PROMPT, schema=GiftRecordList)
        data = json.loads(response.text())
        gifts = data.get("gifts", [])
        if isinstance(gifts, list):
            return gifts
    except Exception as primary_err:
        print(f"    [schema extraction failed: {primary_err}; trying fallback]", file=sys.stderr)

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


def extract_from_pdf(pdf_path: str, model) -> list[dict]:
    """Open a PDF and extract all gift records across all pages."""
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


def process_pdf(pdf_path: str, output_path: str, model) -> int:
    """Extract gifts from pdf_path and write JSON to output_path. Returns count."""
    print(f"Processing {Path(pdf_path).name} ...")
    records = extract_from_pdf(pdf_path, model)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(records, indent=2))
    print(f"  -> {len(records)} records written to {output_path}")
    return len(records)


def extract_directory_or_file(
    pdf_path: str,
    output_dir: str,
    model_id: str | None,
    overwrite: bool = False,
) -> int:
    """Extract gift records from a single PDF or every PDF in a directory."""
    model = get_model(model_id)
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if pdf_path.is_dir():
        pdfs = sorted(pdf_path.glob("*.pdf"))
    elif pdf_path.is_file():
        pdfs = [pdf_path]
    else:
        raise FileNotFoundError(f"{pdf_path} is not a file or directory")

    total = 0
    for pdf in pdfs:
        out = output_dir / f"{pdf.stem}.json"
        if out.exists() and not overwrite:
            print(f"Skipping {pdf.name} (output exists; use --overwrite to force)")
            continue
        total += process_pdf(str(pdf), str(out), model)

    return total
