"""
Prompt template library for building Rattle product configurators.

A named, versioned registry of composable prompt templates that drive the
configurator-building pipeline. Each template:

- starts from :func:`rattle_api.knowledge.system_prompt_base` so the #1 rule,
  anti-patterns, and tenant preferences flow through unchanged;
- appends stage-specific framing, thinking guide, live-state summary, emitted
  operation schema, and a self-check checklist;
- declares which ``ensure_*`` operation types it may emit (applied by
  :class:`rattle_api.builder.ConfigBuilder` directly against the Rattle REST
  API — no intermediate JSON files or hand-apply steps).

The registry is exposed as ``PROMPT_TEMPLATES: dict[str, PromptTemplate]``
and iterated by the CLI for ``ai-prompts list`` / ``ai-prompts show`` /
``ai-build-stage`` / ``ai-build-configurator``.

Per-tenant overrides: drop a markdown file at
``prompt_templates/<tenant>/<template_id>.md`` (or
``prompt_templates/<template_id>.md`` for global) to append a
``## Custom guidance`` section after the code-defined prompt. See
:func:`load_template_override`.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .knowledge import (
    ANTI_PATTERNS,
    CONFIGURATION_RULES,
    FEATURE_EXTRACTION_HEURISTICS,
    GUIDED_SELLING_PATTERNS,
    STAGE_TO_RULE_IDS,
    system_prompt_base,
    system_prompt_build_offer_template,
)

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptTemplate:
    """A named, composable prompt template."""

    id: str
    # stage: discovery|modeling|structuring|enrichment|documents|validation|pipeline
    stage: str
    title: str
    description: str
    required_inputs: tuple[str, ...] = ()
    optional_inputs: tuple[str, ...] = ()
    emits: tuple[str, ...] = ()  # allowed ensure_* op types
    read_only: bool = False
    build: Callable[..., str] = field(default=None, repr=False)  # type: ignore[assignment]

    def render(self, **kwargs) -> str:
        """Render the template to a full system-prompt string.

        Keyword-only inputs required by the individual builder are passed
        through. The ``tenant_profile`` kwarg (optional) flows into
        :func:`knowledge.system_prompt_base`.
        """
        if self.build is None:
            raise RuntimeError(f"Template {self.id!r} has no build function")
        return self.build(**kwargs)


# ---------------------------------------------------------------------------
# Template override loader
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = _ROOT / "prompt_templates"


def load_template_override(
    template_id: str, tenant: str | None = None, *, root: Path | None = None
) -> str | None:
    """Return the markdown override for *template_id* if any, tenant-scoped first.

    Lookup order:
      1. ``prompt_templates/<tenant>/<template_id>.md``
      2. ``prompt_templates/<template_id>.md``
      3. ``None``
    """
    base = root if root is not None else TEMPLATES_DIR
    if tenant:
        tenant_path = base / tenant.lower() / f"{template_id}.md"
        if tenant_path.is_file():
            return tenant_path.read_text(encoding="utf-8")
    global_path = base / f"{template_id}.md"
    if global_path.is_file():
        return global_path.read_text(encoding="utf-8")
    return None


def _apply_override(
    rendered: str, template_id: str, tenant: str | None = None, *, root: Path | None = None
) -> str:
    """Append a ``## Custom guidance`` section if an override file exists."""
    override = load_template_override(template_id, tenant, root=root)
    if not override or not override.strip():
        return rendered
    return f"{rendered}\n\n## Custom guidance\n{override.strip()}"


# ---------------------------------------------------------------------------
# Shared constants used across stage templates
# ---------------------------------------------------------------------------

STAGE_FRAMING: dict[str, str] = {
    "extract-products": (
        "You are a document analyst extracting every distinct product described in "
        "the input document. Products are the top-level entities of the Rattle "
        "configurator — each becomes a row in /products."
    ),
    "discover-features": (
        "You are a configurator consultant discovering EVERY configurable feature "
        "of the given product — including features that only appear as 'standard' / "
        "'Serienausstattung' / implicit baselines. Missing an implicit baseline now "
        "makes it impossible to link BOM lines later."
    ),
    "model-groups-options": (
        "You are turning discovered features into Rattle groups and options. "
        "Reuse existing groups wherever possible (via reuse_existing + "
        "existing_group_id). Every single-select group must have exactly one "
        "recommended=true option. Prices belong on options, never on groups."
    ),
    "link-bom": (
        "You are linking physical options to BOM items via usage_subclauses. "
        "Each physical option must activate at least one BOM line so the "
        "configurator drives the bill of materials. Skip software and service "
        "options — they legitimately have no BOM impact."
    ),
    "discover-constraints": (
        "You are identifying forbidden option combinations and conditional "
        "constraint rules. Simple option-option exclusions become pair "
        "constraints; conditional 'if selected then forbid' logic becomes "
        "constraint rules. Every constraint must carry a verbatim evidence "
        "quote in its description."
    ),
    "plan-areas": (
        "You are organising groups into Rattle areas. Areas host configurable "
        "groups — never narrative content. An area must contain at least one "
        "group; narrative copy is routed to the documents system instead."
    ),
    "guided-selling": (
        "You are drafting a needs-assessment flow that recommends default "
        "options to end-customers. 3–5 high-impact questions map answers to "
        "scored option preferences; top-scored options become recommended "
        "defaults per preset use-case."
    ),
    "build-offer-template": (
        "You are building an offer document template that respects the Rattle "
        "documents system contract. The offer doc_type REQUIRES an attachment "
        "to the system dynamic content block 'dynamic:document_configuration' — "
        "reference it by id, never wrap it."
    ),
    "review-configuration": (
        "You are a senior configurator consultant performing a rule-compliance "
        "review against the live Rattle state. Walk every CONFIGURATION_RULES "
        "entry, flag violations with the offending entity id, and propose the "
        "minimum fix for each."
    ),
    "full-configurator": (
        "You are a full configurator-building pipeline. In one response, "
        "perform product extraction, feature discovery, group/option modeling, "
        "BOM linking, constraint discovery, area planning, guided-selling "
        "recommendations, and offer-template generation. Emit all operations "
        "in a single JSON object for immediate idempotent application."
    ),
}


# ---------------------------------------------------------------------------
# Helper fragments
# ---------------------------------------------------------------------------


def _format_live_state(live_state: dict | None) -> str:
    """Summarise the live Rattle state fetched from the API for the AI."""
    if not live_state:
        return "## Current Rattle live state\n(empty — nothing has been created yet)"

    lines: list[str] = ["## Current Rattle live state"]

    products = live_state.get("products") or []
    if products:
        lines.append("")
        lines.append(f"### Products ({len(products)})")
        for p in products[:20]:
            pid = p.get("id", "?")
            name = p.get("name", "?")
            lines.append(f"- id={pid}  name={name!r}")

    areas = live_state.get("areas") or []
    if areas:
        lines.append("")
        lines.append(f"### Areas ({len(areas)})")
        for a in areas[:30]:
            aid = a.get("id", "?")
            name = a.get("name", "?")
            lines.append(f"- id={aid}  name={name!r}")

    groups = live_state.get("groups") or []
    if groups:
        lines.append("")
        lines.append(f"### Groups ({len(groups)})")
        for g in groups[:50]:
            gid = g.get("id", "?")
            name = g.get("name", "?")
            is_multi = g.get("is_multi", False)
            opts = [o.get("name", "?") for o in (g.get("options") or [])][:8]
            lines.append(f"- id={gid}  name={name!r}  is_multi={is_multi}  options={opts}")

    parts = live_state.get("parts") or []
    if parts:
        lines.append("")
        lines.append(f"### Parts ({len(parts)})")
        for p in parts[:20]:
            pid = p.get("id", "?")
            number = p.get("part_number", p.get("number", "?"))
            name = p.get("part_name", p.get("name", "?"))
            lines.append(f"- id={pid}  number={number}  name={name!r}")

    if len(lines) == 1:
        lines.append("(empty — nothing has been created yet)")
    return "\n".join(lines)


def _format_rules_for_stage(stage_id: str) -> str:
    """Return a bullet list of rule ids this stage must honour."""
    rule_ids = STAGE_TO_RULE_IDS.get(stage_id, [])
    if not rule_ids:
        return "(none specific to this stage — still honour every base rule)"
    by_id = {r["id"]: r for r in CONFIGURATION_RULES}
    lines: list[str] = []
    for rid in rule_ids:
        rule = by_id.get(rid)
        if rule is not None:
            lines.append(f"- **{rid}**: {rule['rule']}")
    return "\n".join(lines)


def _lang_name(language: str) -> str:
    return "German" if language == "de" else language


# ---------------------------------------------------------------------------
# Stage 1 — extract-products
# ---------------------------------------------------------------------------


def build_extract_products(
    *,
    source_content: str = "",
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: extract-products\n{STAGE_FRAMING['extract-products']}\n\n"
        "## Thinking guide\n"
        "1. Scan the document for product names in headings, tables of contents, "
        "column headers, and opening paragraphs.\n"
        "2. Capture the base price and currency if stated; otherwise leave base_price "
        "null rather than guessing.\n"
        "3. Capture a 2-3 sentence marketing description drawn from the document.\n"
        "4. Note model ranges or product families as hints (so downstream stages can "
        "share groups across siblings).\n"
        "5. Keep an evidence_quote (verbatim, <=200 chars) for every product so the "
        "reviewer can verify the extraction.\n\n"
        "## Operations this stage may emit\n"
        "- `ensure_product {name, base_price?, currency?, description?}`\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('extract-products')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"operations": [{"op": "ensure_product", "name": str, "base_price": number?, '
        '"currency": str?, "description": str?, "evidence_quote": str?}], '
        '"notes": [str]}\n'
        "```\n"
        "Emit exactly one `ensure_product` per distinct product found.\n\n"
        "## Self-check before returning\n"
        "- [ ] Every product has a verbatim `evidence_quote` from the source.\n"
        "- [ ] Prices are numbers, not strings with currency suffixes.\n"
        "- [ ] No duplicate product names."
    )
    return _apply_override(rendered, "extract-products", tenant)


# ---------------------------------------------------------------------------
# Stage 2 — discover-features
# ---------------------------------------------------------------------------


def build_discover_features(
    *,
    source_content: str = "",
    product_name: str = "",
    heuristic_findings: list | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    de_markers = ", ".join(FEATURE_EXTRACTION_HEURISTICS["standard_markers_de"])
    en_markers = ", ".join(FEATURE_EXTRACTION_HEURISTICS["standard_markers_en"])
    addon_de = ", ".join(FEATURE_EXTRACTION_HEURISTICS["addon_markers_de"])
    addon_en = ", ".join(FEATURE_EXTRACTION_HEURISTICS["addon_markers_en"])
    scope_q = ", ".join(FEATURE_EXTRACTION_HEURISTICS["scope_qualifiers"])

    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: discover-features\n{STAGE_FRAMING['discover-features']}\n\n"
        "## Critical reminder\n"
        "Every standard / default variant MUST be surfaced as an explicit feature "
        "variant — not as an implicit baseline. This is the #1 rule. Without an "
        "explicit 'standard' variant, no BOM line can reference it later.\n\n"
        "## Feature-extraction heuristics\n"
        f"- **Standard markers (DE)**: {de_markers}\n"
        f"- **Standard markers (EN)**: {en_markers}\n"
        f"- **Add-on markers (DE)**: {addon_de}\n"
        f"- **Add-on markers (EN)**: {addon_en}\n"
        f"- **Scope qualifiers**: {scope_q}\n\n"
        "## Thinking guide\n"
        "1. First pass: list every variant that the document shows explicitly in "
        "an options / add-ons / surcharges section.\n"
        "2. Second pass: re-read every 'standard' / 'Serienausstattung' / "
        "'included' section and TURN EACH STANDARD INTO A FEATURE with the "
        "standard variant marked `is_standard=true`.\n"
        "3. Third pass: look at footnotes and scope qualifiers ('gilt für', "
        "'applicable to') to catch features that only apply to some product "
        "variants.\n"
        "4. Categorise each feature as `physical`, `software`, or `service` — "
        "this drives BOM linkage in the next stage.\n\n"
        "## Operations this stage may emit\n"
        "- (none — this stage is a feature-map producer; its output feeds the "
        "`model-groups-options` stage as user-prompt context)\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('discover-features')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"features": [{"name": str, "product": str, '
        '"category": "physical"|"software"|"service", '
        '"variants": [{"name": str, "is_standard": bool, "price_delta": number?, '
        '"evidence_quote": str?}]}], '
        '"operations": [], "notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] Every feature has at least 2 variants (or explicitly explain why "
        "a single-variant feature is truly fixed).\n"
        "- [ ] Every 'standard' keyword in the source is represented as a "
        "variant marked `is_standard=true`.\n"
        "- [ ] Every feature is categorised (physical/software/service).\n"
        "- [ ] No feature is missing its default/standard variant."
    )
    return _apply_override(rendered, "discover-features", tenant)


# ---------------------------------------------------------------------------
# Stage 3 — model-groups-options
# ---------------------------------------------------------------------------


def build_model_groups_options(
    *,
    live_state: dict | None = None,
    features: list | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: model-groups-options\n{STAGE_FRAMING['model-groups-options']}\n\n"
        f"{live}\n\n"
        "## Thinking guide\n"
        "1. For each discovered feature decide: single-select (is_multi=false) "
        "or multi-select (is_multi=true). Default to single-select unless the "
        "feature genuinely stacks.\n"
        "2. Check the live state above: if a group with the same (or very "
        "similar) name already exists, REUSE IT — emit `ensure_group` with "
        "`reuse_existing=true` and the existing id rather than creating a "
        "duplicate.\n"
        "3. For each feature, every variant becomes an option. Mark exactly "
        "ONE option per single-select group as `recommended=true` (the "
        "standard/default variant).\n"
        "4. Prices go on options, never on groups. Use `price_delta` relative "
        "to the standard variant (so the standard option gets price=0).\n"
        "5. For per-area scaled prices, emit `ensure_area_config` instead of "
        "duplicating the option.\n"
        "6. Do NOT invent custom `key` values unless the tenant profile "
        "explicitly opts in.\n\n"
        "## Operations this stage may emit\n"
        "- `ensure_group {name, is_multi, description?, reuse_existing?, "
        "existing_group_id?}`\n"
        "- `ensure_option {name, price, recommended, group, description?}`\n"
        "- `ensure_area_config {option, area, price}`\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('model-groups-options')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"operations": [{"op": "ensure_group"|"ensure_option"|"ensure_area_config", '
        '...}], "notes": [str]}\n'
        "```\n"
        "Emit operations in dependency order (groups before the options that "
        "reference them).\n\n"
        "## Self-check before returning\n"
        "- [ ] No group is duplicated against the live state above.\n"
        "- [ ] Every single-select group has exactly one `recommended=true` option.\n"
        "- [ ] Every option references a group by name.\n"
        "- [ ] No option has a custom `key` (unless the tenant profile requires it).\n"
        "- [ ] Prices are on options only, never on groups."
    )
    return _apply_override(rendered, "model-groups-options", tenant)


# ---------------------------------------------------------------------------
# Stage 4 — link-bom
# ---------------------------------------------------------------------------


def build_link_bom(
    *,
    live_state: dict | None = None,
    source_content: str = "",
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: link-bom\n{STAGE_FRAMING['link-bom']}\n\n"
        f"{live}\n\n"
        "## Thinking guide\n"
        "1. Iterate the live options above, skipping any whose feature category "
        "is `software` or `service` — those legitimately have no BOM impact.\n"
        "2. For each physical option, identify the child part it adds or "
        "replaces (ask the document, not your imagination).\n"
        "3. Identify the parent part (usually the product's main assembly).\n"
        "4. Emit `ensure_part` for any child part not already in the live state, "
        "then `ensure_bom_item` linking parent→child with "
        "`usage_subclauses: [{option: <name>, factor: 1.0}]`.\n"
        "5. When an option SUPERSEDES a standard variant, emit TWO BOM items "
        "— one activated by the standard option, one by the upgrade — so the "
        "BOM flips correctly on selection. This is the whole point of the "
        "explicit-options-for-all-variants rule.\n\n"
        "## Operations this stage may emit\n"
        "- `ensure_part {part_number, part_name, part_cost?}`\n"
        "- `ensure_bom_item {parent_part, child_part, quantity, uom?, "
        "usage_subclauses: [{option: <option_name>, factor: number}]}`\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('link-bom')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"operations": [{"op": "ensure_part"|"ensure_bom_item", ...}], '
        '"notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] Every physical option activates at least one BOM line.\n"
        "- [ ] No software/service option has a BOM line.\n"
        "- [ ] Every `usage_subclauses` entry references an option by name.\n"
        "- [ ] Standard-vs-upgrade features emit TWO BOM items, one per option."
    )
    return _apply_override(rendered, "link-bom", tenant)


# ---------------------------------------------------------------------------
# Stage 5 — discover-constraints
# ---------------------------------------------------------------------------


def build_discover_constraints(
    *,
    live_state: dict | None = None,
    source_content: str = "",
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    markers = ", ".join(FEATURE_EXTRACTION_HEURISTICS["constraint_markers"])
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: discover-constraints\n{STAGE_FRAMING['discover-constraints']}\n\n"
        f"{live}\n\n"
        "## Constraint-language markers to scan for\n"
        f"{markers}\n\n"
        "## Thinking guide\n"
        "1. Scan the document for explicit exclusion phrases "
        "('nicht wählbar wenn', 'not available with', 'forbidden with').\n"
        "2. For a direct exclusion (A excludes B) emit `ensure_constraint_pair`.\n"
        "3. For conditional 'if selected then forbid' logic (A → forbids "
        "{B, C, D}) emit `ensure_constraint_rule` with the rule_json shape "
        '`[{"if": {"option_selected": A}, "then": {"forbid_options": [B, C, D]}}]`.\n'
        "4. Every constraint MUST carry a verbatim evidence quote in its "
        "description — so reviewers can verify it.\n"
        "5. Do NOT invent constraints the document does not state.\n\n"
        "## Operations this stage may emit\n"
        "- `ensure_constraint_pair {option_1, option_2, description?}`\n"
        "- `ensure_constraint_rule {description, rule_json}`\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('discover-constraints')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"operations": [{"op": "ensure_constraint_pair"|"ensure_constraint_rule", '
        '...}], "notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] Every constraint has a verbatim evidence quote in `description`.\n"
        "- [ ] Every option referenced exists in the live state above.\n"
        "- [ ] `rule_json` matches the Rattle `/constraints/rules` shape."
    )
    return _apply_override(rendered, "discover-constraints", tenant)


# ---------------------------------------------------------------------------
# Stage 6 — plan-areas
# ---------------------------------------------------------------------------


def build_plan_areas(
    *,
    live_state: dict | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: plan-areas\n{STAGE_FRAMING['plan-areas']}\n\n"
        f"{live}\n\n"
        "## Thinking guide\n"
        "1. Cluster the live groups above by domain "
        "(mechanics / electronics / software / services / commercial).\n"
        "2. Emit an `ensure_area` for each cluster — but REFUSE to emit an "
        "area that would end up with zero groups linked.\n"
        "3. Emit `link_group_to_area` for every (group, area) pair.\n"
        "4. If the source includes pure narrative content (overview, "
        "descriptions, marketing copy), route it to the "
        "`narrative_for_offer_template` list instead of creating a "
        "narrative-only area.\n"
        "5. Reuse existing areas where their purpose matches.\n\n"
        "## Operations this stage may emit\n"
        "- `ensure_area {name, description?, parent_product}`\n"
        "- `link_group_to_area {group, area}`\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('plan-areas')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"operations": [{"op": "ensure_area"|"link_group_to_area", ...}], '
        '"narrative_for_offer_template": [{"slug": str, "title": str, '
        '"purpose": str}], "notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] No area has zero groups linked.\n"
        "- [ ] Every narrative snippet is routed to "
        "`narrative_for_offer_template`, not to an area.\n"
        "- [ ] Every link_group_to_area references an area created in this "
        "batch or already in the live state."
    )
    return _apply_override(rendered, "plan-areas", tenant)


# ---------------------------------------------------------------------------
# Stage 7 — guided-selling
# ---------------------------------------------------------------------------


def build_guided_selling(
    *,
    live_state: dict | None = None,
    products: list | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    archetypes = "\n".join(f"- **{p['id']}**: {p['archetype']}" for p in GUIDED_SELLING_PATTERNS)
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: guided-selling\n{STAGE_FRAMING['guided-selling']}\n\n"
        f"{live}\n\n"
        "## Question archetypes to choose from\n"
        f"{archetypes}\n\n"
        "## Thinking guide\n"
        "1. Pick 3–5 high-impact questions from the archetypes above. Each "
        "question should differentiate which options are recommended.\n"
        "2. For each possible answer, assign a score delta to each option "
        "(positive = 'prefer this option', negative = 'avoid').\n"
        "3. Collapse answer combinations into 2–4 named preset use-cases "
        "(e.g. 'Workshop / small batch', 'Production / high throughput').\n"
        "4. Each preset maps each group to one recommended option. Emit "
        "`patch_option_recommended` operations only for the overrides that "
        "differ from the global default.\n\n"
        "## Operations this stage may emit\n"
        "- `patch_option_recommended {option, recommended: bool, preset?}`\n\n"
        f"## Rules to honour\n{_format_rules_for_stage('guided-selling')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"questions": [{"text": str, "answers": [{"label": str, '
        '"option_scores": {"<option_name>": number}}]}], '
        '"recommendation_presets": [{"preset_name": str, "description": str, '
        '"applied_recommendations": {"<group_name>": "<option_name>"}}], '
        '"operations": [{"op": "patch_option_recommended", ...}], '
        '"notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] Every preset picks a valid option for every single-select group.\n"
        "- [ ] Every option referenced exists in the live state above.\n"
        "- [ ] Questions are written in the target language."
    )
    return _apply_override(rendered, "guided-selling", tenant)


# ---------------------------------------------------------------------------
# Stage 8 — build-offer-template  (wraps existing knowledge builder)
# ---------------------------------------------------------------------------


def build_build_offer_template(
    *,
    doc_type_layout: dict | None = None,
    dynamic_content_blocks: list | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    rendered = system_prompt_build_offer_template(
        doc_type_layout=doc_type_layout,
        dynamic_content_blocks=dynamic_content_blocks,
        language=language,
        tenant_profile=tenant_profile,
    )
    return _apply_override(rendered, "build-offer-template", tenant)


# ---------------------------------------------------------------------------
# Stage 9 — review-configuration  (READ-ONLY)
# ---------------------------------------------------------------------------


def build_review_configuration(
    *,
    live_state: dict | None = None,
    heuristic_findings: list | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    heuristic_block = ""
    if heuristic_findings:
        heuristic_block = (
            "\n\n## Heuristic anti-pattern findings (pre-computed)\n"
            f"{json.dumps(heuristic_findings, ensure_ascii=False, indent=2)[:3000]}"
        )
    rule_walk = "\n".join(f"- {r['id']}: {r['rule']}" for r in CONFIGURATION_RULES)
    anti_walk = "\n".join(f"- {a['id']}: {a['name']}" for a in ANTI_PATTERNS)
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: review-configuration (READ-ONLY)\n"
        f"{STAGE_FRAMING['review-configuration']}\n\n"
        f"{live}{heuristic_block}\n\n"
        "## Full rule walk\n"
        f"{rule_walk}\n\n"
        "## Anti-pattern walk\n"
        f"{anti_walk}\n\n"
        "## Thinking guide\n"
        "1. Walk every rule id above in order. For each, state pass or fail "
        "against the live state.\n"
        "2. For every failure, identify the offending entity (type + id + "
        "name) and propose the minimum fix.\n"
        "3. Walk every anti-pattern id. For each live entity that triggers "
        "an anti-pattern, flag it.\n"
        "4. Do NOT emit any operations — this stage is purely advisory.\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"findings": [{"rule_id": str, "severity": "error"|"warning"|"info", '
        '"entity_type": str, "entity_id": int|null, "description": str, '
        '"fix": str}], '
        '"overall": {"status": "ok"|"warnings"|"errors", "summary": str}, '
        '"operations": [], "notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] Every rule id above is addressed (pass or fail explicitly).\n"
        "- [ ] Every finding carries a fix suggestion.\n"
        "- [ ] `operations` is empty (this stage is read-only)."
    )
    return _apply_override(rendered, "review-configuration", tenant)


# ---------------------------------------------------------------------------
# Single-shot wrapper — full-configurator
# ---------------------------------------------------------------------------


def build_full_configurator(
    *,
    source_content: str = "",
    live_state: dict | None = None,
    doc_type_layout: dict | None = None,
    dynamic_content_blocks: list | None = None,
    language: str = "de",
    tenant_profile: str | None = None,
    tenant: str | None = None,
    **_: object,
) -> str:
    live = _format_live_state(live_state)
    stages_framing = "\n\n".join(
        f"### Sub-stage: {sid}\n{STAGE_FRAMING[sid]}"
        for sid in (
            "extract-products",
            "discover-features",
            "model-groups-options",
            "link-bom",
            "discover-constraints",
            "plan-areas",
            "guided-selling",
            "build-offer-template",
        )
    )
    rendered = (
        f"{system_prompt_base(tenant_profile=tenant_profile)}\n\n"
        f"## Stage: full-configurator (single-shot pipeline)\n"
        f"{STAGE_FRAMING['full-configurator']}\n\n"
        f"{live}\n\n"
        "## Sub-stage framings (perform ALL of these in one response)\n"
        f"{stages_framing}\n\n"
        "## Operations this stage may emit (union of sub-stage vocabularies)\n"
        "- `ensure_product`\n"
        "- `ensure_area` / `link_group_to_area`\n"
        "- `ensure_group` / `ensure_option` / `ensure_area_config`\n"
        "- `ensure_part` / `ensure_bom_item`\n"
        "- `ensure_constraint_pair` / `ensure_constraint_rule`\n"
        "- `patch_option_recommended`\n"
        "- `ensure_document_template` / `ensure_structure_block` / "
        "`ensure_attachment`\n\n"
        "## Operation ordering contract\n"
        "Emit operations in topological order so the runner can resolve name "
        "references without lookahead:\n"
        "1. `ensure_product`\n"
        "2. `ensure_part` (parents before children)\n"
        "3. `ensure_area`\n"
        "4. `ensure_group` (before the options that reference it)\n"
        "5. `link_group_to_area`\n"
        "6. `ensure_option`\n"
        "7. `ensure_area_config`\n"
        "8. `ensure_bom_item`\n"
        "9. `ensure_constraint_pair` / `ensure_constraint_rule`\n"
        "10. `patch_option_recommended`\n"
        "11. `ensure_document_template` / `ensure_structure_block` / "
        "`ensure_attachment`\n\n"
        f"## Rules to honour (every rule — this is the full pipeline)\n"
        f"{_format_rules_for_stage('full-configurator')}\n\n"
        f"## Your task (respond in {_lang_name(language)})\n"
        "Return a single JSON object with this shape:\n"
        "```\n"
        '{"operations": [...], "features": [...], "questions": [...], '
        '"recommendation_presets": [...], "narrative_for_offer_template": [...], '
        '"notes": [str]}\n'
        "```\n\n"
        "## Self-check before returning\n"
        "- [ ] Every product mentioned in the source has an `ensure_product` op.\n"
        "- [ ] Every feature (including implicit standards) has a group with "
        "explicit options.\n"
        "- [ ] Every single-select group has exactly one `recommended=true` option.\n"
        "- [ ] Every physical option has at least one `ensure_bom_item` that "
        "references it in `usage_subclauses`.\n"
        "- [ ] No area is emitted without at least one `link_group_to_area`.\n"
        "- [ ] Operations are in topological order so name references resolve "
        "on the first pass."
    )
    return _apply_override(rendered, "full-configurator", tenant)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "extract-products": PromptTemplate(
        id="extract-products",
        stage="discovery",
        title="Extract products",
        description=(
            "Identify every distinct product described in the source document, "
            "capturing base price, currency, description, and evidence quotes."
        ),
        required_inputs=("source_content",),
        optional_inputs=("language",),
        emits=("ensure_product",),
        build=build_extract_products,
    ),
    "discover-features": PromptTemplate(
        id="discover-features",
        stage="discovery",
        title="Discover configurable features",
        description=(
            "Surface EVERY configurable feature — including features that only "
            "appear as standard / Serienausstattung / implicit baselines. "
            "Feeds the model-groups-options stage."
        ),
        required_inputs=("source_content",),
        optional_inputs=("product_name", "heuristic_findings", "language"),
        emits=(),
        build=build_discover_features,
    ),
    "model-groups-options": PromptTemplate(
        id="model-groups-options",
        stage="modeling",
        title="Model groups and options",
        description=(
            "Turn discovered features into Rattle groups and options, reusing "
            "existing groups and respecting price-on-option, "
            "explicit-options-for-all-variants, and minimal-keys."
        ),
        required_inputs=("features",),
        optional_inputs=("live_state", "language"),
        emits=("ensure_group", "ensure_option", "ensure_area_config"),
        build=build_model_groups_options,
    ),
    "link-bom": PromptTemplate(
        id="link-bom",
        stage="modeling",
        title="Link options to BOM",
        description=(
            "Connect physical options to BOM items via usage_subclauses so the "
            "configurator drives the bill of materials."
        ),
        required_inputs=("live_state",),
        optional_inputs=("source_content", "language"),
        emits=("ensure_part", "ensure_bom_item"),
        build=build_link_bom,
    ),
    "discover-constraints": PromptTemplate(
        id="discover-constraints",
        stage="modeling",
        title="Discover forbidden combinations",
        description=(
            "Identify forbidden option pairs and conditional constraint rules, "
            "each with a verbatim evidence quote."
        ),
        required_inputs=("live_state",),
        optional_inputs=("source_content", "language"),
        emits=("ensure_constraint_pair", "ensure_constraint_rule"),
        build=build_discover_constraints,
    ),
    "plan-areas": PromptTemplate(
        id="plan-areas",
        stage="structuring",
        title="Plan areas",
        description=(
            "Organise groups into Rattle areas, honouring no-empty-areas and "
            "routing narrative content to the offer-template stage."
        ),
        required_inputs=("live_state",),
        optional_inputs=("language",),
        emits=("ensure_area", "link_group_to_area"),
        build=build_plan_areas,
    ),
    "guided-selling": PromptTemplate(
        id="guided-selling",
        stage="enrichment",
        title="Guided selling",
        description=(
            "Draft a needs-assessment flow that maps 3-5 questions to "
            "recommended-option presets per use-case."
        ),
        required_inputs=("live_state",),
        optional_inputs=("products", "language"),
        emits=("patch_option_recommended",),
        build=build_guided_selling,
    ),
    "build-offer-template": PromptTemplate(
        id="build-offer-template",
        stage="documents",
        title="Build offer document template",
        description=(
            "Generate an offer document template that attaches the system "
            "dynamic 'document_configuration' block as required by the "
            "offer doc_type contract."
        ),
        required_inputs=(),
        optional_inputs=("doc_type_layout", "dynamic_content_blocks", "language"),
        emits=(
            "ensure_document_template",
            "ensure_structure_block",
            "ensure_attachment",
        ),
        build=build_build_offer_template,
    ),
    "review-configuration": PromptTemplate(
        id="review-configuration",
        stage="validation",
        title="Review configuration",
        description=(
            "Walk every configuration rule against the live Rattle state and "
            "flag violations with fix suggestions. Read-only — emits no "
            "operations."
        ),
        required_inputs=("live_state",),
        optional_inputs=("heuristic_findings", "language"),
        emits=(),
        read_only=True,
        build=build_review_configuration,
    ),
    "full-configurator": PromptTemplate(
        id="full-configurator",
        stage="pipeline",
        title="Full configurator (single-shot pipeline)",
        description=(
            "Single-shot wrapper that performs extract, discover-features, "
            "model-groups-options, link-bom, discover-constraints, plan-areas, "
            "guided-selling, and build-offer-template in one AI call and "
            "emits all ensure_* operations at once for immediate idempotent "
            "application."
        ),
        required_inputs=("source_content",),
        optional_inputs=(
            "live_state",
            "doc_type_layout",
            "dynamic_content_blocks",
            "language",
        ),
        emits=(
            "ensure_product",
            "ensure_part",
            "ensure_area",
            "link_group_to_area",
            "ensure_group",
            "ensure_option",
            "ensure_area_config",
            "ensure_bom_item",
            "ensure_constraint_pair",
            "ensure_constraint_rule",
            "patch_option_recommended",
            "ensure_document_template",
            "ensure_structure_block",
            "ensure_attachment",
        ),
        build=build_full_configurator,
    ),
}


# ---------------------------------------------------------------------------
# Convenience accessors
# ---------------------------------------------------------------------------


def list_templates(stage: str | None = None) -> list[dict]:
    """Return a list of template summaries, optionally filtered by stage."""
    out: list[dict] = []
    for tpl in PROMPT_TEMPLATES.values():
        if stage and tpl.stage != stage:
            continue
        out.append(
            {
                "id": tpl.id,
                "stage": tpl.stage,
                "title": tpl.title,
                "description": tpl.description,
                "emits": list(tpl.emits),
                "read_only": tpl.read_only,
            }
        )
    return out


def get_template(template_id: str) -> PromptTemplate:
    """Return the :class:`PromptTemplate` for *template_id* or raise KeyError."""
    if template_id not in PROMPT_TEMPLATES:
        available = ", ".join(PROMPT_TEMPLATES)
        raise KeyError(f"Unknown template {template_id!r}. Available: {available}")
    return PROMPT_TEMPLATES[template_id]


# Ordered sequence the configurator-build pipeline runs when not in single-shot.
PIPELINE_STAGE_ORDER: tuple[str, ...] = (
    "extract-products",
    "discover-features",
    "model-groups-options",
    "plan-areas",
    "link-bom",
    "discover-constraints",
    "guided-selling",
    "build-offer-template",
    "review-configuration",
)
