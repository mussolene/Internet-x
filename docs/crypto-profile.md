# Crypto Profile

## Current Reference Profile

The reference implementation uses a real classical secure baseline and a simulated PQ extension point.

### Identity And Authentication

- identity signing algorithm: Ed25519
- `NodeID` derivation: `SHA-256(algorithm_id || signing_public_key_b64)`
- mutual authentication: signatures over transcript-bound handshake fields

### Session Establishment

- classical KEX: X25519 ephemeral Diffie-Hellman
- transcript hash: SHA-256 over canonical JSON packet transcript
- key derivation: HKDF-SHA256
- handshake key confirmation: HMAC-SHA256 over transcript-bound context

### Data Protection

- AEAD: ChaCha20-Poly1305
- per-direction keys: derived separately for client-to-server and server-to-client traffic
- replay handling: monotonic per-flow sequence numbers in `DATA` packets

### Locator Update Protection

- Ed25519 signature over locator update fields
- HMAC-SHA256 using a dedicated update key derived from the session secret

## Simulated PQ Layer

The reference implementation supports two advertised modes:

- `simulated-ml-kem-768`
- `none`

When `simulated-ml-kem-768` is selected, both peers exchange simulated PQ shares and mix a digest of those shares into the session derivation context. This improves architectural fidelity for the transition model, but it is not real ML-KEM.

## Why This Profile Was Chosen

- Ed25519, X25519, HKDF-SHA256, and ChaCha20-Poly1305 are widely available and easy to reason about.
- The implementation remains readable and inspectable.
- The classical baseline is strong enough to support honest statements about authenticated and encrypted flows.
- PQ readiness is documented without pretending that this repository already provides quantum-resistant security.

## Out-Of-Scope For The Current Code

- certificate chains or PKI integration
- resumption tickets
- forward-secret locator update keys beyond the per-session derivation
- post-quantum signature verification
- side-channel hardening
