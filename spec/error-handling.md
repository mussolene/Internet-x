# Error Handling

## ERROR Packet

`ERROR` is used when a peer can identify a protocol failure and wishes to fail explicitly.

Payload fields:

- `message`
- `expected_packet_type` when relevant

## Current Error Cases

- malformed packet or invalid JSON
- unsupported classical suite
- unsupported required PQ mode
- transcript mismatch
- signature verification failure
- MAC verification failure
- wrong `flow_id`
- stale locator update counter
- `DATA` packet from a locator that has not been authenticated as current

## Failure Discipline

The reference implementation prefers explicit failure to silent acceptance. It is intentionally strict because the repository values state-machine clarity over permissive interop hacks.
