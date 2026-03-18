import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.rattleapp.de/api/v1"

PREFIX = "RATTLE_API_KEY_"

TENANTS = {
    key[len(PREFIX):].lower(): value
    for key, value in os.environ.items()
    if key.startswith(PREFIX)
}


def get_tenant(name):
    name = name.lower()
    if name not in TENANTS:
        available = ", ".join(TENANTS.keys()) or "(none)"
        raise ValueError(f"Unknown tenant '{name}'. Available: {available}")
    return TENANTS[name]
