"""Tests for ai_tasks.py — AI-driven tasks with mocked API and providers."""

import json
import importlib
import pytest
from unittest.mock import MagicMock, patch, mock_open

from tests.conftest import FakeAIProvider, make_response


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
    import config
    importlib.reload(config)

    with patch("ai_tasks.RattleClient", return_value=mock_client):
        yield mock_client


# ---------------------------------------------------------------------------
# describe_products
# ---------------------------------------------------------------------------

class TestDescribeProducts:
    """AI-generated product descriptions, pushed back to Rattle API."""

    def test_generates_descriptions(self, patched_client):
        from ai_tasks import describe_products
        fake = FakeAIProvider(text_response="A professional drilling machine.")
        results = describe_products("testco", provider=fake, limit=2)

        assert len(results) == 2
        assert results[0]["description"] == "A professional drilling machine."
        assert results[0]["id"] == "p1"
        assert results[0]["name"] == "Drill X100"

    def test_patches_back_to_api(self, patched_client):
        from ai_tasks import describe_products
        fake = FakeAIProvider(text_response="desc")
        describe_products("testco", provider=fake, limit=2)

        assert patched_client.patch.call_count == 2
        patched_client.patch.assert_any_call(
            "products/p1", json={"description": "desc"}
        )

    def test_respects_limit(self, patched_client):
        from ai_tasks import describe_products
        fake = FakeAIProvider(text_response="desc")
        results = describe_products("testco", provider=fake, limit=1)
        assert len(results) == 1

    def test_handles_ai_failure_gracefully(self, patched_client):
        from ai_tasks import describe_products

        class FailProvider(FakeAIProvider):
            def complete(self, *args, **kwargs):
                raise RuntimeError("AI is down")

        results = describe_products("testco", provider=FailProvider(), limit=2)
        assert len(results) == 2
        assert "error" in results[0]
        assert "AI is down" in results[0]["error"]

    def test_language_passed_to_system_prompt(self, patched_client):
        from ai_tasks import describe_products
        fake = FakeAIProvider(text_response="Beschreibung")
        describe_products("testco", provider=fake, limit=1, language="de")
        assert fake.calls[0]["system"] is not None
        assert "German" in fake.calls[0]["system"]

    def test_english_language(self, patched_client):
        from ai_tasks import describe_products
        fake = FakeAIProvider(text_response="Description")
        describe_products("testco", provider=fake, limit=1, language="en")
        assert "en" in fake.calls[0]["system"]

    def test_idempotent_same_result(self, patched_client):
        """Running describe twice with same data produces same results."""
        from ai_tasks import describe_products
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
        from ai_tasks import classify_products
        fake = FakeAIProvider(json_response=["Power Tools", "Drilling"])
        results = classify_products("testco", provider=fake, limit=2)

        assert len(results) == 2
        assert results[0]["tags"] == ["Power Tools", "Drilling"]

    def test_handles_ai_failure(self, patched_client):
        from ai_tasks import classify_products

        class FailProvider(FakeAIProvider):
            def complete_json(self, *args, **kwargs):
                raise json.JSONDecodeError("bad", "", 0)

        results = classify_products("testco", provider=FailProvider(), limit=1)
        assert "error" in results[0]

    def test_respects_limit(self, patched_client):
        from ai_tasks import classify_products
        fake = FakeAIProvider(json_response=["tag"])
        results = classify_products("testco", provider=fake, limit=1)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# transform_interchange
# ---------------------------------------------------------------------------

class TestTransformInterchange:
    """Format conversion with optional push to Rattle API."""

    def test_transforms_data(self, patched_client, tmp_path):
        from ai_tasks import transform_interchange

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
        from ai_tasks import transform_interchange

        data_file = tmp_path / "single.json"
        data_file.write_text(json.dumps({"id": "001"}))

        fake = FakeAIProvider(json_response=[{"name": "A"}])
        results = transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake
        )
        assert isinstance(results, list)

    def test_push_posts_to_api(self, patched_client, tmp_path):
        from ai_tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        fake = FakeAIProvider(json_response=[{"name": "A"}, {"name": "B"}])
        transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake, push=True
        )

        assert patched_client.post.call_count == 2

    def test_no_push_by_default(self, patched_client, tmp_path):
        from ai_tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        fake = FakeAIProvider(json_response=[{"name": "A"}])
        transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake
        )

        patched_client.post.assert_not_called()

    def test_push_failure_does_not_crash(self, patched_client, tmp_path):
        from ai_tasks import transform_interchange

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
        from ai_tasks import transform_interchange
        fake = FakeAIProvider(json_response=[])
        with pytest.raises(FileNotFoundError):
            transform_interchange(
                "testco", "datanorm", "rattle", "/no/such/file.json", provider=fake
            )

    def test_idempotent_transform(self, patched_client, tmp_path):
        """Same input produces same output."""
        from ai_tasks import transform_interchange

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps([{"id": "1"}]))

        fake = FakeAIProvider(json_response=[{"name": "Converted"}])
        r1 = transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake
        )
        r2 = transform_interchange(
            "testco", "datanorm", "rattle", str(data_file), provider=fake
        )
        assert r1 == r2


# ---------------------------------------------------------------------------
# analyse_rental_data
# ---------------------------------------------------------------------------

class TestAnalyseRentalData:
    """Open-ended AI analysis of rental catalogue data."""

    def test_returns_analysis_text(self, patched_client):
        from ai_tasks import analyse_rental_data
        fake = FakeAIProvider(text_response="Your data has 2 products with good coverage.")
        result = analyse_rental_data("testco", provider=fake)
        assert "2 products" in result

    def test_custom_question(self, patched_client):
        from ai_tasks import analyse_rental_data
        fake = FakeAIProvider(text_response="answer")
        analyse_rental_data("testco", provider=fake, question="How many drills?")
        assert "How many drills?" in fake.calls[0]["prompt"]

    def test_default_question_is_quality_audit(self, patched_client):
        from ai_tasks import analyse_rental_data
        fake = FakeAIProvider(text_response="audit")
        analyse_rental_data("testco", provider=fake)
        assert "data quality" in fake.calls[0]["prompt"].lower()

    def test_fetches_sample(self, patched_client):
        from ai_tasks import analyse_rental_data
        fake = FakeAIProvider(text_response="analysis")
        analyse_rental_data("testco", provider=fake)
        patched_client.list_all.assert_called_once_with("products", per_page=20)


# ---------------------------------------------------------------------------
# _ai() helper
# ---------------------------------------------------------------------------

class TestAIHelper:
    """_ai() — lazy provider resolution."""

    def test_returns_explicit_provider(self):
        from ai_tasks import _ai
        fake = FakeAIProvider()
        assert _ai(fake) is fake

    def test_falls_back_to_get_provider(self, monkeypatch):
        from ai_tasks import _ai
        monkeypatch.setenv("AI_PROVIDER", "ollama")
        provider = _ai()
        assert provider.name == "ollama"
