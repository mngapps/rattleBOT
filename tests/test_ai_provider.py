"""Smoke tests for the AI provider registry."""

from ai_provider import PROVIDERS, list_providers


def test_list_providers_returns_all():
    names = list_providers()
    assert "openai" in names
    assert "anthropic" in names
    assert "ollama" in names
    assert "custom" in names


def test_providers_dict_matches_list():
    assert set(list_providers()) == set(PROVIDERS.keys())
