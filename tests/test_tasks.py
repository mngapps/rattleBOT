"""Tests for rattle_api.tasks — AI-driven tasks with mocked API and providers."""

import importlib
import json
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import FakeAIProvider


@pytest.fixture
def mock_client():
    """Return a mocked RattleClient."""
    client = MagicMock()
    client.list_all.return_value = [
        {"id": "p1", "name": "Drill X100", "price": 50},
        {"id": "p2", "name": "Excavator Z3", "price": 200},
    ]
    client.patch.return_value = {"ok": True}
    client.post.return_value = {"id": "new-1"}
    return client


@pytest.fixture
def patched_client(mock_client, monkeypatch):
    """Patch RattleClient constructor to return our mock."""
    monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
    import rattle_api.config as config

    importlib.reload(config)

    with patch("rattle_api.tasks.RattleClient", return_value=mock_client):
        yield mock_client


# ---------------------------------------------------------------------------
# describe_products
# ---------------------------------------------------------------------------


class TestDescribeProducts:
    """AI-generated product descriptions, pushed back to Rattle API."""

    def test_generates_descriptions(self, patched_client):
        from rattle_api.tasks import describe_products

        fake = FakeAIProvider(text_response="A professional drilling machine.")
        results = describe_products("testco", provider=fake, limit=2)

        assert len(results) == 2
        assert results[0]["description"] == "A professional drilling machine."
        assert results[0]["id"] == "p1"
        assert results[0]["name"] == "Drill X100"

    def test_patches_back_to_api(self, patched_client):
        from rattle_api.tasks import describe_products

        fake = FakeAIProvider(text_response="desc")
        describe_products("testco", provider=fake, limit=2)

        assert patched_client.patch.call_count == 2
        patched_client.patch.assert_any_call("products/p1", json={"description": "desc"})

    def test_respects_limit(self, patched_client):
        from rattle_api.tasks import describe_products

        fake = FakeAIProvider(text_response="desc")
        results = describe_products("testco", provider=fake, limit=1)
        assert len(results) == 1

    def test_handles_ai_failure_gracefully(self, patched_client):
        from rattle_api.tasks import describe_products

        class FailProvider(FakeAIProvider):
            def complete(self, *args, **kwargs):
                raise RuntimeError("AI is down")

        results = describe_products("testco", provider=FailProvider(), limit=2)
        assert len(results) == 2
        assert "error" in results[0]
        assert "AI is down" in results[0]["error"]

    def test_language_passed_to_system_prompt(self, patched_client):
        from rattle_api.tasks import describe_products

        fake = FakeAIProvider(text_response="Beschreibung")
        describe_products("testco", provider=fake, limit=1, language="de")
        assert fake.calls[0]["system"] is not None
        assert "German" in fake.calls[0]["system"]

    def test_english_language(self, patched_client):
        from rattle_api.tasks import describe_products

        fake = FakeAIProvider(text_response="Description")
        describe_products("testco", provider=fake, limit=1, language="en")
        assert "en" in fake.calls[0]["system"]

    def test_idempotent_same_result(self, patched_client):
        """Running describe twice with same data produces same results."""
        from rattle_api.tasks import describe_products

        fake = FakeAIProvider(text_response="desc")
        r1 = describe_products("testco", provider=fake, limit=2)
        r2 = describe_products("testco", provider=fake, limit=2)
        assert r1 == r2


# ---------------------------------------------------------------------------
# classify_products
# ---------------------------------------------------------------------------


class TestClassifyProducts:
    """AI-generated category tags for products."""

    def test_returns_tags(self, patched_client):
        from rattle_api.tasks import classify_products

        fake = FakeAIProvider(json_response=["Power Tools", "Drilling"])
        results = classify_products("testco", provider=fake, limit=2)

        assert len(results) == 2
        assert results[0]["tags"] == ["Power Tools", "Drilling"]

    def test_handles_ai_failure(self, patched_client):
        from rattle_api.tasks import classify_products

        class FailProvider(FakeAIProvider):
            def complete_json(self, *args, **kwargs):
                raise json.JSONDecodeError("bad", "", 0)

        results = classify_products("testco", provider=FailProvider(), limit=1)
        assert "error" in results[0]

    def test_respects_limit(self, patched_client):
        from rattle_api.tasks import classify_products

        fake = FakeAIProvider(json_response=["tag"])
        results = classify_products("testco", provider=fake, limit=1)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# transform_interchange
# ---------------------------------------------------------------------------


class TestTransformInterchange:
    """Format conversion with optional push to Rattle API."""

    def test_transforms_data(self, patched_client, tmp_path):
        from rattle_api.tasks import transform_interchange

        source = [{"artikel_nr": "001", "bezeichnung": "Bohrer"}]
        data_file = tmp_path / "input.json"
        data_file.write_text(json.dumps(source))

        fake = FakeAIProvider(json_response=[{"id": "001", "name": "Drill"}])
        results = transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake
        )

        assert len(results) == 1
        assert results[0]["name"] == "Drill"

    def test_single_object_wrapped_in_list(self, patched_client, tmp_path):
        """If input JSON is a single object (not list), it should be wrapped."""
        from rattle_api.tasks import transform_interchange

        data_file = tmp_path / "single.json"
        data_file.write_text(json.dumps({"id": "001"}))

        fake = FakeAIProvider(json_response=[{"name": "A"}])
        results = transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake
        )
        assert isinstance(results, list)

    def test_push_posts_to_api(self, patched_client, tmp_path):
        from rattle_api.tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        fake = FakeAIProvider(json_response=[{"name": "A"}, {"name": "B"}])
        transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake, push=True
        )

        assert patched_client.post.call_count == 2

    def test_no_push_by_default(self, patched_client, tmp_path):
        from rattle_api.tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        fake = FakeAIProvider(json_response=[{"name": "A"}])
        transform_interchange("testco", "datanorm", "rattle", str(data_file), provider=fake)

        patched_client.post.assert_not_called()

    def test_push_failure_does_not_crash(self, patched_client, tmp_path):
        from rattle_api.tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        patched_client.post.side_effect = RuntimeError("API down")
        fake = FakeAIProvider(json_response=[{"name": "A"}])
        # Should not raise
        results = transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake, push=True
        )
        assert len(results) == 1

    def test_file_not_found_raises(self, patched_client):
        from rattle_api.tasks import transform_interchange

        fake = FakeAIProvider(json_response=[])
        with pytest.raises(FileNotFoundError):
            transform_interchange(
                "testco", "datanorm", "rattle", "/no/such/file.json", provider=fake
            )

    def test_idempotent_transform(self, patched_client, tmp_path):
        """Same input produces same output."""
        from rattle_api.tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        fake = FakeAIProvider(json_response=[{"name": "Converted"}])
        r1 = transform_interchange("testco", "datanorm", "rattle", str(data_file), provider=fake)
        r2 = transform_interchange("testco", "datanorm", "rattle", str(data_file), provider=fake)
        assert r1 == r2


# ---------------------------------------------------------------------------
# analyse_data
# ---------------------------------------------------------------------------


class TestAnalyseData:
    """Open-ended AI analysis of product data."""

    def test_returns_analysis_text(self, patched_client):
        from rattle_api.tasks import analyse_data

        fake = FakeAIProvider(text_response="Your data has 2 products with good coverage.")
        result = analyse_data("testco", provider=fake)
        assert "2 products" in result

    def test_custom_question(self, patched_client):
        from rattle_api.tasks import analyse_data

        fake = FakeAIProvider(text_response="answer")
        analyse_data("testco", provider=fake, question="How many drills?")
        assert "How many drills?" in fake.calls[0]["prompt"]

    def test_default_question_is_quality_audit(self, patched_client):
        from rattle_api.tasks import analyse_data

        fake = FakeAIProvider(text_response="audit")
        analyse_data("testco", provider=fake)
        assert "data quality" in fake.calls[0]["prompt"].lower()

    def test_fetches_sample(self, patched_client):
        from rattle_api.tasks import analyse_data

        fake = FakeAIProvider(text_response="analysis")
        analyse_data("testco", provider=fake)
        patched_client.list_all.assert_called_once_with("products", per_page=20)


# ---------------------------------------------------------------------------
# _ai() helper
# ---------------------------------------------------------------------------


class TestAIHelper:
    """_ai() — lazy provider resolution."""

    def test_returns_explicit_provider(self):
        from rattle_api.tasks import _ai

        fake = FakeAIProvider()
        assert _ai(fake) is fake

    def test_falls_back_to_get_provider(self, monkeypatch):
        from rattle_api.tasks import _ai

        monkeypatch.setenv("AI_PROVIDER", "ollama")
        provider = _ai()
        assert provider.name == "ollama"


# ---------------------------------------------------------------------------
# analyse_pricelist
# ---------------------------------------------------------------------------


class TestAnalysePricelist:
    """Pricelist analysis with consulting knowledge — heuristic + AI."""

    @pytest.fixture
    def excel_file(self, tmp_path):
        """Create a fake Excel file and mock read_source."""
        return [
            {"Feature": "Aufpreis Frässpindel HSK-63F", "Price": 2500},
            {"Feature": "Werkzeugmagazin Standard", "Price": 0},
        ]

    def test_returns_analysis_structure(self, patched_client, excel_file):
        from rattle_api.tasks import analyse_pricelist

        fake = FakeAIProvider(
            json_response={
                "products": [{"name": "Machine X"}],
                "features": [{"name": "Spindle"}],
                "anti_patterns": [],
                "recommendations": ["Create explicit groups"],
            }
        )
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": excel_file,
                "filename": "pricelist.xlsx",
            }
            result = analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=fake)

        assert "source_file" in result
        assert "file_type" in result
        assert "anti_patterns_heuristic" in result
        assert "ai_analysis" in result
        assert result["file_type"] == "excel"

    def test_includes_heuristic_anti_patterns(self, patched_client, excel_file):
        from rattle_api.tasks import analyse_pricelist

        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": excel_file,
                "filename": "pricelist.xlsx",
            }
            result = analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=fake)

        # "Aufpreis" should trigger addon-only-options anti-pattern
        pattern_ids = {r["pattern_id"] for r in result["anti_patterns_heuristic"]}
        assert "addon-only-options" in pattern_ids

    def test_skips_heuristic_for_pdf(self, patched_client):
        from rattle_api.tasks import analyse_pricelist

        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "Some PDF text content",
                "filename": "doc.pdf",
            }
            result = analyse_pricelist("testco", "/abs/doc.pdf", provider=fake)

        assert result["anti_patterns_heuristic"] == []
        assert result["file_type"] == "pdf"

    def test_handles_ai_failure_gracefully(self, patched_client, excel_file):
        from rattle_api.tasks import analyse_pricelist

        class FailProvider(FakeAIProvider):
            def complete_json(self, *args, **kwargs):
                raise RuntimeError("AI is down")

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": excel_file,
                "filename": "pricelist.xlsx",
            }
            result = analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=FailProvider())

        assert "error" in result["ai_analysis"]
        # Heuristic should still work
        assert len(result["anti_patterns_heuristic"]) > 0

    def test_resolves_relative_path(self, patched_client):
        from rattle_api.tasks import analyse_pricelist

        fake = FakeAIProvider(json_response={"products": []})
        with (
            patch("rattle_api.source.read_source") as mock_read,
            patch("rattle_api.tasks._resolve_source_file") as mock_resolve,
        ):
            mock_resolve.return_value = "/resolved/path/file.xlsx"
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "file.xlsx",
            }
            analyse_pricelist("testco", "pricelists/file.xlsx", provider=fake)

        mock_resolve.assert_called_once_with("testco", "pricelists/file.xlsx")

    def test_system_prompt_contains_knowledge(self, patched_client, excel_file):
        from rattle_api.tasks import analyse_pricelist

        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": excel_file,
                "filename": "pricelist.xlsx",
            }
            analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=fake)

        system = fake.calls[0]["system"]
        assert "NEVER build" in system
        assert "BOM" in system or "usage_subclause" in system


# ---------------------------------------------------------------------------
# suggest_configuration
# ---------------------------------------------------------------------------


class TestSuggestConfiguration:
    """BOM-aware configuration recommendations with reuse strategy."""

    def test_returns_products_with_groups(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        fake = FakeAIProvider(
            json_response={
                "products": [
                    {
                        "name": "Machine X",
                        "groups": [
                            {
                                "name": "Frässpindel",
                                "description": "Spindle type",
                                "reuse_existing": False,
                                "options": [
                                    {"label": "ISO 30", "is_default": True},
                                    {"label": "HSK-63F", "is_default": False},
                                ],
                            }
                        ],
                        "usage_subclauses": [],
                        "forbidden_combinations": [],
                    }
                ]
            }
        )
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [{"Feature": "Spindle options"}],
                "filename": "pricelist.xlsx",
            }
            result = suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        assert "products" in result
        assert len(result["products"]) == 1
        assert len(result["products"][0]["groups"]) == 1
        assert len(result["products"][0]["groups"][0]["options"]) == 2

    def test_fetches_existing_groups(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        patched_client.list_all.return_value = [
            {"id": 100, "name": "Frässpindel", "options": [{"label": "ISO 30"}]}
        ]

        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            result = suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        # Should have fetched groups
        patched_client.list_all.assert_any_call("groups")
        assert result["existing_groups_checked"] == 1

    def test_existing_groups_in_system_prompt(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        patched_client.list_all.return_value = [
            {"id": 100, "name": "Frässpindel", "options": [{"label": "ISO 30"}]}
        ]

        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        system = fake.calls[0]["system"]
        assert "Frässpindel" in system
        assert "reuse_existing" in system

    def test_product_filter_in_prompt(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        patched_client.list_all.return_value = []
        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            suggest_configuration(
                "testco",
                "/abs/pricelist.xlsx",
                provider=fake,
                product_filter="NIKE TM DPM",
            )

        prompt = fake.calls[0]["prompt"]
        assert "NIKE TM DPM" in prompt

    def test_handles_ai_failure_gracefully(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        patched_client.list_all.return_value = []

        class FailProvider(FakeAIProvider):
            def complete_json(self, *args, **kwargs):
                raise RuntimeError("AI is down")

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            result = suggest_configuration("testco", "/abs/pricelist.xlsx", provider=FailProvider())

        assert "error" in result
        assert "products" in result

    def test_handles_groups_fetch_failure(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        patched_client.list_all.side_effect = RuntimeError("API down")
        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            result = suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        assert result["existing_groups_checked"] == 0

    def test_uses_large_max_tokens(self, patched_client):
        from rattle_api.tasks import suggest_configuration

        patched_client.list_all.return_value = []
        fake = FakeAIProvider(json_response={"products": []})
        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        assert fake.calls[0]["max_tokens"] >= 8192


# ---------------------------------------------------------------------------
# Memory integration into analyse_pricelist + suggest_configuration
# ---------------------------------------------------------------------------


class TestMemoryIntegration:
    """Tasks read TenantMemory.inject_into_prompt() into the system prompt."""

    def test_analyse_pricelist_threads_tenant_profile(self, patched_client, tmp_path):
        from rattle_api.tasks import analyse_pricelist

        mem_root = tmp_path / "memory"
        (mem_root / "testco").mkdir(parents=True)
        (mem_root / "testco" / "profile.md").write_text(
            "# testco — tenant preferences\n\n- custom-keys: never\n",
            encoding="utf-8",
        )

        fake = FakeAIProvider(json_response={"products": []})
        with (
            patch("rattle_api.memory.DEFAULT_MEMORY_ROOT", mem_root),
            patch("rattle_api.source.read_source") as mock_read,
        ):
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=fake)

        system = fake.calls[0]["system"]
        assert "## Tenant preferences" in system
        assert "custom-keys" in system

    def test_analyse_pricelist_without_memory_still_works(self, patched_client, tmp_path):
        """Absent tenant memory must not break existing behaviour."""
        from rattle_api.tasks import analyse_pricelist

        mem_root = tmp_path / "memory-empty"  # nothing inside

        fake = FakeAIProvider(json_response={"products": []})
        with (
            patch("rattle_api.memory.DEFAULT_MEMORY_ROOT", mem_root),
            patch("rattle_api.source.read_source") as mock_read,
        ):
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            result = analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=fake)

        assert "ai_analysis" in result
        system = fake.calls[0]["system"]
        assert "## Tenant preferences" not in system

    def test_suggest_configuration_threads_tenant_profile(self, patched_client, tmp_path):
        from rattle_api.tasks import suggest_configuration

        mem_root = tmp_path / "memory"
        (mem_root / "testco").mkdir(parents=True)
        (mem_root / "testco" / "profile.md").write_text(
            "# testco — tenant preferences\n"
            "\n"
            "- custom-keys: never\n"
            "- area-without-groups: forbidden\n",
            encoding="utf-8",
        )

        patched_client.list_all.return_value = []
        fake = FakeAIProvider(json_response={"products": []})
        with (
            patch("rattle_api.memory.DEFAULT_MEMORY_ROOT", mem_root),
            patch("rattle_api.source.read_source") as mock_read,
        ):
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        system = fake.calls[0]["system"]
        assert "## Tenant preferences" in system
        assert "custom-keys" in system
        assert "area-without-groups" in system

    def test_tasks_do_not_write_to_memory(self, patched_client, tmp_path):
        """Explicit-only writes: task invocations must not touch memory files."""
        from rattle_api.tasks import analyse_pricelist, suggest_configuration

        mem_root = tmp_path / "memory"
        (mem_root / "testco").mkdir(parents=True)
        profile_path = mem_root / "testco" / "profile.md"
        profile_path.write_text("# testco\n\nprior content\n", encoding="utf-8")
        profile_mtime = profile_path.stat().st_mtime

        decisions_path = mem_root / "testco" / "decisions.jsonl"
        audit_path = mem_root / "testco" / "audit_history.jsonl"

        patched_client.list_all.return_value = []
        fake = FakeAIProvider(json_response={"products": []})
        with (
            patch("rattle_api.memory.DEFAULT_MEMORY_ROOT", mem_root),
            patch("rattle_api.source.read_source") as mock_read,
        ):
            mock_read.return_value = {
                "type": "excel",
                "data": [],
                "filename": "pricelist.xlsx",
            }
            analyse_pricelist("testco", "/abs/pricelist.xlsx", provider=fake)
            suggest_configuration("testco", "/abs/pricelist.xlsx", provider=fake)

        # Profile must be untouched
        assert profile_path.stat().st_mtime == profile_mtime
        assert profile_path.read_text(encoding="utf-8") == "# testco\n\nprior content\n"
        # No decisions or audit files created by the tasks themselves
        assert not decisions_path.exists()
        assert not audit_path.exists()


# ---------------------------------------------------------------------------
# run_build_stage + run_build_configurator
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_builder_client():
    """A FakeRattleClient instance reused across the build-pipeline tests."""
    from tests.test_builder import FakeRattleClient

    return FakeRattleClient()


class TestRunBuildStage:
    """Single prompt-template stage runs with a fake AI + fake Rattle client."""

    def test_extract_products_creates_operations_via_builder(
        self, monkeypatch, tmp_path, fake_builder_client
    ):
        from rattle_api.builder import ConfigBuilder
        from rattle_api.tasks import run_build_stage

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        fake = FakeAIProvider(
            json_response={
                "operations": [
                    {"op": "ensure_product", "name": "Drill X100", "base_price": 500},
                    {"op": "ensure_product", "name": "Excavator Z3", "base_price": 900},
                ]
            }
        )

        builder = ConfigBuilder(fake_builder_client, verbose=False)

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "catalogue text",
                "filename": "cat.pdf",
            }
            result = run_build_stage(
                "testco",
                "extract-products",
                "/abs/cat.pdf",
                provider=fake,
                client=fake_builder_client,
                builder=builder,
            )

        assert result["template_id"] == "extract-products"
        assert result["report"]["counts"]["created"] == 2
        assert builder.name_index[("product", "drill x100")] is not None

    def test_dry_run_stage_makes_no_http_writes(self, monkeypatch, fake_builder_client):
        from rattle_api.builder import ConfigBuilder
        from rattle_api.tasks import run_build_stage

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        fake = FakeAIProvider(
            json_response={"operations": [{"op": "ensure_product", "name": "Drill X100"}]}
        )
        builder = ConfigBuilder(fake_builder_client, dry_run=True, verbose=False)

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "some text",
                "filename": "x.pdf",
            }
            run_build_stage(
                "testco",
                "extract-products",
                "/abs/x.pdf",
                provider=fake,
                client=fake_builder_client,
                builder=builder,
                dry_run=True,
            )

        assert fake_builder_client.get_writes("POST") == []
        assert len(builder.report.created) == 1

    def test_review_configuration_is_read_only(self, monkeypatch, fake_builder_client):
        from rattle_api.builder import ConfigBuilder
        from rattle_api.tasks import run_build_stage

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        fake = FakeAIProvider(
            json_response={
                "findings": [],
                "overall": {"status": "ok", "summary": "all good"},
                "operations": [],
            }
        )
        builder = ConfigBuilder(fake_builder_client, verbose=False)

        result = run_build_stage(
            "testco",
            "review-configuration",
            source_file=None,
            provider=fake,
            client=fake_builder_client,
            builder=builder,
        )
        assert result["report"]["counts"]["created"] == 0
        assert fake_builder_client.get_writes("POST") == []


class TestRunBuildConfigurator:
    """End-to-end pipeline orchestration."""

    def _make_pipeline_provider(self):
        """Return a FakeAIProvider that yields a new canned response per call.

        The pipeline walks 9 stages sequentially, so we cycle a list of
        canned responses — one per stage.
        """
        # Note: FakeAIProvider always returns the same ``json_response``, so we
        # subclass it to cycle through stages.
        from tests.conftest import FakeAIProvider as _Fake

        class CyclingFake(_Fake):
            def __init__(self, responses):
                super().__init__(json_response={})
                self._responses = list(responses)
                self._idx = 0

            def complete_json(self, prompt, *, system=None, max_tokens=2048, temperature=0.0):
                self.calls.append(
                    {
                        "prompt": prompt,
                        "system": system,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                payload = self._responses[self._idx % len(self._responses)]
                self._idx += 1
                return payload

        return CyclingFake

    def test_pipeline_walks_nine_stages(self, monkeypatch, fake_builder_client):
        from rattle_api.tasks import run_build_configurator

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        cycling_cls = self._make_pipeline_provider()
        # Nine canned responses, one per stage. All trivially empty op lists
        # except extract-products which creates a product.
        responses = [
            {"operations": [{"op": "ensure_product", "name": "ProdA"}]},  # extract-products
            {
                "features": [
                    {
                        "name": "wheels",
                        "product": "ProdA",
                        "category": "physical",
                        "variants": [
                            {"name": "17", "is_standard": True},
                            {"name": "19", "is_standard": False},
                        ],
                    }
                ],
                "operations": [],
            },  # discover-features
            {
                "operations": [
                    {"op": "ensure_group", "name": "Wheels", "is_multi": False},
                    {"op": "ensure_option", "name": "17", "group": "Wheels", "recommended": True},
                    {"op": "ensure_option", "name": "19", "group": "Wheels", "price": 500},
                ]
            },  # model-groups-options
            {
                "operations": [
                    {"op": "ensure_area", "name": "Mechanics", "parent_product": "ProdA"},
                    {"op": "link_group_to_area", "group": "Wheels", "area": "Mechanics"},
                ]
            },  # plan-areas
            {"operations": []},  # link-bom (nothing to do)
            {"operations": []},  # discover-constraints
            {"operations": []},  # guided-selling
            {"operations": []},  # build-offer-template
            {
                "findings": [],
                "overall": {"status": "ok", "summary": "ok"},
                "operations": [],
            },  # review-configuration
        ]
        fake = cycling_cls(responses)

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "text",
                "filename": "catalogue.pdf",
            }
            result = run_build_configurator(
                "testco",
                "/abs/catalogue.pdf",
                provider=fake,
                client=fake_builder_client,
            )

        assert result["summary"]["stages"][:2] == [
            "extract-products",
            "discover-features",
        ]
        # All 9 stages should have been invoked exactly once.
        assert len(result["stages"]) == 9
        # The builder should have posted at least the product, group,
        # 2 options, area, and link_group_to_area.
        post_count = len(fake_builder_client.get_writes("POST"))
        assert post_count >= 5
        # Frontend URL is present in the summary.
        assert "frontend_url" in result["summary"]

    def test_single_shot_uses_wrapper_and_runs_review(self, monkeypatch, fake_builder_client):
        from rattle_api.tasks import run_build_configurator

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        cycling_cls = self._make_pipeline_provider()
        responses = [
            {"operations": [{"op": "ensure_product", "name": "SingleShotProd"}]},
            {"findings": [], "overall": {"status": "ok", "summary": "ok"}, "operations": []},
        ]
        fake = cycling_cls(responses)

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "text",
                "filename": "catalogue.pdf",
            }
            result = run_build_configurator(
                "testco",
                "/abs/catalogue.pdf",
                provider=fake,
                client=fake_builder_client,
                single_shot=True,
            )

        # full-configurator + review-configuration = 2 stages
        assert len(result["stages"]) == 2
        assert result["stages"][0]["template_id"] == "full-configurator"
        assert result["stages"][1]["template_id"] == "review-configuration"

    def test_dry_run_pipeline_makes_no_http_writes(self, monkeypatch, fake_builder_client):
        from rattle_api.tasks import run_build_configurator

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        cycling_cls = self._make_pipeline_provider()
        responses = [{"operations": [{"op": "ensure_product", "name": "X"}]}] * 10
        fake = cycling_cls(responses)

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "text",
                "filename": "cat.pdf",
            }
            run_build_configurator(
                "testco",
                "/abs/cat.pdf",
                provider=fake,
                client=fake_builder_client,
                dry_run=True,
            )
        assert fake_builder_client.get_writes("POST") == []

    def test_skip_stages_are_not_invoked(self, monkeypatch, fake_builder_client):
        from rattle_api.tasks import run_build_configurator

        monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
        import rattle_api.config as config

        importlib.reload(config)

        cycling_cls = self._make_pipeline_provider()
        responses = [{"operations": []}] * 10
        fake = cycling_cls(responses)

        with patch("rattle_api.source.read_source") as mock_read:
            mock_read.return_value = {
                "type": "pdf",
                "data": "text",
                "filename": "cat.pdf",
            }
            result = run_build_configurator(
                "testco",
                "/abs/cat.pdf",
                provider=fake,
                client=fake_builder_client,
                skip_stages=["guided-selling", "build-offer-template"],
            )

        stage_ids = [s["template_id"] for s in result["stages"]]
        assert "guided-selling" not in stage_ids
        assert "build-offer-template" not in stage_ids
        assert "review-configuration" in stage_ids
