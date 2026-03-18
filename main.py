import argparse
import json
import sys

from client import RattleClient
from source_reader import list_sources


def cmd_test_connection(tenant):
    client = RattleClient(tenant)
    try:
        data = client.get("products", per_page=1)
        print(f"Connection OK for tenant '{tenant}'")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"Connection FAILED: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_sources(tenant):
    files = list_sources(tenant)
    if not files:
        print(f"No source files found for tenant '{tenant}'")
        return
    print(f"Source files for '{tenant}':")
    for f in files:
        print(f"  {f}")


def main():
    parser = argparse.ArgumentParser(description="Rattle API Control Panel")
    parser.add_argument("tenant", help="Tenant name (e.g. pressta)")
    parser.add_argument("command", choices=["test-connection", "list-sources"],
                        help="Command to run")
    args = parser.parse_args()

    commands = {
        "test-connection": cmd_test_connection,
        "list-sources": cmd_list_sources,
    }
    commands[args.command](args.tenant)


if __name__ == "__main__":
    main()
