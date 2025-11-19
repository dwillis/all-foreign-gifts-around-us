# All Foreign Gifts Around Us

> Extracting structured data from Federal Register publications about gifts given to U.S. officials by foreign government officials.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Overview

The Federal Register is the official journal of the United States government, which publishes various notices, rules, and regulatory information. Among these publications are reports detailing gifts received by U.S. government officials from foreign sources. Some presidential administrations are [better than others](https://oversightdemocrats.house.gov/news/press-releases/oversight-democrats-release-evidence-showing-trump-first-family-failed-to) about reporting these gifts. The current minimum value of reportable gifts is [$480](https://www.gsa.gov/policy-regulations/policy/personal-property-policy-overview/special-programs/foreign-gifts).

This project uses Large Language Models (LLMs), specifically Claude 3 Sonnet and Claude 3 Haiku, to extract structured information from these unstructured text reports and convert it into JSON format. The data can then be used for analysis, visualization, or integration with other systems.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dwillis/all-foreign-gifts-around-us.git
cd all-foreign-gifts-around-us

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your API keys

# Run the extraction pipeline
python src/extractors/data_extractor.py
```

For detailed setup instructions, see the [Setup Guide](docs/setup.md).

## Features

- **LLM-Powered Extraction**: Uses Claude and/or Groq models to extract structured data from unstructured text
- **Comprehensive Data**: Extracts donor info (name, title, country), recipient info, gift descriptions, values, and dispositions
- **Multiple Formats**: Output to JSON, SQLite database, and CSV
- **Data Quality**: Built-in deduplication and anonymization for agency employees
- **Configurable**: YAML-based configuration for easy customization
- **Well-Documented**: Comprehensive documentation and examples

## Project Structure

```
all-foreign-gifts-around-us/
├── src/                    # Source code
│   ├── extractors/         # LLM-based data extraction
│   ├── processors/         # Data processing & transformation
│   ├── database/           # Database management
│   ├── api/               # External API clients
│   └── utils/             # Utilities (config, logging)
├── data/                   # Data directories
│   ├── raw/               # PDFs and text files
│   ├── processed/         # Extracted JSON files
│   └── output/            # Final database and exports
├── docs/                   # Documentation
│   ├── setup.md           # Setup instructions
│   ├── workflow.md        # Usage guide
│   └── images/            # Screenshots and diagrams
├── config/                 # Configuration files
│   ├── config.example.yaml
│   └── logging.yaml
├── tests/                  # Test suite
├── scripts/               # Automation scripts
└── notebooks/             # Jupyter notebooks for analysis

```

## Data Extraction Pipeline

The extraction process follows these stages:

1. **PDF Processing** (`src/extractors/pdf_processor.py`)
   - Converts Federal Register PDFs to text files
   - Handles OCR when needed

2. **Data Extraction** (`src/extractors/data_extractor.py`)
   - Splits text into sections
   - Uses LLM to extract structured JSON
   - Handles parsing errors gracefully

3. **Data Combination** (`src/processors/combiner.py`)
   - Merges individual JSON files
   - Deduplicates entries
   - Combines disposition arrays

4. **Information Enrichment**
   - `src/extractors/donor_extractor.py`: Extracts donor details (name, title, country)
   - `src/extractors/recipient_extractor.py`: Extracts recipient details (name, title)
   - `src/processors/anonymizer.py`: Anonymizes agency employees

5. **Database Creation** (`src/database/db_manager.py`)
   - Creates SQLite database
   - Handles type conversions
   - Generates CSV export

For detailed workflow information, see the [Workflow Guide](docs/workflow.md).

## Data Schema

The extracted data includes:

| Field | Type | Description |
|-------|------|-------------|
| `name_and_title` | String | Full recipient name and title |
| `recipient_name` | String | Extracted recipient name |
| `recipient_title` | String | Extracted recipient title |
| `gift_description` | String | Description of the gift |
| `received` | Date | Date gift was received |
| `estimated_value` | Float | Estimated value in USD |
| `disposition` | String | What happened to the gift (e.g., "Transferred to NARA") |
| `foreign_donor` | String | Full donor name and title |
| `donor_name` | String | Extracted donor name |
| `donor_title` | String | Extracted donor title |
| `donor_country` | String | Donor's country |
| `circumstances` | String | Circumstances of the gift |

## Usage Examples

### Query the Database

```python
import sqlite_utils

db = sqlite_utils.Database("data/output/gifts.db")

# Top 10 donor countries
for row in db.execute("""
    SELECT donor_country, COUNT(*) as count
    FROM gifts
    WHERE donor_country IS NOT NULL
    GROUP BY donor_country
    ORDER BY count DESC
    LIMIT 10
"""):
    print(f"{row['donor_country']}: {row['count']}")

# Highest value gifts
for row in db.execute("""
    SELECT recipient_name, donor_country, estimated_value, gift_description
    FROM gifts
    WHERE estimated_value IS NOT NULL
    ORDER BY estimated_value DESC
    LIMIT 5
"""):
    print(f"${row['estimated_value']:,.2f} - {row['gift_description'][:50]}")
```

### Access JSON Data

The processed data is available in JSON format:

- `data/output/combined.json` - Basic extracted data
- `data/output/combined_json_with_names.json` - With donor info
- `data/output/combined_json_with_both_names.json` - Complete data

```python
import json

with open("data/output/combined_json_with_both_names.json", "r") as f:
    gifts = json.load(f)

# Filter gifts from a specific country
irish_gifts = [g for g in gifts if g.get("donor_country") == "Ireland"]
print(f"Found {len(irish_gifts)} gifts from Ireland")
```

## Configuration

Configuration is managed through YAML files and environment variables:

1. Copy `config/config.example.yaml` to `config/config.yaml`
2. Add your API keys
3. Customize paths and parameters as needed

Alternatively, use environment variables:

```bash
export ANTHROPIC_API_KEY=your_key_here
export GROQ_API_KEY=your_key_here
```

See [Setup Guide](docs/setup.md) for details.

## Requirements

- Python 3.12+
- Anthropic API key (for Claude models) or Groq API key
- For PDF processing: `poppler-utils` (Linux) or `poppler` (macOS)

## Installation

### Standard Installation

```bash
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -r requirements.txt
```

Includes testing, linting, and code quality tools.

## Data Updates

The Federal Register publishes gift reports annually and sometimes provides updates to previous records. This project is updated periodically to incorporate new data.

To check for new data:

```bash
python src/api/federal_register.py
```

## Documentation

- [Setup Guide](docs/setup.md) - Installation and configuration
- [Workflow Guide](docs/workflow.md) - How to use the tools
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Improvement Plan](IMPROVEMENT_PLAN.md) - Roadmap and planned features

## Analysis Features

The project includes comprehensive analytical tools to extract insights from the data:

### Command-Line Interface

```bash
# Get summary statistics
python src/cli.py stats

# Search for gifts
python src/cli.py search --keyword "painting" --country "France"
python src/cli.py search --min-value 5000 --recipient "Biden"

# Show top donors and recipients
python src/cli.py top-countries --limit 20
python src/cli.py top-recipients --limit 15

# Find most valuable gifts
python src/cli.py valuable --limit 10

# Classify gifts by type
python src/cli.py categories

# Export data
python src/cli.py export --format csv --output gifts.csv

# Create visualizations
python src/cli.py visualize --type dashboard
```

### Programmatic Analysis

```python
from src.utils.analyzer import GiftsAnalyzer
from src.utils.classifier import GiftClassifier
from src.utils.visualizer import GiftsVisualizer

# Statistical analysis
analyzer = GiftsAnalyzer()
stats = analyzer.get_summary_statistics()
top_countries = analyzer.get_top_donor_countries(limit=20)
valuable_gifts = analyzer.get_most_valuable_gifts(limit=10)

# Automatic categorization
classifier = GiftClassifier()
result = classifier.classify("Gold necklace with diamonds")
# Returns: category, subcategory, confidence, materials

# Create visualizations
visualizer = GiftsVisualizer()
visualizer.create_dashboard()
visualizer.plot_top_donor_countries()
visualizer.plot_value_distribution()
```

### Interactive Analysis

Explore the data with the included Jupyter notebook:

```bash
jupyter notebook notebooks/gift_analysis.ipynb
```

The notebook includes examples of:
- Summary statistics and trends
- Top donors and recipients
- Gift categorization
- Advanced search queries
- Data enrichment
- Custom visualizations

For detailed documentation, see [Analysis Features Guide](docs/analysis_features.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- Report bugs or suggest features via [Issues](https://github.com/dwillis/all-foreign-gifts-around-us/issues)
- Improve documentation
- Add tests
- Implement new features
- Fix bugs

## Roadmap

See [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) for the complete roadmap. Completed features:

- [x] Command-line interface (CLI)
- [x] Enhanced analytics and visualizations
- [x] Multi-format export (CSV, JSON, JSONL)
- [x] Jupyter notebooks for analysis
- [x] Gift categorization system
- [x] Data enrichment tools

Upcoming features:

- [ ] Web dashboard for browsing gifts
- [ ] REST API for programmatic access
- [ ] Automated data updates via GitHub Actions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Data source: [Federal Register](https://www.federalregister.gov/)
- LLM providers: [Anthropic](https://www.anthropic.com/) and [Groq](https://groq.com/)
- Built with Python, SQLite, and open-source tools

## Related Links

- [Federal Register: Foreign Gifts and Decorations](https://www.federalregister.gov/)
- [GSA Foreign Gifts Policy](https://www.gsa.gov/policy-regulations/policy/personal-property-policy-overview/special-programs/foreign-gifts)
- [House Oversight Committee Report](https://oversightdemocrats.house.gov/news/press-releases/oversight-democrats-release-evidence-showing-trump-first-family-failed-to)

## Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This project is for educational and transparency purposes. The data is publicly available from the Federal Register.
