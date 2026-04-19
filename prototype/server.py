"""Educational Internet-X UDP server."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import socket
import uuid

import protocol
from node import NodeIdentity

ALGORITHM_ID = "hybrid-simulated"
CLIENT_PUBLIC_MATERIAL = "internet-x-client-demo-public-key"
SERVER_PUBLIC_MATERIAL = "internet-x-server-demo-public-key"


@dataclass
class SessionState:
    session_id: str
    client_node_id: str
    client_locator: str
    selected_mode: str
    transcript: list[dict[str, object]] = field(default_factory=list)
    flow_id: str | None = None


class UDPServer:
    def __init__(self, host: str, port: int, timeout: float) -> None:
        locator = f"udp://{host}:{port}"
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.sock.bind((host, port))
        self.server_node = NodeIdentity.from_public_material(
            name="server.demo",
            algorithm_id=ALGORITHM_ID,
            locator=locator,
            public_key_material=SERVER_PUBLIC_MATERIAL,
        )
        self.client_node = NodeIdentity.from_public_material(
            name="client.demo",
            algorithm_id=ALGORITHM_ID,
            locator=locator,
            public_key_material=CLIENT_PUBLIC_MATERIAL,
        )
        self.sessions: dict[str, SessionState] = {}

    def log(self, direction: str, packet: dict[str, object], addr: tuple[str, int]) -> None:
        print(f"[{direction}] {addr} {protocol.summarize_packet(packet)}")

    def send_packet(self, packet: dict[str, object], addr: tuple[str, int]) -> None:
        self.sock.sendto(protocol.encode_packet(packet), addr)
        self.log("SEND", packet, addr)

    def serve_forever(self) -> None:
        print(f"[INFO] Internet-X educational UDP server listening on {self.host}:{self.port}")
        try:
            while True:
                try:
                    raw_data, addr = self.sock.recvfrom(65535)
                except socket.timeout:
                    continue

                try:
                    packet = protocol.decode_packet(raw_data)
                    self.log("RECV", packet, addr)
                    self.handle_packet(packet, addr)
                except protocol.ProtocolError as exc:
                    print(f"[ERROR] Protocol failure from {addr}: {exc}")
                    error_packet = protocol.build_error_packet(
                        source_node_id=self.server_node.node_id,
                        destination_node_id=self.client_node.node_id,
                        locator_hint=self.server_node.locator,
                        session_id=None,
                        message=str(exc),
                    )
                    self.send_packet(error_packet, addr)
        except KeyboardInterrupt:
            print("[INFO] Server stopped.")
        finally:
            self.sock.close()

    def handle_packet(self, packet: dict[str, object], addr: tuple[str, int]) -> None:
        packet_type = packet["packet_type"]
        if packet_type == protocol.INIT:
            self.handle_init(packet, addr)
        elif packet_type == protocol.KEM_EXCHANGE:
            self.handle_kem_exchange(packet, addr)
        elif packet_type == protocol.DATA:
            self.handle_data(packet, addr)
        else:
            raise protocol.ProtocolError(f"Unexpected packet type for server state machine: {packet_type}")

    def handle_init(self, packet: dict[str, object], addr: tuple[str, int]) -> None:
        payload = packet["payload"]
        session_id = str(payload["session_id"])
        supported_modes = payload.get("supported_modes", [])
        selected_mode = "hybrid-simulated" if "hybrid-simulated" in supported_modes else "classical-simulated"
        state = SessionState(
            session_id=session_id,
            client_node_id=str(packet["source_node_id"]),
            client_locator=str(packet["locator_hint"]),
            selected_mode=selected_mode,
        )
        state.transcript.append(packet)
        self.sessions[session_id] = state

        response = protocol.make_packet(
            protocol.INIT_ACK,
            source_node_id=self.server_node.node_id,
            destination_node_id=state.client_node_id,
            locator_hint=self.server_node.locator,
            payload={
                "session_id": session_id,
                "selected_mode": selected_mode,
                "server_nonce": uuid.uuid4().hex,
                "server_key_material": "simulated-server-ephemeral-key",
                "transcript_hash": protocol.compute_transcript_hash(state.transcript),
                "note": "Educational INIT_ACK packet only.",
            },
        )
        state.transcript.append(response)
        self.send_packet(response, addr)

    def handle_kem_exchange(self, packet: dict[str, object], addr: tuple[str, int]) -> None:
        payload = packet["payload"]
        session_id = str(payload["session_id"])
        state = self.require_session(session_id)
        expected_hash = protocol.compute_transcript_hash(state.transcript)
        if payload.get("transcript_hash") != expected_hash:
            self.send_error(addr, session_id, "Transcript hash mismatch during KEM_EXCHANGE.", protocol.KEM_EXCHANGE)
            return

        state.transcript.append(packet)
        state.flow_id = protocol.derive_flow_id(
            session_id,
            protocol.compute_transcript_hash(state.transcript),
            self.server_node.node_id,
            state.client_node_id,
        )

        response = protocol.make_packet(
            protocol.AUTH,
            source_node_id=self.server_node.node_id,
            destination_node_id=state.client_node_id,
            locator_hint=self.server_node.locator,
            flow_id=state.flow_id,
            payload={
                "session_id": session_id,
                "auth_result": "accepted",
                "flow_id": state.flow_id,
                "transcript_hash": protocol.compute_transcript_hash(state.transcript),
                "auth_proof": "simulated-server-auth-binding",
                "note": "Educational AUTH packet only; no real cryptographic assurance.",
            },
        )
        state.transcript.append(response)
        self.send_packet(response, addr)

    def handle_data(self, packet: dict[str, object], addr: tuple[str, int]) -> None:
        payload = packet["payload"]
        session_id = str(payload["session_id"])
        state = self.require_session(session_id)
        if packet.get("flow_id") != state.flow_id:
            self.send_error(addr, session_id, "FlowID mismatch for DATA.", protocol.DATA)
            return

        expected_hash = protocol.compute_transcript_hash(state.transcript)
        if payload.get("transcript_hash") != expected_hash:
            self.send_error(addr, session_id, "Transcript hash mismatch during DATA.", protocol.DATA)
            return

        content = str(payload.get("content", ""))
        print(f"[INFO] DATA content for session {session_id}: {content}")
        state.transcript.append(packet)
        response = protocol.make_packet(
            protocol.DATA_ACK,
            source_node_id=self.server_node.node_id,
            destination_node_id=state.client_node_id,
            locator_hint=self.server_node.locator,
            flow_id=state.flow_id,
            payload={
                "session_id": session_id,
                "status": "delivered",
                "flow_id": state.flow_id,
                "received_bytes": len(content.encode("utf-8")),
                "transcript_hash": protocol.compute_transcript_hash(state.transcript),
                "note": "Educational DATA_ACK packet only.",
            },
        )
        state.transcript.append(response)
        self.send_packet(response, addr)

    def require_session(self, session_id: str) -> SessionState:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise protocol.ProtocolError(f"Unknown session_id: {session_id}") from exc

    def send_error(
        self,
        addr: tuple[str, int],
        session_id: str | None,
        message: str,
        expected_packet_type: str | None,
    ) -> None:
        error_packet = protocol.build_error_packet(
            source_node_id=self.server_node.node_id,
            destination_node_id=self.client_node.node_id,
            locator_hint=self.server_node.locator,
            session_id=session_id,
            message=message,
            expected_packet_type=expected_packet_type,
        )
        self.send_packet(error_packet, addr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational Internet-X UDP server.")
    parser.add_argument("--host", default=protocol.DEFAULT_HOST, help="Bind host.")
    parser.add_argument("--port", default=protocol.DEFAULT_PORT, type=int, help="Bind UDP port.")
    parser.add_argument(
        "--timeout",
        default=0.5,
        type=float,
        help="Socket timeout in seconds so the server can react to Ctrl+C promptly.",
    )
    args = parser.parse_args()
    UDPServer(args.host, args.port, args.timeout).serve_forever()


if __name__ == "__main__":
    main()
