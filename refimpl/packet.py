"""Packet model for the Internet-X reference implementation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping

PROTOCOL_VERSION = 2
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9080
DEFAULT_LOCATOR = f"udp://{DEFAULT_HOST}:{DEFAULT_PORT}"

INIT = "INIT"
INIT_ACK = "INIT_ACK"
KEM_EXCHANGE = "KEM_EXCHANGE"
AUTH = "AUTH"
DATA = "DATA"
DATA_ACK = "DATA_ACK"
LOCATOR_UPDATE = "LOCATOR_UPDATE"
LOCATOR_UPDATE_ACK = "LOCATOR_UPDATE_ACK"
ERROR = "ERROR"

PACKET_TYPES = {
    INIT,
    INIT_ACK,
    KEM_EXCHANGE,
    AUTH,
    DATA,
    DATA_ACK,
    LOCATOR_UPDATE,
    LOCATOR_UPDATE_ACK,
    ERROR,
}

HEADER_FIELDS = (
    "version",
    "packet_type",
    "flags",
    "header_length",
    "session_id",
    "flow_id",
    "sequence",
    "source_node_id",
    "destination_node_id",
    "locator_hint",
)

AAD_FIELDS = (
    "version",
    "packet_type",
    "flags",
    "session_id",
    "flow_id",
    "sequence",
    "source_node_id",
    "destination_node_id",
    "locator_hint",
)

REQUIRED_FIELDS = HEADER_FIELDS + ("payload",)


class PacketError(ValueError):
    """Raised when a packet is malformed."""


@dataclass(slots=True)
class PacketTrace:
    direction: str
    packet: dict[str, Any]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def compute_header_length(packet: Mapping[str, Any]) -> int:
    header = {field: packet.get(field) for field in HEADER_FIELDS if field != "header_length"}
    return len(canonical_json(header))


def build_packet(
    packet_type: str,
    *,
    session_id: str,
    source_node_id: str,
    destination_node_id: str,
    locator_hint: str,
    payload: Mapping[str, Any],
    flow_id: str | None = None,
    sequence: int | None = None,
    flags: list[str] | None = None,
    version: int = PROTOCOL_VERSION,
) -> dict[str, Any]:
    if packet_type not in PACKET_TYPES:
        raise PacketError(f"Unsupported packet type: {packet_type}")
    if not isinstance(payload, Mapping):
        raise PacketError("Packet payload must be a mapping.")
    packet: dict[str, Any] = {
        "version": version,
        "packet_type": packet_type,
        "flags": list(flags or []),
        "header_length": 0,
        "session_id": session_id,
        "flow_id": flow_id,
        "sequence": sequence,
        "source_node_id": source_node_id,
        "destination_node_id": destination_node_id,
        "locator_hint": locator_hint,
        "payload": dict(payload),
    }
    packet["header_length"] = compute_header_length(packet)
    validate_packet(packet)
    return packet


def validate_packet(packet: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in packet]
    if missing:
        raise PacketError(f"Missing packet fields: {', '.join(missing)}")
    if packet["packet_type"] not in PACKET_TYPES:
        raise PacketError(f"Unknown packet type: {packet['packet_type']}")
    if not isinstance(packet["payload"], Mapping):
        raise PacketError("Packet payload must be a JSON object.")
    if not isinstance(packet["flags"], list):
        raise PacketError("Packet flags must be a JSON list.")
    if not isinstance(packet["version"], int):
        raise PacketError("Packet version must be an integer.")
    if not isinstance(packet["session_id"], str) or not packet["session_id"]:
        raise PacketError("session_id must be a non-empty string.")



def encode_packet(packet: Mapping[str, Any]) -> bytes:
    validate_packet(packet)
    return canonical_json(packet).encode("utf-8")



def decode_packet(raw: bytes | str) -> dict[str, Any]:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PacketError(f"Invalid JSON packet: {exc}") from exc
    if not isinstance(decoded, dict):
        raise PacketError("Decoded packet must be a JSON object.")
    validate_packet(decoded)
    return decoded



def packet_aad(packet: Mapping[str, Any]) -> bytes:
    header = {field: packet.get(field) for field in AAD_FIELDS}
    return canonical_json(header).encode("utf-8")



def summarize_packet(packet: Mapping[str, Any]) -> str:
    session_id = str(packet.get("session_id", "-"))[:12]
    flow_id = str(packet.get("flow_id") or "-")[:12]
    sequence = packet.get("sequence")
    return (
        f"{packet['packet_type']} session={session_id} flow={flow_id} seq={sequence} "
        f"src={str(packet['source_node_id'])[:12]} dst={str(packet['destination_node_id'])[:12]}"
    )
