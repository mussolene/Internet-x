"""CLI wrapper for the Internet-X reference client."""

from __future__ import annotations

import argparse
from pathlib import Path
import json

from .directory import JSONDirectory, JSONLocatorRegistry
from .engine import InternetXClient
from .identity import NodeIdentity


def main() -> None:
    parser = argparse.ArgumentParser(description="Internet-X reference UDP client")
    parser.add_argument("--identity", required=True, help="Path to node identity JSON")
    parser.add_argument("--directory", required=True, help="Path to directory JSON")
    parser.add_argument("--registry", required=True, help="Path to locator registry JSON")
    parser.add_argument("--peer-name", required=True, help="Remote peer name to resolve")
    parser.add_argument("--message", default="Hello from Internet-X.", help="Application payload")
    parser.add_argument("--trace", default="examples/traces/client-trace.log", help="Trace output path")
    parser.add_argument("--migrate", action="store_true", help="Perform an authenticated locator update mid-session")
    args = parser.parse_args()

    identity = NodeIdentity.load(args.identity)
    directory = JSONDirectory.load(args.directory)
    registry = JSONLocatorRegistry.load(args.registry)
    client = InternetXClient(
        identity,
        peer_name=args.peer_name,
        directory=directory,
        registry=registry,
        trace_path=Path(args.trace),
    )
    result = client.run(args.message, perform_locator_update=args.migrate)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
