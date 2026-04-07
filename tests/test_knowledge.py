"""Tests for rattle_api.knowledge — configurator consulting knowledge module."""

from rattle_api.knowledge import (
    ANTI_PATTERNS,
    CONFIGURATION_RULES,
    RATTLE_DATA_MODEL,
    as_markdown,
    detect_anti_patterns,
    system_prompt_analyse_pricelist,
    system_prompt_base,
    system_prompt_suggest_configuration,
)

# ---------------------------------------------------------------------------
# Data structure integrity
# ---------------------------------------------------------------------------


class TestRattleDataModel:
    """RATTLE_DATA_MODEL structure."""

    REQUIRED_ENTITIES = [
        "product",
        "area",
        "group",
        "option",
        "part",
        "part_placement",
        "usage_subclause",
        "area_override",
    ]

    def test_has_all_entity_types(self):
        for entity in self.REQUIRED_ENTITIES:
            assert entity in RATTLE_DATA_MODEL, f"Missing entity: {entity}"

    def test_entities_have_required_fields(self):
        for name, entity in RATTLE_DATA_MODEL.items():
            assert "description" in entity, f"{name} missing description"
            assert "key_fields" in entity, f"{name} missing key_fields"
            assert "api_endpoint" in entity, f"{name} missing api_endpoint"
            assert "relationships" in entity, f"{name} missing relationships"

    def test_entities_have_non_empty_descriptions(self):
        for name, entity in RATTLE_DATA_MODEL.items():
            assert len(entity["description"]) > 10, f"{name} description too short"


class TestConfigurationRules:
    """CONFIGURATION_RULES data structure integrity."""

    REQUIRED_KEYS = {"id", "rule", "rationale", "applies_to"}

    def test_all_entries_have_required_keys(self):
        for rule in CONFIGURATION_RULES:
            missing = self.REQUIRED_KEYS - set(rule.keys())
            assert not missing, f"Rule {rule.get('id', '?')} missing keys: {missing}"

    def test_ids_are_unique(self):
        ids = [r["id"] for r in CONFIGURATION_RULES]
        assert len(ids) == len(set(ids)), f"Duplicate rule IDs: {ids}"

    def test_has_the_number_one_rule(self):
        ids = [r["id"] for r in CONFIGURATION_RULES]
        assert "explicit-options-for-all-variants" in ids

    def test_has_reuse_rule(self):
        ids = [r["id"] for r in CONFIGURATION_RULES]
        assert "reuse-over-duplicate" in ids

    def test_has_forbidden_combinations_rule(self):
        ids = [r["id"] for r in CONFIGURATION_RULES]
        assert "forbidden-combinations" in ids


class TestAntiPatterns:
    """ANTI_PATTERNS data structure integrity."""

    REQUIRED_KEYS = {
        "id",
        "name",
        "description",
        "indicators",
        "correction",
        "example_wrong",
        "example_correct",
    }

    def test_all_entries_have_required_keys(self):
        for ap in ANTI_PATTERNS:
            missing = self.REQUIRED_KEYS - set(ap.keys())
            assert not missing, f"Pattern {ap.get('id', '?')} missing keys: {missing}"

    def test_ids_are_unique(self):
        ids = [ap["id"] for ap in ANTI_PATTERNS]
        assert len(ids) == len(set(ids)), f"Duplicate pattern IDs: {ids}"

    def test_indicators_are_non_empty(self):
        for ap in ANTI_PATTERNS:
            assert len(ap["indicators"]) > 0, f"Pattern {ap['id']} has no indicators"

    def test_has_implicit_base_pattern(self):
        ids = [ap["id"] for ap in ANTI_PATTERNS]
        assert "implicit-base-config" in ids

    def test_has_addon_only_pattern(self):
        ids = [ap["id"] for ap in ANTI_PATTERNS]
        assert "addon-only-options" in ids


# ---------------------------------------------------------------------------
# System prompt builders
# ---------------------------------------------------------------------------


class TestSystemPromptBase:
    """system_prompt_base() — core consulting rules fragment."""

    def test_contains_the_number_one_rule(self):
        prompt = system_prompt_base()
        assert "NEVER build" in prompt
        assert "base product" in prompt
        assert "implicit" in prompt

    def test_contains_data_model(self):
        prompt = system_prompt_base()
        assert "Usage Subclauses" in prompt
        assert "Groups" in prompt
        assert "Options" in prompt

    def test_contains_car_example(self):
        prompt = system_prompt_base()
        assert "17" in prompt or "wheels" in prompt.lower()

    def test_contains_all_rule_ids(self):
        prompt = system_prompt_base()
        for rule in CONFIGURATION_RULES:
            assert rule["id"] in prompt, f"Rule {rule['id']} missing from base prompt"

    def test_contains_anti_pattern_names(self):
        prompt = system_prompt_base()
        for ap in ANTI_PATTERNS:
            assert ap["name"] in prompt, f"Anti-pattern {ap['name']} missing from base prompt"


class TestSystemPromptAnalysePricelist:
    """system_prompt_analyse_pricelist() — pricelist analysis prompt."""

    def test_contains_base_rules(self):
        prompt = system_prompt_analyse_pricelist()
        assert "NEVER build" in prompt

    def test_default_language_german(self):
        prompt = system_prompt_analyse_pricelist()
        assert "German" in prompt

    def test_custom_language(self):
        prompt = system_prompt_analyse_pricelist(language="en")
        assert "en" in prompt

    def test_requests_json_output(self):
        prompt = system_prompt_analyse_pricelist()
        assert "JSON" in prompt

    def test_requests_anti_pattern_detection(self):
        prompt = system_prompt_analyse_pricelist()
        assert "anti_patterns" in prompt.lower() or "Anti-patterns" in prompt


class TestSystemPromptSuggestConfiguration:
    """system_prompt_suggest_configuration() — configuration suggestion prompt."""

    def test_contains_bom_rules(self):
        prompt = system_prompt_suggest_configuration()
        assert "BOM" in prompt or "usage_subclause" in prompt

    def test_contains_forbidden_combinations(self):
        prompt = system_prompt_suggest_configuration()
        assert "forbidden" in prompt.lower()

    def test_default_language_german(self):
        prompt = system_prompt_suggest_configuration()
        assert "German" in prompt

    def test_without_existing_groups(self):
        prompt = system_prompt_suggest_configuration()
        assert "Existing Groups" not in prompt

    def test_with_existing_groups(self):
        groups = [
            {"id": 100, "name": "Frässpindel", "options": [{"label": "ISO 30"}]},
        ]
        prompt = system_prompt_suggest_configuration(existing_groups=groups)
        assert "Frässpindel" in prompt
        assert "reuse_existing" in prompt
        assert "area_overrides" in prompt

    def test_requests_json_output(self):
        prompt = system_prompt_suggest_configuration()
        assert "JSON" in prompt


# ---------------------------------------------------------------------------
# Heuristic anti-pattern detection
# ---------------------------------------------------------------------------


class TestDetectAntiPatterns:
    """detect_anti_patterns() — heuristic scan of Excel data."""

    def test_detects_aufpreis_pattern(self):
        data = [{"Feature": "Aufpreis Frässpindel HSK-63F", "Price": 2500}]
        results = detect_anti_patterns(data)
        assert len(results) >= 1
        pattern_ids = {r["pattern_id"] for r in results}
        assert "addon-only-options" in pattern_ids

    def test_detects_standard_implicit(self):
        data = [{"Description": "Serienausstattung: 17 Zoll Räder"}]
        results = detect_anti_patterns(data)
        pattern_ids = {r["pattern_id"] for r in results}
        assert "implicit-base-config" in pattern_ids

    def test_detects_ohne_mit(self):
        data = [{"Option": "Teleservice: ohne / mit"}]
        results = detect_anti_patterns(data)
        pattern_ids = {r["pattern_id"] for r in results}
        assert "binary-ohne-mit-no-group" in pattern_ids

    def test_clean_data_returns_empty(self):
        data = [
            {"Name": "Drill X100", "Price": 500},
            {"Name": "Saw Z3", "Price": 200},
        ]
        results = detect_anti_patterns(data)
        assert results == []

    def test_returns_row_references(self):
        data = [
            {"Feature": "Normal feature"},
            {"Feature": "Aufpreis: extra widget"},
        ]
        results = detect_anti_patterns(data)
        assert any(r["row_index"] == 1 for r in results)

    def test_returns_column_references(self):
        data = [{"Price": "Aufpreis 100€"}]
        results = detect_anti_patterns(data)
        assert results[0]["column"] == "Price"

    def test_handles_none_values(self):
        data = [{"A": None, "B": "text", "C": None}]
        results = detect_anti_patterns(data)
        assert results == []

    def test_handles_empty_data(self):
        assert detect_anti_patterns([]) == []

    def test_truncates_long_values(self):
        data = [{"Feature": "Aufpreis " + "x" * 500}]
        results = detect_anti_patterns(data)
        assert len(results[0]["value"]) <= 200


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------


class TestAsMarkdown:
    """as_markdown() — knowledge export as Markdown."""

    def test_contains_header(self):
        md = as_markdown()
        assert "## Configurator Consulting Knowledge" in md

    def test_contains_the_number_one_rule(self):
        md = as_markdown()
        assert "NEVER build" in md
        assert "base product" in md

    def test_contains_all_configuration_rules(self):
        md = as_markdown()
        for rule in CONFIGURATION_RULES:
            assert rule["id"] in md, f"Rule {rule['id']} missing from markdown"

    def test_contains_all_anti_patterns(self):
        md = as_markdown()
        for ap in ANTI_PATTERNS:
            assert ap["name"] in md, f"Anti-pattern {ap['name']} missing from markdown"

    def test_contains_data_model(self):
        md = as_markdown()
        assert "Product" in md
        assert "Groups" in md
        assert "Options" in md
        assert "Usage Subclauses" in md

    def test_contains_cli_commands(self):
        md = as_markdown()
        assert "ai-analyse-pricelist" in md
        assert "ai-suggest-config" in md

    def test_is_nonempty_string(self):
        md = as_markdown()
        assert isinstance(md, str)
        assert len(md) > 500
