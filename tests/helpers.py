from __future__ import annotations

import socket
import time
from pathlib import Path

from refimpl.controlplane import ControlPlaneClient, ControlPlaneService


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


def start_control_plane(tmp_path: Path, *, lease_seconds: int = 60):
    service = ControlPlaneService(
        trace_path=tmp_path / "control-plane.log",
        state_path=tmp_path / "control-plane-state.json",
    )
    thread = service.serve_in_thread()
    time.sleep(0.05)
    client = ControlPlaneClient(service.base_url, lease_seconds=lease_seconds)
    return service, thread, client


def stop_control_plane(service: ControlPlaneService, thread) -> None:
    service.stop()
    thread.join(timeout=2)
