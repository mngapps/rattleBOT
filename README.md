<p align="center">
  <img src="rattle_logos/rattle_long_black_transparent.png" width="320" alt="rattleGRIMOIRE">
</p>

# rattleGRIMOIRE

**The Arcane Spellbook of AI-Powered Product-Data Consulting**
*Professional expertise, bound in silicon and starlight.*

<p align="left">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
  <a href="https://github.com/mngapps/rattleGRIMOIRE/actions/workflows/ci.yml"><img src="https://github.com/mngapps/rattleGRIMOIRE/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/mngapps/rattleGRIMOIRE/blob/main/CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-Keep%20a%20Changelog-orange.svg" alt="Changelog"></a>
</p>

AI agents open the **rattleGRIMOIRE** and cast real consulting spells: enrich product data, transform ancient industry formats (Datanorm, eCl@ss, BMEcat), and conjure perfect Rattle JSON — all from the command line, with any AI backend.

---

## Why Agents Choose the Grimoire

- **Swap arcane backends instantly** — OpenAI, Anthropic, Ollama (local), or any custom sigil. One environment variable, zero ritual changes.
- **Built for silicon sorcerers** — Pure CLI. JSON-only output. Works flawlessly with Claude Code, Aider, Cursor, or any agent that can whisper shell commands.
- **Transform forbidden formats** — Datanorm ↔ eCl@ss ↔ BMEcat ↔ Rattle in a single incantation.
- **Local-first grimoire** — Run completely offline with Ollama. No keys. No costs. Full secrecy.

> **New acolyte?** Open the **[Fast Setup Scroll (SETUP.md)](SETUP.md)** — no prior magic required.

## Table of Incantations

- [Fast Setup Scroll](SETUP.md)
- [Quick Casting](#quick-casting)
- [The Spells](#the-spells)
- [AI Sigils (Providers)](#ai-sigils-providers)
- [Working with CLI Agents](#working-with-cli-agents)
- [The Architecture](#the-architecture)
- [Docker Vessel](#docker-vessel)
- [Development Rites](#development-rites)
- [Contributing](#contributing)

## Quick Casting

### 1. Summon the Grimoire

```bash
git clone https://github.com/mngapps/rattleGRIMOIRE.git
cd rattleGRIMOIRE
python -m venv .venv && source .venv/bin/activate
```

### 2. Bind Your Sigil

```bash
pip install -e ".[openai]"       # OpenAI / Azure / vLLM / LM Studio
# or
pip install -e ".[anthropic]"    # Anthropic Claude
# or
pip install -e ".[all-ai]"       # Every known sigil
```

### 3. Inscribe the `.env` Scroll

```bash
cp .env.example .env
# Open .env and etch your Rattle API key + AI credentials
```

### 4. Test the Binding

```bash
rattle acme test-connection
# → "Connection OK for tenant 'acme'"
```

### 5. Cast Real Spells

```bash
# Conjure marketing descriptions
rattle acme ai-describe --limit 3 --language de

# Classify products into hidden orders
rattle acme ai-classify --limit 5

# Transmute ancient formats and push to the Rattle realm
rattle acme ai-transform datanorm rattle import.json --push

# Divine data quality insights
rattle acme ai-analyse --question "Which products lack descriptions?"
```

## The Spells

| Incantation | Purpose | Key Runes |
|---|---|---|
| `test-connection` | Verify link to the Rattle realm | — |
| `list-sources` | Reveal local data scrolls | — |
| `ai-describe` | Generate enchanting descriptions | `--limit`, `--language` |
| `ai-classify` | Sort into esoteric categories | `--limit` |
| `ai-transform` | Transmute between formats | `source_format`, `target_format`, `--push` |
| `ai-analyse` | Divine audits & deep questions | `--question` |
| `ai-analyse-pricelist` | Uncover configurator anti-patterns in pricelists | `--language` |
| `ai-suggest-config` | Conjure BOM-aware configuration recommendations | `--language`, `--product` |
| `ai-providers` | List available sigils | — |

Every spell returns pure JSON — pipe it, parse it, chain it into greater rituals.

## AI Sigils (Providers)

One rune to rule them all:

```bash
AI_PROVIDER=ollama rattle acme ai-describe   # local & free
```

| Sigil | Realm | Required Runes |
|---|---|---|
| `openai` | OpenAI / Azure / vLLM / LM Studio | `OPENAI_API_KEY`, `OPENAI_BASE_URL`*, `OPENAI_MODEL`* |
| `anthropic` | Anthropic Claude | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`* |
| `ollama` | Local Ollama | `OLLAMA_BASE_URL`*, `OLLAMA_MODEL`* |
| `custom` | Any OpenAI-compatible endpoint | `CUSTOM_AI_BASE_URL`, `CUSTOM_AI_API_KEY`*, `CUSTOM_AI_MODEL`* |

<sub>* optional</sub>

Full list of runes in [`.env.example`](.env.example).

## Working with CLI Agents

The Grimoire was forged for agents:

```bash
# Claude Code or Cursor
rattle acme ai-analyse --question "What are the top 5 missing descriptions?"

# Any agent that speaks shell
rattle acme ai-transform datanorm rattle data.json --push
```

No prompts. No GUI. Just `stdin`/`stdout`/JSON — pure arcane automation.

## The Architecture

```
         ┌───────────────────┐
         │  CLI / AI Agent   │
         └────────┬──────────┘
                  │  rattle acme ai-describe
         ┌────────▼──────────┐
         │     tasks.py       │  describe · classify · transform · analyse
         └────────┬──────────┘
                  │
         ┌────────▼──────────┐
         │   provider.py      │  complete() · complete_json()
         └────────┬──────────┘
                  │
    ┌─────┬───────┼───────┬─────────┐
    │     │       │       │         │
 OpenAI  Anthropic  Ollama  Custom HTTP
```

Full layout inside [`rattle_api/`](rattle_api/).

## Docker Vessel

```bash
docker build -t rattle-grimoire .
docker run --env-file .env rattle-grimoire acme test-connection
docker run --env-file .env rattle-grimoire acme ai-describe --limit 3
```

## Development Rites

```bash
pip install -e ".[dev,all-ai,all-sources]"
make lint    # Ruff — banish formatting demons
make test    # pytest — 170+ tests · ~97% coverage
make check   # All rites, in sequence
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full codex.

## Contributing

The Grimoire grows stronger with every new spell. Read [CONTRIBUTING.md](CONTRIBUTING.md) before adding your own incantations.

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE) — the ancient open-source pact.

---

*Made with dark-academia love by the Rattle coven. May your agents forever cast true.*
