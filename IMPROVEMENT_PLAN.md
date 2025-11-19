# Repository Improvement Plan: All Foreign Gifts Around Us

## Executive Summary
This document outlines a comprehensive plan to reorganize the repository structure and add useful features to improve functionality, maintainability, and usability of the Foreign Gifts tracking project.

---

## Current State Analysis

### Issues Identified

1. **Organization Problems**
   - Root directory is cluttered with 30+ files of mixed types
   - No clear separation between source code, data, documentation, and outputs
   - Test files (`test.json`, `test.txt`) mixed with production files
   - Image files (`before.png`, `after.png`, `wedding.png`, etc.) lack context
   - Multiple large JSON files (2-3MB each) in root directory

2. **Dependency Management**
   - Both `requirements.txt` and `Pipfile` exist but are inconsistent
   - `requirements.txt` only lists 2 dependencies while `Pipfile` lists 6+
   - Missing `sqlite-utils` which is used in `makedb.py`

3. **Documentation Gaps**
   - No clear workflow documentation for running the extraction process
   - API key setup not documented
   - Script execution order unclear
   - No contribution guidelines
   - No examples of usage

4. **Code Quality Issues**
   - No configuration management (hardcoded paths, API keys in env vars)
   - No error logging system
   - No data validation or quality checks
   - Mixed API usage (Groq vs Anthropic/Claude)
   - No test suite

5. **Missing Features**
   - No automated data update pipeline
   - No web interface or API for querying data
   - Limited data export formats
   - No data analysis or visualization tools
   - No search capabilities

---

## Phase 1: Repository Reorganization

### Proposed Directory Structure

```
all-foreign-gifts-around-us/
├── README.md
├── LICENSE
├── CONTRIBUTING.md (new)
├── CHANGELOG.md (new)
├── .gitignore
├── requirements.txt (consolidated)
├── setup.py (new)
├── config/
│   ├── config.example.yaml (new)
│   └── logging.yaml (new)
├── src/
│   ├── __init__.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py (new - base extractor class)
│   │   ├── data_extractor.py (renamed from extract_data.py)
│   │   ├── donor_extractor.py (renamed from extract_donors.py)
│   │   ├── recipient_extractor.py (renamed from extract_recipients.py)
│   │   └── pdf_processor.py (renamed from process_pdfs.py)
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── combiner.py (renamed from combine_json.py)
│   │   ├── anonymizer.py (renamed from agency_employees.py)
│   │   └── validator.py (new)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py (renamed from makedb.py)
│   │   └── models.py (new)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py (new - API client wrapper)
│   │   └── federal_register.py (renamed from federal_register.py)
│   └── utils/
│       ├── __init__.py
│       ├── json_utils.py (renamed from json_checker.py)
│       ├── logger.py (new)
│       └── config_loader.py (new)
├── scripts/
│   ├── run_extraction.sh (new)
│   ├── update_data.sh (new)
│   └── export_data.sh (new)
├── data/
│   ├── raw/
│   │   ├── pdfs/ (moved from root)
│   │   └── text/ (moved from root)
│   ├── processed/
│   │   └── json/ (moved from root)
│   └── output/
│       ├── combined.json (moved)
│       ├── combined_json_with_names.json (moved)
│       ├── combined_json_with_both_names.json (moved)
│       ├── gifts.csv (moved)
│       └── gifts.db (moved)
├── tests/
│   ├── __init__.py
│   ├── test_extractors.py (new)
│   ├── test_processors.py (new)
│   ├── test_database.py (new)
│   └── fixtures/
│       ├── sample_text.txt (new)
│       └── expected_output.json (new)
├── docs/
│   ├── images/ (for before.png, after.png, etc.)
│   ├── setup.md (new)
│   ├── workflow.md (new)
│   ├── api_reference.md (new)
│   └── ire24.md (moved)
├── notebooks/ (new)
│   └── data_analysis.ipynb (new)
└── web/ (new - future web interface)
    ├── app.py
    ├── templates/
    └── static/
```

### File Migrations

- Move all `.py` files to appropriate `src/` subdirectories
- Move `pdfs/` and `text/` to `data/raw/`
- Move `json/` to `data/processed/`
- Move all output files to `data/output/`
- Move image files to `docs/images/`
- Remove or archive test files

---

## Phase 2: Configuration Management

### Implement Config System

1. **Create `config/config.example.yaml`**
   ```yaml
   api:
     anthropic_key: "your-api-key-here"
     groq_key: "your-groq-key-here"
     model: "claude-3-sonnet-20240229"

   paths:
     raw_data: "data/raw"
     processed_data: "data/processed"
     output_data: "data/output"

   extraction:
     batch_size: 10
     temperature: 1.0
     max_tokens: 1024

   database:
     name: "gifts.db"
     path: "data/output"
   ```

2. **Create config loader utility**
   - Support environment variables
   - Support YAML config files
   - Provide sensible defaults

3. **Update all scripts to use centralized config**

---

## Phase 3: Documentation Improvements

### New Documentation Files

1. **CONTRIBUTING.md**
   - Code style guidelines
   - How to submit issues/PRs
   - Development setup instructions

2. **Setup Guide (`docs/setup.md`)**
   - Prerequisites
   - Installation steps
   - API key configuration
   - Virtual environment setup

3. **Workflow Guide (`docs/workflow.md`)**
   - Step-by-step extraction process
   - Script execution order
   - Troubleshooting common issues

4. **API Reference (`docs/api_reference.md`)**
   - Function documentation
   - Class references
   - Usage examples

5. **Enhanced README.md**
   - Quick start guide
   - Project structure overview
   - Links to detailed documentation
   - Usage examples with code snippets

---

## Phase 4: Code Quality Improvements

### Refactoring Tasks

1. **Create Base Classes**
   - Abstract base extractor class
   - Common error handling
   - Shared utility functions

2. **Add Logging System**
   - Structured logging with levels
   - Log to file and console
   - Rotation and archival

3. **Implement Error Handling**
   - Graceful degradation
   - Retry logic for API calls
   - Detailed error messages

4. **Add Data Validation**
   - JSON schema validation
   - Data quality checks
   - Duplicate detection improvements

5. **Create CLI Interface**
   - Use `click` or `argparse`
   - Single entry point for all operations
   - Progress bars for long operations

### Testing Infrastructure

1. **Unit Tests**
   - Test extractors with sample data
   - Test data processors
   - Test database operations

2. **Integration Tests**
   - End-to-end extraction workflow
   - Database creation and queries

3. **Test Fixtures**
   - Sample Federal Register text
   - Expected JSON outputs
   - Mock API responses

---

## Phase 5: New Features

### Priority 1: Essential Features

1. **Automated Data Pipeline**
   - Script to check Federal Register for new publications
   - Automatic download of new PDFs
   - Scheduled extraction runs
   - Notification on completion/errors

2. **Data Quality Dashboard**
   - Statistics on extraction quality
   - Missing data reports
   - Duplicate detection
   - Value validation (e.g., date formats, currency)

3. **Enhanced Export Formats**
   - Excel export with formatting
   - Markdown table export
   - HTML table export
   - XML export for data exchange

4. **Command-Line Interface**
   ```bash
   gifts-tracker extract --input text/file.txt --output json/
   gifts-tracker combine --input json/ --output combined.json
   gifts-tracker export --format csv --output gifts.csv
   gifts-tracker search --recipient "Biden" --country "Ireland"
   ```

### Priority 2: Analysis Features

5. **Data Analysis Tools**
   - Gift value statistics by country
   - Recipient analysis (who receives most gifts)
   - Temporal analysis (gifts over time)
   - Donor country ranking
   - Gift type categorization

6. **Jupyter Notebooks**
   - Exploratory data analysis
   - Visualization examples (charts, graphs)
   - Sample queries and analysis

7. **Search and Query System**
   - Full-text search across gifts
   - Filter by recipient, donor, country, value range
   - Date range queries
   - Export search results

### Priority 3: Web Interface

8. **REST API**
   - Flask/FastAPI-based API
   - Endpoints for searching, filtering
   - JSON response format
   - Rate limiting
   - API documentation (Swagger/OpenAPI)

9. **Web Dashboard**
   - Browse gifts by recipient/donor
   - Interactive visualizations
   - Search interface
   - Export capabilities
   - Responsive design

10. **Public Dataset Publishing**
    - Automated GitHub Pages deployment
    - JSON files with proper CORS
    - CSV downloads
    - API documentation page
    - Last updated timestamp

### Priority 4: Advanced Features

11. **Deduplication Improvements**
    - Fuzzy matching for similar entries
    - Machine learning for duplicate detection
    - Manual review interface for ambiguous cases

12. **Entity Recognition Enhancements**
    - Better country extraction
    - Title normalization
    - Name disambiguation
    - Organization recognition

13. **Data Versioning**
    - Track changes over time
    - Version control for datasets
    - Changelog generation
    - Rollback capabilities

14. **Monitoring and Alerting**
    - Track Federal Register for new publications
    - Email/Slack notifications
    - Error monitoring
    - Usage statistics

---

## Phase 6: Deployment and CI/CD

### Continuous Integration

1. **GitHub Actions Workflows**
   - Run tests on every PR
   - Lint code (flake8, black)
   - Type checking (mypy)
   - Security scanning (bandit)

2. **Automated Data Updates**
   - Scheduled workflow to check for new data
   - Automatic PR creation with new data
   - Validation before merge

3. **Documentation Generation**
   - Auto-generate API docs with Sphinx
   - Deploy to GitHub Pages
   - Keep docs in sync with code

### Deployment Options

1. **Docker Support**
   - Dockerfile for reproducible builds
   - Docker Compose for full stack
   - Pre-built images on Docker Hub

2. **Package Distribution**
   - Publish to PyPI
   - Versioned releases
   - Changelog automation

---

## Implementation Timeline

### Week 1-2: Reorganization
- Implement new directory structure
- Migrate files
- Update imports and paths
- Create configuration system

### Week 3-4: Documentation & Testing
- Write comprehensive documentation
- Create test suite
- Add logging system
- Refactor code for maintainability

### Week 5-6: CLI & Exports
- Create CLI interface
- Implement export formats
- Add data validation
- Create automation scripts

### Week 7-8: Analysis Tools
- Build analysis functions
- Create Jupyter notebooks
- Implement search system
- Add data quality dashboard

### Week 9-10: Web Interface
- Build REST API
- Create web dashboard
- Deploy to hosting platform
- Set up CI/CD

---

## Success Metrics

1. **Code Quality**
   - 80%+ test coverage
   - All linting checks pass
   - Type hints throughout
   - Zero critical security issues

2. **Documentation**
   - Every module documented
   - Clear setup instructions
   - Workflow examples
   - API reference complete

3. **Functionality**
   - One-command data updates
   - Sub-second search queries
   - Multiple export formats
   - Web interface available

4. **Usability**
   - Easy installation (pip install)
   - Clear error messages
   - Progress indicators
   - Comprehensive examples

---

## Dependencies to Add

```
# Core
anthropic>=0.25.0
groq>=0.4.0
requests>=2.31.0
pdftotext>=2.2.0

# Database
sqlite-utils>=3.35
pandas>=2.0.0

# CLI
click>=8.1.0
rich>=13.0.0  # for beautiful CLI output

# Configuration
pyyaml>=6.0
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Web (optional)
flask>=3.0.0
flask-cors>=4.0.0
fastapi>=0.104.0
uvicorn>=0.24.0

# Analysis
jupyter>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Code Quality
black>=23.0.0
flake8>=6.1.0
mypy>=1.5.0
bandit>=1.7.5

# Documentation
sphinx>=7.2.0
sphinx-rtd-theme>=1.3.0
```

---

## Risk Mitigation

1. **Data Loss Prevention**
   - Backup all data before reorganization
   - Use git branches for major changes
   - Keep original files until verified

2. **API Cost Management**
   - Track API usage
   - Implement caching
   - Use cheaper models where appropriate
   - Set usage limits

3. **Backwards Compatibility**
   - Maintain old script names as CLI commands
   - Provide migration guide
   - Keep legacy formats available

---

## Next Steps

1. Review and approve this plan
2. Create backup branch of current state
3. Begin Phase 1 implementation
4. Set up project board for tracking
5. Create GitHub issues for each major task

---

## Questions for Discussion

1. Should we maintain both Groq and Anthropic support, or standardize on one?
2. What hosting platform for the web interface? (Heroku, Railway, Vercel, etc.)
3. Should the database be SQLite or migrate to PostgreSQL for better query performance?
4. Preferred license for the reorganized code? (Currently no clear license info)
5. Should we implement GraphQL in addition to REST API?
6. Priority order for features - any changes to the proposed order?
