# Setup Guide

This guide will help you set up the Foreign Gifts Tracker project on your local machine.

## Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- Git
- API keys for either Anthropic or Groq (or both)

### Linux-specific Prerequisites

For PDF text extraction on Linux systems:

```bash
sudo apt-get install build-essential libpoppler-cpp-dev pkg-config python3-dev
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/dwillis/all-foreign-gifts-around-us.git
cd all-foreign-gifts-around-us
```

### 2. Create Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

For development (includes testing and code quality tools):

```bash
pip install -r requirements.txt
```

Alternatively, if using pipenv:

```bash
pipenv install
pipenv shell
```

### 4. Configure API Keys

You have two options for configuring your API keys:

#### Option A: Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here
```

#### Option B: Configuration File

Copy the example configuration file and edit it:

```bash
cp config/config.example.yaml config/config.yaml
```

Then edit `config/config.yaml` and add your API keys:

```yaml
api:
  anthropic_key: "your-anthropic-api-key-here"
  groq_key: "your-groq-api-key-here"
```

### 5. Verify Installation

Test that everything is installed correctly:

```bash
python -c "import anthropic, groq, sqlite_utils; print('All dependencies installed successfully!')"
```

## Project Structure

After setup, your project structure should look like this:

```
all-foreign-gifts-around-us/
├── config/
│   ├── config.yaml (your config)
│   ├── config.example.yaml
│   └── logging.yaml
├── data/
│   ├── raw/
│   │   ├── pdfs/
│   │   └── text/
│   ├── processed/
│   │   └── json/
│   └── output/
├── src/
│   ├── extractors/
│   ├── processors/
│   ├── database/
│   ├── api/
│   └── utils/
├── docs/
├── tests/
├── logs/ (created automatically)
└── README.md
```

## Obtaining API Keys

### Anthropic (Claude) API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key (you won't be able to see it again)

### Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Generate a new API key
5. Copy the key

## Next Steps

Once setup is complete, proceed to the [Workflow Guide](workflow.md) to learn how to use the tools.

## Troubleshooting

### pdftotext Installation Issues

If you encounter issues installing `pdftotext`:

**On Ubuntu/Debian:**
```bash
sudo apt-get install build-essential libpoppler-cpp-dev pkg-config python3-dev
pip install pdftotext
```

**On macOS:**
```bash
brew install pkg-config poppler
pip install pdftotext
```

### Permission Errors

If you get permission errors when creating directories:

```bash
chmod -R 755 data/ logs/
```

### Import Errors

If you get import errors, make sure you're in the virtual environment:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### API Key Not Found

If the scripts can't find your API keys:

1. Verify the `.env` file is in the project root
2. Or verify `config/config.yaml` exists and contains your keys
3. Ensure you've activated your virtual environment
4. Try setting the environment variable manually:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```

## Getting Help

If you encounter issues not covered here:

1. Check existing [GitHub Issues](https://github.com/dwillis/all-foreign-gifts-around-us/issues)
2. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error message
   - Steps to reproduce
