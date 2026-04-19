# Packet Format

Internet-X v0.2 uses a readable JSON packet envelope in the reference implementation. The architecture still distinguishes packet semantics from serialization choices.

## Common Envelope

Every packet carries these top-level fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `version` | integer | protocol version |
| `packet_type` | string | control or data packet type |
| `flags` | list of strings | extensible packet modifiers |
| `header_length` | integer | advisory length of the common header in JSON form |
| `session_id` | string | session handle established at `INIT` |
| `flow_id` | string or `null` | flow handle established at `AUTH` |
| `sequence` | integer or `null` | data or control sub-sequence number |
| `source_node_id` | string | sender identity digest |
| `destination_node_id` | string | intended peer identity digest |
| `locator_hint` | string | sender's current locator |
| `payload` | object | packet-specific fields |

## Packet Types

- `INIT`
- `INIT_ACK`
- `KEM_EXCHANGE`
- `AUTH`
- `DATA`
- `DATA_ACK`
- `LOCATOR_UPDATE`
- `LOCATOR_UPDATE_ACK`
- `ERROR`

## Architectural Interpretation

The JSON form should not be mistaken for the final wire-image requirement. Architecturally:

- `NodeID` is a stable identity token derived from public key material.
- `LocatorHint` is mutable reachability information.
- `FlowID` is bound to authenticated transcript context, not to the locator alone.
- `Path` selection is an architectural layer above the locator and is out of scope for the current reference implementation.

## Header Visibility

Internet-X intentionally keeps the common packet header visible even when payloads are encrypted. This supports inspectability and debugging, but it also leaks metadata and therefore has privacy costs.
