"""CLI wrapper for the Internet-X reference server."""

from __future__ import annotations

import argparse
from pathlib import Path

from .controlplane import ControlPlaneClient
from .engine import InternetXServer
from .identity import NodeIdentity


def main() -> None:
    parser = argparse.ArgumentParser(description="Internet-X reference UDP server")
    parser.add_argument("--identity", required=True, help="Path to node identity JSON")
    parser.add_argument("--control-plane", required=True, help="Base URL for the control-plane service")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", default=9080, type=int, help="Bind UDP port")
    parser.add_argument("--trace", default="examples/traces/server-trace.log", help="Trace output path")
    args = parser.parse_args()

    identity = NodeIdentity.load(args.identity)
    identity.locator = f"udp://{args.host}:{args.port}"
    control_plane = ControlPlaneClient(args.control_plane)
    server = InternetXServer(
        identity,
        control_plane=control_plane,
        host=args.host,
        port=args.port,
        trace_path=Path(args.trace),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
