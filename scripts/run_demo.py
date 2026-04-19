"""Build demo artifacts and run a full Internet-X exchange."""

from __future__ import annotations

from pathlib import Path
import json
import socket
import subprocess
import sys
import time
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
IDENTITIES = EXAMPLES / "identities"
CONTROL_PLANE_TRACE = EXAMPLES / "traces" / "control-plane-trace.log"
CONTROL_PLANE_STATE = EXAMPLES / "demo-control-plane-state.json"
SERVER_TRACE = EXAMPLES / "traces" / "server-trace.log"
CLIENT_TRACE = EXAMPLES / "traces" / "client-trace.log"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True)


def reserve_udp_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def reserve_tcp_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def wait_for_control_plane(base_url: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with request.urlopen(f"{base_url}/v1/health", timeout=0.5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") == "ok":
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"Control plane did not become ready at {base_url}")


def main() -> None:
    IDENTITIES.mkdir(parents=True, exist_ok=True)
    server_identity = IDENTITIES / "server.json"
    client_identity = IDENTITIES / "client.json"
    control_plane_port = reserve_tcp_port()
    control_plane_url = f"http://127.0.0.1:{control_plane_port}"
    server_port = reserve_udp_port()
    client_port = reserve_udp_port()

    run([
        sys.executable,
        "-m",
        "refimpl.keygen",
        "--name",
        "server.demo",
        "--locator",
        f"udp://127.0.0.1:{server_port}",
        "--out",
        str(server_identity),
    ])
    run([
        sys.executable,
        "-m",
        "refimpl.keygen",
        "--name",
        "client.demo",
        "--locator",
        f"udp://127.0.0.1:{client_port}",
        "--out",
        str(client_identity),
    ])

    control_plane = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "refimpl.controlplane_service",
            "--host",
            "127.0.0.1",
            "--port",
            str(control_plane_port),
            "--trace",
            str(CONTROL_PLANE_TRACE),
            "--state-file",
            str(CONTROL_PLANE_STATE),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    wait_for_control_plane(control_plane_url)

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "refimpl.server",
            "--identity",
            str(server_identity),
            "--control-plane",
            control_plane_url,
            "--port",
            str(server_port),
            "--trace",
            str(SERVER_TRACE),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(1.0)
    try:
        client_output = run(
            [
                sys.executable,
                "-m",
                "refimpl.client",
                "--identity",
                str(client_identity),
                "--control-plane",
                control_plane_url,
                "--peer-name",
                "server.demo",
                "--message",
                "Hello from the Internet-X reference client.",
                "--migrate",
                "--trace",
                str(CLIENT_TRACE),
            ]
        )
        print(client_output)
    finally:
        server.terminate()
        try:
            stdout, _ = server.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            server.kill()
            stdout, _ = server.communicate()
        print(stdout)
        control_plane.terminate()
        try:
            control_plane_stdout, _ = control_plane.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            control_plane.kill()
            control_plane_stdout, _ = control_plane.communicate()
        print(control_plane_stdout)


if __name__ == "__main__":
    main()
