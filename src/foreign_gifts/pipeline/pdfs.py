"""Download Federal Register PDFs.

Text conversion is not a separate step — extract.py reads pages directly
from the PDF via natural-pdf, with OCR fallback for scanned pages.
"""

import json
from pathlib import Path

import requests


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

    return downloaded
