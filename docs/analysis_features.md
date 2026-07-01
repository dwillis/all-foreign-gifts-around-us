# Data Analysis Features

This document describes the comprehensive analytical capabilities available in the Foreign Gifts Tracker.

## Overview

The project includes powerful tools to extract meaning and insights from the foreign gifts data:

1. **Statistical Analysis** - Comprehensive statistics and insights
2. **Gift Classification** - Automatic categorization by type
3. **Data Enrichment** - Add country metadata and temporal info
4. **Visualizations** - Charts, graphs, and dashboards
5. **Command-Line Interface** - Easy access to all features
6. **Interactive Analysis** - Jupyter notebooks

---

## 1. Statistical Analysis (`src/utils/analyzer.py`)

The `GiftsAnalyzer` class provides comprehensive statistical analysis capabilities.

### Features

#### Summary Statistics
```python
from foreign_gifts.analysis.analyzer import GiftsAnalyzer

analyzer = GiftsAnalyzer("data/gifts.db")
stats = analyzer.get_summary_statistics()

# Returns:
# - total_gifts: Total number of gifts
# - gifts_with_value: Count with monetary values
# - average_value: Mean gift value
# - min/max_value: Value range
# - unique_countries: Number of donor countries
# - unique_recipients: Number of recipients
```

#### Top Donor Countries
```python
top_countries = analyzer.get_top_donor_countries(limit=20)
# Returns list with gift_count, total_value, avg_value per country
```

#### Top Recipients
```python
top_recipients = analyzer.get_top_recipients(limit=20)
# Returns recipients ranked by number of gifts received
```

#### Most Valuable Gifts
```python
valuable = analyzer.get_most_valuable_gifts(limit=10)
# Returns the most expensive gifts with full details
```

#### Temporal Analysis
```python
by_year = analyzer.get_gifts_by_year()
# Returns gift statistics grouped by year
```

#### Gift Categories
```python
categories = analyzer.get_gift_categories()
# Automatically categorizes gifts by type:
# - jewelry, art, clothing, books, decorative, etc.
```

#### Advanced Search
```python
results = analyzer.search_gifts(
    keyword="painting",
    country="France",
    recipient="Biden",
    min_value=1000,
    max_value=10000,
    year="2022"
)
```

#### Disposition Analysis
```python
disposition = analyzer.get_disposition_analysis()
# Shows what happened to gifts (transferred to NARA, etc.)
```

#### Generate Reports
```python
report = analyzer.generate_report("data/analysis_report.txt")
# Creates comprehensive text report with all statistics
```

---

## 2. Gift Classification (`src/utils/classifier.py`)

The `GiftClassifier` uses keyword matching and pattern recognition to categorize gifts.

### Supported Categories

- **Jewelry & Accessories** - rings, necklaces, bracelets, earrings
- **Art & Sculpture** - paintings, sculptures, prints
- **Clothing & Textiles** - dresses, suits, robes, traditional garments
- **Books & Publications** - books, albums, manuscripts
- **Decorative Items** - vases, bowls, plates, frames
- **Watches & Timepieces** - watches, clocks
- **Medals & Coins** - medals, medallions, coins
- **Weapons & Military** - swords, daggers
- **Musical Instruments** - guitars, drums, flutes
- **Sporting Goods** - balls, jerseys, equipment
- **Food & Beverages** - wine, champagne, chocolates
- **Rugs & Textiles** - rugs, carpets, tapestries
- **Electronics** - tablets, phones, cameras
- **Furniture** - chairs, tables, desks
- **Religious Items** - bibles, rosaries, icons
- **Diplomatic & Ceremonial** - flags, seals, emblems

### Usage

```python
from foreign_gifts.analysis.classifier import GiftClassifier

classifier = GiftClassifier()

# Classify a gift
result = classifier.classify("Gold necklace with diamond pendant")

# Returns:
# - category: Category ID (e.g., "jewelry")
# - category_name: Full name (e.g., "Jewelry & Accessories")
# - subcategory: More specific classification
# - confidence: 0.0 to 1.0
# - matched_keywords: Keywords that triggered the match

# Extract materials
materials = classifier.extract_materials("Silver sword with gold scabbard")
# Returns: ["silver", "gold"]

# Categorize by value
value_cat = classifier.get_value_category(7500.00)
# Returns: "highly_valuable ($5,000-$10,000)"

# Check if ceremonial
is_ceremonial = classifier.is_ceremonial("Traditional ceremonial robe")
# Returns: True
```

---

## 3. Data Enrichment (`src/utils/enrichment.py`)

The `DataEnricher` adds metadata and derived fields to gift records.

### Features

#### Country Metadata
Enriches gifts with:
- `donor_region`: Geographic region (e.g., "Western Europe")
- `donor_continent`: Continent
- `donor_country_code`: ISO country code

#### Value Analysis
Adds:
- `value_category`: token, modest, moderate, valuable, highly_valuable, extremely_valuable
- `value_tier`: 1-5 rating

#### Temporal Information
Extracts from date:
- `received_year`, `received_month`, `received_quarter`
- `received_month_name`, `received_day_of_week`

#### Description Analysis
Detects:
- `is_set`: Gift is a set/collection
- `is_personalized`: Engraved or monogrammed
- `is_handmade`: Artisan or hand-crafted
- `is_historical`: Antique or historical
- `description_word_count`: Complexity metric
- `quantity_mentioned`: Number of items

#### High-Profile Detection
- `is_high_profile`: Based on value, recipient, and other factors

### Usage

```python
from foreign_gifts.analysis.enrichment import DataEnricher

enricher = DataEnricher()

# Enrich a single gift
gift = {
    "donor_country": "Japan",
    "estimated_value": 7500.00,
    "received": "2022-03-15",
    "gift_description": "Handmade set of 6 ceramic bowls",
    "recipient_title": "President of the United States"
}

enriched = enricher.enrich_gift(gift)
# Returns original fields plus 15+ enriched fields

# Regional statistics
gifts_list = [...]  # List of enriched gifts
regional_stats = enricher.get_regional_statistics(gifts_list)
# Returns statistics grouped by world region
```

---

## 4. Visualizations (`src/utils/visualizer.py`)

The `GiftsVisualizer` creates professional charts and graphs.

### Available Visualizations

#### Top Donor Countries
```python
from foreign_gifts.analysis.visualizer import GiftsVisualizer

viz = GiftsVisualizer("data/gifts.db")
viz.plot_top_donor_countries(limit=15)
# Creates horizontal bar chart
```

#### Value Distribution
```python
viz.plot_value_distribution()
# Creates histogram and box plot of gift values
```

#### Timeline
```python
viz.plot_gifts_over_time()
# Creates line chart showing gifts received per year
```

#### Regional Distribution
```python
viz.plot_regional_distribution()
# Creates pie chart of gifts by world region
```

#### Recipient Analysis
```python
viz.plot_recipient_analysis(limit=10)
# Creates dual bar charts: by count and by total value
```

#### Comprehensive Dashboard
```python
viz.create_dashboard()
# Creates multi-panel dashboard with all key visualizations
```

All visualizations are saved to `data/visualizations/` as high-resolution PNG files.

---

## 5. Command-Line Interface (`src/foreign_gifts/cli.py`)

Access all analysis features from the command line.

### Commands

#### Get Summary Statistics
```bash
uv run gifts stats
```

#### Generate Full Report
```bash
uv run gifts analyze --output report.txt
```

#### Search for Gifts
```bash
uv run gifts search --keyword "painting" --country "France"
uv run gifts search --min-value 5000 --max-value 10000
uv run gifts search --recipient "Biden" --year "2022"
```

#### Top Donor Countries
```bash
uv run gifts top-countries --limit 20
```

#### Top Recipients
```bash
uv run gifts top-recipients --limit 15
```

#### Most Valuable Gifts
```bash
uv run gifts valuable --limit 10
```

#### Gift Categories
```bash
uv run gifts categories
```

#### Classify a Description
```bash
uv run gifts classify "Gold necklace with diamonds"
```

#### Export Data
```bash
uv run gifts export --format csv --output gifts.csv
uv run gifts export --format json --output gifts.json
uv run gifts export --format jsonl --output gifts.jsonl
```

#### Create Visualizations
```bash
uv run gifts visualize --type dashboard
uv run gifts visualize --type countries
uv run gifts visualize --type values
uv run gifts visualize --type timeline
uv run gifts visualize --type recipients
uv run gifts visualize --type all
```

---

## 6. Jupyter Notebook (`notebooks/gift_analysis.ipynb`)

Interactive analysis notebook with examples of:

- Loading and exploring data
- Summary statistics
- Top countries and recipients
- Value analysis
- Gift categorization
- Advanced searches
- Data enrichment
- Creating visualizations
- Custom SQL queries
- Regional comparisons

### Running the Notebook

```bash
jupyter notebook notebooks/gift_analysis.ipynb
```

The notebook includes 12 sections with complete working examples.

---

## Use Cases

### Research Questions You Can Answer

1. **Diplomatic Patterns**
   - Which countries give the most gifts?
   - Are there regional patterns?
   - How has gift-giving changed over time?

2. **Gift Characteristics**
   - What types of gifts are most common?
   - What's the typical value range?
   - Which materials are preferred?

3. **Recipient Analysis**
   - Who receives the most gifts?
   - Do certain positions receive more valuable gifts?
   - Are there patterns in who receives what?

4. **Economic Insights**
   - What's the total value of gifts received?
   - Which countries give the most expensive gifts?
   - How do gift values compare across regions?

5. **Cultural Analysis**
   - What types of gifts do different cultures give?
   - Are certain gift types associated with regions?
   - How do traditional vs. modern gifts compare?

### Example Workflows

#### Investigating a Specific Country
```python
analyzer = GiftsAnalyzer()

# Get all gifts from the country
gifts = analyzer.search_gifts(country="Saudi Arabia")

# Classify them
classifier = GiftClassifier()
categories = [classifier.classify(g['gift_description']) for g in gifts]

# Calculate statistics
total_value = sum(g['estimated_value'] for g in gifts if g['estimated_value'])
avg_value = total_value / len(gifts)

# Identify patterns
common_types = Counter(c['category'] for c in categories)
```

#### Comparing Time Periods
```python
# Get gifts from two years
gifts_2020 = analyzer.search_gifts(year="2020")
gifts_2022 = analyzer.search_gifts(year="2022")

# Compare counts, values, categories, etc.
```

#### Finding Anomalies
```python
# Find unusually expensive gifts
expensive = analyzer.get_most_valuable_gifts(limit=50)

# Find rare gift types
all_categories = analyzer.get_gift_categories()
rare_types = {k: v for k, v in all_categories.items() if v < 5}
```

---

## Performance Considerations

- Database queries are optimized with indexes
- Large result sets can be paginated with `LIMIT` and `OFFSET`
- Visualizations use efficient plotting libraries
- Enrichment can be batched for better performance

## Extensibility

All modules are designed to be extended:

- Add new gift categories in `classifier.py`
- Add custom enrichment fields in `enrichment.py`
- Create new visualizations in `visualizer.py`
- Add CLI commands in `cli.py`
- Build custom analyses in Jupyter notebooks

---

## Examples

See `notebooks/gift_analysis.ipynb` for comprehensive examples of all features.

For questions or feature requests, please open an issue on GitHub.
