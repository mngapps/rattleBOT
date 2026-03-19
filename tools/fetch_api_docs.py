"""
Fetch the latest Rattle API documentation and save it locally.

Downloads the OpenAPI spec and generates a human-readable endpoint summary
so that scripts and AI agents always work against up-to-date definitions.

Usage:
    python3 tools/fetch_api_docs.py

Output:
    api_reference/openapi.json     — full OpenAPI 3.x specification
    api_reference/endpoints.md     — human-readable endpoint summary (generated)
    api_reference/meta.json        — fetch timestamp and source URLs

The api_reference/ folder is gitignored. Run this script whenever you want
to refresh the local copy of the docs.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone

import requests

OPENAPI_URL = "https://www.rattleapp.de/api/v1/openapi.json"
DOCS_URLS = {
    "developer_guide": "https://www.rattleapp.de/api/v1/developers",
    "interactive_docs": "https://www.rattleapp.de/api/v1/docs",
    "openapi_spec": OPENAPI_URL,
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "api_reference")


def fetch_openapi():
    """Fetch the OpenAPI JSON spec."""
    resp = requests.get(OPENAPI_URL, timeout=30)
    resp.raise_for_status()
    return resp.json(), resp.text


def generate_endpoints_md(spec):
    """Generate a human-readable endpoint summary from the OpenAPI spec.

    Groups endpoints by tag and lists method, path, summary, and parameters.
    """
    lines = [
        "# Rattle API — Endpoint Reference",
        "",
        "Auto-generated from the OpenAPI spec. Do not edit manually.",
        f"Run `python3 tools/fetch_api_docs.py` to refresh.",
        "",
        f"**API version**: {spec.get('info', {}).get('version', 'unknown')}",
        f"**Base URL**: {(spec.get('servers') or [{}])[0].get('url', 'https://www.rattleapp.de/api/v1')}",
        "",
    ]

    # Group endpoints by tag
    tagged = defaultdict(list)
    for path, methods in sorted(spec.get("paths", {}).items()):
        for method, details in methods.items():
            if method in ("parameters", "servers", "summary", "description"):
                continue
            tags = details.get("tags", ["Other"])
            summary = details.get("summary", "")
            entry = (method.upper(), path, summary, details)
            for tag in tags:
                tagged[tag].append(entry)

    # Sort tags alphabetically
    for tag in sorted(tagged.keys()):
        endpoints = tagged[tag]
        lines.append(f"## {tag}")
        lines.append("")

        for method, path, summary, details in endpoints:
            desc = f" — {summary}" if summary else ""
            lines.append(f"- `{method} {path}`{desc}")

            # List path and query parameters
            params = details.get("parameters", [])
            if params:
                for p in params:
                    name = p.get("name", "?")
                    location = p.get("in", "?")
                    required = " (required)" if p.get("required") else ""
                    desc = p.get("description", "")
                    if desc:
                        desc = f" — {desc[:80]}"
                    lines.append(f"  - `{name}` ({location}{required}){desc}")

            # Note if request body is required
            req_body = details.get("requestBody", {})
            if req_body:
                content_types = list(req_body.get("content", {}).keys())
                if "multipart/form-data" in content_types:
                    lines.append(f"  - Request: multipart file upload")
                elif content_types:
                    # Try to get the schema ref name
                    schema = req_body.get("content", {}).get(content_types[0], {}).get("schema", {})
                    ref = schema.get("$ref", "")
                    schema_name = ref.split("/")[-1] if ref else ""
                    if schema_name:
                        lines.append(f"  - Request body: `{schema_name}`")

        lines.append("")

    # Summary stats
    total = sum(len(v) for v in tagged.values())
    lines.append("---")
    lines.append(f"**Total: {total} endpoints across {len(tagged)} resource groups**")
    lines.append("")

    return "\n".join(lines)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Fetching Rattle API docs ({timestamp})")
    print(f"Output: {os.path.abspath(OUTPUT_DIR)}/")
    print()

    # Fetch OpenAPI spec
    print("  openapi.json ... ", end="", flush=True)
    try:
        spec, raw = fetch_openapi()
        out_path = os.path.join(OUTPUT_DIR, "openapi.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(raw)

        n_paths = len(spec.get("paths", {}))
        n_schemas = len(spec.get("components", {}).get("schemas", {}))
        print(f"OK ({n_paths} endpoints, {n_schemas} schemas)")
    except Exception as e:
        print(f"FAILED: {e}")
        return

    # Generate endpoint summary
    print("  endpoints.md ... ", end="", flush=True)
    try:
        md = generate_endpoints_md(spec)
        out_path = os.path.join(OUTPUT_DIR, "endpoints.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        endpoint_count = sum(
            1 for path, methods in spec.get("paths", {}).items()
            for method in methods
            if method not in ("parameters", "servers", "summary", "description")
        )
        print(f"OK ({endpoint_count} endpoints documented)")
    except Exception as e:
        print(f"FAILED: {e}")

    # Write metadata
    meta = {
        "fetched_at": timestamp,
        "api_version": spec.get("info", {}).get("version", "unknown"),
        "endpoints": n_paths,
        "schemas": n_schemas,
        "sources": DOCS_URLS,
    }
    meta_path = os.path.join(OUTPUT_DIR, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDone. Agents should read api_reference/ for up-to-date endpoint info.")
    print(f"  Live docs: {DOCS_URLS['developer_guide']}")


if __name__ == "__main__":
    main()
