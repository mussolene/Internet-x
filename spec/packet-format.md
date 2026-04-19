# Internet-X Packet Format

This document defines a simple packet model aligned with the Internet-X architecture and explains how the educational prototype serializes that model as JSON.

The key design rule is that packet fields representing identity and reachability must not be collapsed into short fixed-size placeholders that contradict the architecture.

## 1. Architectural Wire Model

The architectural packet model is:

```text
+------------------+-----------------------------------------------+
| Field            | Meaning                                       |
+------------------+-----------------------------------------------+
| Version          | Protocol version identifier                   |
| PacketType       | Handshake, control, or data packet type       |
| Flags            | Packet-processing flags                       |
| HeaderLength     | Length of the packet header                   |
| FlowID           | Flow/session identifier                       |
| SourceNodeID     | Source cryptographic identity                 |
| DestinationNodeID| Destination cryptographic identity            |
| LocatorHint      | Current reachability information              |
| Payload          | Packet-specific content                       |
+------------------+-----------------------------------------------+
```

### 1.1 Field Requirements

`Version`

- identifies the Internet-X protocol version in use

`PacketType`

- identifies packets such as `INIT`, `INIT_ACK`, `KEM_EXCHANGE`, `AUTH`, `DATA`, `DATA_ACK`, or `ERROR`

`Flags`

- carries per-packet processing modifiers
- is extensible and may be empty

`HeaderLength`

- indicates the size of the header in an eventual structured wire encoding
- remains present in the prototype as an advisory field for consistency

`FlowID`

- identifies a session or sub-session context
- must be stronger than a trivial 32-bit token
- may be represented architecturally as at least a 64-bit-equivalent opaque value or a longer digest-derived identifier

`SourceNodeID` and `DestinationNodeID`

- are cryptographic identities, not addresses
- are variable-length values
- must be large enough to represent `NodeID = HASH(algorithm_id || public_key)` without collapsing to unrealistic fixed-width placeholders

`LocatorHint`

- carries current reachability information
- is variable-length
- may include an overlay locator, address-plus-port tuple, ingress identifier, or other structured reachability hint
- must not be treated as equivalent to `NodeID`

`Payload`

- is packet-type specific
- may contain handshake metadata, transcript bindings, or application data

### 1.2 Architectural Notes

The previous fixed-width model of 4-byte `SourceNodeID`, `DestinationNodeID`, `LocatorHint`, and `FlowID` is rejected for this architecture because:

- a cryptographic `NodeID` is not realistically 4 bytes
- a `Locator` is structurally variable and environment dependent
- a serious `FlowID` should not signal weakness through a 32-bit limit

## 2. Prototype Serialization Model

The educational prototype uses JSON serialization for readability and inspection.

Each packet is a JSON object with these keys:

- `version`
- `packet_type`
- `flags`
- `header_length`
- `flow_id`
- `source_node_id`
- `destination_node_id`
- `locator_hint`
- `payload`

### 2.1 Example Prototype Packet

```json
{
  "version": 1,
  "packet_type": "AUTH",
  "flags": [],
  "header_length": 214,
  "flow_id": "5ca6d7f1bb651f4564488c913740f77b1f4b5932e9517ebc2c62f7d932f5599c",
  "source_node_id": "4707f719ffb2e8f9d02d5ab1e21602cc53f63a8cf8b91c09363d39f0db6be5dd",
  "destination_node_id": "8458e997fe8ecf2ec8e1ef5b0d0fd4482d4addfdb85ca3900f4fb93d08d985ef",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "auth_result": "accepted",
    "flow_id": "5ca6d7f1bb651f4564488c913740f77b1f4b5932e9517ebc2c62f7d932f5599c",
    "transcript_hash": "c632b2a9925c4756f9b407f2ab5d20f3eac9ca2287302447a246e43ef95f0d10",
    "auth_proof": "simulated-server-auth-binding",
    "note": "Educational authentication result only."
  }
}
```

### 2.2 Prototype Field Semantics

`flow_id`

- is `null` before `AUTH`
- becomes a SHA-256-derived hex string after flow establishment

`source_node_id` and `destination_node_id`

- are variable-length hex strings derived from simulated identity material

`locator_hint`

- is a variable-length string such as `udp://localhost:8080`

`payload`

- contains the phase-specific handshake or data fields documented in `spec/handshake.md`

## 3. Relationship Between Architecture and Prototype

The architectural wire model is the serious design target.
The prototype JSON model is the educational serialization used in this repository today.

That means:

- the JSON form is intentionally readable rather than compact
- `header_length` is informative rather than a hard parsing requirement
- no claim is made that the JSON layout is a final or efficient wire format
- the identity and locator semantics still reflect the architecture even in the simplified prototype

## 4. Serialization Guidance

Implementations in this repository should:

- treat `NodeID` as distinct from `Locator`
- treat `FlowID` as a strong, non-trivial identifier
- keep packet-type names stable across documents and code
- prefer explicit fields over ambiguous overloaded ones

The prototype therefore uses one shared serialization module for packet encoding, decoding, transcript hashing, and `FlowID` derivation.
