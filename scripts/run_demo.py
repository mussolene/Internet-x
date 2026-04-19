"""Build demo artifacts and run a full Internet-X exchange."""

from __future__ import annotations

from pathlib import Path
import json
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
IDENTITIES = EXAMPLES / "identities"
DIRECTORY = EXAMPLES / "demo-directory.json"
REGISTRY = EXAMPLES / "demo-registry.json"
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


def main() -> None:
    IDENTITIES.mkdir(parents=True, exist_ok=True)
    server_identity = IDENTITIES / "server.json"
    client_identity = IDENTITIES / "client.json"
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

    server_identity_obj = json.loads(server_identity.read_text(encoding="utf-8"))
    client_identity_obj = json.loads(client_identity.read_text(encoding="utf-8"))

    DIRECTORY.write_text(
        json.dumps(
            {
                "entries": {
                    "server.demo": {
                        "name": "server.demo",
                        "node_id": server_identity_obj["node_id"],
                        "algorithm_id": server_identity_obj["algorithm_id"],
                        "signing_public_key": server_identity_obj["signing_public_key"],
                        "locator": server_identity_obj["locator"],
                    },
                    "client.demo": {
                        "name": "client.demo",
                        "node_id": client_identity_obj["node_id"],
                        "algorithm_id": client_identity_obj["algorithm_id"],
                        "signing_public_key": client_identity_obj["signing_public_key"],
                        "locator": client_identity_obj["locator"],
                    },
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    REGISTRY.write_text(
        json.dumps(
            {
                "locators": {
                    server_identity_obj["node_id"]: {"locator": server_identity_obj["locator"], "epoch": 1, "source": "demo"},
                    client_identity_obj["node_id"]: {"locator": client_identity_obj["locator"], "epoch": 1, "source": "demo"},
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "refimpl.server",
            "--identity",
            str(server_identity),
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
                "--directory",
                str(DIRECTORY),
                "--registry",
                str(REGISTRY),
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


if __name__ == "__main__":
    main()
