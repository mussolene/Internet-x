"""CLI wrapper for the Internet-X control-plane service."""

from __future__ import annotations

import argparse

from .controlplane import ControlPlaneService


def main() -> None:
    parser = argparse.ArgumentParser(description="Internet-X authenticated control-plane service")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", default=0, type=int, help="Bind TCP port")
    parser.add_argument("--trace", default="examples/traces/control-plane-trace.log", help="Trace output path")
    parser.add_argument("--state-file", default=None, help="Optional JSON state snapshot path")
    parser.add_argument("--max-lease-seconds", default=300, type=int, help="Maximum accepted lease duration")
    parser.add_argument("--max-clock-skew", default=30.0, type=float, help="Maximum allowed clock skew in seconds")
    args = parser.parse_args()

    service = ControlPlaneService(
        host=args.host,
        port=args.port,
        trace_path=args.trace,
        state_path=args.state_file,
        max_lease_seconds=args.max_lease_seconds,
        max_clock_skew=args.max_clock_skew,
    )
    print(f"[control-plane] listening on {service.base_url}")
    service.serve_forever()


if __name__ == "__main__":
    main()
