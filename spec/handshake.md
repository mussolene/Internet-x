# Internet-X Educational Handshake Reference

This document is the packet-by-packet handshake reference for the educational prototype in this repository. It describes the actual JSON packet format used by `prototype/client.py` and `prototype/server.py`.

It does not describe a production handshake. It does not claim real post-quantum security. Where future architecture could carry richer material such as real signatures or KEM ciphertexts, those items are explicitly marked as future extensions.

## 1. Common Packet Envelope

Every prototype packet is a JSON object with these top-level fields:

- `version`: protocol version integer
- `packet_type`: one of `INIT`, `INIT_ACK`, `KEM_EXCHANGE`, `AUTH`, `DATA`, `DATA_ACK`, `ERROR`
- `flags`: array of textual flags, usually empty in the prototype
- `header_length`: advisory header-length integer for the educational format
- `flow_id`: `null` before flow establishment, then a SHA-256-derived string
- `source_node_id`: sender `NodeID`
- `destination_node_id`: receiver `NodeID`
- `locator_hint`: sender reachability hint, represented as a string in the prototype
- `payload`: phase-specific JSON object

The transcript hash is maintained locally by each endpoint over the ordered sequence of JSON packets. When a packet contains a `payload.transcript_hash` field, that value represents the sender's view of the transcript before the current packet is appended.

`FlowID` is not established in `INIT` or `INIT_ACK`. It becomes meaningful after `AUTH`.

## 2. Phase: INIT

### Purpose

`INIT` starts a session and announces the initiating identity, locator hint, and supported handshake modes.

### Sender Behavior

The client:

- creates a fresh `session_id`
- sends its stable `source_node_id`
- includes its current locator hint
- announces supported modes such as `hybrid-simulated` and `classical-simulated`
- sends simulated ephemeral or public material for educational tracing

### Receiver Behavior

The server:

- validates that the packet is well-formed JSON
- records the `session_id`
- stores the client `NodeID` and locator hint for the session
- starts the transcript with the `INIT` packet
- chooses a response mode for `INIT_ACK`

### Expected Fields

Top-level:

- `packet_type = "INIT"`
- `flow_id = null`

Payload:

- `session_id`
- `sender_name`
- `algorithm_id`
- `supported_modes`
- `client_nonce`
- `client_key_material`
- `note`

### Transcript Hash Impact

`INIT` starts the transcript. The packet itself does not carry a `transcript_hash` field.

### Flow Establishment Impact

No `FlowID` is established yet.

### Hybrid PQ/Classical Behavior

The client advertises supported modes. In the prototype those are descriptive strings only.

### Fallback Behavior

If the packet is malformed or cannot be parsed, the server sends `ERROR` or drops the packet. If the preferred hybrid mode is not supported, the server may select `classical-simulated` in `INIT_ACK`.

### Architectural Future Extension

Future versions may attach real algorithm negotiation objects, certificates, or authenticated capability descriptors. Those are not required in the prototype.

## 3. Phase: INIT_ACK

### Purpose

`INIT_ACK` acknowledges the session start and binds the server's response to the transcript containing `INIT`.

### Sender Behavior

The server:

- looks up or creates session state for the received `session_id`
- computes the transcript hash over the current transcript containing `INIT`
- selects a handshake mode
- returns simulated server key material

### Receiver Behavior

The client:

- validates the matching `session_id`
- records the selected mode
- appends the packet to its transcript
- prepares `KEM_EXCHANGE`

### Expected Fields

Top-level:

- `packet_type = "INIT_ACK"`
- `flow_id = null`

Payload:

- `session_id`
- `selected_mode`
- `server_nonce`
- `server_key_material`
- `transcript_hash`
- `note`

### Transcript Hash Impact

`payload.transcript_hash` covers the transcript up to and including `INIT`.

### Flow Establishment Impact

No `FlowID` is established yet.

### Hybrid PQ/Classical Behavior

The server indicates whether the educational session proceeds in `hybrid-simulated` or `classical-simulated` mode.

### Fallback Behavior

If the `session_id` is unknown or the packet cannot be matched to current state, the client aborts. If the server cannot support the advertised hybrid mode, it selects classical fallback.

### Architectural Future Extension

Future versions may carry server capabilities, signature suites, or KEM preferences. Those are not present in the prototype.

## 4. Phase: KEM_EXCHANGE

### Purpose

`KEM_EXCHANGE` carries simulated key-establishment material and binds the client to the transcript observed so far.

### Sender Behavior

The client:

- computes the transcript hash over `INIT` and `INIT_ACK`
- includes simulated classical and post-quantum share placeholders
- sends the current `session_id`

### Receiver Behavior

The server:

- validates the `session_id`
- checks that `payload.transcript_hash` matches its local transcript view
- appends the packet to the transcript
- derives a provisional authenticated flow context
- replies with `AUTH`

### Expected Fields

Top-level:

- `packet_type = "KEM_EXCHANGE"`
- `flow_id = null`

Payload:

- `session_id`
- `encapsulated_key_material`
- `classical_share`
- `pq_share`
- `transcript_hash`
- `note`

### Transcript Hash Impact

`payload.transcript_hash` covers the transcript through `INIT_ACK`, before `KEM_EXCHANGE` is appended.

### Flow Establishment Impact

No final `FlowID` is exposed in this packet, but the material needed to derive flow state is now available to the receiver.

### Hybrid PQ/Classical Behavior

The packet carries placeholders for both a classical share and a post-quantum share. In the prototype these are strings and must be understood as simulation only.

### Fallback Behavior

If transcript binding fails, the receiver sends `ERROR`. If hybrid mode is unavailable, the server may ignore the post-quantum placeholder and continue in classical fallback while preserving the packet phase name.

### Architectural Future Extension

A fuller architecture could carry real KEM ciphertexts or hybrid composition structures. Those are intentionally not part of the educational prototype.

## 5. Phase: AUTH

### Purpose

`AUTH` confirms that the server accepts the session and publishes the derived `FlowID` for subsequent data packets.

### Sender Behavior

The server:

- computes the transcript hash over `INIT`, `INIT_ACK`, and `KEM_EXCHANGE`
- derives a `FlowID` from session and transcript context
- sends a simulated authentication proof and the selected `FlowID`

### Receiver Behavior

The client:

- validates the `session_id`
- records the returned `FlowID`
- appends the packet to the transcript
- uses the `FlowID` when sending `DATA`

### Expected Fields

Top-level:

- `packet_type = "AUTH"`
- `flow_id` set to the new `FlowID`

Payload:

- `session_id`
- `auth_result`
- `flow_id`
- `transcript_hash`
- `auth_proof`
- `note`

### Transcript Hash Impact

`payload.transcript_hash` covers the transcript through `KEM_EXCHANGE`, before `AUTH` is appended.

### Flow Establishment Impact

`AUTH` establishes the flow context used by `DATA` and `DATA_ACK`.

### Hybrid PQ/Classical Behavior

The authentication proof is simulated, but the phase exists to represent where a real hybrid authentication result would become binding.

### Fallback Behavior

If transcript verification fails or the session is unknown, the server sends `ERROR`. If the selected mode is classical fallback, the `FlowID` is still derived, but the packet note makes clear that the educational session is not a real secure channel.

### Architectural Future Extension

Future versions could carry real signatures, certificates, or multi-algorithm authentication proofs. Those do not exist in the prototype.

## 6. Phase: DATA

### Purpose

`DATA` carries application data once the flow has been established.

### Sender Behavior

The client:

- sends `DATA` using the established `FlowID`
- includes a transcript hash representing the transcript through `AUTH`
- includes the application content in the payload

### Receiver Behavior

The server:

- validates the `session_id` and `flow_id`
- checks that the transcript hash matches the local transcript through `AUTH`
- appends `DATA` to the transcript
- returns `DATA_ACK`

### Expected Fields

Top-level:

- `packet_type = "DATA"`
- `flow_id` set to the established `FlowID`

Payload:

- `session_id`
- `content`
- `transcript_hash`

### Transcript Hash Impact

`payload.transcript_hash` covers the transcript through `AUTH`, before `DATA` is appended.

### Flow Establishment Impact

`DATA` uses an already-established `FlowID`; it does not create a new one.

### Hybrid PQ/Classical Behavior

The mode chosen earlier remains descriptive context only. No real encryption is performed in the prototype.

### Fallback Behavior

If the `FlowID` is absent or inconsistent, the server sends `ERROR`. The server then avoids silently hanging the client by either returning `DATA_ACK` or returning an explicit error packet.

### Architectural Future Extension

Future versions may define integrity tags, encryption framing, rekey logic, or mobility-related data continuation behavior. Those are not part of the prototype.

## 7. Post-Data Packet: DATA_ACK

`DATA_ACK` is not one of the required five handshake phases. It is a post-data acknowledgement used by the educational prototype to make the end-to-end flow observable and to avoid client hangs.

Expected payload fields:

- `session_id`
- `status`
- `flow_id`
- `received_bytes`
- `transcript_hash`
- `note`

The `transcript_hash` in `DATA_ACK` covers the transcript through the received `DATA` packet, before `DATA_ACK` itself is appended.

## 8. Error Packet: ERROR

The prototype uses an `ERROR` packet rather than silent failure when it can identify a parse, session, flow, or transcript mismatch.

Expected payload fields:

- `session_id` when known
- `message`
- `expected_packet_type` when helpful

`ERROR` packets are educational diagnostics and must not be interpreted as secure alerts.
