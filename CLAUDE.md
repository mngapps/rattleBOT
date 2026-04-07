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

## Rattle REST API Reference

A comprehensive reference of all ~500 REST API operations is at `docs/API_REFERENCE.md`.
Consult it before making any API calls to understand available endpoints, required parameters,
request/response shapes, and example JSON. The `RattleClient` in `rattle_api/client.py` is a
thin HTTP wrapper — paths are relative (e.g. `client.get("products")` calls `GET /api/v1/products`).

## Configurator Consulting Knowledge

This codebase embeds deep consulting expertise about building correct product configurators. The knowledge is codified in `rattle_api/knowledge.py` and automatically applied by the AI analysis tasks (`ai-analyse-pricelist`, `ai-suggest-config`).

### The #1 Rule: Explicit Options for ALL Variants

**NEVER build 'base product + add-ons' where the base configuration is implicit.** Every configurable feature MUST have an explicit group with ALL variants as separate options — including the 'standard' variant.

**Why?** Without an explicit option for the standard variant, no BOM item can carry a `usage_subclause` referencing it. The configurator can only activate BOM lines linked to selected options — it cannot remove an implicit baseline.

**Example — WRONG (classic pricelist):**
Product comes with 17" wheels as standard. Option '19 inch' (price: 500). Problem: no BOM item can have a usage_subclause for the 17" wheels because no option represents them.

**Example — CORRECT (BOM-aware):**
Group 'Wheels' (is_multi: false): Option '17 inch' (recommended: true, price: 0), Option '19 inch' (recommended: false, price: 500). BOM: child_part '17-inch wheel assy' with usage_subclauses: [{option_id: <17_inch>, factor: 1.0}]; child_part '19-inch wheel assy' with usage_subclauses: [{option_id: <19_inch>, factor: 1.0}].

### Rattle Data Model

```
Product
  ├── Areas (configurable sections, assigned via /products/{id}/areas)
  │   └── Groups (linked to areas via /groups/{id}/areas, is_multi: single/multi)
  │       └── Options (name, price, key, recommended)
  ├── Parts (physical components)
  │   └── BOM items (parent→child, quantity, usage_subclauses)
  └── Constraints (/constraints + /constraints/rules)
```

- **usage_subclauses** on BOM items: `[{"option_id": 301, "factor": 1.0}]` — when option 301 is selected, this BOM line is active with quantity × factor.
- **Option area-config** (`/options/{id}/area-config`): per-area overrides for option price, description, recommended flag — avoids duplicating groups.
- **Pair-level constraints** (`POST /constraints`): simple option-option exclusions as `{option_id1, option_id2}` pairs. Atomically replaces all pairs for a product (use `X-Constraints-Version` header).
- **Constraint rules** (`POST /constraints/rules`): conditional logic with `rule_json: [{"if": {"option_selected": X}, "then": {"forbid_options": [Y, Z]}}]`.

### Configuration Rules

- **explicit-options-for-all-variants**: Every configurable feature MUST have an explicit group with ALL variants as separate options — including the "standard" variant. The standard variant must be a named, selectable option, never an implicit baseline.
- **price-on-option**: Price modifiers belong on the option level (the `price` field), not as separate line items
- **reuse-over-duplicate**: Always prefer reusing existing groups/options over creating duplicates; use option area-config and price-overrides for area-specific differences
- **forbidden-combinations**: Identify and define constraints for invalid option combinations. Use pair-level constraints (`POST /constraints` with `{option_id1, option_id2}` pairs) for simple exclusions, constraint rules (`POST /constraints/rules`) for conditional logic

Note: Not every option maps to BOM parts. Options for software features, services, or cosmetic choices may have no usage_subclauses — that is normal. Usage subclauses are only needed for options that affect the physical bill of materials.

### Anti-Patterns to Detect

- **Implicit Base Configuration** (`implicit-base-config`): Standard features listed without explicit options. Indicators: standard, Grundausstattung, Serienausstattung, im Lieferumfang, serienmäßig
- **Add-on Only Options** (`addon-only-options`): Options listed only as surcharges without stating the default. Indicators: Aufpreis, Zuschlag, zusätzlich, extra, Mehrpreis

### AI Commands for Configuration

- `rattle <tenant> ai-analyse-pricelist <file>` — Analyse a pricelist for configurator anti-patterns (heuristic + AI)
- `rattle <tenant> ai-suggest-config <file>` — Generate BOM-aware configuration recommendations (reuses existing groups, suggests forbidden combinations)
