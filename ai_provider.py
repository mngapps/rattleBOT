"""
AI-agnostic provider abstraction for the Rattle AI Workspace.

Supports any LLM backend (OpenAI, Anthropic, local/Ollama, or custom HTTP
endpoints) through a unified interface.  CLI coding agents (Claude Code,
Aider, Cursor, Continue, etc.) can use this module to drive AI-powered
tasks against rental and interchange data without being locked to a
single vendor.

Usage:
    provider = get_provider("openai")      # or "anthropic", "ollama", "custom"
    result   = provider.complete("Summarise this rental data: ...")
"""

import json
import os
from abc import ABC, abstractmethod

# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class AIProvider(ABC):
    """Vendor-neutral interface every AI backend must implement."""

    name: str = "base"

    @abstractmethod
    def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
        """Return the model's text response for *prompt*.

        Args:
            prompt:      User / task prompt.
            system:      Optional system prompt.
            max_tokens:  Response length cap.
            temperature: Sampling temperature.

        Returns:
            str – the model's reply text.
        """

    def complete_json(self, prompt, *, system=None, max_tokens=2048, temperature=0.0):
        """Convenience wrapper that parses the response as JSON."""
        raw = self.complete(prompt, system=system, max_tokens=max_tokens, temperature=temperature)
        # Strip markdown fences if the model wraps its response
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())


# ---------------------------------------------------------------------------
# OpenAI-compatible provider (works with OpenAI, Azure, vLLM, LM Studio…)
# ---------------------------------------------------------------------------


class OpenAIProvider(AIProvider):
    """OpenAI-compatible chat completions (v1/chat/completions)."""

    name = "openai"

    def __init__(self):
        try:
            import openai  # noqa: F401
        except ImportError:
            raise ImportError("Install the openai package:  pip install openai")
        self._api_key = os.environ.get("OPENAI_API_KEY", "")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
        self._base_url = os.environ.get("OPENAI_BASE_URL")  # None → default
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o")

    def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
        import openai

        kwargs = {}
        if self._base_url:
            kwargs["base_url"] = self._base_url
        client = openai.OpenAI(api_key=self._api_key, **kwargs)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content


# ---------------------------------------------------------------------------
# Anthropic provider
# ---------------------------------------------------------------------------


class AnthropicProvider(AIProvider):
    """Anthropic Messages API."""

    name = "anthropic"

    def __init__(self):
        try:
            import anthropic  # noqa: F401
        except ImportError:
            raise ImportError("Install the anthropic package:  pip install anthropic")
        self._api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for Anthropic provider"
            )
        self._model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)
        kwargs = {}
        if system:
            kwargs["system"] = system

        resp = client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return resp.content[0].text


# ---------------------------------------------------------------------------
# Ollama / local models
# ---------------------------------------------------------------------------


class OllamaProvider(AIProvider):
    """Local inference via Ollama HTTP API."""

    name = "ollama"

    def __init__(self):
        self._base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = os.environ.get("OLLAMA_MODEL", "llama3")

    def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
        import requests

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = requests.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": messages,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": temperature},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]


# ---------------------------------------------------------------------------
# Generic HTTP provider (any REST endpoint)
# ---------------------------------------------------------------------------


class CustomHTTPProvider(AIProvider):
    """Bring-your-own endpoint.  Must accept and return OpenAI-shaped JSON."""

    name = "custom"

    def __init__(self):
        self._base_url = os.environ.get("CUSTOM_AI_BASE_URL")
        if not self._base_url:
            raise ValueError("Set CUSTOM_AI_BASE_URL to use the custom provider")
        self._api_key = os.environ.get("CUSTOM_AI_API_KEY", "")
        self._model = os.environ.get("CUSTOM_AI_MODEL", "default")

    def complete(self, prompt, *, system=None, max_tokens=1024, temperature=0.2):
        import requests

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        resp = requests.post(
            f"{self._base_url.rstrip('/')}/v1/chat/completions",
            headers=headers,
            json={
                "model": self._model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
    "custom": CustomHTTPProvider,
}


def get_provider(name=None):
    """Instantiate an AI provider by name.

    Falls back to the ``AI_PROVIDER`` env var, then to ``"openai"``.
    """
    name = (name or os.environ.get("AI_PROVIDER", "openai")).lower()
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS)
        raise ValueError(f"Unknown AI provider '{name}'. Available: {available}")
    return PROVIDERS[name]()


def list_providers():
    """Return list of registered provider names."""
    return list(PROVIDERS.keys())
