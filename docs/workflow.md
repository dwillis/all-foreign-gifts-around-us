# Workflow Guide

This guide explains how to use the Foreign Gifts Tracker to extract, process, and analyze data.

## Overview

The data processing pipeline consists of several stages:

1. **Data Acquisition** - Download PDFs or text from Federal Register
2. **Text Extraction** - Convert PDFs to text
3. **Data Extraction** - Use LLMs to extract structured data
4. **Data Processing** - Combine, deduplicate, and enrich data
5. **Database Creation** - Store in SQLite database
6. **Export** - Generate CSV and other formats
7. **Analysis** - Query and visualize the data

## Detailed Workflow

### Stage 1: Data Acquisition

#### Manual Download

1. Visit the [Federal Register website](https://www.federalregister.gov/)
2. Search for "foreign gifts"
3. Download relevant PDF documents to `data/raw/pdfs/`

#### Automated Download (using federal_register.py)

```bash
python src/api/federal_register.py
```

This script queries the Federal Register API and downloads new documents automatically.

### Stage 2: Text Extraction

Convert PDFs to text files:

```bash
python src/extractors/pdf_processor.py
```

This will:
- Read PDFs from `data/raw/pdfs/`
- Extract text content
- Save to `data/raw/text/`

**Input:** `data/raw/pdfs/*.pdf`
**Output:** `data/raw/text/*.txt`

### Stage 3: Data Extraction

Extract structured data from text using LLMs:

```bash
python src/extractors/data_extractor.py
```

This script:
- Reads text files from `data/raw/text/`
- Splits into sections based on "Federal Register / Vol."
- Sends each section to LLM (Claude or Groq)
- Extracts structured JSON with fields:
  - `name_and_title` (recipient)
  - `gift_description`
  - `foreign_donor`
  - `circumstances`
  - `received` (date)
  - `estimated_value`
  - `disposition`
- Saves individual JSON files to `data/processed/json/`

**Input:** `data/raw/text/*.txt`
**Output:** `data/processed/json/*.json`

### Stage 4: Data Processing

#### Step 4a: Combine JSON Files

Merge all individual JSON files into a single dataset:

```bash
python src/processors/combiner.py
```

This script:
- Reads all JSON files from `data/processed/json/`
- Deduplicates entries based on key fields
- Merges disposition arrays for duplicates
- Outputs `data/output/combined.json`

**Input:** `data/processed/json/*.json`
**Output:** `data/output/combined.json`

#### Step 4b: Extract Donor Information

Parse donor details (name, title, country):

```bash
python src/extractors/donor_extractor.py
```

This script:
- Reads `data/output/combined.json`
- Uses Claude to extract structured donor info from `foreign_donor` field
- Outputs `data/output/combined_json_with_names.json`

**Input:** `data/output/combined.json`
**Output:** `data/output/combined_json_with_names.json`

#### Step 4c: Extract Recipient Information

Parse recipient details (name, title):

```bash
python src/extractors/recipient_extractor.py
```

This script:
- Reads `data/output/combined_json_with_names.json`
- Uses Claude to extract recipient info from `name_and_title` field
- Outputs `data/output/combined_json_with_both_names.json`

**Input:** `data/output/combined_json_with_names.json`
**Output:** `data/output/combined_json_with_both_names.json`

#### Step 4d: Anonymize Agency Employees

Remove donor information for anonymous recipients:

```bash
python src/processors/anonymizer.py
```

This script:
- Identifies entries where recipient is "An Agency Employee"
- Sets donor name, title, and country to empty strings
- Maintains anonymity of recipients

**Input/Output:** `data/output/combined_json_with_both_names.json` (modified in place)

### Stage 5: Database Creation

Create SQLite database from processed JSON:

```bash
python src/database/db_manager.py
```

This script:
- Reads `data/output/combined_json_with_both_names.json`
- Creates/updates `data/output/gifts.db`
- Creates `gifts` table with proper schema
- Handles data type conversions
- Parses estimated values
- Assigns sequential IDs

**Input:** `data/output/combined_json_with_both_names.json`
**Output:** `data/output/gifts.db`

**Database Schema:**

```sql
CREATE TABLE gifts (
    id INTEGER PRIMARY KEY,
    name_and_title TEXT,
    gift_description TEXT,
    received TEXT,
    estimated_value REAL,
    disposition TEXT,
    foreign_donor TEXT,
    circumstances TEXT,
    donor_name TEXT,
    donor_title TEXT,
    donor_country TEXT,
    recipient_name TEXT,
    recipient_title TEXT
);
```

### Stage 6: Export Data

The database can be exported to various formats:

#### Export to CSV

```bash
sqlite3 data/output/gifts.db ".headers on" ".mode csv" ".output data/output/gifts.csv" "SELECT * FROM gifts;"
```

Or use Python:

```python
import sqlite_utils
db = sqlite_utils.Database("data/output/gifts.db")
with open("data/output/gifts.csv", "w") as f:
    db["gifts"].rows_where(order_by="id").write_csv(f)
```

### Stage 7: Data Analysis

#### Query Examples

Using sqlite3 command line:

```bash
# Total gifts by country
sqlite3 data/output/gifts.db "SELECT donor_country, COUNT(*) as count FROM gifts GROUP BY donor_country ORDER BY count DESC LIMIT 10;"

# Highest value gifts
sqlite3 data/output/gifts.db "SELECT recipient_name, donor_country, estimated_value, gift_description FROM gifts WHERE estimated_value IS NOT NULL ORDER BY estimated_value DESC LIMIT 10;"

# Gifts by recipient
sqlite3 data/output/gifts.db "SELECT recipient_name, COUNT(*) as count FROM gifts GROUP BY recipient_name ORDER BY count DESC;"
```

Using Python:

```python
import sqlite_utils

db = sqlite_utils.Database("data/output/gifts.db")

# Total gifts by country
for row in db.execute("SELECT donor_country, COUNT(*) as count FROM gifts GROUP BY donor_country ORDER BY count DESC LIMIT 10;"):
    print(f"{row['donor_country']}: {row['count']}")
```

## Complete Pipeline Script

To run the entire pipeline from start to finish:

```bash
#!/bin/bash
# scripts/run_extraction.sh

echo "Starting Foreign Gifts extraction pipeline..."

echo "Step 1: Processing PDFs..."
python src/extractors/pdf_processor.py

echo "Step 2: Extracting data with LLM..."
python src/extractors/data_extractor.py

echo "Step 3: Combining JSON files..."
python src/processors/combiner.py

echo "Step 4: Extracting donor information..."
python src/extractors/donor_extractor.py

echo "Step 5: Extracting recipient information..."
python src/extractors/recipient_extractor.py

echo "Step 6: Anonymizing agency employees..."
python src/processors/anonymizer.py

echo "Step 7: Creating database..."
python src/database/db_manager.py

echo "Pipeline complete! Database available at data/output/gifts.db"
```

## Best Practices

1. **Incremental Processing**: Process new data separately and merge with existing database
2. **Backup Data**: Keep backups of raw PDFs and text files
3. **Version Control**: Commit processed data periodically
4. **Cost Management**: Monitor API usage when using LLMs
5. **Quality Checks**: Manually review sample extractions for accuracy
6. **Logging**: Check `logs/gifts_tracker.log` for errors or warnings

## Troubleshooting

### LLM Extraction Errors

If extraction fails:
- Check API key configuration
- Verify API rate limits
- Review the problematic text section
- Try with a different model

### JSON Parsing Errors

If JSON is malformed:
- Use `src/utils/json_utils.py` to validate
- Check LLM output for formatting issues
- Adjust temperature parameter for more consistent output

### Database Errors

If database creation fails:
- Verify JSON structure is correct
- Check for missing required fields
- Review data type conversions in `db_manager.py`

## Next Steps

- See [API Reference](api_reference.md) for detailed function documentation
- Explore Jupyter notebooks in `notebooks/` for analysis examples
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for how to add features
