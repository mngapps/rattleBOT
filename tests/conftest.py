"""Shared fixtures for the Rattle API test suite."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Environment isolation — prevent real API calls
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove real credentials and prevent .env from re-populating them."""
    for key in list(os.environ):
        if key.startswith("RATTLE_API_KEY_"):
            monkeypatch.delenv(key, raising=False)
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Prevent load_dotenv() from re-reading .env during importlib.reload()
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)


@pytest.fixture
def tenant_env(monkeypatch):
    """Set up a fake tenant credential."""
    monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key-abc123")
    # Reload config module to pick up new env
    import importlib

    import config
    importlib.reload(config)
    return "testco"


@pytest.fixture
def mock_session():
    """Return a mocked requests.Session for RattleClient tests."""
    with patch("client.requests.Session") as mock_cls:
        session = MagicMock()
        mock_cls.return_value = session
        yield session


# ---------------------------------------------------------------------------
# Fake AI provider
# ---------------------------------------------------------------------------

class FakeAIProvider:
    """Deterministic AI provider for testing — returns canned responses."""

    name = "fake"

    def __init__(self, text_response="AI response", json_response=None):
        self._text = text_response
        self._json = json_response
        self.calls = []

    def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
        self.calls.append({
            "prompt": prompt, "system": system,
            "max_tokens": max_tokens, "temperature": temperature,
        })
        return self._text

    def complete_json(self, prompt, *, system=None, max_tokens=2048, temperature=0.0):
        self.calls.append({
            "prompt": prompt, "system": system,
            "max_tokens": max_tokens, "temperature": temperature,
        })
        if self._json is not None:
            return self._json
        return json.loads(self._text)


@pytest.fixture
def fake_ai():
    """Return a FakeAIProvider factory."""
    def _make(text_response="AI response", json_response=None):
        return FakeAIProvider(text_response=text_response, json_response=json_response)
    return _make


# ---------------------------------------------------------------------------
# Fake HTTP response
# ---------------------------------------------------------------------------

def make_response(status_code=200, json_data=None, text="", method="GET", url="http://test"):
    """Build a fake requests.Response."""
    resp = MagicMock()
    resp.ok = 200 <= status_code < 300
    resp.status_code = status_code
    resp.text = text or json.dumps(json_data or {})
    resp.content = resp.text.encode() if resp.text else b""
    resp.json.return_value = json_data
    resp.request = MagicMock()
    resp.request.method = method
    resp.url = url
    return resp
