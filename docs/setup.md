# Setup Guide

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

## Installation

```bash
git clone https://github.com/dwillis/all-foreign-gifts-around-us.git
cd all-foreign-gifts-around-us
uv sync
```

This installs the `foreign_gifts` package and the `gifts` command into a project-local virtual environment. `uv sync --group dev` additionally installs Jupyter, matplotlib, seaborn, and pytest.

Verify it worked:

```bash
uv run gifts --help
```

Nothing else is required to explore the data already committed in `data/gifts.db`.

## Configuring a model (only needed to rebuild the dataset)

Every LLM call in the extraction pipeline goes through the [`llm`](https://llm.datasette.io/) library, so you can use Anthropic, a local Ollama model, or anything else `llm` supports.

### Anthropic (default)

```bash
uv run llm keys set anthropic
# paste your key from https://console.anthropic.com/
```

### Ollama (local, no API key)

```bash
brew install ollama       # or see https://ollama.com/download
ollama pull llama3.2
uv run gifts pipeline extract data/raw/pdfs --model llama3.2
```

Run `uv run llm models` to see every model `llm` currently knows about. Set the `GIFTS_MODEL` environment variable to change the default without passing `--model` on every command.

## Next Steps

See the [Workflow Guide](workflow.md) to run the extraction pipeline, or the [Analysis Features Guide](analysis_features.md) to explore data already in the repo.

## Troubleshooting

### `natural-pdf` OCR or PDF rendering issues

`natural-pdf[all]` pulls in its own PDF/OCR dependencies via `uv sync` — no system Poppler install needed.

### Model not found

Run `uv run llm models` to confirm the model ID you passed to `--model` is installed/available (for Ollama, run `ollama list` too).

### API key not found

```bash
uv run llm keys set anthropic
```

or set `ANTHROPIC_API_KEY` in your shell.
