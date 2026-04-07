# Rattle AI Workspace

AI-powered console CLI for the Rattle API. Users run CLI commands with their choice of AI backend (OpenAI, Anthropic, Ollama, or any custom endpoint) to enrich, classify, transform, and analyse product data. The codebase embeds deep configurator consulting expertise so AI agents working with it can guide users in building correct, BOM-aware product configurations.

## Architecture

Standard Python package layout — all source lives in `rattle_api/`:

| Module | Purpose |
|--------|---------|
| `rattle_api/main.py` | CLI entry point (argparse dispatch). All AI imports are lazy to avoid import errors when a provider SDK isn't installed. |
| `rattle_api/config.py` | Loads `.env`, resolves tenant API keys from `RATTLE_API_KEY_*` env vars, selects AI provider. |
| `rattle_api/client.py` | `RattleClient` — HTTP client for the Rattle REST API (GET/POST/PATCH/PUT/DELETE + pagination + image upload). |
| `rattle_api/provider.py` | `AIProvider` ABC + 4 implementations (OpenAI, Anthropic, Ollama, CustomHTTP). Registry pattern via `PROVIDERS` dict. |
| `rattle_api/tasks.py` | Task functions: `describe_products`, `classify_products`, `transform_interchange`, `analyse_data`, `analyse_pricelist`, `suggest_configuration`. Each fetches data from Rattle, sends to AI, optionally pushes results back. |
| `rattle_api/knowledge.py` | Configurator consulting knowledge: data model, configuration rules, anti-patterns, system prompts, heuristic detection. Source of truth for all domain expertise. |
| `rattle_api/source.py` | Reads local files from `source/<tenant>/` — Excel (.xlsx/.xlsm), PDF, and Word (.docx). |
| `rattle_api/image.py` | Image processing — shadow generation for "ohne" (without) product options. |

## Key Patterns

- **Env-var config**: All configuration via environment variables (see `.env.example`). No config files.
- **Tenant convention**: `RATTLE_API_KEY_ACME=abc` → tenant name `acme` on CLI.
- **AI provider registry**: Add provider by subclassing `AIProvider`, implementing `complete()`, registering in `PROVIDERS` dict in `provider.py`.
- **Lazy AI imports**: `main.py` imports AI task functions inside command handlers to avoid requiring AI SDKs for non-AI commands.
- **JSON stdout**: All commands output JSON to stdout for piping/parsing. Progress messages go to stderr.
- **Relative imports**: Within the package, modules use relative imports (e.g. `from .config import BASE_URL`).

## Development

```bash
pip install -e ".[dev,all-ai,all-sources]"  # Install everything
make check                         # Run lint + type-check + test
make lint                          # Ruff linter + formatter check
make type-check                    # mypy
make test                          # pytest
make format                        # Auto-format with Ruff
```

## Testing

- `pytest` — 170+ tests, ~97% coverage
- All tests run **without network or real API keys** — `conftest.py` has an autouse `clean_env` fixture that strips credentials
- `FakeAIProvider` in `conftest.py` provides deterministic responses for testing
- Tests that need file I/O use `tmp_path` fixture
- Config tests use `importlib.reload(rattle_api.config)` to test env var changes
- Tests import from `rattle_api.*` (e.g. `from rattle_api.provider import get_provider`)

## Adding a New AI Provider

1. Subclass `AIProvider` in `rattle_api/provider.py`
2. Implement `complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2) -> str`
3. Register in the `PROVIDERS` dict at the bottom of `provider.py`
4. Document env vars in `config.py` comments and `.env.example`

## Adding a New CLI Command

1. Add handler function `cmd_your_command(tenant, args)` in `rattle_api/main.py`
2. Add subparser in `main()` function
3. Register in the `commands` dispatch dict
4. Add tests in `tests/test_main.py`

## Configurator Consulting Knowledge

This codebase embeds deep consulting expertise about building correct product configurators. The knowledge is codified in `rattle_api/knowledge.py` and automatically applied by the AI analysis tasks (`ai-analyse-pricelist`, `ai-suggest-config`).

### The #1 Rule: Explicit Options for ALL Variants

**NEVER build 'base product + add-ons' where the base configuration is implicit.** Every configurable feature MUST have an explicit group with ALL variants as separate options — including the 'standard' variant.

**Why?** Without an explicit option for the standard variant, it is impossible to write a `usage_subclause` that adds the standard parts to the BOM. The configurator cannot remove an implicit baseline — it can only activate parts linked to selected options.

**Example — WRONG (classic pricelist):**
Product comes with 17" wheels as standard. Option: '19 inch wheels (+500€)'. Problem: no way to create a usage_subclause that removes 17" wheels from BOM when 19" is selected.

**Example — CORRECT (BOM-aware):**
Group 'Wheels': Option '17 inch wheels' (default), Option '19 inch wheels' (+500€). usage_subclause: if '17 inch' selected → add 17" parts; if '19 inch' selected → add 19" parts.

### Rattle Data Model

```
Product
  ├── Areas (rich text content sections)
  ├── Groups (configuration groups, e.g. 'Wheels', 'Frässpindel')
  │   └── Options (choices: '17 inch', '19 inch', 'ohne', 'mit')
  ├── Parts (BOM items — physical components)
  └── Part Placements (connect parts to areas)
      └── Usage Subclauses (conditional BOM rules based on selected options)
```

- **Area Overrides**: allow reusing groups/options across products with per-product price differences (avoids duplicating groups).

### Configuration Rules

- **explicit-options-for-all-variants**: Every configurable feature MUST have an explicit group with ALL variants as separate options — including the "standard" variant
- **default-option-required**: Every group must have exactly one default (pre-selected) option
- **no-implicit-standard**: The standard/base variant must be a named, selectable option, never an implicit baseline
- **bom-coverage**: Every option must map to a clear BOM impact via usage_subclauses
- **mutual-exclusivity**: Options within a single-select group must be mutually exclusive
- **price-on-option**: Price modifiers belong on the option level, not as separate line items
- **reuse-over-duplicate**: Always prefer reusing existing groups/options over creating duplicates; use areaOverrides for product-specific price differences
- **forbidden-combinations**: Identify and define rules for invalid option combinations across groups (e.g., machine variant X incompatible with accessory Y)

### Anti-Patterns to Detect

- **Implicit Base Configuration** (`implicit-base-config`): Standard features listed without explicit options. Indicators: standard, Grundausstattung, Serienausstattung, im Lieferumfang, serienmäßig
- **Add-on Only Options** (`addon-only-options`): Options listed only as surcharges without stating the default. Indicators: Aufpreis, Zuschlag, zusätzlich, extra, Mehrpreis
- **Binary ohne/mit Without Explicit Group** (`binary-ohne-mit-no-group`): Features as 'with/without' but not in a proper group. Indicators: ohne, mit, ja/nein
- **Options Without BOM Mapping** (`missing-bom-mapping`): Features without part/article references. Indicators: auf Anfrage, nach Absprache
- **Ambiguous Group Boundaries** (`overlapping-groups`): Same feature in multiple groups. Indicators: siehe auch, alternativ

### AI Commands for Configuration

- `rattle <tenant> ai-analyse-pricelist <file>` — Analyse a pricelist for configurator anti-patterns (heuristic + AI)
- `rattle <tenant> ai-suggest-config <file>` — Generate BOM-aware configuration recommendations (reuses existing groups, suggests forbidden combinations)
