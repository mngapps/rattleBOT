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
            "(e.g. a machine, furniture piece, vehicle)."
        ),
        "key_fields": ["id", "name", "description", "price"],
        "api_endpoint": "/products",
        "relationships": ["areas", "groups", "parts"],
    },
    "area": {
        "description": (
            "Rich-text content section of a product. Contains structured "
            "blocks (paragraphs, headers, images, tables, lists). "
            "Multiple areas per product (e.g. different sections or languages)."
        ),
        "key_fields": ["id", "description", "content", "language"],
        "api_endpoint": "/areas",
        "relationships": ["product", "part_placements"],
    },
    "group": {
        "description": (
            "Configuration group collecting related options "
            "(e.g. 'Wheels', 'Frässpindel', 'Auftragsverwaltung IoT'). "
            "Each group represents ONE configurable feature."
        ),
        "key_fields": ["id", "name", "description"],
        "api_endpoint": "/groups",
        "relationships": ["product", "options"],
    },
    "option": {
        "description": (
            "A single selectable choice within a group "
            "(e.g. '17 inch wheels', '19 inch wheels', 'ohne', 'mit'). "
            "Every variant — including the default/standard — must be an "
            "explicit option."
        ),
        "key_fields": ["id", "label", "is_default", "price_modifier", "image"],
        "api_endpoint": "/options",
        "relationships": ["group", "usage_subclauses"],
    },
    "part": {
        "description": (
            "A physical BOM item — a component, sub-assembly, or finished "
            "good that can appear in a product's bill of materials."
        ),
        "key_fields": ["id", "name", "sku", "price", "unit"],
        "api_endpoint": "/parts",
        "relationships": ["part_placements"],
    },
    "part_placement": {
        "description": (
            "Connects a part to an area, specifying quantity and placement. "
            "This is the bridge between the physical BOM and the product "
            "structure."
        ),
        "key_fields": ["id", "part_id", "area_id", "quantity"],
        "api_endpoint": "/part-placements",
        "relationships": ["part", "area", "usage_subclauses"],
    },
    "usage_subclause": {
        "description": (
            "Conditional BOM rule: when a specific option is selected, "
            "the linked part placement becomes active in the final BOM. "
            "This is the core mechanism that makes configuration drive "
            "the bill of materials."
        ),
        "key_fields": ["id", "part_placement_id", "option_id", "condition"],
        "api_endpoint": "/usage-subclauses",
        "relationships": ["part_placement", "option"],
    },
    "area_override": {
        "description": (
            "Per-product override for a shared group or option. Allows "
            "reusing the same group/option across products while adjusting "
            "price, label, or availability for a specific product/area. "
            "Avoids duplicating groups and options."
        ),
        "key_fields": ["id", "area_id", "group_id", "option_id", "price_modifier"],
        "api_endpoint": "/area-overrides",
        "relationships": ["area", "group", "option"],
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
            "creating duplicates. Use areaOverrides for product-specific "
            "price or label differences."
        ),
        "rationale": (
            "Duplicate groups with identical names fragment the "
            "configuration catalogue and make maintenance harder. "
            "areaOverrides let one group/option serve many products "
            "with per-product pricing."
        ),
        "applies_to": ["groups", "options", "area_overrides"],
    },
    {
        "id": "forbidden-combinations",
        "rule": (
            "Identify and define rules for invalid option combinations "
            "across groups (e.g. machine variant X is incompatible with "
            "accessory Y)."
        ),
        "rationale": (
            "Without forbidden-combination rules, users can select "
            "impossible configurations that cannot be manufactured or "
            "delivered."
        ),
        "applies_to": ["groups", "options", "rules"],
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
            "Option: '19 inch wheels (+500€)'. "
            "Problem: no way to create a usage_subclause that removes "
            '17" wheels from BOM when 19" is selected.'
        ),
        "example_correct": (
            "Group 'Wheels': Option '17 inch wheels' (default), "
            "Option '19 inch wheels' (+500€). "
            "usage_subclause: if '17 inch' → add 17\" parts; "
            "if '19 inch' → add 19\" parts."
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
            "Group 'Frässpindel': Option 'ISO 30 Standard' (default), "
            "Option 'HSK-63F ohne Encoder' (+1.800€), "
            "Option 'HSK-63F mit Encoder' (+2.500€)."
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
        "Product → Areas (rich text), Groups → Options, "
        "Parts → Part Placements → Usage Subclauses.\n"
        "- Groups collect related Options (e.g. 'Wheels' → '17 inch', '19 inch')\n"
        "- Usage Subclauses link selected Options to Part Placements in the BOM\n"
        "- Area Overrides allow reusing groups/options across products with "
        "per-product price differences\n\n"
        "## THE #1 RULE\n"
        "NEVER build 'base product + add-ons' where the base configuration is "
        "implicit. Every configurable feature MUST have an explicit group with "
        "ALL variants as separate options — including the 'standard' variant.\n\n"
        "WRONG: Product has 17\" wheels standard. Option: '19 inch (+500€)'. "
        '→ No usage_subclause can add 17" parts to BOM.\n'
        "CORRECT: Group 'Wheels': '17 inch' (default), '19 inch' (+500€). "
        "→ Each option has a usage_subclause linking to its parts.\n\n"
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
            f"options: {[o.get('label', '?') for o in g.get('options', [])]}"
            for g in existing_groups[:50]  # limit to avoid token overflow
        )
        reuse_section = (
            "\n\n## Existing Groups & Options (MUST check for reuse)\n"
            f"{groups_text}\n\n"
            "IMPORTANT: Before suggesting a new group, check if an existing "
            "group with the same or very similar name already exists above. "
            "If it does:\n"
            "- Set reuse_existing=true and provide the existing_group_id\n"
            "- If prices differ for this product, use area_overrides instead "
            "of creating a duplicate group\n"
            "- Only create a new group if the name and options genuinely differ"
        )

    return (
        f"{system_prompt_base()}{reuse_section}\n\n"
        "## Your Task\n"
        "Generate an explicit, BOM-aware configuration structure for the Rattle "
        f"product configurator (respond in {lang_name}).\n\n"
        "For each product found in the document, produce:\n"
        "1. **groups**: each with name, description, and options "
        "(each option: label, is_default, price_modifier, description). "
        "If reusing existing group: set reuse_existing=true, existing_group_id, "
        "and area_overrides for price differences.\n"
        "2. **usage_subclauses**: for each option, a rule describing which "
        "parts to include/exclude in the BOM (description, condition, effect).\n"
        "3. **forbidden_combinations**: rules for invalid option combinations "
        "across groups (description, rule, reason).\n\n"
        "Return JSON with key 'products' (array of objects with keys: "
        "name, groups, usage_subclauses, forbidden_combinations)."
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
        "it is impossible to write a `usage_subclause` that adds the standard "
        "parts to the BOM. The configurator cannot remove an implicit baseline — "
        "it can only activate parts linked to selected options."
    )
    lines.append("")
    lines.append("**Example — WRONG (classic pricelist):**")
    lines.append(
        'Product comes with 17" wheels as standard. '
        "Option: '19 inch wheels (+500€)'. "
        "Problem: no way to create a usage_subclause that removes "
        '17" wheels from BOM when 19" is selected.'
    )
    lines.append("")
    lines.append("**Example — CORRECT (BOM-aware):**")
    lines.append(
        "Group 'Wheels': Option '17 inch wheels' (default), "
        "Option '19 inch wheels' (+500€). "
        "usage_subclause: if '17 inch' selected → add 17\" parts; "
        "if '19 inch' selected → add 19\" parts."
    )
    lines.append("")

    # Data model
    lines.append("### Rattle Data Model")
    lines.append("")
    lines.append("```")
    lines.append("Product")
    lines.append("  ├── Areas (rich text content sections)")
    lines.append("  ├── Groups (configuration groups, e.g. 'Wheels', 'Frässpindel')")
    lines.append("  │   └── Options (choices: '17 inch', '19 inch', 'ohne', 'mit')")
    lines.append("  ├── Parts (BOM items — physical components)")
    lines.append("  └── Part Placements (connect parts to areas)")
    lines.append("      └── Usage Subclauses (conditional BOM rules based on selected options)")
    lines.append("```")
    lines.append("")
    lines.append(
        "- **Area Overrides**: allow reusing groups/options across products "
        "with per-product price differences (avoids duplicating groups)."
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
