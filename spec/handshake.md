# Handshake

The reference handshake preserves the required five phases:

1. `INIT`
2. `INIT_ACK`
3. `KEM_EXCHANGE`
4. `AUTH`
5. `DATA`

`DATA_ACK` acknowledges application data after the five-phase establishment sequence. Locator migration is handled through separate `LOCATOR_UPDATE` control packets.

## Phase 1: INIT

Purpose:

- announce client identity material
- start the transcript
- advertise supported classical suite and PQ mode choices

Payload fields:

- `sender_name`
- `identity_algorithm`
- `signing_public_key`
- `client_ephemeral_key`
- `supported_suites`
- `supported_pq_modes`
- `allow_classical_fallback`
- `client_nonce`
- `note`

Receiver behavior:

- verify `NodeID` matches the advertised signing public key
- select a mutually supported classical suite
- either select `simulated-ml-kem-768` or fall back to `none` if allowed

## Phase 2: INIT_ACK

Purpose:

- return server identity material
- bind the response to the transcript containing `INIT`
- advertise the selected suite and PQ mode

Payload fields:

- `sender_name`
- `identity_algorithm`
- `signing_public_key`
- `server_ephemeral_key`
- `server_pq_share` or `null`
- `selected_suite`
- `selected_pq_mode`
- `fallback_used`
- `server_nonce`
- `transcript_hash`
- `note`

Receiver behavior:

- verify `transcript_hash`
- record selected suite and server ephemeral material

## Phase 3: KEM_EXCHANGE

Purpose:

- prove possession of the client identity key
- prove that the client sees the same transcript as the server
- complete the material needed for the session secret

Payload fields:

- `transcript_hash`
- `client_pq_share` or `null`
- `client_signature`
- `key_confirmation`

Receiver behavior:

- verify transcript hash against local state
- derive the mixed secret from X25519 and, if selected, simulated PQ shares
- verify client signature and handshake MAC

## Phase 4: AUTH

Purpose:

- publish the authenticated `FlowID`
- prove server possession of the server identity key and handshake keys

Payload fields:

- `auth_result`
- `selected_suite`
- `selected_pq_mode`
- `fallback_used`
- `transcript_hash`
- `server_signature`
- `key_confirmation`
- `note`

Receiver behavior:

- verify transcript hash through `KEM_EXCHANGE`
- verify server signature and handshake MAC
- accept `flow_id`

## Phase 5: DATA

Purpose:

- send encrypted application data on the established flow

Header requirements:

- `flow_id` is mandatory
- `sequence` is mandatory and monotonic per sender

Payload fields:

- `nonce`
- `ciphertext`

Receiver behavior:

- reject packets with an unexpected sequence from an unauthenticated flow state
- handle an exact duplicate of an already acknowledged sequence idempotently by re-sending the cached `DATA_ACK` without re-delivering the payload
- reject packets from a locator that has not been authenticated as current
- decrypt using the direction-specific AEAD key

## DATA_ACK

Purpose:

- acknowledge delivery of application data

Payload fields:

- `nonce`
- `ciphertext`

The encrypted plaintext includes:

- `status`
- `acked_sequence`
- `received_bytes`
- `server_time`

## Transcript Binding

The transcript hash is computed over canonical JSON packet representations. The reference implementation binds the transcript at three points:

- `INIT_ACK` covers the transcript through `INIT`
- `KEM_EXCHANGE` covers the transcript through `INIT_ACK`
- `AUTH` covers the transcript through `KEM_EXCHANGE`

## Hybrid And Fallback Semantics

- `simulated-ml-kem-768` means the session derivation includes simulated PQ shares in addition to the real classical shared secret.
- `none` means the session uses only the real classical baseline.
- `fallback_used = true` is explicit whenever the peer offered PQ but the final mode is classical-only.

The current repository does not implement real ML-KEM. The hybrid branch is a transition hook, not a quantum-safe claim.
