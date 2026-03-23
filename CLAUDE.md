# Rattle AI Workspace

AI-agnostic rental data toolkit for the Rattle API. Users run CLI commands with their choice of AI backend (OpenAI, Anthropic, Ollama, or any custom endpoint) to enrich, classify, transform, and analyse rental product data.

## Architecture

Flat module structure — all core modules live in the project root:

| Module | Purpose |
|--------|---------|
| `main.py` | CLI entry point (argparse dispatch). All AI imports are lazy to avoid import errors when a provider SDK isn't installed. |
| `config.py` | Loads `.env`, resolves tenant API keys from `RATTLE_API_KEY_*` env vars, selects AI provider. |
| `client.py` | `RattleClient` — HTTP client for the Rattle REST API (GET/POST/PATCH/PUT/DELETE + pagination + image upload). |
| `ai_provider.py` | `AIProvider` ABC + 4 implementations (OpenAI, Anthropic, Ollama, CustomHTTP). Registry pattern via `PROVIDERS` dict. |
| `ai_tasks.py` | Task functions: `describe_products`, `classify_products`, `transform_interchange`, `analyse_rental_data`. Each fetches data from Rattle, sends to AI, optionally pushes results back. |
| `source_reader.py` | Reads local Excel files from `source/<tenant>/`. |
| `image_utils.py` | Image processing — shadow generation for "ohne" (without) product options. |

## Key Patterns

- **Env-var config**: All configuration via environment variables (see `.env.example`). No config files.
- **Tenant convention**: `RATTLE_API_KEY_PRESSTA=abc` → tenant name `pressta` on CLI.
- **AI provider registry**: Add provider by subclassing `AIProvider`, implementing `complete()`, registering in `PROVIDERS` dict.
- **Lazy AI imports**: `main.py` imports AI task functions inside command handlers to avoid requiring AI SDKs for non-AI commands.
- **JSON stdout**: All commands output JSON to stdout for piping/parsing. Progress messages go to stderr.

## Development

```bash
pip install -e ".[dev,all-ai]"    # Install everything
make check                         # Run lint + type-check + test
make lint                          # Ruff linter + formatter check
make type-check                    # mypy
make test                          # pytest
make format                        # Auto-format with Ruff
```

## Testing

- `pytest` — 135+ tests, ~97% coverage
- All tests run **without network or real API keys** — `conftest.py` has an autouse `clean_env` fixture that strips credentials
- `FakeAIProvider` in `conftest.py` provides deterministic responses for testing
- Tests that need file I/O use `tmp_path` fixture
- Config tests use `importlib.reload(config)` to test env var changes

## Adding a New AI Provider

1. Subclass `AIProvider` in `ai_provider.py`
2. Implement `complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2) -> str`
3. Register in the `PROVIDERS` dict at the bottom of `ai_provider.py`
4. Document env vars in `config.py` comments and `.env.example`

## Adding a New CLI Command

1. Add handler function `cmd_your_command(tenant, args)` in `main.py`
2. Add subparser in `main()` function
3. Register in the `commands` dispatch dict
4. Add tests in `tests/test_main.py`
