"""Tests for config.py — tenant resolution and AI provider selection."""

import importlib

import pytest


class TestGetTenant:
    """Tenant lookup from RATTLE_API_KEY_* environment variables."""

    def test_known_tenant(self, monkeypatch):
        monkeypatch.setenv("RATTLE_API_KEY_ACME", "key-acme")
        import config

        importlib.reload(config)
        assert config.get_tenant("acme") == "key-acme"

    def test_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("RATTLE_API_KEY_MYCO", "key-myco")
        import config

        importlib.reload(config)
        assert config.get_tenant("MYCO") == "key-myco"
        assert config.get_tenant("Myco") == "key-myco"
        assert config.get_tenant("myco") == "key-myco"

    def test_unknown_tenant_raises(self, monkeypatch):
        import config

        importlib.reload(config)
        with pytest.raises(ValueError, match="Unknown tenant"):
            config.get_tenant("nonexistent")

    def test_error_lists_available_tenants(self, monkeypatch):
        monkeypatch.setenv("RATTLE_API_KEY_ALPHA", "k1")
        monkeypatch.setenv("RATTLE_API_KEY_BETA", "k2")
        import config

        importlib.reload(config)
        with pytest.raises(ValueError, match="alpha") as exc_info:
            config.get_tenant("nope")
        assert "beta" in str(exc_info.value).lower()

    def test_no_tenants_shows_none(self):
        import config

        importlib.reload(config)
        with pytest.raises(ValueError, match="none"):
            config.get_tenant("anything")

    def test_multiple_tenants(self, monkeypatch):
        monkeypatch.setenv("RATTLE_API_KEY_FIRST", "k1")
        monkeypatch.setenv("RATTLE_API_KEY_SECOND", "k2")
        import config

        importlib.reload(config)
        assert config.get_tenant("first") == "k1"
        assert config.get_tenant("second") == "k2"


class TestAIProviderConfig:
    """AI_PROVIDER env var defaults and selection."""

    def test_default_provider_is_openai(self):
        import config

        importlib.reload(config)
        assert config.AI_PROVIDER == "openai"

    def test_custom_provider(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "anthropic")
        import config

        importlib.reload(config)
        assert config.AI_PROVIDER == "anthropic"


class TestBaseURL:
    """API base URL configuration."""

    def test_base_url_is_set(self):
        import config

        importlib.reload(config)
        assert config.BASE_URL.startswith("https://")
        assert "rattleapp.de" in config.BASE_URL
        assert "/api/v1" in config.BASE_URL
