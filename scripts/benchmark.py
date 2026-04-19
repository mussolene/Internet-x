"""Small local benchmark harness for the Internet-X reference implementation."""

from __future__ import annotations

from pathlib import Path
import json
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from urllib import request

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=ROOT, stdout=subprocess.DEVNULL)


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


def extract_json_block(output: str) -> dict[str, object]:
    lines = output.strip().splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith("{"):
            return json.loads("\n".join(lines[index:]))
    raise ValueError("No JSON object found in subprocess output.")


def main(iterations: int = 5) -> None:
    results = []
    with tempfile.TemporaryDirectory() as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        identities = tmpdir / "identities"
        identities.mkdir(parents=True, exist_ok=True)
        server_identity = identities / "server.json"
        client1_identity = identities / "client1.json"
        client2_identity = identities / "client2.json"
        control_plane_port = reserve_tcp_port()
        control_plane_url = f"http://127.0.0.1:{control_plane_port}"
        server_port = reserve_udp_port()
        client1_port = reserve_udp_port()
        client2_port = reserve_udp_port()
        run([sys.executable, "-m", "refimpl.keygen", "--name", "server.bench", "--locator", f"udp://127.0.0.1:{server_port}", "--out", str(server_identity)])
        run([sys.executable, "-m", "refimpl.keygen", "--name", "client1.bench", "--locator", f"udp://127.0.0.1:{client1_port}", "--out", str(client1_identity)])
        run([sys.executable, "-m", "refimpl.keygen", "--name", "client2.bench", "--locator", f"udp://127.0.0.1:{client2_port}", "--out", str(client2_identity)])
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
                str(tmpdir / "control-plane.log"),
                "--state-file",
                str(tmpdir / "control-plane-state.json"),
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
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
                str(tmpdir / "server.log"),
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1.0)
        try:
            for index, client_identity in enumerate((client1_identity, client2_identity) * iterations, start=1):
                started = time.perf_counter()
                output = subprocess.check_output(
                    [
                        sys.executable,
                        "-m",
                        "refimpl.client",
                        "--identity",
                        str(client_identity),
                        "--control-plane",
                        control_plane_url,
                        "--peer-name",
                        "server.bench",
                        "--message",
                        f"benchmark-message-{index}",
                    ],
                    cwd=ROOT,
                    text=True,
                )
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                result = extract_json_block(output)
                results.append({
                    "run": index,
                    "elapsed_ms": round(elapsed_ms, 3),
                    "acked_sequence": result["first_ack"]["acked_sequence"],
                    "received_bytes": result["first_ack"]["received_bytes"],
                })
        finally:
            server.terminate()
            server.wait(timeout=3)
            control_plane.terminate()
            control_plane.wait(timeout=3)

    summary = {
        "runs": len(results),
        "latency_ms_min": min(item["elapsed_ms"] for item in results),
        "latency_ms_median": round(statistics.median(item["elapsed_ms"] for item in results), 3),
        "latency_ms_max": max(item["elapsed_ms"] for item in results),
        "results": results,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
