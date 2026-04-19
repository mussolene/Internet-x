"""Educational Internet-X UDP client."""

from __future__ import annotations

import argparse
import socket
import uuid

import protocol
from node import NodeIdentity

ALGORITHM_ID = "hybrid-simulated"
CLIENT_PUBLIC_MATERIAL = "internet-x-client-demo-public-key"
SERVER_PUBLIC_MATERIAL = "internet-x-server-demo-public-key"


class UDPClient:
    def __init__(self, server_host: str, server_port: int, timeout: float) -> None:
        locator = f"udp://{server_host}:{server_port}"
        self.server_host = server_host
        self.server_port = server_port
        self.server_locator = locator
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.client_node = NodeIdentity.from_public_material(
            name="client.demo",
            algorithm_id=ALGORITHM_ID,
            locator=locator,
            public_key_material=CLIENT_PUBLIC_MATERIAL,
        )
        self.server_node = NodeIdentity.from_public_material(
            name="server.demo",
            algorithm_id=ALGORITHM_ID,
            locator=locator,
            public_key_material=SERVER_PUBLIC_MATERIAL,
        )
        self.session_id = uuid.uuid4().hex
        self.transcript: list[dict[str, object]] = []
        self.flow_id: str | None = None

    def log(self, direction: str, packet: dict[str, object]) -> None:
        print(f"[{direction}] {protocol.summarize_packet(packet)}")

    def send_packet(self, packet: dict[str, object]) -> None:
        self.sock.sendto(protocol.encode_packet(packet), (self.server_host, self.server_port))
        self.log("SEND", packet)
        self.transcript.append(packet)

    def receive_packet(self, expected_type: str) -> dict[str, object]:
        raw_data, _ = self.sock.recvfrom(65535)
        packet = protocol.decode_packet(raw_data)
        self.log("RECV", packet)
        if packet["packet_type"] == protocol.ERROR:
            message = packet["payload"].get("message", "unknown server error")
            raise protocol.ProtocolError(f"Server returned ERROR: {message}")
        if packet["packet_type"] != expected_type:
            raise protocol.ProtocolError(
                f"Expected {expected_type}, received {packet['packet_type']}"
            )
        self.transcript.append(packet)
        return packet

    def run(self) -> None:
        try:
            self.send_init()
            init_ack = self.receive_packet(protocol.INIT_ACK)
            self.send_kem_exchange(init_ack)
            auth = self.receive_packet(protocol.AUTH)
            self.flow_id = str(auth["flow_id"])
            self.send_data()
            self.receive_packet(protocol.DATA_ACK)
            print("[INFO] Educational handshake and data exchange completed.")
        except (socket.timeout, protocol.ProtocolError) as exc:
            print(f"[ERROR] Client exchange failed: {exc}")
        finally:
            self.sock.close()

    def send_init(self) -> None:
        packet = protocol.make_packet(
            protocol.INIT,
            source_node_id=self.client_node.node_id,
            destination_node_id=self.server_node.node_id,
            locator_hint=self.client_node.locator,
            payload={
                "session_id": self.session_id,
                "sender_name": self.client_node.name,
                "algorithm_id": self.client_node.algorithm_id,
                "supported_modes": ["hybrid-simulated", "classical-simulated"],
                "client_nonce": uuid.uuid4().hex,
                "client_key_material": "simulated-client-ephemeral-key",
                "note": "Educational INIT packet only.",
            },
        )
        self.send_packet(packet)

    def send_kem_exchange(self, init_ack: dict[str, object]) -> None:
        selected_mode = init_ack["payload"]["selected_mode"]
        packet = protocol.make_packet(
            protocol.KEM_EXCHANGE,
            source_node_id=self.client_node.node_id,
            destination_node_id=self.server_node.node_id,
            locator_hint=self.client_node.locator,
            payload={
                "session_id": self.session_id,
                "encapsulated_key_material": "simulated-kem-ciphertext",
                "classical_share": "simulated-classical-share",
                "pq_share": "simulated-pq-share" if selected_mode == "hybrid-simulated" else "not-used",
                "transcript_hash": protocol.compute_transcript_hash(self.transcript),
                "note": "Simulated KEM exchange material for architecture testing.",
            },
        )
        self.send_packet(packet)

    def send_data(self) -> None:
        packet = protocol.make_packet(
            protocol.DATA,
            source_node_id=self.client_node.node_id,
            destination_node_id=self.server_node.node_id,
            locator_hint=self.client_node.locator,
            flow_id=self.flow_id,
            payload={
                "session_id": self.session_id,
                "content": "Hello from the educational Internet-X client.",
                "transcript_hash": protocol.compute_transcript_hash(self.transcript),
            },
        )
        self.send_packet(packet)


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational Internet-X UDP client.")
    parser.add_argument("--host", default=protocol.DEFAULT_HOST, help="Server host.")
    parser.add_argument("--port", default=protocol.DEFAULT_PORT, type=int, help="Server UDP port.")
    parser.add_argument("--timeout", default=3.0, type=float, help="Socket timeout in seconds.")
    args = parser.parse_args()
    UDPClient(args.host, args.port, args.timeout).run()


if __name__ == "__main__":
    main()
