"""Download Federal Register PDFs.

Text conversion is not a separate step — extract.py reads pages directly
from the PDF via natural-pdf, with OCR fallback for scanned pages.
"""

import json
from pathlib import Path

import requests


def build_pdf_index(metadata_path: str = "data/raw/federal_register.json") -> dict:
    """Map PDF filename -> Federal Register document metadata (document
    number, notice URL) so extract.py can stamp provenance onto each gift
    record it pulls from that PDF."""
    metadata = json.loads(Path(metadata_path).read_text())
    index = {}
    for item in metadata.get("results", []):
        pdf_url = item.get("pdf_url")
        if not pdf_url:
            continue
        filename = pdf_url.split("/")[-1]
        index[filename] = {
            "document_number": item.get("document_number"),
            "html_url": item.get("html_url"),
            "publication_date": item.get("publication_date"),
        }
    return index


def save_pdf_index(
    metadata_path: str = "data/raw/federal_register.json",
    index_path: str = "data/raw/pdf_index.json",
) -> str:
    index = build_pdf_index(metadata_path)
    out = Path(index_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=2))
    return str(out)


def download_pdfs(
    metadata_path: str = "data/raw/federal_register.json",
    pdf_dir: str = "data/raw/pdfs",
) -> list[str]:
    pdf_dir_p = Path(pdf_dir)
    pdf_dir_p.mkdir(parents=True, exist_ok=True)

    metadata = json.loads(Path(metadata_path).read_text())
    pdf_urls = [item["pdf_url"] for item in metadata["results"] if "pdf_url" in item]

    downloaded = []
    for url in pdf_urls:
        filename = url.split("/")[-1]
        pdf_path = pdf_dir_p / filename
        if pdf_path.exists():
            continue

        response = requests.get(url)
        response.raise_for_status()
        pdf_path.write_bytes(response.content)
        print(f"Downloaded {pdf_path}")
        downloaded.append(str(pdf_path))

    save_pdf_index(metadata_path, str(pdf_dir_p.parent / "pdf_index.json"))

    return downloaded
