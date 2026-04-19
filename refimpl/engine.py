"""Client and server engines for the Internet-X reference implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import socket
import threading
import time
from typing import Any, Iterable

from . import crypto
from .directory import JSONDirectory, JSONLocatorRegistry
from .identity import NodeIdentity, PeerRecord, derive_node_id
from .packet import (
    AUTH,
    DATA,
    DATA_ACK,
    DEFAULT_HOST,
    DEFAULT_PORT,
    ERROR,
    INIT,
    INIT_ACK,
    KEM_EXCHANGE,
    LOCATOR_UPDATE,
    LOCATOR_UPDATE_ACK,
    PacketTrace,
    PacketError,
    build_packet,
    canonical_json,
    decode_packet,
    encode_packet,
    summarize_packet,
)


@dataclass(slots=True)
class SessionState:
    session_id: str
    client_peer: PeerRecord
    server_peer: PeerRecord
    selected_suite: str
    selected_pq_mode: str
    fallback_used: bool
    client_ephemeral_public: str
    server_ephemeral_public: str
    server_ephemeral_private: Any | None = None
    transcript: list[dict[str, Any]] = field(default_factory=list)
    server_pq_share: str | None = None
    flow_id: str | None = None
    keys: crypto.SessionKeys | None = None
    stage: str = "INIT_ACK_SENT"
    next_server_sequence: int = 0
    next_client_sequence: int = 0
    seen_client_sequences: set[int] = field(default_factory=set)
    last_data_ack: dict[int, dict[str, Any]] = field(default_factory=dict)
    last_locator_update_counter: int = -1
    client_locator: str | None = None
    last_client_addr: tuple[str, int] | None = None
    auth_packet: dict[str, Any] | None = None
    init_ack_packet: dict[str, Any] | None = None
    application_messages: list[str] = field(default_factory=list)


class TraceRecorder:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.events: list[PacketTrace] = []
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    def write(self, direction: str, packet: dict[str, Any]) -> None:
        trace = PacketTrace(direction=direction, packet=packet)
        self.events.append(trace)
        if self.path:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(f"[{direction}] {summarize_packet(packet)}\n")
                handle.write(f"{canonical_json(packet)}\n")


class InternetXServer:
    def __init__(
        self,
        identity: NodeIdentity,
        *,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout: float = 0.2,
        trace_path: str | Path | None = None,
        drop_once: Iterable[str] | None = None,
    ) -> None:
        self.identity = identity
        self.host = host
        self.port = port
        self.timeout = timeout
        self.trace = TraceRecorder(trace_path)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.sock.bind((host, port))
        self.sessions: dict[str, SessionState] = {}
        self.drop_once = set(drop_once or [])
        self.drop_history: set[str] = set()
        self.running = False

    @property
    def locator(self) -> str:
        return f"udp://{self.host}:{self.port}"

    def log(self, message: str) -> None:
        print(f"[server] {message}")

    def maybe_drop(self, packet_type: str) -> bool:
        if packet_type in self.drop_once and packet_type not in self.drop_history:
            self.drop_history.add(packet_type)
            self.log(f"dropping first {packet_type} reply for retransmission testing")
            return True
        return False

    def send_packet(self, packet: dict[str, Any], addr: tuple[str, int]) -> None:
        self.trace.write("SEND", packet)
        self.sock.sendto(encode_packet(packet), addr)
        self.log(f"send {addr} {summarize_packet(packet)}")

    def build_error(self, packet: dict[str, Any], message: str, *, expected: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"message": message}
        if expected is not None:
            payload["expected_packet_type"] = expected
        return build_packet(
            ERROR,
            session_id=packet["session_id"],
            source_node_id=self.identity.node_id,
            destination_node_id=str(packet["source_node_id"]),
            locator_hint=self.locator,
            flow_id=packet.get("flow_id"),
            sequence=packet.get("sequence"),
            payload=payload,
        )

    def serve_forever(self) -> None:
        self.running = True
        self.log(f"listening on {self.host}:{self.port}")
        try:
            while self.running:
                try:
                    raw, addr = self.sock.recvfrom(65535)
                except socket.timeout:
                    continue
                try:
                    packet = decode_packet(raw)
                except PacketError as exc:
                    if self.running:
                        self.log(f"discard malformed packet from {addr}: {exc}")
                    continue
                self.trace.write("RECV", packet)
                self.log(f"recv {addr} {summarize_packet(packet)}")
                try:
                    self.handle_packet(packet, addr)
                except (PacketError, crypto.CryptoError, KeyError, ValueError) as exc:
                    self.log(f"error for session {packet['session_id']}: {exc}")
                    self.send_packet(self.build_error(packet, str(exc)), addr)
        finally:
            self.sock.close()
            self.running = False

    def stop(self) -> None:
        self.running = False
        self.sock.close()

    def serve_in_thread(self) -> threading.Thread:
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        return thread

    def handle_packet(self, packet: dict[str, Any], addr: tuple[str, int]) -> None:
        packet_type = str(packet["packet_type"])
        if packet_type == INIT:
            self.handle_init(packet, addr)
            return
        state = self.sessions[str(packet["session_id"])]
        state.last_client_addr = addr
        if packet_type == KEM_EXCHANGE:
            self.handle_kem_exchange(state, packet, addr)
        elif packet_type == DATA:
            self.handle_data(state, packet, addr)
        elif packet_type == LOCATOR_UPDATE:
            self.handle_locator_update(state, packet, addr)
        else:
            raise PacketError(f"Unexpected packet type for server: {packet_type}")

    def handle_init(self, packet: dict[str, Any], addr: tuple[str, int]) -> None:
        payload = packet["payload"]
        session_id = str(packet["session_id"])
        if session_id in self.sessions and self.sessions[session_id].init_ack_packet is not None:
            self.send_packet(self.sessions[session_id].init_ack_packet, addr)
            return

        client_node_id = str(packet["source_node_id"])
        algorithm_id = str(payload["identity_algorithm"])
        signing_public_key = str(payload["signing_public_key"])
        expected_node_id = derive_node_id(algorithm_id, signing_public_key)
        if expected_node_id != client_node_id:
            raise PacketError("Client node_id does not match signing public key.")

        supported_suites = list(payload.get("supported_suites", []))
        selected_suite = next((suite for suite in supported_suites if suite in crypto.SUPPORTED_SUITES), None)
        if selected_suite is None:
            raise PacketError("No mutually supported classical secure suite.")

        offered_pq_modes = list(payload.get("supported_pq_modes", []))
        allow_classical_fallback = bool(payload.get("allow_classical_fallback", False))
        if crypto.SIMULATED_PQ_MODE in offered_pq_modes:
            selected_pq_mode = crypto.SIMULATED_PQ_MODE
            fallback_used = False
        elif allow_classical_fallback:
            selected_pq_mode = crypto.NO_PQ_MODE
            fallback_used = True
        else:
            raise PacketError("Peer requires PQ mode but no mutually supported PQ mode exists.")

        server_ephemeral_private, server_ephemeral_public = crypto.generate_ephemeral_keypair()
        server_pq_share = crypto.b64encode(b"server-pq-" + bytes.fromhex(crypto.random_token(16)))
        client_peer = PeerRecord(
            name=str(payload["sender_name"]),
            node_id=client_node_id,
            algorithm_id=algorithm_id,
            signing_public_key=signing_public_key,
            locator=str(packet["locator_hint"]),
        )
        server_peer = self.identity.peer_record()
        state = SessionState(
            session_id=session_id,
            client_peer=client_peer,
            server_peer=server_peer,
            selected_suite=selected_suite,
            selected_pq_mode=selected_pq_mode,
            fallback_used=fallback_used,
            client_ephemeral_public=str(payload["client_ephemeral_key"]),
            server_ephemeral_public=server_ephemeral_public,
            server_ephemeral_private=server_ephemeral_private,
            server_pq_share=server_pq_share,
            client_locator=str(packet["locator_hint"]),
            last_client_addr=addr,
        )
        state.transcript.append(packet)
        response = build_packet(
            INIT_ACK,
            session_id=session_id,
            source_node_id=self.identity.node_id,
            destination_node_id=client_node_id,
            locator_hint=self.locator,
            payload={
                "sender_name": self.identity.name,
                "identity_algorithm": self.identity.algorithm_id,
                "signing_public_key": self.identity.signing_public_key,
                "server_ephemeral_key": server_ephemeral_public,
                "server_pq_share": server_pq_share if selected_pq_mode == crypto.SIMULATED_PQ_MODE else None,
                "selected_suite": selected_suite,
                "selected_pq_mode": selected_pq_mode,
                "fallback_used": fallback_used,
                "server_nonce": crypto.random_token(),
                "transcript_hash": crypto.transcript_hash(state.transcript),
                "note": "Classical security is real; PQ material is simulated when selected.",
            },
        )
        state.transcript.append(response)
        state.init_ack_packet = response
        self.sessions[session_id] = state
        if not self.maybe_drop(INIT_ACK):
            self.send_packet(response, addr)

    def handle_kem_exchange(self, state: SessionState, packet: dict[str, Any], addr: tuple[str, int]) -> None:
        if state.auth_packet is not None:
            self.send_packet(state.auth_packet, addr)
            return
        payload = packet["payload"]
        expected_transcript = crypto.transcript_hash(state.transcript)
        if payload.get("transcript_hash") != expected_transcript:
            raise crypto.CryptoError("Transcript mismatch during KEM_EXCHANGE.")

        classical_secret = crypto.compute_shared_secret(state.server_ephemeral_private, state.client_ephemeral_public)
        mixed_secret = crypto.mix_secret(
            classical_secret,
            selected_pq_mode=state.selected_pq_mode,
            client_pq_share=payload.get("client_pq_share"),
            server_pq_share=state.server_pq_share,
        )
        keys = crypto.derive_keys(
            mixed_secret,
            session_id=state.session_id,
            client_node_id=state.client_peer.node_id,
            server_node_id=state.server_peer.node_id,
            transcript_digest=expected_transcript,
        )

        signature_fields = {
            "session_id": state.session_id,
            "transcript_hash": expected_transcript,
            "client_node_id": state.client_peer.node_id,
            "server_node_id": state.server_peer.node_id,
            "selected_suite": state.selected_suite,
            "selected_pq_mode": state.selected_pq_mode,
            "client_ephemeral_key": state.client_ephemeral_public,
            "server_ephemeral_key": state.server_ephemeral_public,
            "client_pq_share": payload.get("client_pq_share"),
        }
        crypto.verify_fields(state.client_peer, "KEM_EXCHANGE", signature_fields, str(payload["client_signature"]))
        crypto.verify_mac(keys.handshake_key, "KEM_EXCHANGE", signature_fields, str(payload["key_confirmation"]))

        state.keys = keys
        state.transcript.append(packet)
        transcript_after_kem = crypto.transcript_hash(state.transcript)
        flow_id = crypto.derive_flow_id(
            session_id=state.session_id,
            client_node_id=state.client_peer.node_id,
            server_node_id=state.server_peer.node_id,
            transcript_digest=transcript_after_kem,
            selected_suite=state.selected_suite,
            selected_pq_mode=state.selected_pq_mode,
        )
        state.flow_id = flow_id
        auth_fields = {
            "session_id": state.session_id,
            "flow_id": flow_id,
            "transcript_hash": transcript_after_kem,
            "selected_suite": state.selected_suite,
            "selected_pq_mode": state.selected_pq_mode,
        }
        response = build_packet(
            AUTH,
            session_id=state.session_id,
            source_node_id=state.server_peer.node_id,
            destination_node_id=state.client_peer.node_id,
            locator_hint=self.locator,
            flow_id=flow_id,
            payload={
                "auth_result": "accepted",
                "selected_suite": state.selected_suite,
                "selected_pq_mode": state.selected_pq_mode,
                "fallback_used": state.fallback_used,
                "transcript_hash": transcript_after_kem,
                "server_signature": crypto.sign_fields(self.identity.signing_private(), "AUTH", auth_fields),
                "key_confirmation": crypto.compute_mac(keys.handshake_key, "AUTH", auth_fields),
                "note": "PQ mode remains simulated if selected; baseline authentication and AEAD are real classical crypto.",
            },
        )
        state.transcript.append(response)
        state.stage = "ESTABLISHED"
        state.auth_packet = response
        if not self.maybe_drop(AUTH):
            self.send_packet(response, addr)

    def handle_data(self, state: SessionState, packet: dict[str, Any], addr: tuple[str, int]) -> None:
        if packet.get("flow_id") != state.flow_id:
            raise PacketError("DATA packet has wrong flow_id.")
        sequence = int(packet.get("sequence") or 0)
        if sequence in state.last_data_ack:
            self.send_packet(state.last_data_ack[sequence], addr)
            return
        if sequence in state.seen_client_sequences:
            raise crypto.CryptoError("Replay detected for DATA sequence.")
        if packet.get("locator_hint") != state.client_locator:
            raise PacketError("DATA locator does not match current authenticated locator.")

        plaintext = crypto.decrypt_payload(packet, state.keys.client_to_server_key, packet["payload"])
        state.seen_client_sequences.add(sequence)
        state.next_client_sequence = max(state.next_client_sequence, sequence + 1)
        content = str(plaintext["content"])
        state.application_messages.append(content)
        self.log(f"application data: {content}")

        ack_sequence = state.next_server_sequence
        ack_packet = build_packet(
            DATA_ACK,
            session_id=state.session_id,
            source_node_id=state.server_peer.node_id,
            destination_node_id=state.client_peer.node_id,
            locator_hint=self.locator,
            flow_id=state.flow_id,
            sequence=ack_sequence,
            payload={},
        )
        ack_plaintext = {
            "status": "delivered",
            "acked_sequence": sequence,
            "received_bytes": len(content.encode("utf-8")),
            "server_time": time.time(),
        }
        ack_packet["payload"] = crypto.encrypt_payload(
            ack_packet,
            state.keys.server_to_client_key,
            state.keys.server_to_client_iv,
            ack_sequence,
            ack_plaintext,
        )
        state.last_data_ack[sequence] = ack_packet
        state.next_server_sequence += 1
        self.send_packet(ack_packet, addr)

    def handle_locator_update(self, state: SessionState, packet: dict[str, Any], addr: tuple[str, int]) -> None:
        if packet.get("flow_id") != state.flow_id:
            raise PacketError("LOCATOR_UPDATE packet has wrong flow_id.")
        payload = packet["payload"]
        update_counter = int(payload["update_counter"])
        if update_counter <= state.last_locator_update_counter:
            raise crypto.CryptoError("Stale locator update counter.")

        fields = {
            "session_id": state.session_id,
            "flow_id": state.flow_id,
            "new_locator": str(payload["new_locator"]),
            "previous_locator": str(payload["previous_locator"]),
            "update_counter": update_counter,
        }
        crypto.verify_fields(state.client_peer, "LOCATOR_UPDATE", fields, str(payload["signature"]))
        crypto.verify_mac(state.keys.update_key, "LOCATOR_UPDATE", fields, str(payload["update_mac"]))

        state.last_locator_update_counter = update_counter
        state.client_locator = str(payload["new_locator"])
        state.client_peer.locator = state.client_locator
        state.last_client_addr = addr

        ack_packet = build_packet(
            LOCATOR_UPDATE_ACK,
            session_id=state.session_id,
            source_node_id=state.server_peer.node_id,
            destination_node_id=state.client_peer.node_id,
            locator_hint=self.locator,
            flow_id=state.flow_id,
            sequence=update_counter,
            payload={
                "acknowledged_counter": update_counter,
                "active_locator": state.client_locator,
                "signature": crypto.sign_fields(self.identity.signing_private(), "LOCATOR_UPDATE_ACK", fields),
                "update_mac": crypto.compute_mac(state.keys.update_key, "LOCATOR_UPDATE_ACK", fields),
            },
        )
        self.send_packet(ack_packet, addr)


class InternetXClient:
    def __init__(
        self,
        identity: NodeIdentity,
        *,
        peer_name: str,
        directory: JSONDirectory,
        registry: JSONLocatorRegistry,
        timeout: float = 0.5,
        retries: int = 3,
        trace_path: str | Path | None = None,
    ) -> None:
        self.identity = identity
        self.peer_name = peer_name
        self.directory = directory
        self.registry = registry
        self.timeout = timeout
        self.retries = retries
        self.trace = TraceRecorder(trace_path)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.session_id = crypto.random_token()
        self.client_ephemeral_private, self.client_ephemeral_public = crypto.generate_ephemeral_keypair()
        self.client_pq_share = crypto.b64encode(b"client-pq-" + bytes.fromhex(crypto.random_token(16)))
        self.peer = self.resolve_peer()
        self.transcript: list[dict[str, Any]] = []
        self.init_packet: dict[str, Any] | None = None
        self.kem_packet: dict[str, Any] | None = None
        self.selected_suite: str | None = None
        self.selected_pq_mode: str | None = None
        self.flow_id: str | None = None
        self.keys: crypto.SessionKeys | None = None
        self.server_ephemeral_public: str | None = None
        self.server_pq_share: str | None = None
        self.next_client_sequence = 0
        self.next_server_sequence = 0
        self.last_server_locator = self.peer.locator
        self.locator_update_counter = 0

    def resolve_peer(self) -> PeerRecord:
        peer = self.directory.resolve_name(self.peer_name)
        locator_info = self.registry.lookup(peer.node_id)
        peer.locator = str(locator_info["locator"])
        return peer

    def log(self, message: str) -> None:
        print(f"[client] {message}")

    def send_packet(self, packet: dict[str, Any], *, locator: str | None = None) -> None:
        target = locator or self.peer.locator
        host, port = parse_locator(target)
        self.trace.write("SEND", packet)
        self.sock.sendto(encode_packet(packet), (host, port))
        self.log(f"send {(host, port)} {summarize_packet(packet)}")

    def receive_packet(self, expected_types: set[str]) -> dict[str, Any]:
        raw, _ = self.sock.recvfrom(65535)
        packet = decode_packet(raw)
        self.trace.write("RECV", packet)
        self.log(f"recv {summarize_packet(packet)}")
        if packet["packet_type"] == ERROR:
            raise PacketError(str(packet["payload"].get("message", "unknown error")))
        if packet["packet_type"] not in expected_types:
            raise PacketError(f"Expected {sorted(expected_types)}, got {packet['packet_type']}")
        return packet

    def send_with_retry(self, builder, expected_types: set[str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            packet = builder()
            try:
                self.send_packet(packet)
                return self.receive_packet(expected_types)
            except (socket.timeout, PacketError, crypto.CryptoError) as exc:
                last_error = exc
                self.log(f"attempt {attempt}/{self.retries} failed: {exc}")
        raise RuntimeError(f"exchange failed after {self.retries} attempts: {last_error}")

    def run(self, message: str, *, perform_locator_update: bool = False) -> dict[str, Any]:
        try:
            init_ack = self.send_with_retry(self.build_init, {INIT_ACK})
            self.handle_init_ack(init_ack)
            auth = self.send_with_retry(self.build_kem_exchange, {AUTH})
            self.handle_auth(auth)
            first_ack = self.send_data(message)
            result = {"first_ack": first_ack}
            if perform_locator_update:
                update_ack = self.perform_locator_update()
                second_ack = self.send_data(message + " [post-migration]")
                result.update({"locator_update_ack": update_ack, "second_ack": second_ack})
            return result
        finally:
            self.sock.close()

    def build_init(self) -> dict[str, Any]:
        if self.init_packet is None:
            self.init_packet = build_packet(
                INIT,
                session_id=self.session_id,
                source_node_id=self.identity.node_id,
                destination_node_id=self.peer.node_id,
                locator_hint=self.identity.locator,
                payload={
                    "sender_name": self.identity.name,
                    "identity_algorithm": self.identity.algorithm_id,
                    "signing_public_key": self.identity.signing_public_key,
                    "client_ephemeral_key": self.client_ephemeral_public,
                    "supported_suites": list(crypto.SUPPORTED_SUITES),
                    "supported_pq_modes": [crypto.SIMULATED_PQ_MODE, crypto.NO_PQ_MODE],
                    "allow_classical_fallback": True,
                    "client_nonce": crypto.random_token(),
                    "note": "Client requests identity-bound flow establishment.",
                },
            )
        self.transcript = [self.init_packet]
        return self.init_packet

    def handle_init_ack(self, packet: dict[str, Any]) -> None:
        expected_transcript = crypto.transcript_hash(self.transcript)
        if packet["payload"].get("transcript_hash") != expected_transcript:
            raise crypto.CryptoError("INIT_ACK transcript hash mismatch.")
        self.transcript.append(packet)
        self.selected_suite = str(packet["payload"]["selected_suite"])
        self.selected_pq_mode = str(packet["payload"]["selected_pq_mode"])
        self.server_ephemeral_public = str(packet["payload"]["server_ephemeral_key"])
        self.server_pq_share = packet["payload"].get("server_pq_share")
        self.last_server_locator = str(packet["locator_hint"])

    def build_kem_exchange(self) -> dict[str, Any]:
        transcript_digest = crypto.transcript_hash(self.transcript)
        classical_secret = crypto.compute_shared_secret(self.client_ephemeral_private, self.server_ephemeral_public)
        mixed_secret = crypto.mix_secret(
            classical_secret,
            selected_pq_mode=self.selected_pq_mode,
            client_pq_share=self.client_pq_share,
            server_pq_share=self.server_pq_share,
        )
        self.keys = crypto.derive_keys(
            mixed_secret,
            session_id=self.session_id,
            client_node_id=self.identity.node_id,
            server_node_id=self.peer.node_id,
            transcript_digest=transcript_digest,
        )
        fields = {
            "session_id": self.session_id,
            "transcript_hash": transcript_digest,
            "client_node_id": self.identity.node_id,
            "server_node_id": self.peer.node_id,
            "selected_suite": self.selected_suite,
            "selected_pq_mode": self.selected_pq_mode,
            "client_ephemeral_key": self.client_ephemeral_public,
            "server_ephemeral_key": self.server_ephemeral_public,
            "client_pq_share": self.client_pq_share if self.selected_pq_mode == crypto.SIMULATED_PQ_MODE else None,
        }
        self.kem_packet = build_packet(
            KEM_EXCHANGE,
            session_id=self.session_id,
            source_node_id=self.identity.node_id,
            destination_node_id=self.peer.node_id,
            locator_hint=self.identity.locator,
            payload={
                "transcript_hash": transcript_digest,
                "client_pq_share": self.client_pq_share if self.selected_pq_mode == crypto.SIMULATED_PQ_MODE else None,
                "client_signature": crypto.sign_fields(self.identity.signing_private(), "KEM_EXCHANGE", fields),
                "key_confirmation": crypto.compute_mac(self.keys.handshake_key, "KEM_EXCHANGE", fields),
            },
        )
        return self.kem_packet

    def handle_auth(self, packet: dict[str, Any]) -> None:
        if self.kem_packet is None:
            raise PacketError("AUTH received before the client built KEM_EXCHANGE.")
        self.transcript.append(self.kem_packet)
        transcript_after_kem = crypto.transcript_hash(self.transcript)
        if packet["payload"].get("transcript_hash") != transcript_after_kem:
            raise crypto.CryptoError("AUTH transcript hash mismatch.")
        auth_fields = {
            "session_id": self.session_id,
            "flow_id": str(packet["flow_id"]),
            "transcript_hash": transcript_after_kem,
            "selected_suite": self.selected_suite,
            "selected_pq_mode": self.selected_pq_mode,
        }
        crypto.verify_fields(self.peer, "AUTH", auth_fields, str(packet["payload"]["server_signature"]))
        crypto.verify_mac(self.keys.handshake_key, "AUTH", auth_fields, str(packet["payload"]["key_confirmation"]))
        self.flow_id = str(packet["flow_id"])
        self.transcript.append(packet)

    def send_data(self, content: str) -> dict[str, Any]:
        sequence = self.next_client_sequence
        packet = build_packet(
            DATA,
            session_id=self.session_id,
            source_node_id=self.identity.node_id,
            destination_node_id=self.peer.node_id,
            locator_hint=self.identity.locator,
            flow_id=self.flow_id,
            sequence=sequence,
            payload={},
        )
        packet["payload"] = crypto.encrypt_payload(
            packet,
            self.keys.client_to_server_key,
            self.keys.client_to_server_iv,
            sequence,
            {"content": content, "sent_at": time.time()},
        )
        self.send_packet(packet)
        ack = self.receive_packet({DATA_ACK})
        sequence_reply = int(ack.get("sequence") or 0)
        plaintext = crypto.decrypt_payload(ack, self.keys.server_to_client_key, ack["payload"])
        self.next_client_sequence += 1
        self.next_server_sequence = max(self.next_server_sequence, sequence_reply + 1)
        return plaintext

    def perform_locator_update(self) -> dict[str, Any]:
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        new_sock.bind((DEFAULT_HOST, 0))
        new_sock.settimeout(self.timeout)
        new_host, new_port = new_sock.getsockname()
        new_locator = f"udp://{new_host}:{new_port}"
        previous_locator = self.identity.locator
        self.identity.locator = new_locator
        self.registry.register_locator(self.identity.node_id, new_locator, source="client-locator-update")
        self.sock.close()
        self.sock = new_sock
        fields = {
            "session_id": self.session_id,
            "flow_id": self.flow_id,
            "new_locator": new_locator,
            "previous_locator": previous_locator,
            "update_counter": self.locator_update_counter,
        }
        packet = build_packet(
            LOCATOR_UPDATE,
            session_id=self.session_id,
            source_node_id=self.identity.node_id,
            destination_node_id=self.peer.node_id,
            locator_hint=new_locator,
            flow_id=self.flow_id,
            sequence=self.locator_update_counter,
            payload={
                "new_locator": new_locator,
                "previous_locator": previous_locator,
                "update_counter": self.locator_update_counter,
                "signature": crypto.sign_fields(self.identity.signing_private(), "LOCATOR_UPDATE", fields),
                "update_mac": crypto.compute_mac(self.keys.update_key, "LOCATOR_UPDATE", fields),
            },
        )
        self.send_packet(packet)
        response = self.receive_packet({LOCATOR_UPDATE_ACK})
        crypto.verify_fields(self.peer, "LOCATOR_UPDATE_ACK", fields, str(response["payload"]["signature"]))
        crypto.verify_mac(self.keys.update_key, "LOCATOR_UPDATE_ACK", fields, str(response["payload"]["update_mac"]))
        self.locator_update_counter += 1
        return {
            "acknowledged_counter": response["payload"]["acknowledged_counter"],
            "active_locator": response["payload"]["active_locator"],
        }



def parse_locator(locator: str) -> tuple[str, int]:
    if not locator.startswith("udp://"):
        raise ValueError(f"Unsupported locator format: {locator}")
    host_port = locator.removeprefix("udp://")
    host, port = host_port.rsplit(":", 1)
    return host, int(port)
