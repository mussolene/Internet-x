"""Shared packet helpers for the educational Internet-X prototype."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

PROTOCOL_VERSION = 1
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080

INIT = "INIT"
INIT_ACK = "INIT_ACK"
KEM_EXCHANGE = "KEM_EXCHANGE"
AUTH = "AUTH"
DATA = "DATA"
DATA_ACK = "DATA_ACK"
ERROR = "ERROR"

PACKET_TYPES = {
    INIT,
    INIT_ACK,
    KEM_EXCHANGE,
    AUTH,
    DATA,
    DATA_ACK,
    ERROR,
}

HEADER_FIELDS = (
    "version",
    "packet_type",
    "flags",
    "header_length",
    "flow_id",
    "source_node_id",
    "destination_node_id",
    "locator_hint",
)

REQUIRED_FIELDS = HEADER_FIELDS + ("payload",)


class ProtocolError(ValueError):
    """Raised when a prototype packet is malformed."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def compute_header_length(packet: Mapping[str, Any]) -> int:
    """Return an advisory header length for the JSON prototype.

    The prototype is not a binary wire format. This number exists only to keep a
    header-length concept visible while the repository stays JSON-based.
    """

    header_only = {field: packet.get(field) for field in HEADER_FIELDS if field != "header_length"}
    return len(_canonical_json(header_only))


def make_packet(
    packet_type: str,
    *,
    source_node_id: str,
    destination_node_id: str,
    locator_hint: str,
    payload: Mapping[str, Any],
    flow_id: str | None = None,
    flags: list[str] | None = None,
    version: int = PROTOCOL_VERSION,
) -> dict[str, Any]:
    """Create a validated prototype packet."""

    if packet_type not in PACKET_TYPES:
        raise ProtocolError(f"Unsupported packet type: {packet_type}")
    if not isinstance(payload, Mapping):
        raise ProtocolError("Packet payload must be a mapping.")

    packet: dict[str, Any] = {
        "version": version,
        "packet_type": packet_type,
        "flags": list(flags or []),
        "header_length": 0,
        "flow_id": flow_id,
        "source_node_id": source_node_id,
        "destination_node_id": destination_node_id,
        "locator_hint": locator_hint,
        "payload": dict(payload),
    }
    packet["header_length"] = compute_header_length(packet)
    validate_packet(packet)
    return packet


def validate_packet(packet: Mapping[str, Any]) -> None:
    """Validate the common packet envelope."""

    missing = [field for field in REQUIRED_FIELDS if field not in packet]
    if missing:
        raise ProtocolError(f"Missing required packet fields: {', '.join(missing)}")
    if packet["packet_type"] not in PACKET_TYPES:
        raise ProtocolError(f"Unknown packet type: {packet['packet_type']}")
    if not isinstance(packet["payload"], Mapping):
        raise ProtocolError("Packet payload must be a JSON object.")
    if not isinstance(packet["flags"], list):
        raise ProtocolError("Packet flags must be a list.")


def encode_packet(packet: Mapping[str, Any]) -> bytes:
    """Serialize a packet to UTF-8 JSON."""

    validate_packet(packet)
    return _canonical_json(packet).encode("utf-8")


def decode_packet(encoded_packet: bytes | str) -> dict[str, Any]:
    """Deserialize a UTF-8 JSON packet and validate its envelope."""

    if isinstance(encoded_packet, bytes):
        encoded_packet = encoded_packet.decode("utf-8")
    try:
        packet = json.loads(encoded_packet)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Invalid JSON packet: {exc}") from exc
    if not isinstance(packet, dict):
        raise ProtocolError("Decoded packet must be a JSON object.")
    validate_packet(packet)
    return packet


def compute_transcript_hash(messages: Iterable[Any]) -> str:
    """Hash the ordered transcript using SHA-256."""

    canonical_messages = [_canonical_json(message) for message in messages]
    return hashlib.sha256("||".join(canonical_messages).encode("utf-8")).hexdigest()


def derive_flow_id(*components: Any) -> str:
    """Derive a readable educational FlowID from transcript and identity context."""

    return hashlib.sha256(_canonical_json(list(components)).encode("utf-8")).hexdigest()


def build_error_packet(
    *,
    source_node_id: str,
    destination_node_id: str,
    locator_hint: str,
    session_id: str | None,
    message: str,
    expected_packet_type: str | None = None,
) -> dict[str, Any]:
    """Create an ERROR packet for explicit failure reporting."""

    payload: dict[str, Any] = {"message": message}
    if session_id is not None:
        payload["session_id"] = session_id
    if expected_packet_type is not None:
        payload["expected_packet_type"] = expected_packet_type
    return make_packet(
        ERROR,
        source_node_id=source_node_id,
        destination_node_id=destination_node_id,
        locator_hint=locator_hint,
        payload=payload,
        flow_id=None,
    )


def summarize_packet(packet: Mapping[str, Any]) -> str:
    """Return a compact packet summary for logs."""

    session_id = packet.get("payload", {}).get("session_id", "-")
    flow_id = packet.get("flow_id") or "-"
    return (
        f"{packet['packet_type']} "
        f"session={session_id} flow={flow_id} "
        f"src={packet['source_node_id'][:12]} dst={packet['destination_node_id'][:12]}"
    )
