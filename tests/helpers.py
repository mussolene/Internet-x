from __future__ import annotations

import socket


def reserve_udp_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def make_udp_locator(port: int) -> str:
    return f"udp://127.0.0.1:{port}"


def udp_port(locator: str) -> int:
    return int(locator.rsplit(":", 1)[1])
