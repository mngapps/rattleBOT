# Rattle API

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/mngapps/rattle_api/actions/workflows/ci.yml/badge.svg)](https://github.com/mngapps/rattle_api/actions/workflows/ci.yml)

AI-agnostic rental data toolkit for the [Rattle](https://www.rattleapp.de) platform. Manage rental product catalogues, generate descriptions, classify items, and transform interchange data — all from the command line with your choice of AI backend.

---

## Features

- **AI-agnostic** — swap between OpenAI, Anthropic, Ollama (local), or any custom HTTP endpoint with a single environment variable.
- **CLI-first** — designed for automation, scripting, and use with coding agents (Claude Code, Codex, Aider, Cursor, …).
- **Data interchange** — transform between Datanorm, eCl@ss, BMEcat, and Rattle formats.
- **Product enrichment** — generate marketing descriptions and category tags via AI.
- **Rental data analysis** — ask open-ended questions about your catalogue.
- **Image processing** — extract images from PDF/DOCX price lists and generate option-group variants.

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/mngapps/rattle_api.git
cd rattle_api

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install with your preferred AI provider
pip install -e ".[openai]"      # OpenAI / Azure / vLLM / LM Studio
pip install -e ".[anthropic]"   # Anthropic Claude
pip install -e ".[all-ai]"      # Both providers
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys and provider choice
```

| Variable | Description |
|---|---|
| `RATTLE_API_KEY_<TENANT>` | Rattle API key — one per tenant (e.g. `RATTLE_API_KEY_PRESSTA`) |
| `AI_PROVIDER` | `openai` (default), `anthropic`, `ollama`, or `custom` |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434`) |

See [`.env.example`](.env.example) for the full list of configuration options.

### 3. Run

```bash
# Verify connectivity
python main.py pressta test-connection

# Generate product descriptions
python main.py pressta ai-describe --limit 5 --language de

# Classify products
python main.py pressta ai-classify --limit 10

# Transform interchange data
python main.py pressta ai-transform datanorm rattle data.json --push

# Analyse rental data
python main.py pressta ai-analyse --question "Which products lack descriptions?"

# List available AI providers
python main.py pressta ai-providers
```

## Architecture

```
rattle_api/
├── main.py            # CLI entry point (argparse)
├── config.py          # Environment & tenant configuration
├── client.py          # Rattle API HTTP client
├── ai_provider.py     # AI provider abstraction layer
├── ai_tasks.py        # AI-powered task implementations
├── source_reader.py   # Data source file reader (Excel, …)
├── image_utils.py     # Image processing utilities
├── pyproject.toml     # Project metadata & dependencies
└── source/            # Local data files (per-tenant, gitignored)
```

### AI Provider Layer

The provider abstraction (`ai_provider.py`) implements a simple interface:

```python
from ai_provider import get_provider

provider = get_provider()  # Uses AI_PROVIDER env var
result = provider.complete("Summarise this rental data: ...")
data = provider.complete_json("Return JSON: ...")
```

Supported backends:

| Provider | Env var | Notes |
|---|---|---|
| OpenAI | `AI_PROVIDER=openai` | Also works with Azure, vLLM, LM Studio via `OPENAI_BASE_URL` |
| Anthropic | `AI_PROVIDER=anthropic` | Claude models |
| Ollama | `AI_PROVIDER=ollama` | Local inference, no API key needed |
| Custom | `AI_PROVIDER=custom` | Any OpenAI-compatible REST endpoint |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linter
make lint

# Run tests
make test

# Run all checks
make check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## Security

For reporting vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
