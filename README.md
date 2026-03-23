<p align="center">
  <img src="rattle_logos/rattle_long_black_transparent.png" width="320" alt="Rattle">
  <br>
  <strong>Rattle AI Workspace</strong><br>
  <em>AI-agnostic rental data toolkit for the Rattle API</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
  <a href="https://github.com/mngapps/rattle_api/actions/workflows/ci.yml"><img src="https://github.com/mngapps/rattle_api/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/mngapps/rattle_api/blob/main/CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-Keep%20a%20Changelog-orange.svg" alt="Changelog"></a>
</p>

<p align="center">
  Manage rental product catalogues, enrich data with AI, and transform industry<br>
  interchange formats — all from the command line, with <strong>your choice of AI backend</strong>.
</p>

---

## Why Rattle AI Workspace?

- **Swap AI providers in seconds** — OpenAI, Anthropic, Ollama (local), or any custom endpoint. One env var, zero code changes.
- **Built for automation** — pure CLI with JSON output, no interactive prompts. Works out of the box with Claude Code, Codex, Aider, Cursor, and any tool that can run shell commands.
- **Industry data formats** — transform between Datanorm, eCl@ss, BMEcat, and Rattle with a single command.
- **Local-first option** — run completely offline with Ollama. No API keys, no costs, full privacy.

## Table of Contents

- [Quick Start](#quick-start)
- [Commands](#commands)
- [AI Providers](#ai-providers)
- [Using with CLI Agents](#using-with-cli-agents)
- [Architecture](#architecture)
- [Docker](#docker)
- [Development](#development)
- [Contributing](#contributing)

## Quick Start

### 1. Install

```bash
git clone https://github.com/mngapps/rattle_api.git
cd rattle_api
python -m venv .venv && source .venv/bin/activate
```

Pick your AI provider:

```bash
pip install -e ".[openai]"       # OpenAI / Azure / vLLM / LM Studio
pip install -e ".[anthropic]"    # Anthropic Claude
pip install -e ".[all-ai]"       # All providers
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — add your Rattle API key and AI provider credentials
```

### 3. Verify

```bash
$ python main.py pressta test-connection
Connection OK for tenant 'pressta'
```

### 4. Use

```bash
# Generate product descriptions
$ python main.py pressta ai-describe --limit 3 --language de
[{"id": "p-001", "description": "Professionelle Industriebohrmaschine …"}, …]

# Classify products into categories
$ python main.py pressta ai-classify --limit 5

# Transform interchange data and push to Rattle
$ python main.py pressta ai-transform datanorm rattle import.json --push

# Ask questions about your catalogue
$ python main.py pressta ai-analyse --question "Which products lack descriptions?"
```

## Commands

| Command | Description | Key Options |
|---|---|---|
| `test-connection` | Verify API connectivity | |
| `list-sources` | List local data files | |
| `ai-describe` | Generate marketing descriptions | `--limit`, `--language` |
| `ai-classify` | Classify products into categories | `--limit` |
| `ai-transform` | Convert between data formats | `source_format`, `target_format`, `--push` |
| `ai-analyse` | Run data quality audits & analysis | `--question` |
| `ai-providers` | Show available AI backends | |

Every command outputs JSON to stdout — pipe it, parse it, chain it.

## AI Providers

Switch providers with a single environment variable:

```bash
AI_PROVIDER=openai     python main.py pressta ai-describe  # default
AI_PROVIDER=anthropic  python main.py pressta ai-describe
AI_PROVIDER=ollama     python main.py pressta ai-describe  # local, free
AI_PROVIDER=custom     python main.py pressta ai-describe  # your endpoint
```

| Provider | Backend | Env Vars |
|---|---|---|
| `openai` | OpenAI, Azure, vLLM, LM Studio | `OPENAI_API_KEY`, `OPENAI_BASE_URL`*, `OPENAI_MODEL`* |
| `anthropic` | Anthropic Claude | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`* |
| `ollama` | Local Ollama server | `OLLAMA_BASE_URL`*, `OLLAMA_MODEL`* |
| `custom` | Any OpenAI-compatible REST API | `CUSTOM_AI_BASE_URL`, `CUSTOM_AI_API_KEY`*, `CUSTOM_AI_MODEL`* |

<sub>* optional</sub>

See [`.env.example`](.env.example) for all configuration options.

## Using with CLI Agents

Rattle AI Workspace is designed to be driven by any CLI coding agent:

```bash
# Claude Code
python main.py pressta ai-analyse --question "Summarise product categories"

# Codex CLI
python main.py pressta ai-describe --limit 10

# Any agent — just run shell commands and parse JSON stdout
python main.py pressta ai-transform datanorm rattle data.json --push
```

No interactive prompts, no TUI, no special SDKs — just `stdin`/`stdout`/`stderr` and JSON.

## Architecture

```
rattle_api/
├── main.py            CLI entry point (argparse dispatch)
├── config.py          Tenant & provider configuration via .env
├── client.py          Rattle API HTTP client (REST + pagination)
├── ai_provider.py     Provider abstraction layer
├── ai_tasks.py        AI task implementations
├── source_reader.py   Data file reader (Excel, JSON)
├── image_utils.py     Image processing & shadow generation
└── tests/             Test suite
```

```
         ┌───────────────────┐
         │  CLI / AI Agent   │
         └────────┬──────────┘
                  │
         ┌────────▼──────────┐
         │    ai_tasks.py     │  describe · classify · transform · analyse
         └────────┬──────────┘
                  │
         ┌────────▼──────────┐
         │  ai_provider.py    │  complete() · complete_json()
         └────────┬──────────┘
                  │
    ┌─────┬───────┼───────┬─────────┐
    │     │       │       │         │
 OpenAI  Anthropic  Ollama  Custom HTTP
```

### Adding a new provider

1. Subclass `AIProvider` in `ai_provider.py`
2. Implement `complete()`
3. Register in the `PROVIDERS` dict
4. Document env vars in `config.py` and `.env.example`

## Docker

```bash
docker build -t rattle-api .
docker run --env-file .env rattle-api pressta test-connection
docker run --env-file .env rattle-api pressta ai-describe --limit 3
```

## Development

```bash
# Install everything
pip install -e ".[dev,all-ai]"

# Run checks
make lint          # Ruff linter + formatter check
make test          # pytest
make check         # All of the above

# Auto-format
make format

# Pre-commit hooks (optional but recommended)
pre-commit install
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE)
