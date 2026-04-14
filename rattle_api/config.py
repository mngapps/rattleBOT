import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("RATTLE_BASE_URL", "https://www.rattleapp.de/api/v1")

# ---------------------------------------------------------------------------
# Tenant configuration (Rattle API keys)
# ---------------------------------------------------------------------------

PREFIX = "RATTLE_API_KEY_"

TENANTS = {
    key[len(PREFIX) :].lower(): value for key, value in os.environ.items() if key.startswith(PREFIX)
}


def get_tenant(name):
    name = name.lower()
    if name not in TENANTS:
        available = ", ".join(TENANTS.keys()) or "(none)"
        raise ValueError(f"Unknown tenant '{name}'. Available: {available}")
    return TENANTS[name]


# ---------------------------------------------------------------------------
# Frontend URL — used by the configurator builder to print click-through
# validation links after a run. Per-tenant override takes precedence over
# the global default.
#   RATTLE_FRONTEND_URL              — default for all tenants
#   RATTLE_FRONTEND_URL_<TENANT>     — override for one tenant (uppercased)
# ---------------------------------------------------------------------------

FRONTEND_URL_PREFIX = "RATTLE_FRONTEND_URL_"
DEFAULT_FRONTEND_URL = os.environ.get("RATTLE_FRONTEND_URL", "https://www.rattleapp.de")

FRONTEND_URLS = {
    key[len(FRONTEND_URL_PREFIX) :].lower(): value
    for key, value in os.environ.items()
    if key.startswith(FRONTEND_URL_PREFIX)
}


def get_frontend_url(tenant):
    """Return the Rattle frontend URL for *tenant*, trimmed of trailing slashes.

    Lookup order:
      1. ``RATTLE_FRONTEND_URL_<TENANT>``
      2. ``RATTLE_FRONTEND_URL``
      3. The built-in default (``https://www.rattleapp.de``)
    """
    url = FRONTEND_URLS.get(tenant.lower()) or DEFAULT_FRONTEND_URL
    return url.rstrip("/")


# ---------------------------------------------------------------------------
# AI provider configuration
# ---------------------------------------------------------------------------
# AI_PROVIDER          – which backend to use: openai | anthropic | ollama | custom
#
# OpenAI / compatible:
#   OPENAI_API_KEY     – API key
#   OPENAI_BASE_URL    – (optional) custom base URL (Azure, vLLM, LM Studio …)
#   OPENAI_MODEL       – model name (default: gpt-4o)
#
# Anthropic:
#   ANTHROPIC_API_KEY  – API key
#   ANTHROPIC_MODEL    – model name (default: claude-sonnet-4-20250514)
#
# Ollama (local):
#   OLLAMA_BASE_URL    – server URL (default: http://localhost:11434)
#   OLLAMA_MODEL       – model name (default: llama3)
#
# Custom HTTP endpoint:
#   CUSTOM_AI_BASE_URL – base URL (required)
#   CUSTOM_AI_API_KEY  – bearer token (optional)
#   CUSTOM_AI_MODEL    – model name (default: default)
# ---------------------------------------------------------------------------

AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai")
