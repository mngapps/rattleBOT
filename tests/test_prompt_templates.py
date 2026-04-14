"""Tests for rattle_api.prompt_templates — the prompt template library."""

from pathlib import Path

import pytest

from rattle_api.prompt_templates import (
    PIPELINE_STAGE_ORDER,
    PROMPT_TEMPLATES,
    STAGE_FRAMING,
    PromptTemplate,
    get_template,
    list_templates,
    load_template_override,
)

VALID_STAGES = {
    "discovery",
    "modeling",
    "structuring",
    "enrichment",
    "documents",
    "validation",
    "pipeline",
}


MINIMAL_RENDER_KWARGS: dict = {
    "source_content": "some source text",
    "live_state": {"products": [], "areas": [], "groups": [], "parts": []},
    "features": [],
    "heuristic_findings": [],
    "tenant_profile": None,
    "tenant": None,
    "language": "de",
}


# ---------------------------------------------------------------------------
# Registry integrity
# ---------------------------------------------------------------------------


class TestRegistryIntegrity:
    """PROMPT_TEMPLATES dict and PromptTemplate dataclass invariants."""

    def test_registry_not_empty(self):
        assert len(PROMPT_TEMPLATES) >= 10

    def test_keys_match_template_ids(self):
        for key, tpl in PROMPT_TEMPLATES.items():
            assert key == tpl.id, f"registry key {key!r} != template id {tpl.id!r}"

    def test_ids_are_unique(self):
        ids = [t.id for t in PROMPT_TEMPLATES.values()]
        assert len(ids) == len(set(ids))

    def test_all_stages_are_valid(self):
        for tpl in PROMPT_TEMPLATES.values():
            assert tpl.stage in VALID_STAGES, f"template {tpl.id!r} has invalid stage {tpl.stage!r}"

    def test_every_template_has_build_function(self):
        for tpl in PROMPT_TEMPLATES.values():
            assert tpl.build is not None
            assert callable(tpl.build)

    def test_every_template_has_non_empty_description(self):
        for tpl in PROMPT_TEMPLATES.values():
            assert tpl.description
            assert len(tpl.description) > 30

    def test_every_template_has_non_empty_title(self):
        for tpl in PROMPT_TEMPLATES.values():
            assert tpl.title

    def test_required_stages_are_registered(self):
        required = {
            "extract-products",
            "discover-features",
            "model-groups-options",
            "link-bom",
            "discover-constraints",
            "plan-areas",
            "guided-selling",
            "build-offer-template",
            "review-configuration",
            "full-configurator",
        }
        assert required <= set(PROMPT_TEMPLATES.keys())

    def test_review_configuration_is_read_only(self):
        assert PROMPT_TEMPLATES["review-configuration"].read_only is True
        assert PROMPT_TEMPLATES["review-configuration"].emits == ()

    def test_full_configurator_emits_all_op_types(self):
        emits = set(PROMPT_TEMPLATES["full-configurator"].emits)
        # must at least cover the union of its sub-stages
        assert "ensure_product" in emits
        assert "ensure_group" in emits
        assert "ensure_option" in emits
        assert "ensure_bom_item" in emits
        assert "ensure_constraint_pair" in emits


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


class TestTemplateRendering:
    """Every template must render with minimal inputs."""

    @pytest.mark.parametrize("template_id", list(PROMPT_TEMPLATES.keys()))
    def test_template_renders_without_error(self, template_id):
        tpl = PROMPT_TEMPLATES[template_id]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        assert isinstance(rendered, str)
        assert len(rendered) > 500

    @pytest.mark.parametrize("template_id", list(PROMPT_TEMPLATES.keys()))
    def test_rendered_contains_system_prompt_base(self, template_id):
        """Composition check — every template must include the consulting base."""
        tpl = PROMPT_TEMPLATES[template_id]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        assert "configurator consultant" in rendered
        assert "Rattle Data Model" in rendered
        assert "THE #1 RULE" in rendered

    # build-offer-template is a thin wrapper around the existing
    # knowledge.system_prompt_build_offer_template builder and therefore
    # does not embed the new STAGE_FRAMING constant; we cover it separately.
    FRAMING_CHECKED = [tid for tid in PROMPT_TEMPLATES if tid != "build-offer-template"]

    @pytest.mark.parametrize("template_id", FRAMING_CHECKED)
    def test_rendered_contains_stage_framing(self, template_id):
        tpl = PROMPT_TEMPLATES[template_id]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        # Each stage's framing snippet should appear in its own rendering.
        if template_id in STAGE_FRAMING:
            assert STAGE_FRAMING[template_id] in rendered

    def test_build_offer_template_wraps_existing_builder(self):
        """build-offer-template delegates to knowledge.system_prompt_build_offer_template."""
        tpl = PROMPT_TEMPLATES["build-offer-template"]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        # The legacy builder's distinctive task statement must appear.
        assert "Propose a document template" in rendered
        assert "dynamic:document_configuration" in rendered

    def test_full_configurator_embeds_sub_stage_framings(self):
        """Wrapper stays in lockstep with the 9 stage templates."""
        tpl = PROMPT_TEMPLATES["full-configurator"]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        for stage_id in (
            "extract-products",
            "discover-features",
            "model-groups-options",
            "link-bom",
            "discover-constraints",
            "plan-areas",
            "guided-selling",
            "build-offer-template",
        ):
            assert STAGE_FRAMING[stage_id] in rendered, (
                f"wrapper is missing sub-stage framing: {stage_id}"
            )

    def test_tenant_profile_is_injected(self):
        tpl = PROMPT_TEMPLATES["extract-products"]
        kwargs = dict(MINIMAL_RENDER_KWARGS)
        kwargs["tenant_profile"] = "- **custom-keys**: never"
        rendered = tpl.render(**kwargs)
        assert "Tenant preferences" in rendered
        assert "custom-keys" in rendered

    def test_language_de_appears_in_rendered_prompt(self):
        tpl = PROMPT_TEMPLATES["extract-products"]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        assert "German" in rendered

    def test_language_en_appears_in_rendered_prompt(self):
        tpl = PROMPT_TEMPLATES["extract-products"]
        kwargs = dict(MINIMAL_RENDER_KWARGS)
        kwargs["language"] = "en"
        rendered = tpl.render(**kwargs)
        assert "en" in rendered


# ---------------------------------------------------------------------------
# Live-state formatting
# ---------------------------------------------------------------------------


class TestLiveStateFormatting:
    """Templates that consume live_state should summarise it in the prompt."""

    def test_model_groups_options_lists_existing_groups(self):
        tpl = PROMPT_TEMPLATES["model-groups-options"]
        kwargs = dict(MINIMAL_RENDER_KWARGS)
        kwargs["live_state"] = {
            "products": [],
            "areas": [],
            "groups": [
                {
                    "id": 1,
                    "name": "Wheels",
                    "is_multi": False,
                    "options": [{"name": "17 inch"}, {"name": "19 inch"}],
                }
            ],
            "parts": [],
        }
        rendered = tpl.render(**kwargs)
        assert "Wheels" in rendered
        assert "17 inch" in rendered or "19 inch" in rendered

    def test_empty_live_state_renders_cleanly(self):
        tpl = PROMPT_TEMPLATES["model-groups-options"]
        kwargs = dict(MINIMAL_RENDER_KWARGS)
        kwargs["live_state"] = None
        rendered = tpl.render(**kwargs)
        assert "Current Rattle live state" in rendered

    def test_review_configuration_includes_heuristic_findings(self):
        tpl = PROMPT_TEMPLATES["review-configuration"]
        kwargs = dict(MINIMAL_RENDER_KWARGS)
        kwargs["heuristic_findings"] = [
            {
                "pattern_id": "implicit-base-config",
                "row_index": 3,
                "column": "Feature",
                "value": "Serienausstattung",
            }
        ]
        rendered = tpl.render(**kwargs)
        assert "implicit-base-config" in rendered
        assert "Heuristic anti-pattern findings" in rendered


# ---------------------------------------------------------------------------
# Pipeline ordering
# ---------------------------------------------------------------------------


class TestPipelineOrder:
    """PIPELINE_STAGE_ORDER sequences the 9 stages correctly."""

    def test_pipeline_order_covers_nine_stages(self):
        assert len(PIPELINE_STAGE_ORDER) == 9

    def test_pipeline_order_entries_are_valid_template_ids(self):
        for stage_id in PIPELINE_STAGE_ORDER:
            assert stage_id in PROMPT_TEMPLATES

    def test_extract_is_first(self):
        assert PIPELINE_STAGE_ORDER[0] == "extract-products"

    def test_review_is_last(self):
        assert PIPELINE_STAGE_ORDER[-1] == "review-configuration"

    def test_model_groups_before_bom_and_constraints(self):
        idx_groups = PIPELINE_STAGE_ORDER.index("model-groups-options")
        idx_bom = PIPELINE_STAGE_ORDER.index("link-bom")
        idx_cons = PIPELINE_STAGE_ORDER.index("discover-constraints")
        assert idx_groups < idx_bom
        assert idx_groups < idx_cons


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------


class TestAccessors:
    """list_templates / get_template convenience helpers."""

    def test_list_templates_returns_all_by_default(self):
        items = list_templates()
        assert len(items) == len(PROMPT_TEMPLATES)

    def test_list_templates_filters_by_stage(self):
        items = list_templates(stage="modeling")
        stages = {i["stage"] for i in items}
        assert stages == {"modeling"}
        ids = {i["id"] for i in items}
        assert "model-groups-options" in ids
        assert "link-bom" in ids
        assert "discover-constraints" in ids

    def test_list_templates_contains_required_fields(self):
        item = list_templates()[0]
        for field in ("id", "stage", "title", "description", "emits", "read_only"):
            assert field in item

    def test_get_template_returns_instance(self):
        tpl = get_template("extract-products")
        assert isinstance(tpl, PromptTemplate)
        assert tpl.id == "extract-products"

    def test_get_template_raises_for_unknown_id(self):
        with pytest.raises(KeyError):
            get_template("nonexistent")


# ---------------------------------------------------------------------------
# File-override loader
# ---------------------------------------------------------------------------


class TestOverrideLoader:
    """prompt_templates/<tenant>/<id>.md overrides trump global overrides."""

    def test_returns_none_when_no_override(self, tmp_path):
        assert load_template_override("extract-products", root=tmp_path) is None

    def test_loads_global_override(self, tmp_path):
        (tmp_path / "extract-products.md").write_text(
            "Always also capture SKU if present.", encoding="utf-8"
        )
        result = load_template_override("extract-products", root=tmp_path)
        assert result is not None
        assert "SKU" in result

    def test_tenant_override_wins_over_global(self, tmp_path):
        (tmp_path / "extract-products.md").write_text("global", encoding="utf-8")
        (tmp_path / "acme").mkdir()
        (tmp_path / "acme" / "extract-products.md").write_text(
            "acme-specific guidance", encoding="utf-8"
        )
        result = load_template_override("extract-products", tenant="acme", root=tmp_path)
        assert result == "acme-specific guidance"

    def test_falls_back_to_global_when_tenant_missing(self, tmp_path):
        (tmp_path / "extract-products.md").write_text("global fallback", encoding="utf-8")
        result = load_template_override("extract-products", tenant="unknown-tenant", root=tmp_path)
        assert result == "global fallback"

    def test_override_is_appended_to_rendered_prompt(self, tmp_path, monkeypatch):
        """When a tenant override exists, the rendered prompt includes it."""
        (tmp_path / "extract-products.md").write_text(
            "Remember to extract serial numbers.", encoding="utf-8"
        )
        monkeypatch.setattr("rattle_api.prompt_templates.TEMPLATES_DIR", Path(tmp_path))
        tpl = PROMPT_TEMPLATES["extract-products"]
        rendered = tpl.render(**MINIMAL_RENDER_KWARGS)
        assert "Custom guidance" in rendered
        assert "serial numbers" in rendered
