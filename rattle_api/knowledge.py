"""
Configurator consulting knowledge for the Rattle product configurator.

Contains structured expertise about building correct, BOM-aware product
configurations.  Used as:
  (a) system prompts for AI tasks
  (b) heuristic anti-pattern detection (no AI needed)
  (c) reference documentation (Markdown export for CLAUDE.md)

All data is plain Python — zero external dependencies.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Rattle data model reference
# ---------------------------------------------------------------------------

RATTLE_DATA_MODEL: dict = {
    "product": {
        "description": (
            "Top-level entity representing a configurable product "
            "(e.g. a machine, furniture piece, vehicle). Areas are "
            "assigned to products via /products/{id}/areas."
        ),
        "key_fields": ["id", "name", "description", "base_price", "currency", "is_active"],
        "api_endpoint": "/products",
        "relationships": ["areas", "parts", "constraints"],
    },
    "area": {
        "description": (
            "A configurable section of a product. Areas are assigned to "
            "products and groups are linked to areas. Rich-text content "
            "(EditorJS blocks) is managed via /areas/{id}/content. "
            "Multiple areas per product (e.g. different configurable zones)."
        ),
        "key_fields": ["id", "name", "description", "price", "language", "allow_disable"],
        "api_endpoint": "/areas",
        "relationships": ["product", "groups"],
    },
    "group": {
        "description": (
            "Configuration group collecting related options "
            "(e.g. 'Wheels', 'Frässpindel', 'Auftragsverwaltung IoT'). "
            "Groups are linked to areas (not directly to products) via "
            "/groups/{id}/areas. The is_multi field controls whether "
            "the user can select one option (single-select) or multiple "
            "(multi-select)."
        ),
        "key_fields": ["id", "name", "description", "key", "is_multi", "area_ids"],
        "api_endpoint": "/groups",
        "relationships": ["areas", "options"],
    },
    "option": {
        "description": (
            "A single selectable choice within a group "
            "(e.g. '17 inch wheels', '19 inch wheels', 'ohne', 'mit'). "
            "Every variant — including the default/standard — must be an "
            "explicit option. The 'recommended' flag marks the pre-selected "
            "default. Per-area overrides (price, description) are set via "
            "/options/{id}/area-config?area_id=X."
        ),
        "key_fields": ["id", "name", "description", "price", "key", "recommended", "group_id"],
        "api_endpoint": "/options",
        "relationships": ["group"],
    },
    "part": {
        "description": (
            "A physical component, sub-assembly, or finished good that "
            "can appear in a product's bill of materials."
        ),
        "key_fields": ["id", "part_number", "part_name", "part_cost", "part_type", "status"],
        "api_endpoint": "/parts",
        "relationships": ["bom_items", "placements"],
    },
    "bom_item": {
        "description": (
            "A parent→child relationship in the hierarchical BOM. "
            "Each BOM item links a parent part to a child part with a "
            "quantity. The 'usage_subclauses' array conditionally includes "
            "this BOM line based on selected options: each entry is "
            '{"option_id": <id>, "factor": <multiplier>}. When the '
            "referenced option is selected, this BOM line is active with "
            "quantity × factor. This is the core mechanism that makes "
            "configuration drive the bill of materials."
        ),
        "key_fields": [
            "id",
            "parent_part_id",
            "child_part_id",
            "quantity",
            "uom",
            "usage_subclauses",
            "option_scalings",
        ],
        "api_endpoint": "/parts/{id}/bom",
        "relationships": ["parent_part", "child_part", "options (via usage_subclauses)"],
    },
    "constraint": {
        "description": (
            "Forbidden option combinations. Two mechanisms:\n"
            "1) Pair-level: simple option-option exclusions. "
            "POST /constraints atomically replaces all pairs for a product "
            "(use X-Constraints-Version header). Each pair is "
            "{option_id1, option_id2} — selecting one forbids the other. "
            "Check via POST /constraints/check "
            '{"product_id", "option_id1", "option_id2"}.\n'
            "2) Rule-level: conditional rules via /constraints/rules. "
            "Each rule has rule_json: "
            '[{"if": {"option_selected": X}, "then": {"forbid_options": [Y, Z]}}]. '
            "Scoped to product_id and optionally area_id."
        ),
        "key_fields": ["id", "product_id", "area_id", "description", "rule_json"],
        "api_endpoint": "/constraints (pairs), /constraints/rules (conditional)",
        "relationships": ["product", "options"],
    },
    "option_area_config": {
        "description": (
            "Per-area override for an option's price, key, description, "
            "or recommended flag. Allows reusing the same group/option "
            "across areas while adjusting properties per area. Avoids "
            "duplicating groups and options."
        ),
        "key_fields": ["option_id", "area_id", "price", "key", "description", "recommended"],
        "api_endpoint": "/options/{id}/area-config?area_id=X",
        "relationships": ["option", "area"],
    },
}


# ---------------------------------------------------------------------------
# Configuration rules
# ---------------------------------------------------------------------------

CONFIGURATION_RULES: list[dict] = [
    {
        "id": "explicit-options-for-all-variants",
        "rule": (
            "Every configurable feature MUST have an explicit group with "
            "ALL variants as separate, selectable options — including the "
            "'standard' or 'default' variant. The standard variant must "
            "be a named, selectable option, never an implicit baseline."
        ),
        "rationale": (
            "Without an explicit option for the standard variant, it is "
            "impossible to write a usage_subclause that adds the standard "
            "parts to the BOM. The configurator cannot remove an implicit "
            "baseline — it can only activate parts linked to selected options. "
            "Example: if '17 inch wheels' is implicit (not an option), "
            "there is no way to write a rule that adds 17-inch wheel parts "
            "to the BOM."
        ),
        "applies_to": ["groups", "options"],
    },
    {
        "id": "price-on-option",
        "rule": (
            "Price modifiers belong on the option level, not on the "
            "group or as separate line items in the pricelist."
        ),
        "rationale": (
            "Prices attached to groups or external line items cannot "
            "be conditionally applied based on option selection."
        ),
        "applies_to": ["options"],
    },
    {
        "id": "reuse-over-duplicate",
        "rule": (
            "Always prefer reusing existing groups and options over "
            "creating duplicates. Use option area-config "
            "(/options/{id}/area-config) and price-overrides for "
            "per-area differences."
        ),
        "rationale": (
            "Duplicate groups with identical names fragment the "
            "configuration catalogue and make maintenance harder. "
            "Option area-config lets one group/option serve many areas "
            "with per-area pricing and descriptions."
        ),
        "applies_to": ["groups", "options"],
    },
    {
        "id": "forbidden-combinations",
        "rule": (
            "Identify and define constraints for invalid option "
            "combinations. Use pair-level constraints (POST /constraints "
            "with {option_id1, option_id2} pairs) for simple exclusions. "
            "Use constraint rules (POST /constraints/rules with rule_json) "
            "for conditional logic."
        ),
        "rationale": (
            "Without constraints, users can select impossible "
            "configurations that cannot be manufactured or delivered."
        ),
        "applies_to": ["options", "constraints"],
    },
]


# ---------------------------------------------------------------------------
# Anti-patterns
# ---------------------------------------------------------------------------

ANTI_PATTERNS: list[dict] = [
    {
        "id": "implicit-base-config",
        "name": "Implicit Base Configuration",
        "description": (
            "The pricelist describes standard features as included in the "
            "base product without creating explicit options for them. "
            "Only upgrades/add-ons appear as selectable options."
        ),
        "indicators": [
            "standard",
            "Grundausstattung",
            "Serienausstattung",
            "im Lieferumfang",
            "included",
            "inkl.",
            "serienmäßig",
            "Basisausstattung",
        ],
        "correction": (
            "Create an explicit group with explicit options for ALL "
            "variants — including the standard one. Mark the standard "
            "option as default."
        ),
        "example_wrong": (
            'Product comes with 17" wheels as standard. '
            "Option '19 inch wheels' (price: 500). "
            "Problem: no BOM item can carry a usage_subclause for the "
            '17" wheels because no option represents them.'
        ),
        "example_correct": (
            "Group 'Wheels' (is_multi: false): "
            "Option '17 inch' (recommended: true, price: 0), "
            "Option '19 inch' (recommended: false, price: 500). "
            "BOM: child_part '17-inch wheel assy' with "
            "usage_subclauses: [{option_id: <17_inch>, factor: 1.0}]; "
            "child_part '19-inch wheel assy' with "
            "usage_subclauses: [{option_id: <19_inch>, factor: 1.0}]."
        ),
    },
    {
        "id": "addon-only-options",
        "name": "Add-on Only Options",
        "description": (
            "Options are listed only as surcharges or add-ons to a base "
            "product, without explicitly stating what the base/default is."
        ),
        "indicators": [
            "Aufpreis",
            "Zuschlag",
            "surcharge",
            "zusätzlich",
            "extra",
            "Mehrpreis",
            "Aufschlag",
            "optional",
        ],
        "correction": (
            "For every add-on, identify the base variant it replaces "
            "or supplements. Create a group with both the base and the "
            "add-on as explicit options."
        ),
        "example_wrong": (
            "Aufpreis Frässpindel HSK-63F mit Encoder: +2.500€. "
            "Problem: what is the default spindle? No option exists for it."
        ),
        "example_correct": (
            "Group 'Frässpindel' (is_multi: false): "
            "Option 'ISO 30 Standard' (recommended: true, price: 0), "
            "Option 'HSK-63F ohne Encoder' (price: 1800), "
            "Option 'HSK-63F mit Encoder' (price: 2500)."
        ),
    },
]


# ---------------------------------------------------------------------------
# System prompt builders
# ---------------------------------------------------------------------------


def system_prompt_base() -> str:
    """Core consulting rules fragment, usable as a prefix for any prompt."""
    rules_text = "\n".join(
        f"  {i + 1}. **{r['id']}**: {r['rule']}" for i, r in enumerate(CONFIGURATION_RULES)
    )

    anti_text = "\n".join(
        f"  - **{ap['name']}**: {ap['description']} Indicators: {', '.join(ap['indicators'][:5])}"
        for ap in ANTI_PATTERNS
    )

    return (
        "You are a product configurator consultant with deep expertise in "
        "building correct, BOM-aware product configurations for the Rattle "
        "product configurator platform.\n\n"
        "## Rattle Data Model\n"
        "Product → Areas → Groups (is_multi: single/multi-select) → Options\n"
        "Parts → BOM items (parent→child with quantity + usage_subclauses)\n"
        "Constraints (forbidden option combinations + conditional rules)\n\n"
        "- Groups are linked to Areas (not directly to Products). "
        "A group's is_multi field controls single-select vs multi-select.\n"
        "- Options have: name, price, key, recommended (=pre-selected default).\n"
        "- BOM items contain usage_subclauses: "
        '[{"option_id": <id>, "factor": <multiplier>}]. '
        "When the referenced option is selected, this BOM line is active "
        "with quantity × factor.\n"
        "- Per-area price/config overrides: /options/{id}/area-config "
        "and /options/{id}/price-overrides — avoids duplicating groups.\n"
        "- Pair-level constraints (POST /constraints): "
        "simple option-option exclusions as {option_id1, option_id2} pairs. "
        "Atomically replaces all pairs for a product.\n"
        "- Constraint rules (POST /constraints/rules): conditional logic "
        "with rule_json: "
        '[{"if": {"option_selected": X}, "then": {"forbid_options": [Y, Z]}}].\n\n'
        "## THE #1 RULE\n"
        "NEVER build 'base product + add-ons' where the base configuration is "
        "implicit. Every configurable feature MUST have an explicit group with "
        "ALL variants as separate options — including the 'standard' variant.\n\n"
        "WRONG: Product has 17\" wheels as standard. Option: '19 inch' (price: 500). "
        '→ No usage_subclause can include 17" wheel parts in the BOM.\n'
        "CORRECT: Group 'Wheels' (is_multi: false):\n"
        "  Option '17 inch' (recommended: true, price: 0)\n"
        "  Option '19 inch' (recommended: false, price: 500)\n"
        "BOM items:\n"
        '  child_part: "17-inch wheel assembly", '
        "usage_subclauses: [{option_id: <17_inch_opt>, factor: 1.0}]\n"
        '  child_part: "19-inch wheel assembly", '
        "usage_subclauses: [{option_id: <19_inch_opt>, factor: 1.0}]\n"
        "→ Each option's BOM line is only active when that option is selected.\n\n"
        f"## Configuration Rules\n{rules_text}\n\n"
        f"## Anti-Patterns to Detect\n{anti_text}"
    )


def system_prompt_analyse_pricelist(*, language: str = "de") -> str:
    """System prompt for pricelist analysis with embedded consulting rules."""
    lang_name = "German" if language == "de" else language
    return (
        f"{system_prompt_base()}\n\n"
        "## Your Task\n"
        f"Analyse the following pricelist or technical document (respond in {lang_name}). "
        "Identify:\n"
        "1. **Products**: name, description, base price\n"
        "2. **Configurable features**: what can be configured, variants, pricing\n"
        "3. **Anti-patterns**: instances of the anti-patterns listed above\n"
        "4. **Recommendations**: how to restructure for correct BOM-aware configuration\n\n"
        "Return a JSON object with keys: products, features, anti_patterns, recommendations."
    )


def system_prompt_suggest_configuration(
    *, language: str = "de", existing_groups: list[dict] | None = None
) -> str:
    """System prompt for configuration suggestion with BOM-aware rules."""
    lang_name = "German" if language == "de" else language

    reuse_section = ""
    if existing_groups:
        groups_text = "\n".join(
            f"  - Group '{g.get('name', '?')}' (id={g.get('id', '?')}): "
            f"options: {[o.get('name', '?') for o in g.get('options', [])]}"
            for g in existing_groups[:50]  # limit to avoid token overflow
        )
        reuse_section = (
            "\n\n## Existing Groups & Options (MUST check for reuse)\n"
            f"{groups_text}\n\n"
            "IMPORTANT: Before suggesting a new group, check if an existing "
            "group with the same or very similar name already exists above. "
            "If it does:\n"
            "- Set reuse_existing=true and provide the existing_group_id\n"
            "- If prices differ for this area, use option area-config or "
            "price-overrides instead of creating a duplicate group\n"
            "- Only create a new group if the name and options genuinely differ"
        )

    return (
        f"{system_prompt_base()}{reuse_section}\n\n"
        "## Your Task\n"
        "Generate an explicit, BOM-aware configuration structure for the Rattle "
        f"product configurator (respond in {lang_name}).\n\n"
        "For each product found in the document, produce:\n"
        "1. **groups**: each with name, description, is_multi, and options "
        "(each option: name, recommended, price, description). "
        "If reusing existing group: set reuse_existing=true, existing_group_id, "
        "and note price_overrides for area-specific pricing.\n"
        "2. **bom_rules**: for options that affect physical parts, describe "
        "the BOM item with child_part_name and "
        "usage_subclauses [{option_id, factor}] format.\n"
        "3. **forbidden_pairs**: simple option-option exclusions as "
        "[{option_name_1, option_name_2, reason}] — these map directly to "
        "POST /constraints with {option_id1, option_id2} pairs.\n"
        "4. **constraint_rules**: conditional rules as "
        '[{"description", "rule_json": [{"if": {"option_selected": name}, '
        '"then": {"forbid_options": [names]}}]}].\n\n'
        "Return JSON with key 'products' (array of objects with keys: "
        "name, groups, bom_rules, forbidden_pairs, constraint_rules)."
    )


# ---------------------------------------------------------------------------
# Heuristic anti-pattern detection (no AI required)
# ---------------------------------------------------------------------------


def detect_anti_patterns(data: list[dict]) -> list[dict]:
    """Scan parsed pricelist rows for common anti-patterns.

    Works on structured data (list of dicts from Excel parsing).
    Checks cell values against indicator keywords for each anti-pattern.

    Args:
        data: Row dicts from :func:`source.read_excel`.

    Returns:
        List of detected issues, each with ``pattern_id``, ``pattern_name``,
        ``row_index``, ``column``, ``value``, and ``correction``.
    """
    detections: list[dict] = []

    for row_idx, row in enumerate(data):
        for col, value in row.items():
            if value is None:
                continue
            cell_str = str(value).strip()
            if not cell_str:
                continue
            cell_lower = cell_str.lower()

            for ap in ANTI_PATTERNS:
                for indicator in ap["indicators"]:
                    if indicator.lower() in cell_lower:
                        detections.append(
                            {
                                "pattern_id": ap["id"],
                                "pattern_name": ap["name"],
                                "row_index": row_idx,
                                "column": col,
                                "value": cell_str[:200],
                                "indicator": indicator,
                                "correction": ap["correction"],
                            }
                        )
                        break  # one match per anti-pattern per cell

    return detections


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------


def as_markdown() -> str:
    """Render all knowledge as Markdown for embedding in CLAUDE.md or docs."""
    lines: list[str] = []

    # Header
    lines.append("## Configurator Consulting Knowledge")
    lines.append("")
    lines.append(
        "This codebase embeds deep consulting expertise about building correct "
        "product configurators. The knowledge is codified in "
        "`rattle_api/knowledge.py` and automatically applied by the AI "
        "analysis tasks (`ai-analyse-pricelist`, `ai-suggest-config`)."
    )
    lines.append("")

    # The #1 Rule
    lines.append("### The #1 Rule: Explicit Options for ALL Variants")
    lines.append("")
    lines.append(
        "**NEVER build 'base product + add-ons' where the base configuration "
        "is implicit.** Every configurable feature MUST have an explicit group "
        "with ALL variants as separate options — including the 'standard' variant."
    )
    lines.append("")
    lines.append(
        "**Why?** Without an explicit option for the standard variant, "
        "no BOM item can carry a `usage_subclause` referencing it. "
        "The configurator can only activate BOM lines linked to selected "
        "options — it cannot remove an implicit baseline."
    )
    lines.append("")
    lines.append("**Example — WRONG (classic pricelist):**")
    lines.append(
        'Product comes with 17" wheels as standard. '
        "Option '19 inch' (price: 500). "
        "Problem: no BOM item can have a usage_subclause for the "
        '17" wheels because no option represents them.'
    )
    lines.append("")
    lines.append("**Example — CORRECT (BOM-aware):**")
    lines.append(
        "Group 'Wheels' (is_multi: false): "
        "Option '17 inch' (recommended: true, price: 0), "
        "Option '19 inch' (recommended: false, price: 500). "
        "BOM: child_part '17-inch wheel assy' with "
        "usage_subclauses: [{option_id: <17_inch>, factor: 1.0}]; "
        "child_part '19-inch wheel assy' with "
        "usage_subclauses: [{option_id: <19_inch>, factor: 1.0}]."
    )
    lines.append("")

    # Data model
    lines.append("### Rattle Data Model")
    lines.append("")
    lines.append("```")
    lines.append("Product")
    lines.append("  ├── Areas (configurable sections, assigned via /products/{id}/areas)")
    lines.append("  │   └── Groups (linked to areas, is_multi: single/multi-select)")
    lines.append("  │       └── Options (name, price, key, recommended)")
    lines.append("  ├── Parts (physical components)")
    lines.append("  │   └── BOM items (parent→child, quantity, usage_subclauses)")
    lines.append("  └── Constraints (/constraints + /constraints/rules)")
    lines.append("```")
    lines.append("")
    lines.append(
        "- **usage_subclauses** on BOM items: "
        '`[{"option_id": 301, "factor": 1.0}]` — when option 301 is '
        "selected, this BOM line is active with quantity × factor."
    )
    lines.append(
        "- **Option area-config**: per-area overrides for option price, "
        "description, recommended flag — avoids duplicating groups."
    )
    lines.append(
        "- **Constraints**: pair-level forbidden combinations + conditional "
        'rules with `rule_json: [{"if": {"option_selected": X}, '
        '"then": {"forbid_options": [Y, Z]}}]`.'
    )
    lines.append("")

    # Configuration rules
    lines.append("### Configuration Rules")
    lines.append("")
    for r in CONFIGURATION_RULES:
        lines.append(f"- **{r['id']}**: {r['rule']}")
    lines.append("")

    # Anti-patterns
    lines.append("### Anti-Patterns to Detect")
    lines.append("")
    for ap in ANTI_PATTERNS:
        lines.append(f"- **{ap['name']}** (`{ap['id']}`): {ap['description']}")
        lines.append(f"  - Indicators: {', '.join(ap['indicators'])}")
        lines.append(f"  - Correction: {ap['correction']}")
    lines.append("")

    # New commands
    lines.append("### AI Commands for Configuration")
    lines.append("")
    lines.append(
        "- `rattle <tenant> ai-analyse-pricelist <file>` — "
        "Analyse a pricelist for configurator anti-patterns"
    )
    lines.append(
        "- `rattle <tenant> ai-suggest-config <file>` — "
        "Generate BOM-aware configuration recommendations "
        "(reuses existing groups, suggests forbidden combinations)"
    )
    lines.append("")

    return "\n".join(lines)
