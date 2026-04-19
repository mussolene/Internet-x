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

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=ROOT, stdout=subprocess.DEVNULL)


def reserve_udp_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


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
        server_port = reserve_udp_port()
        client1_port = reserve_udp_port()
        client2_port = reserve_udp_port()
        run([sys.executable, "-m", "refimpl.keygen", "--name", "server.bench", "--locator", f"udp://127.0.0.1:{server_port}", "--out", str(server_identity)])
        run([sys.executable, "-m", "refimpl.keygen", "--name", "client1.bench", "--locator", f"udp://127.0.0.1:{client1_port}", "--out", str(client1_identity)])
        run([sys.executable, "-m", "refimpl.keygen", "--name", "client2.bench", "--locator", f"udp://127.0.0.1:{client2_port}", "--out", str(client2_identity)])
        server_data = json.loads(server_identity.read_text())
        client1_data = json.loads(client1_identity.read_text())
        client2_data = json.loads(client2_identity.read_text())
        directory = tmpdir / "directory.json"
        registry = tmpdir / "registry.json"
        directory.write_text(json.dumps({
            "entries": {
                name: {
                    "name": data["name"],
                    "node_id": data["node_id"],
                    "algorithm_id": data["algorithm_id"],
                    "signing_public_key": data["signing_public_key"],
                    "locator": data["locator"],
                }
                for name, data in {
                    server_data["name"]: server_data,
                    client1_data["name"]: client1_data,
                    client2_data["name"]: client2_data,
                }.items()
            }
        }, indent=2, sort_keys=True) + "\n")
        registry.write_text(json.dumps({
            "locators": {
                data["node_id"]: {"locator": data["locator"], "epoch": 1, "source": "benchmark"}
                for data in (server_data, client1_data, client2_data)
            }
        }, indent=2, sort_keys=True) + "\n")

        server = subprocess.Popen(
            [sys.executable, "-m", "refimpl.server", "--identity", str(server_identity), "--port", str(server_port), "--trace", str(tmpdir / "server.log")],
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
                        "--directory",
                        str(directory),
                        "--registry",
                        str(registry),
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
