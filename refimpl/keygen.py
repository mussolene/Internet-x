"""Generate Internet-X identity material."""

from __future__ import annotations

import argparse

from .identity import NodeIdentity


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Internet-X node identity")
    parser.add_argument("--name", required=True, help="Human-readable node name")
    parser.add_argument("--locator", required=True, help="Initial locator, for example udp://127.0.0.1:9080")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()
    identity = NodeIdentity.generate(name=args.name, locator=args.locator)
    identity.save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
