"""Tests for ai_provider.py — provider registry, complete_json parsing, all backends."""

import json
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestProviderRegistry:
    """get_provider() and list_providers() — provider lookup and enumeration."""

    def test_list_providers_returns_all(self):
        from ai_provider import list_providers

        names = list_providers()
        assert set(names) == {"openai", "anthropic", "ollama", "custom"}

    def test_list_providers_is_stable(self):
        from ai_provider import list_providers

        assert list_providers() == list_providers()

    def test_get_provider_unknown_raises(self):
        from ai_provider import get_provider

        with pytest.raises(ValueError, match="Unknown AI provider"):
            get_provider("nonexistent")

    def test_get_provider_error_lists_available(self):
        from ai_provider import get_provider

        with pytest.raises(ValueError) as exc_info:
            get_provider("bad")
        msg = str(exc_info.value)
        assert "openai" in msg
        assert "anthropic" in msg

    def test_get_provider_defaults_to_openai(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        from ai_provider import get_provider

        provider = get_provider()
        assert provider.name == "openai"

    def test_get_provider_respects_env_var(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "ollama")
        from ai_provider import get_provider

        provider = get_provider()
        assert provider.name == "ollama"

    def test_get_provider_explicit_overrides_env(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "anthropic")
        from ai_provider import get_provider

        provider = get_provider("ollama")
        assert provider.name == "ollama"

    def test_get_provider_case_insensitive(self):
        from ai_provider import get_provider

        provider = get_provider("OLLAMA")
        assert provider.name == "ollama"


# ---------------------------------------------------------------------------
# complete_json() — JSON parsing from AI responses
# ---------------------------------------------------------------------------


class TestCompleteJSON:
    """AIProvider.complete_json() strips markdown fences and parses JSON."""

    def _make_provider(self, text_response):
        """Create a concrete provider subclass for testing complete_json."""
        from ai_provider import AIProvider

        class TestProvider(AIProvider):
            name = "test"

            def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
                return text_response

        return TestProvider()

    def test_plain_json(self):
        provider = self._make_provider('["a", "b"]')
        assert provider.complete_json("test") == ["a", "b"]

    def test_json_with_markdown_fences(self):
        provider = self._make_provider('```json\n["a", "b"]\n```')
        assert provider.complete_json("test") == ["a", "b"]

    def test_json_with_plain_fences(self):
        provider = self._make_provider('```\n{"key": "value"}\n```')
        assert provider.complete_json("test") == {"key": "value"}

    def test_json_with_whitespace(self):
        provider = self._make_provider('  \n  {"x": 1}  \n  ')
        assert provider.complete_json("test") == {"x": 1}

    def test_invalid_json_raises(self):
        provider = self._make_provider("not json at all")
        with pytest.raises(json.JSONDecodeError):
            provider.complete_json("test")

    def test_nested_json(self):
        data = {"products": [{"id": 1, "tags": ["a", "b"]}]}
        provider = self._make_provider(json.dumps(data))
        assert provider.complete_json("test") == data

    def test_json_array_of_objects(self):
        data = [{"name": "A"}, {"name": "B"}]
        provider = self._make_provider(json.dumps(data))
        assert provider.complete_json("test") == data


# ---------------------------------------------------------------------------
# OpenAI provider
# ---------------------------------------------------------------------------


class TestOpenAIProvider:
    """OpenAIProvider — OpenAI / Azure / vLLM / LM Studio compatible."""

    def test_requires_openai_package(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        with patch.dict("sys.modules", {"openai": None}):
            from ai_provider import OpenAIProvider

            with pytest.raises(ImportError, match="openai"):
                OpenAIProvider()

    def test_default_model(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            from ai_provider import OpenAIProvider

            p = OpenAIProvider()
            assert p._model == "gpt-4o"

    def test_custom_model(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            from ai_provider import OpenAIProvider

            p = OpenAIProvider()
            assert p._model == "gpt-3.5-turbo"

    def test_custom_base_url(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:8080")
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            from ai_provider import OpenAIProvider

            p = OpenAIProvider()
            assert p._base_url == "http://localhost:8080"

    def test_complete_builds_messages(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="response text"))
        ]

        with patch.dict("sys.modules", {"openai": mock_openai}):
            from ai_provider import OpenAIProvider

            p = OpenAIProvider()
            result = p.complete("hello", system="be helpful")

        assert result == "response text"
        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


# ---------------------------------------------------------------------------
# Anthropic provider
# ---------------------------------------------------------------------------


class TestAnthropicProvider:
    """AnthropicProvider — Anthropic Messages API."""

    def test_requires_anthropic_package(self):
        with patch.dict("sys.modules", {"anthropic": None}):
            from ai_provider import AnthropicProvider

            with pytest.raises(ImportError, match="anthropic"):
                AnthropicProvider()

    def test_default_model(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
        with patch.dict("sys.modules", {"anthropic": MagicMock()}):
            from ai_provider import AnthropicProvider

            p = AnthropicProvider()
            assert "claude" in p._model

    def test_complete_passes_system(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.return_value.content = [MagicMock(text="response text")]

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from ai_provider import AnthropicProvider

            p = AnthropicProvider()
            result = p.complete("hello", system="be helpful")

        assert result == "response text"
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("system") == "be helpful"


# ---------------------------------------------------------------------------
# Ollama provider
# ---------------------------------------------------------------------------


class TestOllamaProvider:
    """OllamaProvider — local inference via Ollama HTTP API."""

    def test_default_config(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        from ai_provider import OllamaProvider

        p = OllamaProvider()
        assert "localhost" in p._base_url
        assert p._model == "llama3"

    def test_custom_config(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://gpu-server:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "mistral")
        from ai_provider import OllamaProvider

        p = OllamaProvider()
        assert p._base_url == "http://gpu-server:11434"
        assert p._model == "mistral"

    def test_complete_calls_api(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        from ai_provider import OllamaProvider

        p = OllamaProvider()

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "ollama says hi"}}
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = p.complete("test prompt", system="sys")

        assert result == "ollama says hi"
        call_kwargs = mock_post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["stream"] is False
        assert len(body["messages"]) == 2  # system + user


# ---------------------------------------------------------------------------
# Custom HTTP provider
# ---------------------------------------------------------------------------


class TestCustomHTTPProvider:
    """CustomHTTPProvider — generic OpenAI-compatible REST endpoint."""

    def test_requires_base_url(self, monkeypatch):
        monkeypatch.delenv("CUSTOM_AI_BASE_URL", raising=False)
        from ai_provider import CustomHTTPProvider

        with pytest.raises(ValueError, match="CUSTOM_AI_BASE_URL"):
            CustomHTTPProvider()

    def test_optional_api_key(self, monkeypatch):
        monkeypatch.setenv("CUSTOM_AI_BASE_URL", "http://my-api")
        monkeypatch.delenv("CUSTOM_AI_API_KEY", raising=False)
        from ai_provider import CustomHTTPProvider

        p = CustomHTTPProvider()
        assert p._api_key == ""

    def test_complete_sends_bearer(self, monkeypatch):
        monkeypatch.setenv("CUSTOM_AI_BASE_URL", "http://my-api")
        monkeypatch.setenv("CUSTOM_AI_API_KEY", "secret-token")
        from ai_provider import CustomHTTPProvider

        p = CustomHTTPProvider()

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"choices": [{"message": {"content": "custom reply"}}]}
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = p.complete("test")

        assert result == "custom reply"
        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["Authorization"] == "Bearer secret-token"

    def test_strips_trailing_slash_from_url(self, monkeypatch):
        monkeypatch.setenv("CUSTOM_AI_BASE_URL", "http://my-api/")
        from ai_provider import CustomHTTPProvider

        p = CustomHTTPProvider()

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp) as mock_post:
            p.complete("test")

        url = mock_post.call_args[0][0]
        assert "//v1" not in url
