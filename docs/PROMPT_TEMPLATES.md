# Prompt Templates Reference

User-facing reference for the prompt template library that powers
`ai-prompts`, `ai-build-stage`, and `ai-build-configurator`. Every template
is a named, versioned builder registered in
[`rattle_api/prompt_templates.py`](../rattle_api/prompt_templates.py) and
composes [`knowledge.system_prompt_base`](../rattle_api/knowledge.py) so the
#1 rule, anti-patterns, and tenant preferences flow through automatically.

**Direct-apply**: each template emits `ensure_*` operations that
[`rattle_api/builder.py`](../rattle_api/builder.py) applies immediately to
the Rattle REST API as idempotent get-or-create calls. There are no
intermediate JSON files. You validate the result by opening the Rattle
frontend — the `ai-build-configurator` command prints the tenant URL and
the created product ids after it finishes.

## Discoverability

```bash
# list every template as JSON
rattle <tenant> ai-prompts list

# filter by stage
rattle <tenant> ai-prompts list --stage modeling

# print the fully-rendered system prompt for inspection
rattle <tenant> ai-prompts show extract-products --language de
```

## Pipeline stages

The default pipeline order is:

1. `extract-products`
2. `discover-features`
3. `model-groups-options`
4. `plan-areas`
5. `link-bom`
6. `discover-constraints`
7. `guided-selling`
8. `build-offer-template`
9. `review-configuration` (read-only)

Run the full pipeline:

```bash
rattle <tenant> ai-build-configurator pricelist.xlsx
```

Or in single-shot mode (one AI call via `full-configurator`):

```bash
rattle <tenant> ai-build-configurator pricelist.xlsx --single-shot
```

Inspect without applying any changes:

```bash
rattle <tenant> ai-build-configurator pricelist.xlsx --dry-run
```

Run ONE stage on its own:

```bash
rattle <tenant> ai-build-stage extract-products cat.pdf
```

## Templates

---

### `extract-products`

**Stage**: discovery — **Emits**: `ensure_product`

Identify every distinct product described in the source document, capturing
base price, currency, short marketing description, and a verbatim evidence
quote for each.

**Required inputs**: `source_content`
**Optional inputs**: `language`

**Operation schema**:
```json
{"op": "ensure_product", "name": str, "base_price": number?,
 "currency": str?, "description": str?}
```

**Example**:
```bash
rattle acme ai-build-stage extract-products pricelist.xlsx --language de
```

**Validates in the frontend**: open the products list in the Rattle UI and
confirm every product from the document is present with the correct base
price.

---

### `discover-features`

**Stage**: discovery — **Emits**: (nothing — produces an in-memory feature
map consumed by `model-groups-options`)

Surface EVERY configurable feature — including features that only appear as
'standard' / 'Serienausstattung' / implicit baselines. Without an explicit
baseline, no BOM line can reference it later. This is the #1 rule.

**Required inputs**: `source_content`
**Optional inputs**: `product_name`, `heuristic_findings`, `language`

Runs `knowledge.detect_anti_patterns()` as a free heuristic pre-pass and
feeds those findings into the user prompt so the AI sees exactly which
keywords in the document signal implicit baselines.

**Feature categories** the AI must assign to each feature:
- `physical` — maps to BOM lines in `link-bom`
- `software` — no BOM impact
- `service` — no BOM impact

---

### `model-groups-options`

**Stage**: modeling — **Emits**: `ensure_group`, `ensure_option`,
`ensure_area_config`

Turn discovered features into Rattle groups and options, reusing existing
groups wherever possible and respecting price-on-option,
explicit-options-for-all-variants, and minimal-keys.

**Required inputs**: `features` (from `discover-features`)
**Optional inputs**: `live_state`, `language`

**Operation schema**:
```json
{"op": "ensure_group", "name": str, "is_multi": bool, "description": str?,
 "reuse_existing": bool?, "existing_group_id": int?}
{"op": "ensure_option", "name": str, "group": str, "price": number,
 "recommended": bool, "description": str?}
{"op": "ensure_area_config", "option": str, "area": str, "price": number}
```

**Self-check**: every single-select group has exactly one
`recommended=true` option; no group is duplicated against the live state.

---

### `link-bom`

**Stage**: modeling — **Emits**: `ensure_part`, `ensure_bom_item`

Connect physical options to BOM items via `usage_subclauses` so the
configurator drives the bill of materials. Skip software and service
options — they legitimately have no BOM impact.

**Required inputs**: `live_state`
**Optional inputs**: `source_content`, `language`

**Operation schema**:
```json
{"op": "ensure_part", "part_number": str, "part_name": str, "part_cost": number?}
{"op": "ensure_bom_item", "parent_part": str, "child_part": str,
 "quantity": number, "uom": str?,
 "usage_subclauses": [{"option": str, "factor": number}]}
```

The builder resolves `option` names in `usage_subclauses` to the option ids
created by the preceding `model-groups-options` stage — within a single
batch, stages reference each other purely by name.

---

### `discover-constraints`

**Stage**: modeling — **Emits**: `ensure_constraint_pair`,
`ensure_constraint_rule`

Identify forbidden option combinations and conditional constraint rules.
Every constraint carries a verbatim evidence quote in its description.

**Required inputs**: `live_state`
**Optional inputs**: `source_content`, `language`

**Operation schema**:
```json
{"op": "ensure_constraint_pair", "option_1": str, "option_2": str,
 "description": str?}
{"op": "ensure_constraint_rule", "description": str,
 "rule_json": [{"if": {"option_selected": str},
                "then": {"forbid_options": [str]}}]}
```

---

### `plan-areas`

**Stage**: structuring — **Emits**: `ensure_area`, `link_group_to_area`

Organise groups into Rattle areas, honouring `no-empty-areas`. Narrative
content is routed to the `narrative_for_offer_template` list instead of
creating a narrative-only area.

**Required inputs**: `live_state`
**Optional inputs**: `language`

**Operation schema**:
```json
{"op": "ensure_area", "name": str, "description": str?,
 "parent_product": str}
{"op": "link_group_to_area", "group": str, "area": str}
```

---

### `guided-selling`

**Stage**: enrichment — **Emits**: `patch_option_recommended`

Draft a needs-assessment flow that maps 3–5 questions to
recommended-option presets per use-case. The builder applies the resulting
`recommended=true` overrides to the options via PATCH.

**Required inputs**: `live_state`
**Optional inputs**: `products`, `language`

**Operation schema**:
```json
{"op": "patch_option_recommended", "option": str,
 "recommended": bool, "preset": str?}
```

---

### `build-offer-template`

**Stage**: documents — **Emits**: `ensure_document_template`,
`ensure_structure_block`, `ensure_attachment`

Generate an offer document template that attaches the system dynamic
`document_configuration` block as required by the offer doc_type contract.
Wraps the existing `knowledge.system_prompt_build_offer_template()` builder.

**Optional inputs**: `doc_type_layout`, `dynamic_content_blocks`,
`language`

---

### `review-configuration`

**Stage**: validation — **Read-only**

Walks every configuration rule against the current live Rattle state and
flags violations with fix suggestions. Emits NO operations. Also prints the
tenant frontend URL so the reviewer can click through and visually
validate.

**Required inputs**: `live_state`
**Optional inputs**: `heuristic_findings`, `language`

**Output schema**:
```json
{"findings": [{"rule_id": str, "severity": "error"|"warning"|"info",
               "entity_type": str, "entity_id": int|null,
               "description": str, "fix": str}],
 "overall": {"status": "ok"|"warnings"|"errors", "summary": str}}
```

---

### `full-configurator`

**Stage**: pipeline — **Single-shot wrapper**

Performs extract-products, discover-features, model-groups-options,
link-bom, discover-constraints, plan-areas, guided-selling, and
build-offer-template in ONE AI call and emits all operations at once for
immediate idempotent application via `ConfigBuilder`.

Use when the catalogue is small and you want a single response; the
per-stage mode is preferred for larger catalogues because it gives more
granular logs and lets you inspect intermediate state.

```bash
rattle <tenant> ai-build-configurator pricelist.xlsx --single-shot
```

## Per-tenant customisation

Drop a markdown file at:

- `prompt_templates/<tenant>/<template_id>.md` — tenant-specific (wins)
- `prompt_templates/<template_id>.md` — global override

It is appended under `## Custom guidance` after the code-defined prompt.
Tenant memory (`memory/<tenant>/profile.md`) continues to flow through
`system_prompt_base` automatically.

## Validation workflow

1. `rattle <tenant> ai-build-configurator pricelist.xlsx --dry-run` —
   inspect the operations the pipeline would apply.
2. `rattle <tenant> ai-build-configurator pricelist.xlsx` — apply directly
   to Rattle. The command prints `OPEN <frontend_url>` on completion.
3. Click through the frontend URL and verify:
   - Every product exists with the correct base price.
   - Standard options are pre-selected as recommended.
   - Upgrade options change the price as expected.
   - Forbidden pairs cannot both be selected.
   - Each area contains its configurable groups (no empty areas).
4. Re-run the same command — every op should report `unchanged` (zero
   writes). This is the idempotency check.
5. Run the audit pass at any time:
   ```bash
   rattle <tenant> ai-build-stage review-configuration
   ```
