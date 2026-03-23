import argparse
import json
import os
import sys

from client import RattleClient
from source_reader import list_sources

# ---------------------------------------------------------------------------
# Original commands
# ---------------------------------------------------------------------------

def cmd_test_connection(tenant, args):
    client = RattleClient(tenant)
    try:
        data = client.get("products", per_page=1)
        print(f"Connection OK for tenant '{tenant}'")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"Connection FAILED: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_sources(tenant, args):
    files = list_sources(tenant)
    if not files:
        print(f"No source files found for tenant '{tenant}'")
        return
    print(f"Source files for '{tenant}':")
    for f in files:
        print(f"  {f}")


# ---------------------------------------------------------------------------
# AI-powered commands
# ---------------------------------------------------------------------------

def cmd_ai_describe(tenant, args):
    """Generate AI product descriptions and push to Rattle."""
    from ai_tasks import describe_products
    results = describe_products(
        tenant, limit=args.limit, language=args.language,
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_ai_classify(tenant, args):
    """Classify products using AI."""
    from ai_tasks import classify_products
    results = classify_products(tenant, limit=args.limit)
    print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_ai_transform(tenant, args):
    """Transform interchange data between formats using AI."""
    from ai_tasks import transform_interchange
    results = transform_interchange(
        tenant, args.source_format, args.target_format,
        args.data_file, push=args.push,
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_ai_analyse(tenant, args):
    """Ask AI to analyse rental data."""
    from ai_tasks import analyse_rental_data
    analyse_rental_data(tenant, question=args.question)


def cmd_ai_providers(tenant, args):
    """List available AI providers."""
    from ai_provider import list_providers
    print("Available AI providers:")
    for name in list_providers():
        print(f"  - {name}")
    current = os.environ.get("AI_PROVIDER", "openai")
    print(f"\nActive provider (AI_PROVIDER): {current}")


# ---------------------------------------------------------------------------
# CLI setup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Rattle AI Workspace — AI-agnostic rental data toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "AI provider is selected via the AI_PROVIDER env var:\n"
            "  openai (default), anthropic, ollama, custom\n\n"
            "Examples:\n"
            "  python main.py pressta test-connection\n"
            "  AI_PROVIDER=anthropic python main.py pressta ai-describe --limit 3\n"
            "  python main.py pressta ai-transform datanorm rattle data.json --push\n"
        ),
    )
    parser.add_argument("tenant", help="Tenant name (e.g. pressta)")
    sub = parser.add_subparsers(dest="command", required=True, help="Command")

    # -- existing commands ---------------------------------------------------
    sub.add_parser("test-connection", help="Verify API connectivity")
    sub.add_parser("list-sources", help="List source files for a tenant")

    # -- AI commands ---------------------------------------------------------
    p_desc = sub.add_parser(
        "ai-describe", help="Generate product descriptions with AI",
    )
    p_desc.add_argument("--limit", type=int, default=5,
                        help="Max products to process (default 5)")
    p_desc.add_argument("--language", default="de",
                        help="Target language (default de)")

    p_cls = sub.add_parser(
        "ai-classify", help="Classify products with AI",
    )
    p_cls.add_argument("--limit", type=int, default=10,
                       help="Max products to process (default 10)")

    p_xform = sub.add_parser(
        "ai-transform",
        help="Transform interchange data between formats",
    )
    p_xform.add_argument("source_format",
                         help="Source format (datanorm, eclass, bmecat, …)")
    p_xform.add_argument("target_format",
                         help="Target format (rattle, datanorm, …)")
    p_xform.add_argument("data_file", help="Path to JSON input file")
    p_xform.add_argument("--push", action="store_true",
                         help="POST transformed records to Rattle API")

    p_analyse = sub.add_parser(
        "ai-analyse", help="Ask AI to analyse rental data",
    )
    p_analyse.add_argument("--question", default=None,
                           help="Custom question (default: data quality audit)")

    sub.add_parser("ai-providers", help="List available AI providers")

    # -- dispatch ------------------------------------------------------------
    args = parser.parse_args()

    commands = {
        "test-connection": cmd_test_connection,
        "list-sources":    cmd_list_sources,
        "ai-describe":     cmd_ai_describe,
        "ai-classify":     cmd_ai_classify,
        "ai-transform":    cmd_ai_transform,
        "ai-analyse":      cmd_ai_analyse,
        "ai-providers":    cmd_ai_providers,
    }
    commands[args.command](args.tenant, args)


if __name__ == "__main__":
    main()
